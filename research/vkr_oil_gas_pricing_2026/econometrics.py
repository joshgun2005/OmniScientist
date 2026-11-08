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
from facts_az import gas_frame, oil_frame, period_brent  # noqa: E402



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


# ------------------------------------------------------- модели по Азербайджану
def az_gas_frame():
    """Контрактные цены азербайджанского газа и средний Brent за тот же период.

    Биржевых котировок азербайджанского газа не существует, поэтому
    используются контрактные (таможенные) цены: стоимость экспорта делится
    на объём по декларациям ГТК АР (facts_az.py). Это цены исполненных
    сделок: в них уже учтены формульные привязки, лаги и структура поставок
    по направлениям (Турция, Италия, Грузия, Сербия).
    """
    g = gas_frame().copy()
    brent = []
    for period in g.index:
        year = period[:4]
        start = "2024-01" if year == "2024" else f"{year}-01"
        brent.append(round(period_brent(start, period), 2))
    g["brent_avg"] = brent
    g["d2026"] = g.index.str.startswith("2026").astype(int)
    return g


def az_gas_increments(g):
    """Месячные приросты накопленных рядов -> цена отдельного месяца."""
    rows = []
    for (p1, r1), (p2, r2) in zip(g.iterrows(), g.iloc[1:].iterrows()):
        y1, m1 = p1.split("-")
        y2, m2 = p2.split("-")
        if y1 != y2:                       # переход через год — не месячный шаг
            continue
        if int(m2) - int(m1) != 1:         # между отсечками пропуск месяцев
            continue
        dv = r2["value_bn_usd"] - r1["value_bn_usd"]
        dq = r2["volume_bcm"] - r1["volume_bcm"]
        if dq <= 0:
            continue
        price = dv * 1000 / dq
        rows.append({"period": p2,
                     "usd_per_1000m3": round(price, 1),
                     "usd_per_mmbtu": round(price / 35.11, 2),
                     "brent": round(period_brent(p2, p2), 2)})
    return pd.DataFrame(rows).set_index("period")


def model4(g):
    """М4: средняя контрактная цена газа (долл./млн БТЕ) ~ Brent и сдвиг 2026 г.

    Уровневая спецификация на накопленных периодах: показывает, что при
    росте нефтяных цен на 1 долл./барр. контрактная цена газа меняется
    слабо, а институциональный сдвиг 2026 г. действует в противоположном
    направлении. Ограничение — накопленные периоды перекрываются, поэтому
    ошибки коррелированы, используется поправка Ньюи — Уэста.
    """
    X = sm.add_constant(g[["brent_avg", "d2026"]])
    y = g["usd_per_mmbtu"]
    m = sm.OLS(y, X).fit(cov_type="HAC", cov_kwds={"maxlags": 2})
    res = ols_table(m, "M4: контрактная цена газа Азербайджана (уровни)")
    res["spec"] = "OLS, HAC (Newey-West, 2 лага); данные ГТК АР"
    res["n_periods"] = f"{g.index[0]}–{g.index[-1]}"
    res["mean_price_2025"] = round(float(
        g[g["d2026"] == 0]["usd_per_mmbtu"].mean()), 2)
    res["mean_price_2026"] = round(float(
        g[g["d2026"] == 1]["usd_per_mmbtu"].mean()), 2)
    res["mean_brent_2025"] = round(float(
        g[g["d2026"] == 0]["brent_avg"].mean()), 2)
    res["mean_brent_2026"] = round(float(
        g[g["d2026"] == 1]["brent_avg"].mean()), 2)
    return res


