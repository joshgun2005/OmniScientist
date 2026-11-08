# -*- coding: utf-8 -*-
"""Единственная эконометрическая модель ВКР: годовая панель «страна — год».

Идея в одной фразе: цена экспортной партии равна мировому бенчмарку плюс
контрактный дифференциал; поэтому цена российской нефти объясняется через
Brent и контрактный режим (санкции, потолок цен), а цена азербайджанской —
через тот же Brent и её контрактный ориентир — бюджетную цену АЧГ.

Уравнение (МНК по годовой панели, 2018—2025 гг., 16 наблюдений):

    P = a + b_AZ · (Brent · AZ) + b_RU · (Brent · RU)
          + c_RU · RU + d_S · SANCTIONS + d_C · CAP + d_B · (BUDGET − Brent) + u,

    P        — среднегодовая цена экспорта, долл./барр.;
    Brent    — среднегодовая котировка, долл./барр.;
    RU       — 1 для России, 0 для Азербайджана;
    SANCTIONS — 1 для России в 2022 г. (санкционный режим до потолка цен);
    CAP      — 1 для России в 2023—2025 гг. (действует потолок цен);
    BUDGET   — бюджетная (контрактная) цена нефти Азербайджана, долл./барр.

На контрактном блоке оценивается также уравнение выручки:
    REV = f(объём поставки, цена по контракту), — см. блок 6.

Все результаты сохраняются в out/model.json; документ собирается из него,
поэтому «ручных» чисел в тексте нет. Запуск: python3 model.py
"""
import json
import os

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy import stats
from statsmodels.stats.diagnostic import (
    acorr_breusch_godfrey, het_breuschpagan, linear_reset)
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.stats.stattools import durbin_watson, jarque_bera

from facts_panel import FACTS, SOURCE_OF

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "out")
DATA = os.path.join(BASE, "data", "panel_annual.csv")

BBL_PER_T = 7.33          # баррелей в тонне (формула (16) главы 1)
FORMULA = ("price ~ AZ_BR + RU_BR + RU + SANCTIONS + CAP + AZ_BUDGET")
Y0, Y1 = 2018, 2025       # окно сбалансированной панели
RATE = 92.2               # среднегодовой курс, руб./долл. (бюджет 2026 г.)

YEARS_RU = list(range(2013, 2026))


# --------------------------------------------------------------------- данные
def load():
    df = pd.read_csv(DATA)
    df["RU"] = (df["country"] == "RUS").astype(int)
    df["AZ"] = 1 - df["RU"]
    df["D"] = df["price"] - df["brent"]
    df["AZ_BR"] = df["AZ"] * df["brent"]
    df["RU_BR"] = df["RU"] * df["brent"]
    df["AZ_BUDGET"] = df["AZ"] * (df["budget_price"] - df["brent"])
    df["SANCTIONS"] = ((df["RU"] == 1) & (df["year"] == 2022)).astype(int)
    df["CAP"] = ((df["RU"] == 1) & (df["year"] >= 2023)).astype(int)
    return df.sort_values(["year", "country"]).reset_index(drop=True)


def panel(df, y0=Y0, y1=Y1):
    """Сбалансированная панель: обе страны за каждый год окна."""
    p = df[(df.year >= y0) & (df.year <= y1)].copy()
    assert p.groupby("year").size().eq(2).all(), "панель несбалансирована"
    assert p.groupby("country").size().eq(y1 - y0 + 1).all()
    return p.reset_index(drop=True)


# ------------------------------------------------------------------ оценивание
def fit_ols(formula, data, cov="HC1"):
    m = smf.ols(formula, data).fit(cov_type=cov)
    rows = []
    ci = m.conf_int()
    for name in m.params.index:
        rows.append(dict(
            var=name, coef=float(m.params[name]), se=float(m.bse[name]),
            t=float(m.tvalues[name]), p=float(m.pvalues[name]),
            ci_lo=float(ci.loc[name, 0]), ci_hi=float(ci.loc[name, 1])))
    fit = dict(n=int(m.nobs), r2=float(m.rsquared), r2_adj=float(m.rsquared_adj),
               r2_within=None, f=float(m.fvalue), f_p=float(m.f_pvalue),
               sigma=float(np.sqrt(m.mse_resid)), aic=float(m.aic),
               bic=float(m.bic), k=int(len(m.params)), df_resid=int(m.df_resid))
    return m, rows, fit


