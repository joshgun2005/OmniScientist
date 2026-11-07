# -*- coding: utf-8 -*-
"""Эконометрическое приложение к ВКР: три спецификации модели.

Строится по месячным данным:
  * Brent и WTI — github.com/datasets/oil-prices (котировки спот, долл./барр.);
  * Urals — помесячные расчётные цены Минэкономразвития России 2025–2026 гг.
    (файл facts.py), скидка к Brent — из тех же публикаций и оценок Argus;
  * институциональные события — даты вступления в силу решений ЕС и
    Правительства РФ (цена потолка, эмбарго, запреты на импорт газа).

Модели:
  (М1) регрессия с фиктивными переменными институциональных сдвигов — на
       полной выборке Brent–WTI (1987–2026), проверка устойчивости связи
       двух бенчмарков к институциональным шокам;
  (М2) модель дифференциала Urals к Brent (2025–2026) с проверкой вклада
       дамми-переменных санкционного расширения;
  (М3) AR(1)-модель цены Brent для прогноза сценариев 2027 г.

Все оценки сохраняются в out/econometrics.json и используются в тексте
работы; «ручных» коэффициентов в тексте нет.
"""
import csv
import json
import os

import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.tsa.ar_model import AutoReg
from statsmodels.tsa.stattools import adfuller, coint

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "out")
DATA = os.path.join(BASE, "data")

from facts import ALL, value  # noqa: E402


def load_pair():
    b = pd.read_csv(os.path.join(DATA, "brent-monthly.csv"))
    w = pd.read_csv(os.path.join(DATA, "wti-monthly.csv"))
    for df in (b, w):
        df["Date"] = pd.to_datetime(df["Date"])
        df["m"] = df["Date"].dt.to_period("M")
    b = b.set_index("m")["Price"].rename("brent")
    w = w.set_index("m")["Price"].rename("wti")
    df = pd.concat([b, w], axis=1).dropna()
    df["spread"] = df["brent"] - df["wti"]
    return df


def institutional_dummies(idx):
    """Дамми институциональных сдвигов мировой архитектуры рынка."""
    dates = {
        "d_cap": "2022-12",        # введение предельной цены (ЕС/ G7)
        "d_embargo": "2023-02",    # запрет поставок по механизму потолка
        "d_hormuz": "2026-10",     # обострение в Ормузском проливе
    }
    d = pd.DataFrame(index=idx)
    for name, start in dates.items():
        d[name] = (idx >= pd.Period(start, "M")).astype(int)
    return d


def ols_table(res, name, extra=None):
    out = {
        "name": name,
        "n": int(res.nobs),
        "r2": round(float(res.rsquared), 3),
        "r2_adj": round(float(res.rsquared_adj), 3),
        "f": round(float(res.fvalue), 2),
        "f_p": float(res.f_pvalue),
        "dw": round(float(sm.stats.durbin_watson(res.resid)), 2),
        "params": {},
    }
    ci = res.conf_int()
    for k in res.params.index:
        out["params"][k] = {
            "coef": round(float(res.params[k]), 4),
            "se": round(float(res.bse[k]), 4),
            "t": round(float(res.tvalues[k]), 2),
            "p": float(res.pvalues[k]),
            "lo": round(float(ci.loc[k, 0]), 4),
            "hi": round(float(ci.loc[k, 1]), 4),
        }
    if extra:
        out.update(extra)
    return out


# ------------------------------------------------------------------ М1
def model1(df):
    """Brent ~ WTI + институциональные дамми + тренд.

    Проверяет, устойчива ли связь двух бенчмарков к изменению режима
    регулирования: значимость дамми означает сдвиг спреда.
    """
    d = institutional_dummies(df.index)
    X = pd.concat([df["wti"].rename("wti"), d], axis=1)
    X["trend"] = np.arange(len(X)) / 12.0
    X = sm.add_constant(X)
    m = sm.OLS(df["brent"], X).fit(cov_type="HAC", cov_kwds={"maxlags": 6})
    return ols_table(m, "M1: Brent ~ WTI + институциональные сдвиги",
                     extra={"spec": "OLS, HAC (Newey-West, 6 лагов)"})


