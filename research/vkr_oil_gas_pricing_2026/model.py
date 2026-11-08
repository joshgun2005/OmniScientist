# -*- coding: utf-8 -*-
"""Единственная эконометрическая модель ВКР.

Спецификация (дифференциал фактической экспортной цены к Brent):

    D_it = a + b·Brent_t + g·RUS_i + d·1[t >= 2025-11] + q·(1[t >= 2025-11]·RUS_i) + u_it,
    D_it = P_it - Brent_t.

Все числа, попадающие в документы, считаются здесь и сохраняются в
out/model.json; в тексте «ручных» коэффициентов нет.

Запуск: python3 model.py
"""
import json
import os

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.stats.diagnostic import (
    acorr_breusch_godfrey, het_breuschpagan, linear_reset)
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.stats.stattools import durbin_watson, jarque_bera

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "out")
BBL_PER_T = 7.33          # барр./т (нетбэк-пересчёт, формула (16) главы 1)
SPLIT = "2025-11"         # дата институционального сдвига
FORMULA = "D ~ Brent + RUS + d + RUS:d"
FORMULA_NB = "D ~ Brent + RUS + d + RUS:d"   # та же модель для проверок


def load_metrics():
    """Показатели из out/metrics.json (реестр исходных данных)."""
    path = os.path.join(OUT, "metrics.json")
    if not os.path.exists(path):
        raise SystemExit("сначала выполните python3 analysis.py")
    with open(path, encoding="utf-8") as fh:
        m = json.load(fh)
    return m["inputs"], m["derived"]


# ------------------------------------------------------------------ данные
def load():
    df = pd.read_csv(os.path.join(BASE, "data", "panel_prices.csv"))
    df = df.rename(columns={"brent": "Brent"})
    df["D"] = df["price"] - df["Brent"]
    df["RUS"] = (df["country"] == "RUS").astype(int)
    df["d"] = (df["month"] >= SPLIT).astype(int)
    df["month"] = df["month"].astype(str)
    df["src"] = df["country"].map({"RUS": "minec_urals", "AZE": "az_light_2026"})
    df["split_note"] = SPLIT
    return df.sort_values(["month", "country"]).reset_index(drop=True)


def fit(df, formula=FORMULA):
    """Обычный МНК + ковариационная матрица HAC (Newey-West, 2 лага)."""
    ols = smf.ols(formula, data=df).fit()
    hac = smf.ols(formula, data=df).fit(cov_type="HAC",
                                        cov_kwds={"maxlags": 2})
    return ols, hac


def spec_table(ols, hac):
    """Таблица коэффициентов: обычные и HAC-ошибки, доверительные интервалы."""
    rows = []
    ci = hac.conf_int()
    for name in ols.params.index:
        rows.append({
            "var": name,
            "coef": float(ols.params[name]),
            "se": float(ols.bse[name]),
            "t": float(ols.tvalues[name]),
            "p": float(ols.pvalues[name]),
            "hac_se": float(hac.bse[name]),
            "hac_t": float(hac.tvalues[name]),
            "hac_p": float(hac.pvalues[name]),
            "ci_lo": float(ci.loc[name, 0]),
            "ci_hi": float(ci.loc[name, 1]),
        })
    return rows


def diagnostics(ols, df):
    resid = ols.resid
    exog = ols.model.exog
    bp = het_breuschpagan(resid, exog)
    bg = acorr_breusch_godfrey(ols, nlags=2)
    jb = jarque_bera(resid)
    reset = linear_reset(ols, power=2, use_f=True)
    bg2 = acorr_breusch_godfrey(ols, nlags=1)
    vif = {}
    names = list(ols.params.index)
    for i, nm in enumerate(names):
        if nm == "Intercept":
            continue
        vif[nm] = float(variance_inflation_factor(exog, i))
    return {
        "bp_lm": float(bp[0]), "bp_p": float(bp[1]),
        "bg_lm": float(bg[0]), "bg_p": float(bg[1]),
        "bg1_lm": float(bg2[0]), "bg1_p": float(bg2[1]),
        "jb": float(jb[0]), "jb_p": float(jb[1]),
        "reset_f": float(reset.statistic), "reset_p": float(reset.pvalue),
        "dw": float(durbin_watson(resid)),
        "vif": {k: round(v, 2) for k, v in vif.items()},
        "vif_max": round(max(vif.values()), 2),
        "skew": float(pd.Series(resid).skew()),
        "kurt": float(pd.Series(resid).kurtosis() + 3),
    }


