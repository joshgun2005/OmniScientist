# -*- coding: utf-8 -*-
"""Единственная эконометрическая модель ВКР — модель «до и после» (DiD).

Идея в одной фразе: сравниваем, как изменился разрыв между ценой российской
и азербайджанской нефти после 1 января 2026 г. — то есть после очередного
снижения потолка цен.

Уравнение (простая линейная регрессия по 24 наблюдениям «страна — месяц»):

    D = a + b · Brent + c · RUS + e · Y26 + k · (RUS · Y26) + u,

    D     = P − Brent  — дифференциал фактической цены экспорта, долл./барр.;
    RUS   = 1 для России, 0 для Азербайджана;
    Y26   = 1 для месяцев 2026 г., 0 для 2025 г.;
    RUS·Y26 — искомая величина: дополнительное расширение российского
              дифференциала после смены режима (коэффициент k).

Всё считается здесь: out/model.json — единственный источник чисел для
документа, поэтому в тексте нет «ручных» значений.

Запуск: python3 model.py
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
from statsmodels.stats.stattools import durbin_watson, jarque_bera

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "out")
DATA = os.path.join(BASE, "data", "panel_prices.csv")

BBL_PER_T = 7.33          # барр. в тонне (формула (16) главы 1)
SPLIT = "2026-01"         # начало действия потолка 44,1 долл./барр.
FORMULA = "D ~ brent + RUS + Y26 + RUSY"


# --------------------------------------------------------------------- данные
def load():
    df = pd.read_csv(DATA)
    df["D"] = df["price"] - df["brent"]
    df["RUS"] = (df["country"] == "RUS").astype(int)
    df["Y26"] = df["d_phase"].astype(int)
    df["RUSY"] = df["RUS"] * df["Y26"]
    df["month"] = df["month"].astype(str)
    return df.sort_values(["month", "country"]).reset_index(drop=True)


# ----------------------------------------------------------------- оценивание
def cluster_se(ols, df, group="month"):
    """Ошибки, сгруппированные по месяцу: в каждом месяце две страны."""
    X = ols.model.exog
    u = ols.resid.values
    bread = np.linalg.pinv(X.T @ X)
    meat = np.zeros((X.shape[1], X.shape[1]))
    for _, idx in df.groupby(group).indices.items():
        Xg, ug = X[idx], u[idx]
        s = Xg.T @ ug
        meat += np.outer(s, s)
    n, k = X.shape
    g = df[group].nunique()
    factor = g / (g - 1) * (n - 1) / (n - k)
    V = factor * bread @ meat @ bread
    se = np.sqrt(np.diag(V))
    t = ols.params.values / se
    p = 2 * (1 - stats.t.cdf(np.abs(t), g - 1))
    return se, t, p, V


def rows_table(ols, se, t, p, ci):
    out = []
    for i, name in enumerate(ols.params.index):
        out.append({"var": name,
                    "coef": float(ols.params[name]),
                    "se": float(ols.bse[name]),
                    "t": float(ols.tvalues[name]),
                    "p": float(ols.pvalues[name]),
                    "cl_se": float(se[i]),
                    "cl_t": float(t[i]),
                    "cl_p": float(p[i]),
                    "ci_lo": float(ci[i][0]),
                    "ci_hi": float(ci[i][1])})
    return out


def diagnostics(ols):
    resid = ols.resid
    bp = het_breuschpagan(resid, ols.model.exog)
    bg = acorr_breusch_godfrey(ols, nlags=1)
    jb = jarque_bera(resid)
    reset = linear_reset(ols, power=2, use_f=True)
    return {"bp_lm": float(bp[0]), "bp_p": float(bp[1]),
            "bg_lm": float(bg[0]), "bg_p": float(bg[1]),
            "jb": float(jb[0]), "jb_p": float(jb[1]),
            "skew": float(pd.Series(resid).skew()),
            "kurt": float(pd.Series(resid).kurtosis() + 3),
            "reset_f": float(reset.statistic), "reset_p": float(reset.pvalue),
            "dw": float(durbin_watson(resid))}


def chow_test(df):
    """Тест Чоу: одна регрессия на весь период против двух по подпериодам.

    Внутри каждой страны оценивается зависимость P от Brent; проверяется
    равенство коэффициентов до 2026 г. и с 2026 г.
    """
    res = {}
    pre, post = df[df.Y26 == 0], df[df.Y26 == 1]
    for code, name in (("RUS", "rus"), ("AZE", "aze")):
        a, b = pre[pre.country == code], post[post.country == code]
        pooled = sm.OLS(df[df.country == code].price,
                        sm.add_constant(df[df.country == code][["brent"]])).fit()
        m1 = sm.OLS(a.price, sm.add_constant(a[["brent"]])).fit()
        m2 = sm.OLS(b.price, sm.add_constant(b[["brent"]])).fit()
        q = 2
        n = int(pooled.nobs)
        f = ((pooled.ssr - (m1.ssr + m2.ssr)) / q) / ((m1.ssr + m2.ssr) /
                                                      (n - 2 * q))
        res[name] = {"F": float(f), "p": float(stats.f.sf(f, q, n - 2 * q)),
                     "df1": q, "df2": n - 2 * q, "n": n,
                     "n_pre": int(m1.nobs), "n_post": int(m2.nobs)}
    return res


def date_check(df):
    """Проверка даты сдвига: оценка k при разных границах года."""
    out = []
    for split in ("2025-12", "2026-01", "2026-02", "2026-03"):
        d = df.copy()
        d["Y26"] = (d.month >= split).astype(int)
        d["RUSY"] = d.RUS * d.Y26
        m = smf.ols(FORMULA, data=d).fit()
        out.append({"split": split, "k": float(m.params["RUSY"]),
                    "p": float(m.pvalues["RUSY"]),
                    "r2_adj": float(m.rsquared_adj),
                    "aic": float(m.aic)})
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    df = load()
    ols = smf.ols(FORMULA, data=df).fit()
    se, t, p, V = cluster_se(ols, df)
    coefs = ols.params.values
    ci = np.array([[coefs[i] - 1.96 * se[i], coefs[i] + 1.96 * se[i]]
                   for i in range(len(se))])
    names = list(ols.params.index)
    rows = rows_table(ols, se, t, p, ci)
    get = {r["var"]: r for r in rows}

    # --- устойчивость: без января 2026 г. и без «плоских» месяцев 2025 г.
    rob = {}

    def check(key, sub, formula=FORMULA, label=""):
        m = smf.ols(formula, data=sub).fit()
        s2, _, p2, _ = cluster_se(m, sub)
        i = list(m.params.index).index("RUSY")
        rob[key] = {"n": int(m.nobs), "k": float(m.params["RUSY"]),
                    "cl_se": float(s2[i]), "cl_p": float(p2[i]),
                    "r2_adj": float(m.rsquared_adj), "label": label}

    check("no_jan", df[df.month != "2026-01"],
          label="без января 2026 г. (переходный месяц)")
    check("no_brent", df, formula="D ~ RUS + Y26 + RUSY",
          label="без учёта Brent (только страна и год)")
    # jackknife: поочерёдное исключение одного месяца
    ks = []
    for m in sorted(df.month.unique()):
        sub = df[df.month != m]
        ks.append(float(smf.ols(FORMULA, data=sub).fit().params["RUSY"]))
    rob["jackknife"] = {"min": float(min(ks)), "max": float(max(ks)),
                        "n_cases": len(ks),
                        "label": "поочерёдное исключение одного месяца"}

    # --- предпосылка DiD: в 2025 г. разрыв между странами не имел тренда
    wide = df.pivot(index="month", columns="country", values="D")
    wide["gap"] = wide["RUS"] - wide["AZE"]
    pre = wide.loc[[m for m in wide.index if m < SPLIT]].reset_index()
    pre["t"] = range(1, len(pre) + 1)
    trend = smf.ols("gap ~ t", data=pre).fit()
    pretrend = {"slope": float(trend.params["t"]),
                "p": float(trend.pvalues["t"]),
                "months": int(len(pre)),
                "sd": float(pre["gap"].std(ddof=1))}

    def mean(sub):
        return {"n": int(len(sub)), "D": float(sub.D.mean()),
                "sd": float(sub.D.std(ddof=1)) if len(sub) > 1 else 0.0,
                "P": float(sub.price.mean()),
                "brent": float(sub.brent.mean())}

    desc = {
        "RUS_2025": mean(df[(df.country == "RUS") & (df.Y26 == 0)]),
        "RUS_2026": mean(df[(df.country == "RUS") & (df.Y26 == 1)]),
        "AZE_2025": mean(df[(df.country == "AZE") & (df.Y26 == 0)]),
        "AZE_2026": mean(df[(df.country == "AZE") & (df.Y26 == 1)]),
    }
    did_manual = ((desc["RUS_2026"]["D"] - desc["RUS_2025"]["D"]) -
                  (desc["AZE_2026"]["D"] - desc["AZE_2025"]["D"]))

    # --- точность модели
    pred = ols.fittedvalues
    acc = {"mae": float(np.abs(ols.resid).mean()),
           "max_abs": float(np.abs(ols.resid).max()),
           "mape_price": float((np.abs(ols.resid) / df.price).mean() * 100)}

    # --- перевод в деньги (данные — Минэк и Минфин)
    met = json.load(open(os.path.join(OUT, "metrics.json"), encoding="utf-8"))
    V_in, D_in = met["inputs"], met["derived"]
    k = abs(get["RUSY"]["coef"])
    export_mt = V_in["ru_oil_export_2026"]
    loss_bn = k * export_mt * BBL_PER_T / 1000
    export_value_bn = D_in["oil_export_value_2026"]
    per_dollar = export_mt * BBL_PER_T / 1000
    ngd_9m_tln = V_in["ru_ngd_9m2026"]
    rate = V_in["ru_budget_rate_2026"]
    ngd_9m_bn = ngd_9m_tln * 1000 / rate

    econ = {
        "k": k,
        "full_shift": abs(get["RUSY"]["coef"] + get["Y26"]["coef"]),
        "export_mt": export_mt,
        "bbl_per_t": BBL_PER_T,
        "loss_bn": loss_bn,
        "export_value_bn": export_value_bn,
        "loss_share": loss_bn / export_value_bn * 100,
        "per_dollar_bn": per_dollar,
        "loss_5usd_bn": 5 * per_dollar,
        "gap_share_brent": k / desc["RUS_2025"]["brent"] * 100,
        "ngd_9m_tln": ngd_9m_tln,
        "ngd_9m_bn": ngd_9m_bn,
        "ngd_share": loss_bn / ngd_9m_bn * 100,
        "ngd_loss_pct_of_ngd": loss_bn / ngd_9m_bn * 100,
        "budget_price": V_in["ru_budget_urals_2026"],
        "az_export_mt": V_in["az_oil_export_2025"],
        "az_premium_2026": desc["AZE_2026"]["D"],
        "az_premium_2025": desc["AZE_2025"]["D"],
        "az_budget_price": V_in["az_budget_oil_2026"],
        "rate": V_in["ru_budget_rate_2026"],
        "loss_rub_trln": loss_bn * V_in["ru_budget_rate_2026"] / 1000,
        "per_dollar_rub_bn": (V_in["ru_budget_rate_2026"] * per_dollar),
        "az_per_dollar_bn": V_in["az_oil_export_2025"] * BBL_PER_T / 1000,
    }

    res = {
        "meta": {"n": int(ols.nobs), "k_params": int(len(ols.params)),
                 "months": int(df.month.nunique()),
                 "period": f"{df.month.min()} — {df.month.max()}",
                 "split": SPLIT, "formula": FORMULA,
                 "df_resid": int(ols.df_resid),
                 "n_rus": int((df.country == "RUS").sum()),
                 "n_aze": int((df.country == "AZE").sum())},
        "fit": {"r2": float(ols.rsquared), "r2_adj": float(ols.rsquared_adj),
                "f": float(ols.fvalue), "f_p": float(ols.f_pvalue),
                "sigma": float(np.sqrt(ols.mse_resid)),
                "aic": float(ols.aic)},
        "rows": rows,
        "diag": diagnostics(ols),
        "chow": chow_test(df),
        "dates": date_check(df),
        "desc": desc,
        "did_manual": float(did_manual),
        "pretrend": pretrend,
        "robust": rob,
        "acc": acc,
        "econ": econ,
        "data": df.assign(D=df.D.round(2)).to_dict("records"),
    }
    with open(os.path.join(OUT, "model.json"), "w", encoding="utf-8") as fh:
        json.dump(res, fh, ensure_ascii=False, indent=1)

    # --------------------------------------------------------------- отчёт
    print(f"n = {res['meta']['n']}, месяцев {res['meta']['months']}, "
          f"R² = {res['fit']['r2']:.3f}, adj R² = {res['fit']['r2_adj']:.3f}")
    for r in rows:
        print(f"  {r['var']:9s} {r['coef']:8.3f}  se {r['se']:6.3f} "
              f"p {r['p']:.4g} | кластер: se {r['cl_se']:6.3f} p {r['cl_p']:.3g}")
    print(f"DiD вручную: {did_manual:.3f}, коэффициент k: {get['RUSY']['coef']:.3f}")
    print(f"тренд разрыва в 2025 г.: {pretrend['slope']:.3f} долл./барр. в месяц "
          f"(p {pretrend['p']:.3f})")
    print(f"потери: {econ['loss_bn']:.2f} млрд долл., "
          f"{econ['loss_share']:.1f} % экспорта, "
          f"{econ['ngd_share']:.1f} % НГД")
    print("сохранено:", os.path.join(OUT, "model.json"))


if __name__ == "__main__":
    main()