# ------------------------------------------------------------------ М2
def urals_series():
    """Помесячный ряд дифференциала Urals к Brent, 2025–2026."""
    rows = []
    for y in (2025, 2026):
        for m in range(1, 13):
            key = f"ru_urals_{y}_{m:02d}"
            if key in ALL:
                rows.append((pd.Period(f"{y}-{m:02d}", "M"),
                             ALL[key][0]))
    u = pd.Series(dict(rows), name="urals").sort_index()
    return u


def model2(df):
    """Дифференциал Urals–Brent: связь с уровнем цены и институциональными дамми.

    На короткой выборке (2025–2026) оценивается регрессия
    D = a + b*Brent + c*d_cap2026 + d*d_peak
    """
    u = urals_series()
    idx = u.index
    brent = df["brent"].reindex(idx)
    disc = brent - u

    d = pd.DataFrame(index=idx)
    d["d_cap_2026"] = (idx >= pd.Period("2026-02", "M")).astype(int)
    d["d_peak"] = (idx >= pd.Period("2026-05", "M")).astype(int)
    X = pd.concat([brent.rename("brent"), d], axis=1).dropna()
    y = disc.reindex(X.index)
    X = sm.add_constant(X)
    m = sm.OLS(y, X).fit(cov_type="HAC", cov_kwds={"maxlags": 2})
    res = ols_table(m, "M2: дифференциал Urals–Brent (2025–2026)",
                    extra={"spec": "OLS, HAC (Newey-West, 2 лага)",
                           "n_periods": f"{X.index[0]}–{X.index[-1]}"})
    # фактический и расчётный дисконт
    res["fitted"] = {str(k): round(float(v), 2)
                     for k, v in zip(X.index, m.fittedvalues)}
    res["actual"] = {str(k): round(float(v), 2) for k, v in y.items()}
    res["mean_disc"] = round(float(y.mean()), 2)
    res["max_disc"] = round(float(y.max()), 2)
    res["max_disc_month"] = str(y.idxmax())
    return res


# ------------------------------------------------------------------ М2'
def model2b(df):
    """Расширенная модель дифференциала: отдельные дамми на потолок цены
    и на запрет импорта газа, а также логарифм цены вместо уровня."""
    u = urals_series()
    idx = u.index
    brent = df["brent"].reindex(idx)
    disc = brent - u

    d = pd.DataFrame(index=idx)
    d["d_cap_2026"] = (idx >= pd.Period("2026-02", "M")).astype(int)   # потолок $44,1
    d["d_gasban"] = (idx >= pd.Period("2026-01", "M")).astype(int)     # регламент ЕС
    d["d_geopolit"] = (idx >= pd.Period("2026-03", "M")).astype(int)   # Ормузский шок
    d["ln_brent"] = np.log(brent)
    X = pd.concat([d], axis=1).dropna()
    y = disc.reindex(X.index)
    X = sm.add_constant(X)
    m = sm.OLS(y, X).fit(cov_type="HAC", cov_kwds={"maxlags": 2})
    res = ols_table(m, "M2': расширенная модель дифференциала")
    res["spec"] = "OLS, HAC (Newey-West, 2 лага), лог-спецификация"
    res["fitted"] = {str(k): round(float(v), 2)
                     for k, v in zip(X.index, m.fittedvalues)}
    return res


# ------------------------------------------------------------------ М3
def model3(df, h=14):
    """AR(1) логарифма Brent + тесты на единичный корень и полураспад."""
    s = np.log(df["brent"])
    m = AutoReg(s, lags=1).fit()
    fc = m.predict(start=len(s), end=len(s) + h - 1)
    last = float(s.iloc[-1])
    pred = np.exp(fc)
    return {
        "name": "M3: AR(1) для логарифма цены Brent",
        "spec": "AutoReg, лаг 1, константа",
        "phi": round(float(m.params[f"{s.name}.L1"] if f"{s.name}.L1" in m.params else m.params.iloc[1]), 4),
        "const": round(float(m.params["const"]), 4),
        "r2": round(float(m.rsquared), 3),
        "aic": round(float(m.aic), 1),
        "n": int(m.nobs),
        "last_level": round(float(np.exp(last)), 2),
        "forecast_mean": round(float(pred.mean()), 2),
        "forecast_min": round(float(pred.min()), 2),
        "forecast_max": round(float(pred.max()), 2),
        "half_life_months": round(float(np.log(0.5) / np.log(abs(
            float(m.params[f"{s.name}.L1"] if f"{s.name}.L1" in m.params else m.params.iloc[1])))), 1),
        "forecast": {str(k): round(float(v), 2)
                     for k, v in zip(fc.index, pred)},
        "adf_brent": _adf(df["brent"]),
        "adf_dln": _adf(np.log(df["brent"]).diff().dropna()),
        "coint_p": round(float(coint(df["brent"], df["wti"])[1]), 4),
        "mean_reversion_note": (
            "phi близка к единице: шок цены затухает медленно, поэтому "
            "сценарии на 2027 г. строятся как условные, а не как точечный "
            "прогноз"),
    }