def chow(df):
    """Тест Чоу на структурный сдвиг в дату SPLIT.

    Классическая форма: сравниваются остатки единой регрессии по всей выборке
    и двух регрессий по подвыборкам «до» и «после» (все коэффициенты свободны).
    Дополнительно считается частная форма: совместная значимость фиктивных
    переменных сдвига при неизменном наклоне по Brent — именно она
    соответствует уравнению (1).
    """
    from scipy import stats

    pool = smf.ols("D ~ Brent + RUS", data=df).fit()
    pre, post = df[df.d == 0], df[df.d == 1]
    a = smf.ols("D ~ Brent + RUS", data=pre).fit()
    b = smf.ols("D ~ Brent + RUS", data=post).fit()
    q = len(pool.params)
    n = int(pool.nobs)
    su = a.ssr + b.ssr
    f = ((pool.ssr - su) / q) / (su / (n - 2 * q))

    # отдельная регрессия по России: проверка сдвига внутри одной страны
    rus = df[df.RUS == 1]
    r0 = smf.ols("D ~ Brent", data=rus[rus.d == 0]).fit()
    r1 = smf.ols("D ~ Brent", data=rus[rus.d == 1]).fit()
    rp = smf.ols("D ~ Brent", data=rus).fit()
    q_rus = len(rp.params)
    n_rus = int(rp.nobs)
    su_rus = r0.ssr + r1.ssr
    f_rus = ((rp.ssr - su_rus) / q_rus) / (su_rus / (n_rus - 2 * q_rus))

    unrestr = smf.ols(FORMULA, data=df).fit()
    k = len(unrestr.params)
    f_shift = ((pool.ssr - unrestr.ssr) / 2) / (unrestr.ssr / (n - k))
    return {"F": float(f), "p": float(stats.f.sf(f, q, n - 2 * q)),
            "df1": q, "df2": n - 2 * q,
            "F_shift": float(f_shift),
            "p_shift": float(stats.f.sf(f_shift, 2, n - k)),
            "df1_shift": 2, "df2_shift": n - k,
            "F_rus": float(f_rus),
            "p_rus": float(stats.f.sf(f_rus, q_rus, n_rus - 2 * q_rus)),
            "df1_rus": q_rus, "df2_rus": n_rus - 2 * q_rus,
            "n_rus": n_rus}


def linear_combo(ols, weights):
    """Линейная комбинация коэффициентов: оценка, se, t, p, интервал."""
    b = ols.params
    V = ols.cov_params()
    est = sum(weights.get(k, 0.0) * b[k] for k in b.index)
    var = 0.0
    for i in b.index:
        for j in b.index:
            var += weights.get(i, 0.0) * weights.get(j, 0.0) * V.loc[i, j]
    se = float(np.sqrt(var))
    from scipy import stats
    t = est / se
    p = 2 * (1 - stats.t.cdf(abs(t), ols.df_resid))
    crit = stats.t.ppf(0.975, ols.df_resid)
    return {"est": float(est), "se": se, "t": float(t), "p": float(p),
            "lo": float(est - crit * se), "hi": float(est + crit * se)}


def date_search(df, dates):
    """Поиск даты сдвига: перебор месяцев, выбор по максимуму adj. R2 и AIC."""
    out = []
    for dt in dates:
        sub = df.copy()
        sub["dd"] = (sub["month"] >= dt).astype(int)
        m = smf.ols("D ~ Brent + RUS + dd + RUS:dd", data=sub).fit()
        h = smf.ols("D ~ Brent + RUS + dd + RUS:dd", data=sub).fit(
            cov_type="HAC", cov_kwds={"maxlags": 2})
        out.append({"date": dt,
                    "coef": float(h.params["RUS:dd"]),
                    "se": float(h.bse["RUS:dd"]),
                    "p": float(h.pvalues["RUS:dd"]),
                    "r2_adj": float(m.rsquared_adj),
                    "aic": float(m.aic)})
    return out