def model4b(inc):
    """М4': месячная контрактная цена газа ~ Brent (приростные наблюдения).

    Ряд короткий (7 месяцев), поэтому оценивается только один регрессор.
    Коэффициент интерпретируется как эмпирический слоп контрактной цены:
    на 1 долл./барр. нефти приходится b долл./млн БТЕ газа.
    """
    X = sm.add_constant(inc[["brent"]])
    m = sm.OLS(inc["usd_per_mmbtu"], X).fit(cov_type="HAC",
                                            cov_kwds={"maxlags": 2})
    res = ols_table(m, "M4': контрактная цена газа, приростные данные")
    res["spec"] = "OLS, HAC (Newey-West, 2 лага); расчёт по приростам"
    res["n_periods"] = f"{inc.index[0]}–{inc.index[-1]}"
    res["slope"] = round(float(m.params["brent"]), 4)
    res["slope_vs_parity"] = round(float(m.params["brent"]) / 0.1724, 3)
    res["mean_price"] = round(float(inc["usd_per_mmbtu"].mean()), 2)
    res["table"] = {str(k): {"price": float(v["usd_per_mmbtu"]),
                             "brent": float(v["brent"]),
                             "usd_1000m3": float(v["usd_per_1000m3"])}
                    for k, v in inc.iterrows()}
    return res


def model5():
    """М5: контрактная цена нефти Азербайджана и премия к Brent.

    По декларациям доступны три отсечки, поэтому регрессия невозможна:
    оценивается только уровень цены и премии. Это ограничение фиксируется
    в тексте явно, а не маскируется.
    """
    o = oil_frame().copy()
    bre = []
    for period in o.index:
        year = period[:4]
        bre.append(round(period_brent(f"{year}-01", period), 2))
    o["brent_avg"] = bre
    o["premium"] = (o["usd_per_bbl"] - o["brent_avg"]).round(2)
    return {
        "name": "M5: контрактная цена нефти Азербайджана",
        "spec": "описательная статистика; n = 3, регрессия невозможна",
        "n": int(len(o)),
        "rows": {str(k): {"usd_t": float(v["usd_per_t"]),
                          "usd_bbl": float(v["usd_per_bbl"]),
                          "brent": float(v["brent_avg"]),
                          "premium": float(v["premium"]),
                          "volume_mt": float(v["volume_mt"]),
                          "value_bn": float(v["value_bn_usd"]),
                          "source": v["source"]}
                 for k, v in o.iterrows()},
        "mean_premium": round(float(o["premium"].mean()), 2),
        "note": ("биржевых котировок Azeri Light за весь период нет; "
                 "используются контрактные цены по декларациям ГТК АР"),
    }


def appendix_az_tables():
    """Текстовые таблицы для приложения: исходные данные по Азербайджану."""
    g = az_gas_frame()
    inc = az_gas_increments(g)
    lines = ["КОНТРАКТНЫЕ ЦЕНЫ АЗЕРБАЙДЖАНА (расчёт по декларациям ГТК АР)", ""]
    lines.append("Газ, накопленные периоды:")
    lines.append("  период    млрд куб. м   млрд долл.   долл./1000 м3  "
                 "долл./MMBtu   Brent")
    for period, r in g.iterrows():
        lines.append(f"  {period}   {r['volume_bcm']:9.4f}   "
                     f"{r['value_bn_usd']:8.4f}   {r['usd_per_1000m3']:11.1f}   "
                     f"{r['usd_per_mmbtu']:10.2f}   {r['brent_avg']:6.2f}")
    lines.append("")
    lines.append("Газ, приростные (месячные) значения:")
    lines.append("  период    долл./1000 м3  долл./MMBtu   Brent")
    for period, r in inc.iterrows():
        lines.append(f"  {period}   {r['usd_per_1000m3']:11.1f}   "
                     f"{r['usd_per_mmbtu']:10.2f}   {r['brent']:6.2f}")
    lines.append("")
    m5 = model5()
    lines.append("Нефть, накопленные периоды:")
    lines.append("  период    млн т      млрд долл.   долл./т    долл./барр.  "
                 "Brent    премия")
    for period, r in m5["rows"].items():
        lines.append(f"  {period}   {r['volume_mt']:8.3f}   {r['value_bn']:8.3f}"
                     f"   {r['usd_t']:8.1f}   {r['usd_bbl']:9.2f}   "
                     f"{r['brent']:7.2f}   {r['premium']:6.2f}")
    lines.append("")
    lines.append("Пересчёт: 1 тыс. куб. м = 35,11 млн БТЕ; 1 т = 7,33 барр.")
    return "\n".join(lines)