def chow(m_small, m_big, n_big, k_big, name=""):
    """F-тест Чоу: сравнение усечённой и полной спецификации."""
    q = k_big - len(m_small.params)
    rss_s, rss_b = float(m_small.ssr), float(m_big.ssr)
    df2 = n_big - k_big
    F = ((rss_s - rss_b) / q) / (rss_b / df2)
    p = float(1 - stats.f.cdf(F, q, df2))
    return dict(F=float(F), df1=int(q), df2=int(df2), p=p, name=name)


def block_test(restricted_formula, full_formula, data):
    small = smf.ols(restricted_formula, data).fit()
    big = smf.ols(full_formula, data).fit()
    return chow(small, big, int(big.nobs), len(big.params),
                name="усечённая спецификация")


def desc(df, mask, label):
    s = df[mask]
    return dict(label=label, n=int(len(s)), P=float(s.price.mean()),
                brent=float(s.brent.mean()), D=float(s.D.mean()),
                budget=float(s.budget_price.mean()) if s.budget_price.any() else None,
                q=float(s.q_export_mt.mean()))


def diagnostics(m, data, formula):
    resid = m.resid.values
    exog = m.model.exog
    names = list(m.model.exog_names)
    bp = het_breuschpagan(resid, exog)
    bg = acorr_breusch_godfrey(m, nlags=1, store=False)
    jb = jarque_bera(resid)
    r = linear_reset(m, power=2, use_f=True)
    vif = [variance_inflation_factor(exog, i) for i in range(1, exog.shape[1])]
    return dict(bp_lm=float(bp[0]), bp_p=float(bp[1]), bg_lm=float(bg[0]),
                bg_p=float(bg[1]), jb=float(jb[0]), jb_p=float(jb[1]),
                dw=float(durbin_watson(resid)), reset_F=float(r.fvalue),
                reset_p=float(r.pvalue), max_vif=float(max(vif)),
                vif=dict(zip(names[1:], [round(float(v), 2) for v in vif])))


def accuracy(rows_df, preds):
    a = np.abs(rows_df["price"].values - preds)
    rel = np.abs(a / rows_df["price"].values) * 100
    return dict(mae=float(a.mean()), max_abs=float(a.max()),
                mape_price=float(rel.mean()),
                mape_max=float(rel.max()))


def loo_cv(formula, data):
    """Leave-one-out: насколько оценка k держится без каждого наблюдения."""
    est = []
    for i in range(len(data)):
        sub = data.drop(index=i)
        m = smf.ols(formula, sub).fit()
        if "CAP" not in m.params:
            continue
        est.append(dict(year=int(data.loc[i, "year"]),
                        country=data.loc[i, "country"],
                        cap=float(m.params["CAP"]),
                        p=float(m.pvalues["CAP"])))
    return dict(cases=est, n=len(est),
                cap_min=float(min(e["cap"] for e in est)),
                cap_max=float(max(e["cap"] for e in est)),
                max_p=float(max(e["p"] for e in est)),
                argmin_year=int(max(est, key=lambda e: abs(e["cap"]))["year"]))


def placebo(cap_year, data):
    """Попытка сдвинуть дату потолка: потолок «введён» в другом году."""
    d = data.copy()
    d["CAP_P"] = ((d.RU == 1) & (d.year >= cap_year)).astype(int)
    m = smf.ols("price ~ AZ_BR + RU_BR + RU + SANCTIONS + CAP_P + AZ_BUDGET",
                d).fit(cov_type="HC1")
    return dict(cap_year=int(cap_year), coef=float(m.params["CAP_P"]),
                se=float(m.bse["CAP_P"]), p=float(m.pvalues["CAP_P"]),
                r2_adj=float(m.rsquared_adj))