def spec_compare(df):
    """Сравнение спецификаций-кандидатов: R2, AIC/BIC, устойчивость сдвига."""
    cands = [("S1", "D ~ Brent + RUS + d", "общий сдвиг без страновой асимметрии"),
             ("S2", FORMULA, "страновой сдвиг (базовая)"),
             ("S3", "D ~ Brent + RUS + d + RUS:d + Brent:RUS",
              "добавлен наклон Brent для России"),
             ("S4", "D ~ Brent + RUS + d + RUS:d + Brent:d",
              "наклон Brent меняется после сдвига"),
             ("S5", "D ~ Brent + RUS + d + RUS:d + Brent:RUS + Brent:d",
              "оба дополнительных наклона")]
    out = []
    for code, formula, note in cands:
        m = smf.ols(formula, data=df).fit()
        h = smf.ols(formula, data=df).fit(cov_type="HAC",
                                          cov_kwds={"maxlags": 2})
        key = "RUS:d"
        out.append({"code": code, "formula": formula, "note": note,
                    "k": int(len(m.params)),
                    "r2_adj": float(m.rsquared_adj), "aic": float(m.aic),
                    "bic": float(m.bic),
                    "gap": float(m.params[key]) if key in m.params else None,
                    "gap_p": float(h.pvalues[key]) if key in m.params else None})
    return out


def accuracy(df, ols):
    """Точность: ошибки по дифференциалу и по цене, вклад Brent (F-тест)."""
    resid = ols.resid.to_numpy()
    d = df["D"].to_numpy()
    price = df["price"].to_numpy()
    pred_price = df["Brent"].to_numpy() + ols.fittedvalues.to_numpy()
    mape = float(np.mean(np.abs(resid) / np.abs(d)) * 100)
    mape_p = float(np.mean(np.abs(pred_price - price) / price) * 100)
    # вклад Brent: сравнение с моделью только из фиктивных переменных
    restr = smf.ols("D ~ RUS + d + RUS:d", data=df).fit()
    q = 1
    k = len(ols.params)
    n = int(ols.nobs)
    f = ((restr.ssr - ols.ssr) / q) / (ols.ssr / (n - k))
    from scipy import stats
    return {"rmse_D": float(np.sqrt(np.mean(resid ** 2))),
            "mae_D": float(np.mean(np.abs(resid))),
            "mape_D": mape,
            "rmse_P": float(np.sqrt(np.mean((pred_price - price) ** 2))),
            "mape_P": mape_p,
            "max_abs_D": float(np.max(np.abs(resid))),
            "f_brent": float(f),
            "f_brent_p": float(1 - stats.f.cdf(f, q, n - k)),
            "r2_restr": float(restr.rsquared)}