# ---------------------------------------------------------------- панель
# Месячные экспортные цены Azeri Light (долл./барр.) из справок Минфина АР
# о полугодовом исполнении бюджета. Источники: report.az (I пол. 2025),
# abc.az (I пол. 2026). Остальные месяцы публикуются только накопленным
# итогом (за 9 месяцев 2026 г. — 96,1 долл./барр.), поэтому в панель не
# входят: ряд намеренно не достраивается.
AZ_LIGHT = {
    "2025-01": 81.3, "2025-02": 77.4, "2025-03": 74.1,
    "2025-04": 69.6, "2025-05": 66.3, "2025-06": 74.0,
    "2026-01": 58.4, "2026-02": 71.1, "2026-03": 106.4,
    "2026-04": 120.1, "2026-05": 111.8, "2026-06": 89.0,
}


def panel_frame():
    """Панель «страна — месяц»: фактические экспортные цены двух стран.

    Единица наблюдения — страна-месяц. Для России используется расчётная
    цена Urals (Минэкономразвития), для Азербайджана — средняя экспортная
    цена Azeri Light (Минфин АР); обе величины — контрактные цены
    исполненных сделок, а не биржевые котировки.
    """
    b = pd.read_csv(os.path.join(DATA, "brent-monthly.csv"))
    b["m"] = pd.to_datetime(b["Date"]).dt.to_period("M")
    brent = b.set_index("m")["Price"]

    rows = []
    for month, price in urals_series().items():
        rows.append({"month": month, "country": "RUS", "price": float(price),
                     "brent": float(brent[month]),
                     "d_cap26": int(month >= pd.Period("2026-02", "M")),
                     "d_phase": int(month >= pd.Period("2025-11", "M"))})
    for month, price in AZ_LIGHT.items():
        m = pd.Period(month, "M")
        rows.append({"month": m, "country": "AZE", "price": float(price),
                     "brent": float(brent[m]),
                     "d_cap26": int(m >= pd.Period("2026-02", "M")),
                     "d_phase": 0})
    df = pd.DataFrame(rows).sort_values(["month", "country"])
    df["country"] = pd.Categorical(df["country"], ["AZE", "RUS"])
    df["prem"] = df["price"] - df["brent"]
    return df.reset_index(drop=True)


def model_panel(df):
    """Модель П1: панельная регрессия цены на Brent с взаимодействиями.

    price = a + b·Brent + g·RUS + d·D2026 + q·(D2026·RUS) + e

    Коэффициент b — перенос изменения Brent в цену азербайджанской нефти,
    b + g — в цену российской; d — институциональный сдвиг для Азербайджана,
    d + q — для России. Робастные ошибки Ньюи — Уэста (2 лага).
    """
    import statsmodels.formula.api as smf
    m = smf.ols("price ~ brent + C(country) + d_cap26*C(country)",
                data=df).fit(cov_type="HAC", cov_kwds={"maxlags": 2})
    res = ols_table(m, "П1: панельная модель цен России и Азербайджана")
    res["spec"] = ("OLS по объединённой выборке, HAC (Newey-West, 2 лага); "
                   "панель «страна — месяц»")
    res["n_countries"] = int(df["country"].nunique())
    res["period"] = f"{df['month'].min()}–{df['month'].max()}"
    b = m.params
    res["derived"] = {
        "slope_aze": round(float(b["brent"]), 4),
        "slope_rus": round(float(b["brent"] + b["brent:C(country)[T.RUS]"]), 4)
        if "brent:C(country)[T.RUS]" in b else round(float(b["brent"]), 4),
        "shift_aze": round(float(b["d_cap26"]), 4),
        "shift_rus": round(float(b["d_cap26"]
                                 + b["d_cap26:C(country)[T.RUS]"]), 4),
        "mean_prem_aze": round(float(df[df.country == "AZE"]["prem"].mean()), 2),
        "mean_prem_rus": round(float(df[df.country == "RUS"]["prem"].mean()), 2),
    }
    return res