def _adf(x):
    stat, p = adfuller(x, maxlag=6, autolag=None)[:2]
    return {"stat": round(float(stat), 2), "p": round(float(p), 3)}


def text_dump():
    """Полный вывод оценок в виде текста — для приложения к ВКР."""
    df = load_pair()
    u = urals_series()
    lines = []
    lines.append("МОДЕЛЬ М1. Зависимая переменная: цена Brent, долл./барр.")
    lines.append("Выборка: %s, n = %d" % (f"{df.index[0]}–{df.index[-1]}",
                                          len(df)))
    d = institutional_dummies(df.index)
    X = pd.concat([df["wti"].rename("wti"), d], axis=1)
    X["trend"] = np.arange(len(X)) / 12.0
    X = sm.add_constant(X)
    m = sm.OLS(df["brent"], X).fit(cov_type="HAC", cov_kwds={"maxlags": 6})
    lines.append(str(m.summary()))
    lines.append("")
    lines.append("МОДЕЛЬ М2. Зависимая переменная: дифференциал Urals–Brent")
    brent = df["brent"].reindex(u.index)
    disc = brent - u
    dd = pd.DataFrame(index=u.index)
    dd["d_cap_2026"] = (u.index >= pd.Period("2026-02", "M")).astype(int)
    dd["d_peak"] = (u.index >= pd.Period("2026-05", "M")).astype(int)
    X2 = pd.concat([brent.rename("brent"), dd], axis=1).dropna()
    X2 = sm.add_constant(X2)
    m2 = sm.OLS(disc.reindex(X2.index), X2).fit(
        cov_type="HAC", cov_kwds={"maxlags": 2})
    lines.append(str(m2.summary()))
    lines.append("")
    lines.append("МОДЕЛЬ М3. AR(1) для логарифма цены Brent")
    s3 = np.log(df["brent"])
    m3 = AutoReg(s3, lags=1).fit()
    lines.append(str(m3.summary()))
    return "\n".join(lines)


def main():
    df = load_pair()
    res = {
        "n_months": int(len(df)),
        "period": f"{df.index[0]}–{df.index[-1]}",
        "M1": model1(df),
        "M2": model2(df),
        "M2b": model2b(df),
        "M3": model3(df),
    }
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "econometrics.json"), "w",
              encoding="utf-8") as fh:
        json.dump(res, fh, ensure_ascii=False, indent=1)

    for key in ("M1", "M2", "M2b", "M3"):
        m = res[key]
        print(f"\n{m['name']}")
        print(f"  n={m.get('n')}, R2={m.get('r2')}, "
              f"spec={m.get('spec')}")
        for k, p in (m.get("params") or {}).items():
            print(f"  {k:12s} {p['coef']:>10.4f}  se={p['se']:.4f} "
                  f"t={p['t']:>7.2f} p={p['p']:.4f}")
        if key == "M3":
            print(f"  phi={m['phi']}, полураспад={m['half_life_months']} мес., "
                  f"прогноз {m['forecast_min']}–{m['forecast_max']}")
    with open(os.path.join(OUT, "econometrics_dump.txt"), "w",
              encoding="utf-8") as fh:
        fh.write(text_dump())
    print("\nсохранено: out/econometrics.json, out/econometrics_dump.txt")


if __name__ == "__main__":
    main()