def contract_block(df):
    """Контрактный блок: проверка того, что цены — формульные, а объёмы — контрактные.

    Три проверки, каждая на своих данных:
      1) постоянство премии Azeri Light к Brent: если цена формируется по
         формуле «Brent + премия», наклон тренда премии равен нулю;
      2) эластичность физического экспорта по цене: по долгосрочным контрактам
         объём фиксирован, поэтому эластичность должна быть близка к нулю, —
         тогда выручка меняется за счёт цены, а не количества;
      3) разложение изменения выручки 2018 -> 2025 на ценовой и объёмный эффекты.
    """
    p = df[(df.year >= Y0) & (df.year <= Y1)].copy()
    p["REV"] = p["price"] * p["q_export_mt"] * BBL_PER_T / 1000   # млрд долл.
    p["lnQ"] = np.log(p["q_export_mt"])
    p["lnP"] = np.log(p["price"])

    # 1) премия Azeri Light: константа и тренд
    aze = p[p.AZ == 1].copy()
    aze["t"] = aze.year - Y0
    prem = smf.ols("D ~ t", aze).fit(cov_type="HC1")
    prem0 = smf.ols("D ~ 1", aze).fit(cov_type="HC1")
    premium = dict(mean=float(aze.D.mean()), sd=float(aze.D.std(ddof=1)),
                   slope=float(prem.params["t"]), slope_se=float(prem.bse["t"]),
                   slope_p=float(prem.pvalues["t"]),
                   min=float(aze.D.min()), max=float(aze.D.max()),
                   r2=float(prem.rsquared), const_ci_lo=float(prem0.conf_int().loc["Intercept", 0]),
                   const_ci_hi=float(prem0.conf_int().loc["Intercept", 1]))

    # 2) эластичность объёма экспорта по цене (раздельно по странам)
    vol = smf.ols("lnQ ~ lnP + RU + lnP:RU", p).fit(cov_type="HC1")
    vol_s = {c: float(smf.ols("lnQ ~ lnP", p[p.country == c]).fit().params["lnP"])
             for c in ("RUS", "AZE")}
    vol_p = {c: float(smf.ols("lnQ ~ lnP", p[p.country == c]).fit().pvalues["lnP"])
             for c in ("RUS", "AZE")}
    volume = dict(
        az=float(vol.params["lnP"]), az_se=float(vol.bse["lnP"]),
        az_p=float(vol.pvalues["lnP"]),
        ru=float(vol.params["lnP"] + vol.params["lnP:RU"]),
        ru_se=float(vol.bse["lnP"] + vol.bse["lnP:RU"]),
        ru_p=float(vol.pvalues["lnP:RU"]),
        r2=float(vol.rsquared), r2_adj=float(vol.rsquared_adj),
        simple=vol_s, simple_p=vol_p)

    # 3) разложение изменения выручки
    a = p[p.year == Y0].set_index("country")
    b = p[p.year == Y1].set_index("country")
    dec = {}
    for c in ("RUS", "AZE"):
        dec[c] = dict(
            rev_0=float(a.loc[c, "REV"]), rev_1=float(b.loc[c, "REV"]),
            q_0=float(a.loc[c, "q_export_mt"]), q_1=float(b.loc[c, "q_export_mt"]),
            p_0=float(a.loc[c, "price"]), p_1=float(b.loc[c, "price"]),
            rev_change=float(b.loc[c, "REV"] - a.loc[c, "REV"]),
            price_effect=float((b.loc[c, "price"] - a.loc[c, "price"])
                               * b.loc[c, "q_export_mt"] * BBL_PER_T / 1000),
            volume_effect=float((b.loc[c, "q_export_mt"] - a.loc[c, "q_export_mt"])
                                * b.loc[c, "price"] * BBL_PER_T / 1000))
        d = dec[c]
        d["price_share"] = d["price_effect"] / d["rev_change"] * 100
        d["volume_share"] = d["volume_effect"] / d["rev_change"] * 100
        d["price_share_abs"] = abs(d["price_effect"]) / (
            abs(d["price_effect"]) + abs(d["volume_effect"])) * 100
    return dict(premium=premium, volume=volume, decomp=dec,
                rev=dict(zip(p.country + p.year.astype(str),
                             p.REV.round(2).tolist())))