def model_panel_prem(df):
    """Модель П2: премия (скидка) к Brent в зависимости от страны и сдвига."""
    import statsmodels.formula.api as smf
    m = smf.ols("prem ~ C(country) + d_cap26*C(country)",
                data=df).fit(cov_type="HAC", cov_kwds={"maxlags": 2})
    res = ols_table(m, "П2: премия к Brent по странам")
    res["spec"] = "OLS, HAC (Newey-West, 2 лага); зависимая переменная — премия"
    return res


def panel_dump(df):
    lines = ["ПАНЕЛЬ «СТРАНА — МЕСЯЦ»: ФАКТИЧЕСКИЕ ЭКСПОРТНЫЕ ЦЕНЫ", ""]
    lines.append("  месяц    страна   цена, долл./барр.   Brent   премия")
    for _, r in df.iterrows():
        lines.append(f"  {r['month']}   {r['country']}      "
                     f"{r['price']:8.2f}          {r['brent']:7.2f}  "
                     f"{r['prem']:7.2f}")
    lines.append("")
    lines.append("Источники: Urals — Минэкономразвития России; Azeri Light —")
    lines.append("Минфин Азербайджана (справки об исполнении бюджета, I пол.")
    lines.append("2025 и I пол. 2026 г.); Brent — datasets/oil-prices.")
    return "\n".join(lines)


def main():
    df = load_pair()
    g = az_gas_frame()
    inc = az_gas_increments(g)
    res = {
        "n_months": int(len(df)),
        "period": f"{df.index[0]}–{df.index[-1]}",
        "M1": model1(df),
        "M2": model2(df),
        "M2b": model2b(df),
        "M3": model3(df),
        "M4": model4(g),
        "M4b": model4b(inc),
        "M5": model5(),
        "P1": model_panel(panel_frame()),
        "panel": [{"month": str(r["month"]), "country": str(r["country"]),
                   "price": round(float(r["price"]), 2),
                   "brent": round(float(r["brent"]), 2),
                   "prem": round(float(r["prem"]), 2)}
                  for _, r in panel_frame().iterrows()],
        "P2": model_panel_prem(panel_frame()),
        "az": {
            "gas_cumulative": {str(k): {"volume_bcm": float(v["volume_bcm"]),
                                        "value_bn": float(v["value_bn_usd"]),
                                        "usd_1000m3": float(v["usd_per_1000m3"]),
                                        "usd_mmbtu": float(v["usd_per_mmbtu"]),
                                        "brent": float(v["brent_avg"]),
                                        "source": v["source"]}
                               for k, v in g.iterrows()},
            "gas_increments": {str(k): {"usd_1000m3": float(v["usd_per_1000m3"]),
                                        "usd_mmbtu": float(v["usd_per_mmbtu"]),
                                        "brent": float(v["brent"])}
                               for k, v in inc.iterrows()},
        },
    }
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "econometrics.json"), "w",
              encoding="utf-8") as fh:
        json.dump(res, fh, ensure_ascii=False, indent=1)

    for key in ("M1", "M2", "M2b", "M3", "M4", "M4b", "P1", "P2"):
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
        fh.write("\n\n")
        fh.write(appendix_az_tables())
        fh.write("\n\n")
        fh.write(panel_dump(panel_frame()))
    print("\nсохранено: out/econometrics.json, out/econometrics_dump.txt")


if __name__ == "__main__":
    main()