def describe(df):
    out = {}
    for key, sub in (("all", df),
                     ("RUS", df[df.country == "RUS"]),
                     ("AZE", df[df.country == "AZE"]),
                     ("RUS_before", df[(df.country == "RUS") & (df.d == 0)]),
                     ("RUS_after", df[(df.country == "RUS") & (df.d == 1)]),
                     ("AZE_before", df[(df.country == "AZE") & (df.d == 0)]),
                     ("AZE_after", df[(df.country == "AZE") & (df.d == 1)])):
        out[key] = {"n": int(len(sub)),
                    "D_mean": float(sub.D.mean()),
                    "D_sd": float(sub.D.std(ddof=1)) if len(sub) > 1 else 0.0,
                    "D_min": float(sub.D.min()),
                    "D_max": float(sub.D.max()),
                    "P_mean": float(sub.price.mean()),
                    "Brent_mean": float(sub.Brent.mean())}
    out["brent"] = {"mean": float(df.Brent.mean()),
                    "sd": float(df.Brent.std(ddof=1)),
                    "min": float(df.Brent.min()),
                    "max": float(df.Brent.max())}
    out["D"] = {"mean": float(df.D.mean()), "sd": float(df.D.std(ddof=1)),
                "min": float(df.D.min()), "max": float(df.D.max())}
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    df = load()
    ols, hac = fit(df)
    rob = {}

    # 1) без наблюдения-выброса 2026-01 (сдвиг цены Azeri Light)
    sub = df[df.month != "2026-01"]
    o2, h2 = fit(sub)
    rob["no_outlier"] = {"n": int(o2.nobs), "r2_adj": float(o2.rsquared_adj),
                         "sigma": float(np.sqrt(o2.mse_resid)),
                         "rows": spec_table(o2, h2),
                         "diag": diagnostics(o2, sub)}

    # 2) сбалансированная панель (только месяцы, где есть обе страны)
    months = set(df[df.country == "AZE"].month)
    bal = df[df.month.isin(months)]
    o3, h3 = fit(bal)
    rob["balanced"] = {"n": int(o3.nobs), "months": int(bal.month.nunique()),
                       "r2_adj": float(o3.rsquared_adj),
                       "sigma": float(np.sqrt(o3.mse_resid)),
                       "rows": spec_table(o3, h3),
                       "diag": diagnostics(o3, bal)}

    # 3) поиск даты сдвига: перебор всех месяцев с непустыми подвыборками
    months = sorted(df.month.unique())
    cand_dates = []
    for m in months:
        # в обеих подвыборках должны остаться наблюдения обеих стран
        before, after = df[df.month < m], df[df.month >= m]
        if (before.country.nunique() == 2 and after.country.nunique() == 2
                and len(before) >= 8 and len(after) >= 8):
            cand_dates.append(m)
    alt = date_search(df, cand_dates)
    best = max(alt, key=lambda r: r["r2_adj"])

    # 4) эконометрическая эквивалентность: взаимодействие Brent×RUS
    m_int = smf.ols("D ~ Brent*RUS + d + RUS:d", data=df).fit()
    from scipy import stats as st
    f_add = ((ols.ssr - m_int.ssr) / 1) / (m_int.ssr / m_int.df_resid)

    res = {
        "meta": {
            "n": int(ols.nobs), "k": int(len(ols.params)),
            "months": int(df.month.nunique()),
            "period": f"{df.month.min()} — {df.month.max()}",
            "split": SPLIT, "formula": FORMULA,
            "df_resid": int(ols.df_resid),
        },
        "fit": {"r2": float(ols.rsquared), "r2_adj": float(ols.rsquared_adj),
                "f": float(ols.fvalue), "f_p": float(ols.f_pvalue),
                "sigma": float(np.sqrt(ols.mse_resid)),
                "aic": float(ols.aic), "bic": float(ols.bic),
                "ssr": float(ols.ssr), "loglik": float(ols.llf)},
        "rows": spec_table(ols, hac),
        "diag": diagnostics(ols, df),
        "chow": chow(df),
        "desc": describe(df),
        "effects": {
            "slope_aze": linear_combo(ols, {"Brent": 1}),
            "slope_rus": linear_combo(ols, {"Brent": 1, "Brent:RUS": 1}),
            "shift_aze": linear_combo(ols, {"d": 1}),
            "shift_rus": linear_combo(ols, {"d": 1, "RUS:d": 1}),
            "gap": linear_combo(ols, {"RUS:d": 1}),
        },
        "robust": {"no_outlier": rob["no_outlier"],
                   "balanced": rob["balanced"], "dates": alt,
                   "best_date": best},
        "specs": spec_compare(df),
        "acc": accuracy(df, ols),
        "eq_test": {"f": float(f_add), "p": float(1 - st.f.cdf(
            f_add, 1, m_int.df_resid)), "r2_adj_int": float(m_int.rsquared_adj)},
        "data": [{"month": r.month, "country": r.country,
                  "price": float(r.price), "brent": float(r.Brent),
                  "D": float(r.D), "pred": float(p),
                  "resid": float(r.D - p)}
                 for r, p in zip(df.itertuples(), ols.fittedvalues)],
    }

    # ------------------------------------------------ экономические пересчёты
    V, D = load_metrics()
    gap = res["effects"]["gap"]["est"]          # специфический сдвиг РФ
    export_mt = float(V["ru_oil_export_2026"])
    export_value_bn = float(D["oil_export_value_2026"])
    per_dollar = export_mt * BBL_PER_T / 1000          # млрд долл. на 1 долл./барр.
    az_export_mt = float(V["az_oil_export_2025"])
    az_per_dollar = az_export_mt * BBL_PER_T / 1000
    res["econ"] = {
        "gap": gap,
        "export_mt": export_mt,
        "bbl_per_t": BBL_PER_T,
        "loss_bn": round(per_dollar * abs(gap), 2),
        "export_value_bn": export_value_bn,
        "per_dollar_bn": round(per_dollar, 3),
        "loss_5usd_bn": round(per_dollar * 5, 2),
        "az_export_mt": az_export_mt,
        "az_per_dollar_bn": round(az_per_dollar, 3),
        "az_premium_bn": round(az_per_dollar * res["desc"]["AZE"]["D_mean"], 2),
        "az_premium_mean": round(res["desc"]["AZE"]["D_mean"], 2),
    }
    res["econ"]["loss_share"] = round(
        res["econ"]["loss_bn"] / export_value_bn * 100, 1)
    res["econ"]["gap_share_brent"] = round(
        abs(gap) / res["desc"]["brent"]["mean"] * 100, 1)
    res["econ"]["ngd_9m_share"] = round(
        res["econ"]["loss_bn"] * float(V["ru_budget_rate_2026"])
        / (float(V["ru_ngd_9m2026"]) * 1000) * 100, 1)
    # доля Urals в цене Brent до и после сдвига при среднем Brent выборки
    bm = res["desc"]["brent"]["mean"]
    c = {r["var"]: r["coef"] for r in res["rows"]}
    res["econ"]["brent_mean"] = round(bm, 2)
    res["econ"]["urals_share_before"] = round(
        (bm + c["Intercept"] + c["Brent"] * bm + c["RUS"]) / bm * 100, 1)
    res["econ"]["urals_share_after"] = round(
        (bm + c["Intercept"] + c["Brent"] * bm + c["RUS"] + c["d"]
         + c["RUS:d"]) / bm * 100, 1)

    # сценарии по Brent: цена Urals и Azeri Light до/после сдвига
    scen = []
    for b in (60, 80, 100, 120):
        d_aze_b = c["Intercept"] + c["Brent"] * b
        d_aze_a = d_aze_b + c["d"]
        d_rus_b = d_aze_b + c["RUS"]
        d_rus_a = d_rus_b + c["d"] + c["RUS:d"]
        scen.append({"brent": b,
                     "urals_before": b + d_rus_b, "urals_after": b + d_rus_a,
                     "aze_before": b + d_aze_b, "aze_after": b + d_aze_a,
                     "gap_before": d_rus_b, "gap_after": d_rus_a})
    res["scenarios"] = scen

    with open(os.path.join(OUT, "model.json"), "w", encoding="utf-8") as fh:
        json.dump(res, fh, ensure_ascii=False, indent=1)

    # ------------------------------------------------------------- отчёт
    print(f"n = {res['meta']['n']}, месяцев = {res['meta']['months']}, "
          f"период {res['meta']['period']}")
    print(f"R2 = {res['fit']['r2']:.4f}, adj = {res['fit']['r2_adj']:.4f}, "
          f"F = {res['fit']['f']:.2f} (p = {res['fit']['f_p']:.3g}), "
          f"sigma = {res['fit']['sigma']:.3f}")
    print(f"{'переменная':12s} {'коэф.':>9s} {'se':>7s} {'p':>8s} "
          f"{'HAC se':>8s} {'HAC p':>8s}")
    for r in res["rows"]:
        print(f"{r['var']:12s} {r['coef']:9.3f} {r['se']:7.3f} {r['p']:8.3f} "
              f"{r['hac_se']:8.3f} {r['hac_p']:8.3f}")
    dg = res["diag"]
    print(f"BP p={dg['bp_p']:.3f}  BG(2) p={dg['bg_p']:.3f}  JB p={dg['jb_p']:.3f}  "
          f"RESET p={dg['reset_p']:.3f}  DW={dg['dw']:.2f}  VIF max={dg['vif_max']}")
    print(f"Чоу: F={res['chow']['F']:.2f}, p={res['chow']['p']:.3g}")
    e = res["effects"]
    for k, nm in (("slope_aze", "наклон АР"), ("slope_rus", "наклон РФ"),
                  ("shift_aze", "сдвиг АР"), ("shift_rus", "сдвиг РФ"),
                  ("gap", "разрыв сдвигов")):
        print(f"{nm:16s} {e[k]['est']:8.3f}  se={e[k]['se']:6.3f}  "
              f"t={e[k]['t']:6.2f}  p={e[k]['p']:.4f}  "
              f"[{e[k]['lo']:.2f}; {e[k]['hi']:.2f}]")
    print("робастность: без выброса n=%d adj=%.3f | сбалансированная n=%d adj=%.3f"
          % (res["robust"]["no_outlier"]["n"],
             res["robust"]["no_outlier"]["r2_adj"],
             res["robust"]["balanced"]["n"],
             res["robust"]["balanced"]["r2_adj"]))
    for a in alt:
        print(f"  дата {a['date']}: {a['coef']:7.2f} (se {a['se']:.2f}, "
              f"p {a['p']:.3f}), adj R2 {a['r2_adj']:.3f}")
    print(f"цена адаптации {res['econ']['gap']:.2f} долл./барр. → "
          f"{res['econ']['loss_bn']:.2f} млрд долл. "
          f"({res['econ']['loss_share']:.1f} % нефтяного экспорта)")
    print("сохранено: out/model.json")


if __name__ == "__main__":
    main()