# --------------------------------------------------------------------- сборка
def main():
    df = load()
    p = panel(df)

    # ---- 1. базовая модель
    m, rows, fit = fit_ols(FORMULA, p)
    P = {r["var"]: r for r in rows}
    preds = m.fittedvalues.values
    acc = accuracy(p, preds)

    # ошибки с поправкой Ньюи—Уэста (1 лаг при 16 наблюдениях)
    m_nw = smf.ols(FORMULA, p).fit(cov_type="HAC", cov_kwds={"maxlags": 1})
    for r in rows:
        r["nw_se"] = float(m_nw.bse[r["var"]])
        r["nw_p"] = float(m_nw.pvalues[r["var"]])

    diag = diagnostics(m, p, FORMULA)

    # ---- 2. описательные статистики
    desc_stats = [
        desc(p, p.RU == 1, "Россия, весь период"),
        desc(p, p.AZ == 1, "Азербайджан, весь период"),
        desc(p, (p.RU == 1) & (p.year <= 2021), "Россия, 2018—2021"),
        desc(p, (p.RU == 1) & (p.year >= 2022), "Россия, 2022—2025"),
        desc(p, (p.AZ == 1) & (p.year <= 2021), "Азербайджан, 2018—2021"),
        desc(p, (p.AZ == 1) & (p.year >= 2022), "Азербайджан, 2022—2025"),
    ]

    # ---- 3. контрастные периоды (вклад блоков RU_* в разрыв)
    pre = p[p.year <= 2021]
    post = p[p.year >= 2022]
    rus_cap = p[(p.RU == 1) & (p.year >= 2023)]
    ru_pre = pre[pre.RU == 1]
    split = dict(
        pre_disc=float(ru_pre.D.mean()),
        post_disc=float(post[post.RU == 1].D.mean()),
        cap_disc=float(rus_cap.D.mean()),
        az_pre=float(pre[pre.AZ == 1].D.mean()),
        az_post=float(post[post.AZ == 1].D.mean()),
        pre_gap=float(ru_pre.D.mean() - pre[pre.AZ == 1].D.mean()),
        post_gap=float(post[post.RU == 1].D.mean() - post[post.AZ == 1].D.mean()),
        budget_gap_az=float((p[p.AZ == 1].budget_price - p[p.AZ == 1].brent).mean()),
        df_r2=dict(
            none=float(smf.ols("price ~ AZ_BR + RU_BR + RU", p)
                       .fit().rsquared_adj),
            sanct=float(smf.ols("price ~ AZ_BR + RU_BR + RU + SANCTIONS", p)
                        .fit().rsquared_adj),
            cap=float(smf.ols("price ~ AZ_BR + RU_BR + RU + CAP", p)
                      .fit().rsquared_adj),
            both=float(smf.ols("price ~ AZ_BR + RU_BR + RU + SANCTIONS + CAP", p)
                       .fit().rsquared_adj)),
    )

    # ---- 4. тесты спецификации и структурных сдвигов
    tests = dict(
        # единый наклон по Brent для двух стран: b_AZ = b_RU
        slope_equal=block_test("price ~ brent + RUS_DUMMY_ + 0", FORMULA, p)
        if False else None,
    )
    d2 = p.copy()
    d2["BRENT"] = d2["brent"]
    small = smf.ols("price ~ BRENT + RU + SANCTIONS + CAP + AZ_BUDGET", d2).fit()
    big = smf.ols(FORMULA, d2).fit()
    tests["slope_equal"] = chow(small, big, int(big.nobs), len(big.params),
                                name="единый наклон по Brent")
    # сдвиг всей российской ветви в 2022—2025 гг.
    small2 = smf.ols("price ~ BRENT + RU + AZ_BUDGET", d2).fit()
    tests["ru_shift"] = chow(small2, big, int(big.nobs), len(big.params),
                             name="сдвиг российской ветви")
    # сдвиг азербайджанской ветви в 2022—2025 гг.
    aze = p[p.AZ == 1].copy()
    aze["POST22"] = (aze.year >= 2022).astype(int)
    small3 = smf.ols("price ~ brent + POST22", aze).fit()
    big3 = smf.ols("price ~ brent + POST22 + brent:POST22", aze).fit()
    tests["az_shift"] = chow(small3, big3, int(big3.nobs), len(big3.params),
                             name="сдвиг азербайджанской ветви")
    # азербайджанский блок: объясняет ли контрактная бюджетная цена премию
    small4 = smf.ols("price ~ brent", aze).fit()
    big4 = smf.ols("price ~ brent + budget_price", aze).fit()
    tests["az_contract"] = chow(small4, big4, int(big4.nobs), len(big4.params),
                                name="контрактный ориентир Азербайджана")
    # структурный сдвиг российской ветви по годам (перебор)
    ru = p[p.RU == 1].copy()
    chow_ru = []
    for y in range(2021, 2025):
        ru["POST"] = (ru.year >= y).astype(int)
        s = smf.ols("price ~ brent + POST", ru).fit()
        b = smf.ols("price ~ brent + POST + brent:POST", ru).fit()
        chow_ru.append(chow(s, b, int(b.nobs), len(b.params), name=str(y)))
        chow_ru[-1]["year"] = y

    # ---- 5. устойчивость
    rob = {}
    p22 = p[p.year != 2022].copy()
    p22["BRENT"] = p22["brent"]
    rob["no_2022"] = dict(block_test(
        "price ~ BRENT + RU + CAP + AZ_BUDGET",
        "price ~ AZ_BR + RU_BR + RU + CAP + AZ_BUDGET",
        p22))
    m_alt = smf.ols("price ~ AZ_BR + RU_BR + RU + SANCTIONS + CAP + AZ_BUDGET",
                    p[p.year != 2022]).fit(cov_type="HC1")
    rob["no_2022"].update(cap=float(m_alt.params["CAP"]),
                          cap_p=float(m_alt.pvalues["CAP"]),
                          r2_adj=float(m_alt.rsquared_adj),
                          n=int(m_alt.nobs))
    # без Азербайджана: только российская ветвь 2013—2025
    ru_long = df[df.RU == 1].copy()
    m_ru = smf.ols("price ~ brent + SANCTIONS + CAP", ru_long).fit(cov_type="HC1")
    rob["ru_only"] = dict(n=int(m_ru.nobs), cap=float(m_ru.params["CAP"]),
                          cap_se=float(m_ru.bse["CAP"]),
                          cap_p=float(m_ru.pvalues["CAP"]),
                          sanct=float(m_ru.params["SANCTIONS"]),
                          sanct_p=float(m_ru.pvalues["SANCTIONS"]),
                          r2_adj=float(m_ru.rsquared_adj))
    # без Азербайджана в окне 2018—2025
    m_ru_s = smf.ols("price ~ brent + SANCTIONS + CAP",
                     p[p.RU == 1]).fit(cov_type="HC1")
    rob["ru_window"] = dict(n=int(m_ru_s.nobs), cap=float(m_ru_s.params["CAP"]),
                            cap_se=float(m_ru_s.bse["CAP"]),
                            cap_p=float(m_ru_s.pvalues["CAP"]))
    # без контрактного ориентира Азербайджана (сокращённая запись)
    m_nb = smf.ols("price ~ AZ_BR + RU_BR + RU + SANCTIONS + CAP",
                   p).fit(cov_type="HC1")
    rob["no_budget"] = dict(
        n=int(m_nb.nobs), cap=float(m_nb.params["CAP"]),
        cap_se=float(m_nb.bse["CAP"]), cap_p=float(m_nb.pvalues["CAP"]),
        sanct=float(m_nb.params["SANCTIONS"]),
        sanct_p=float(m_nb.pvalues["SANCTIONS"]),
        r2_adj=float(m_nb.rsquared_adj), aic=float(m_nb.aic),
        df_resid=int(m_nb.df_resid))
    rob["loo"] = loo_cv(FORMULA, p)
    rob["placebo"] = [placebo(y, p) for y in (2019, 2020, 2021, 2022, 2023, 2024)]

    # ---- 6. контрактный блок
    cb = contract_block(df)

    # ---- 7. экономическая интерпретация
    sigma = fit["sigma"]
    k_s = P["SANCTIONS"]["coef"]
    k_c = P["CAP"]["coef"]
    q25, q18 = float(p[(p.RU == 1) & (p.year == 2025)].q_export_mt.iloc[0]), \
        float(p[(p.RU == 1) & (p.year == 2018)].q_export_mt.iloc[0])
    pr25 = float(p[(p.RU == 1) & (p.year == 2025)].price.iloc[0])
    pr18 = float(p[(p.RU == 1) & (p.year == 2018)].price.iloc[0])
    az25 = float(p[(p.AZ == 1) & (p.year == 2025)].price.iloc[0])
    az18 = float(p[(p.AZ == 1) & (p.year == 2018)].price.iloc[0])
    q_az25 = float(p[(p.AZ == 1) & (p.year == 2025)].q_export_mt.iloc[0])

    # эффект санкционного режима: скидка вместо «нормального» дисконта
    ef = {}
    ef["norm_disc"] = abs(split["pre_disc"])
    ef["cap_disc"] = abs(split["cap_disc"])
    ef["sanct_disc"] = abs(split["post_disc"])
    ef["cap_excess"] = ef["cap_disc"] - ef["norm_disc"]
    ef["loss_2025_bn"] = ef["cap_excess"] * q25 * BBL_PER_T / 1000
    ef["loss_2025_rub_trln"] = ef["loss_2025_bn"] * RATE / 1000
    ef["loss_per_dollar_bn"] = q25 * BBL_PER_T / 1000
    ef["loss_per_dollar_rub_bn"] = ef["loss_per_dollar_bn"] * RATE
    ef["ngd_2025_trln"] = FACTS["ngd_2025_trln"]
    ef["ngd_share"] = ef["loss_2025_rub_trln"] / ef["ngd_2025_trln"] * 100
    ef["cap_effect_bn"] = k_c * q25 * BBL_PER_T / 1000
    ef["sanct_effect_bn"] = k_s * q25 * BBL_PER_T / 1000
    # выручка 2018 и 2025 (фактическая цена × физический экспорт)
    ef["rev_ru_2018"] = pr18 * q18 * BBL_PER_T / 1000
    ef["rev_ru_2025"] = pr25 * q25 * BBL_PER_T / 1000
    ef["rev_ru_if_az"] = (pr25 + (ef["cap_excess"])) * q25 * BBL_PER_T / 1000
    ef["rev_az_2018"] = az18 * float(
        p[(p.AZ == 1) & (p.year == 2018)].q_export_mt.iloc[0]) * BBL_PER_T / 1000
    ef["rev_az_2025"] = az25 * q_az25 * BBL_PER_T / 1000
    ef["rev_az_if_brent"] = float(p[(p.AZ == 1) & (p.year == 2025)].brent.iloc[0]) \
        * q_az25 * BBL_PER_T / 1000
    ef["az_premium_2025"] = az25 - float(p[(p.AZ == 1) & (p.year == 2025)].brent.iloc[0])
    ef["az_premium_2018"] = az18 - float(p[(p.AZ == 1) & (p.year == 2018)].brent.iloc[0])
    ef["az_budget_gap_2025"] = float(
        p[(p.AZ == 1) & (p.year == 2025)].budget_price.iloc[0]) - az25
    ef["cap_per_1usd_bn"] = ef["loss_per_dollar_bn"]
    ef["loss_1usd_bn"] = ef["loss_per_dollar_bn"]
    ef["loss_5usd_bn"] = ef["loss_per_dollar_bn"] * 5
    ef["loss_5usd_rub_trln"] = ef["loss_5usd_bn"] * RATE / 1000
    ef["shift_two"] = k_s + k_c
    ef["shift_total"] = k_s + k_c + P["RU"]["coef"]
    ef["loss_two_bn"] = abs(ef["shift_two"]) * q25 * BBL_PER_T / 1000
    ef["cap_share_brent"] = ef["cap_excess"] / \
        float(p[(p.RU == 1) & (p.year == 2025)].brent.iloc[0]) * 100
    ef["sigma_share"] = ef["cap_excess"] / sigma
    ef["gap_ratio"] = ef["cap_disc"] / ef["cap_excess"]
    ef["loss_share_rev"] = ef["loss_2025_bn"] / ef["rev_ru_2025"] * 100
    ef["rate"] = RATE

    # предел потолка: доля Urals в цене Brent, при которой потолок становится
    # связывающим (потолок / Brent 2025)
    ef["cap_bind_2025"] = FACTS["cap_2025"] / \
        float(p[(p.RU == 1) & (p.year == 2025)].brent.iloc[0])
    ef["cap_level_2025"] = FACTS["cap_2025"]
    ef["cap_level_2026"] = FACTS["cap_2026"]

    econ = ef
    econ["contract"] = dict(
        cnpc_mt=FACTS["cnpc_volume_mt"], cnpc_bn=FACTS["cnpc_value_bn"],
        cnpc_prepay=FACTS["cnpc_prepay_bn"],
        cnpc_annual=FACTS["cnpc_annual_mt"], cnpc_peak=FACTS["cnpc_peak_mt"],
        cnpc_price_bn=FACTS["cnpc_value_bn"] / FACTS["cnpc_volume_mt"],
        acg_profit=FACTS["acg_profit_share"],
        acg_socar_2017=FACTS["acg_socar_2017"],
        acg_socar_2026=FACTS["acg_socar_2026"],
        acg_bonus=FACTS["acg_bonus_bn"], acg_horizon=FACTS["acg_horizon"],
        acg_share_prod=FACTS["acg_share_prod"],
        acg_profit_2025=FACTS["acg_profit_share"] * q_az25,
        acg_socar_volume_2025=FACTS["acg_socar_2026"] / 100 * q_az25,
        budget_gap_2025=ef["az_budget_gap_2025"],)
    econ["contract"]["cnpc_share_2025"] = \
        econ["contract"]["cnpc_annual"] / q25 * 100.

    out = dict(
        meta=dict(model="panel_fe_annual", n=int(len(p)), y0=Y0, y1=Y1,
                  countries=2, formula=FORMULA, estimator="МНК, HC1",
                  nw_lags=1, years_ru=[min(YEARS_RU), max(YEARS_RU)],
                  n_ru_only=int((df.RU == 1).sum()), bbl=BBL_PER_T, rate=RATE,
                  spec="годовая панель, раздельные блоки RU и AZ"),
        data=p.to_dict(orient="records"),
        full=df.to_dict(orient="records"),
        rows=rows, fit=fit, diag=diag, acc=acc,
        desc=desc_stats, split=split, tests=tests,
        chow=dict(ru=chow_ru, az=tests["az_shift"]),
        robust=rob, econ=econ, contract=cb,
        facts=FACTS,
    )
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "model.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)

    print(f"n = {len(p)}; adjR2 = {fit['r2_adj']:.4f}; F = {fit['f']:.2f}")
    for r in rows:
        print(f"  {r['var']:12s} {r['coef']:9.3f} se={r['se']:6.3f} "
              f"p={r['p']:.4f}  (NW se={r['nw_se']:6.3f})")
    print("  потери 2025:", round(ef["loss_2025_bn"], 2), "млрд долл.")
    return out


if __name__ == "__main__":
    main()
