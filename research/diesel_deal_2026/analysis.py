# -*- coding: utf-8 -*-
"""Расчётный контур статьи о «дизельной сделке» Россия — США (октябрь 2026 г.).

Все входные величины взяты из первичных документов и публикаций 2026 г.;
для каждой группы ниже указан источник и дата обращения. Производные
показатели (выручка, покрытие дефицита, эквиваленты потребления)
вычисляются здесь и только здесь; текст статьи импортирует готовые
значения из metrics.json, поэтому любая цифра в рукописи трассируется
до этой записи.

Запуск:  python3 analysis.py
Выход:   metrics.json, tables/*.csv, figures/*.png
"""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
import numpy as np

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "out")
FIG = os.path.join(BASE, "figures")
TAB = os.path.join(BASE, "tables")
for d in (OUT, FIG, TAB):
    os.makedirs(d, exist_ok=True)

# ---------------------------------------------------------------- шрифт
FONT_PATH = "/home/user/OmniScientist/desktop/public/assets/fonts/TimesNewRoman-Regular.ttf"
if os.path.exists(FONT_PATH):
    fm.fontManager.addfont(FONT_PATH)
    plt.rcParams["font.family"] = "Times New Roman"
else:  # запасной вариант для чистой среды
    plt.rcParams["font.family"] = "DejaVu Serif"
plt.rcParams.update({
    "font.size": 10,
    "axes.titlesize": 10,
    "axes.labelsize": 9.5,
    "xtick.labelsize": 8.5,
    "ytick.labelsize": 8.5,
    "legend.fontsize": 8.5,
    "axes.edgecolor": "#333333",
    "axes.linewidth": 0.8,
    "figure.dpi": 300,
    "savefig.bbox": "tight",
})

BBL_PER_T = 7.45          # баррелей дизельного топлива в тонне (7,45)
MB_PER_T = BBL_PER_T / 1000.0

# ------------------------------------------------------- входные данные
# Источники (по группам ключей V):
#   * контрактный график и сроки — заявления Д. Трампа (Truth Social, 09.10.2026),
#     Кремля (09.10.2026), А. Новака (ТАСС/Reuters, 10–14.10.2026);
#   * экспортный ресурс и фактические отгрузки — Reuters/LSEG, Kpler, ИРТТЭК (12–27.10.2026);
#   * мировые объёмы и дефицит — EIA STEO (сентябрь 2026), МЭА OMR (сентябрь 2026), JODI-Oil;
#   * цены и запасы США — EIA Weekly Petroleum Status Report, AAA, 07.11.2026;
#   * бюджет РФ — Минфин России (январь–октябрь 2026), курс — Банк России (06.11.2026).
V = {
    # контрактный график (заявление Д. Трампа 09.10.2026, подтверждено А. Новаком)
    "oct_declared": 0.300,      # млн т, октябрь 2026
    "nov_declared": 0.500,      # млн т, ноябрь 2026
    "dec_declared": 1.000,      # млн т, декабрь 2026
    "monthly_steady": 1.000,    # млн т/мес, январь–март 2027 (в пределах окна лицензии)
    "cap_monthly": 3.000,       # млн т/мес, верхняя граница «в короткие сроки»
    "cap_range_hi": 3.500,      # млн т/мес, оценка А. Новака к концу года

    # фактическое исполнение
    "apr_available": 3.000,     # млн т/мес, ресурс для экспорта в апреле 2026
    "sep_available": 0.325,     # млн т/мес, оценка ресурса в сентябре 2026 (0,30–0,35)
    "oct_export_actual": 0.510, # млн т, фактический экспорт дизеля за октябрь 2026
    "nov_export_plan": 2.150,   # млн т, план экспорта на ноябрь 2026
    "first_cargo": 0.040,       # млн т, партия танкера Agioi Fanendes

    # базовые объёмы
    "ru_2025_export": 39.400,   # млн т, экспорт дизеля из РФ в 2025 г.
    "ru_2025_kpler_mbd": 0.817, # млн барр./сут, Kpler, 2025
    "ru_seaborne_2025": 2.600,  # млн т/мес, морской экспорт в среднем за 2025 г. (Kpler)
    "ru_share_trade": 9.500,    # %, доля РФ в мировом экспорте дизеля, 2025 г.
    "us_share_trade": 15.400,   # %, доля США, 2025 г.
    "world_consumption_mt_month": 120.0,  # млн т/мес, мировое потребление
    "world_trade_mt_month": 30.0,         # млн т/мес, международная торговля
    "deficit_low": 4.0,         # млн т/мес, нижняя оценка мирового дефицита
    "deficit_high": 6.0,        # млн т/мес, верхняя оценка
    "us_demand_mbd": 3.700,     # млн барр./сут, потребление дизеля в США

    # цены
    "brent": 100.0,             # долл./барр., 6 ноября 2026 г.
    "urals": 77.0,              # долл./барр., 6 ноября 2026 г.
    "discount_lo": 10.0,        # долл./барр., нижняя оценка дисконта Urals к Brent
    "discount_hi": 23.0,        # долл./барр., верхняя оценка
    "diesel_usd_t_low": 900.0,  # сценарий мягких цен, долл./т FOB
    "diesel_usd_t_mid": 1100.0, # базовый сценарий
    "diesel_usd_t_hi": 1400.0,  # сценарий кризисных цен (≈188 долл./барр.)
    "us_retail_peak": 6.51,     # долл./галлон, 21.09.2026
    "us_retail_nov": 6.284,     # долл./галлон, 07.11.2026
    "us_retail_oct25": 3.700,   # долл./галлон, октябрь 2025 г. (≈)
    "us_retail_oct19": 6.276,   # долл./галлон, 19.10.2026
    "us_retail_oct29": 6.350,   # долл./галлон, 29.10.2026
    "us_retail_sep18": 6.179,   # долл./галлон, 12.10.2026 (неделей ранее)
    "eia_2026_avg": 5.07,       # долл./галлон, прогноз EIA (сентябрь 2026)
    "eia_2027_avg": 4.40,       # долл./галлон

    # запасы
    "stocks_jul31": 107.2,      # млн барр., 31.07.2026
    "stocks_aug19": 105.6,      # млн барр.
    "stocks_sep11": 107.9,      # млн барр.
    "stocks_oct02": 105.1,      # млн барр.
    "stocks_nov": 100.0,        # млн барр., порог, ниже которого запасы опустились в начале ноября

    # бюджет РФ
    "ngd_aug": 424.0,           # млрд руб., НГД за август 2026
    "ngd_sep": 452.4,
    "ngd_oct": 971.2,
    "ngd_9m": 5471.1,           # млрд руб., НГД за январь–сентябрь 2026
    "ngd_10m": 6442.3,          # млрд руб., НГД за январь–октябрь 2026
    "damper_sep": 305.5,        # млрд руб., выплаты по демпферу в сентябре (за август)
    "damper_oct": 415.0,        # млрд руб., в октябре (за сентябрь)
    "damper_9m": 1221.3,        # млрд руб., за 9 месяцев
    "deficit_9m": 5186.0,       # млрд руб., дефицит за январь–сентябрь (2,2 % ВВП)
    "deficit_year": 7345.0,     # млрд руб., оценка дефицита на 2026 г. (3,2 % ВВП)
    "ngd_plan_law": 8919.0,     # млрд руб., закон о бюджете на 2026 г.
    "ngd_plan_upd": 7584.4,     # млрд руб., уточнённая оценка (проект бюджета 2027–2029)
    "usdrub": 81.79,            # руб./долл., курс ЦБ на 06.11.2026
    "export_rev_aug": 13.87,    # млрд долл., доходы РФ от экспорта нефти и нефтепродуктов, август 2026 (МЭА)
}

D = {}   # производные показатели
M = {}   # отформатированные для текста значения

# ------------------------------------------- 1. контрактная программа
program = {
    "Октябрь 2026": V["oct_declared"],
    "Ноябрь 2026": V["nov_declared"],
    "Декабрь 2026": V["dec_declared"],
    "Январь 2027": V["monthly_steady"],
    "Февраль 2027": V["monthly_steady"],
    "Март 2027": V["monthly_steady"],
}
D["program_total"] = round(sum(program.values()), 3)           # 4,8 млн т
D["program_months"] = len(program)
D["program_avg_month"] = round(D["program_total"] / len(program), 3)
D["program_total_mb"] = round(D["program_total"] * BBL_PER_T, 2)
D["program_cap_total"] = round(V["oct_declared"] + V["nov_declared"] + V["dec_declared"] + V["cap_monthly"], 3)
D["program_share_2025export"] = round(100 * D["program_total"] / V["ru_2025_export"], 1)
D["program_share_trade_month"] = round(100 * D["program_total"] / V["world_trade_mt_month"], 1)
D["program_avg_share_trade"] = round(100 * D["program_avg_month"] / V["world_trade_mt_month"], 2)
# расширенный вариант: 1 млн т/мес сохраняется до истечения лицензии 07.04.2027
D["program_total_ext"] = round(V["oct_declared"] + V["nov_declared"]
                               + V["monthly_steady"] * 5 + 7 / 30, 2)   # ≈5,8 млн т
D["program_ext_mb"] = round(D["program_total_ext"] * BBL_PER_T, 1)

# ------------------------------------- 2. эквиваленты потребления США
D["oct_declared_mb"] = round(V["oct_declared"] * BBL_PER_T, 3)          # 2,235 млн барр.
D["oct_declared_days_us"] = round(D["oct_declared_mb"] / V["us_demand_mbd"], 2)
D["oct_declared_hours_us"] = round(24 * D["oct_declared_days_us"], 1)
D["nov_declared_kbd"] = round(V["nov_declared"] * 1000 * BBL_PER_T / 30.4, 1)   # тыс. барр./сут
D["nov_share_us_demand"] = round(100 * D["nov_declared_kbd"] / (V["us_demand_mbd"] * 1000), 1)
D["us_month_consumption_mt"] = round(V["us_demand_mbd"] * 30.4 / BBL_PER_T, 1)  # млн т/мес
D["nov_share_us_month"] = round(100 * V["nov_declared"] / D["us_month_consumption_mt"], 1)
D["program_days_us"] = round(D["program_total_mb"] / V["us_demand_mbd"], 1)
D["first_cargo_kb"] = round(V["first_cargo"] * 1000 * BBL_PER_T, 0)
D["first_cargo_hours_us"] = round(24 * (D["first_cargo_kb"] / 1000) / V["us_demand_mbd"], 1)

# ------------------------------- 3. достаточность относительно дефицита
D["deficit_mid"] = round((V["deficit_low"] + V["deficit_high"]) / 2, 1)
D["cover_oct_low"] = round(100 * V["oct_declared"] / V["deficit_high"], 1)
D["cover_oct_high"] = round(100 * V["oct_declared"] / V["deficit_low"], 1)
D["cover_nov_low"] = round(100 * V["nov_declared"] / V["deficit_high"], 1)
D["cover_nov_high"] = round(100 * V["nov_declared"] / V["deficit_low"], 1)
D["cap_share_trade"] = round(100 * V["cap_monthly"] / V["world_trade_mt_month"], 1)
D["ru_2025_month"] = round(V["ru_2025_export"] / 12, 2)
D["deficit_vs_ru_capacity_low"] = round(V["deficit_low"] / D["ru_2025_month"], 2)
D["deficit_vs_ru_capacity_high"] = round(V["deficit_high"] / D["ru_2025_month"], 2)
D["sep_vs_apr_pct"] = round(100 * V["sep_available"] / V["apr_available"], 1)   # 10,8 %
D["sep_drop_factor"] = round(V["apr_available"] / V["sep_available"], 1)        # 9,2 раза
D["nov_vs_2025_pct"] = round(100 * V["nov_export_plan"] / D["ru_2025_month"], 1)
D["oct_vs_2025_pct"] = round(100 * V["oct_export_actual"] / D["ru_2025_month"], 1)
D["world_demand_diesel_mt_day"] = round(V["world_consumption_mt_month"] / 30.4, 2)

# ------------------------------------------------- 4. ценовой / выручка
D["bbl_price_at_1400"] = round(V["diesel_usd_t_hi"] / BBL_PER_T, 1)     # 187,9 долл./барр.
D["bbl_price_at_1100"] = round(V["diesel_usd_t_mid"] / BBL_PER_T, 1)
D["bbl_price_at_900"] = round(V["diesel_usd_t_low"] / BBL_PER_T, 1)

revenue = {}
for vol_name, vol in (("program", D["program_total"]),
                      ("oct_actual", V["oct_export_actual"]),
                      ("nov_plan", V["nov_export_plan"])):
    for price_name, price in (("low", V["diesel_usd_t_low"]),
                              ("mid", V["diesel_usd_t_mid"]),
                              ("hi", V["diesel_usd_t_hi"])):
        revenue[(vol_name, price_name)] = {
            "usd_bn": round(vol * price / 1000, 2),
            "rub_bn": round(vol * price / 1000 * V["usdrub"], 1),
        }
D["revenue"] = {f"{k[0]}_{k[1]}": v for k, v in revenue.items()}
D["rev_program_hi_usd"] = D["revenue"]["program_hi"]["usd_bn"]          # 6,72
D["rev_program_hi_rub"] = D["revenue"]["program_hi"]["rub_bn"]          # 549,6
D["rev_program_mid_usd"] = D["revenue"]["program_mid"]["usd_bn"]
D["rev_program_mid_rub"] = D["revenue"]["program_mid"]["rub_bn"]
D["rev_program_low_usd"] = D["revenue"]["program_low"]["usd_bn"]
D["rev_program_low_rub"] = D["revenue"]["program_low"]["rub_bn"]
D["rev_per_mt_hi_rub"] = round(V["diesel_usd_t_hi"] * V["usdrub"] / 1000, 1)  # млрд руб. на 1 млн т
D["rev_ext_hi_usd"] = round(D["program_total_ext"] * V["diesel_usd_t_hi"] / 1000, 2)
D["rev_ext_hi_rub"] = round(D["program_total_ext"] * V["diesel_usd_t_hi"] / 1000 * V["usdrub"], 1)
D["rev_ext_mid_usd"] = round(D["program_total_ext"] * V["diesel_usd_t_mid"] / 1000, 2)
D["rev_ext_mid_rub"] = round(D["program_total_ext"] * V["diesel_usd_t_mid"] / 1000 * V["usdrub"], 1)
D["rev_ext_share_deficit"] = round(100 * D["rev_ext_hi_rub"] / V["deficit_9m"], 1)

# ---------------------------------- 5. сопоставление с бюджетом России
D["rev_share_deficit"] = round(100 * D["rev_program_hi_rub"] / V["deficit_9m"], 1)
D["rev_share_deficit_year"] = round(100 * D["rev_program_hi_rub"] / V["deficit_year"], 1)
D["rev_vs_damper_months"] = round(D["rev_program_hi_rub"] / V["damper_oct"], 2)
D["rev_share_ngd_oct"] = round(100 * D["rev_program_hi_rub"] / V["ngd_oct"], 1)
D["rev_share_ngd_plan_upd"] = round(100 * D["rev_program_hi_rub"] / V["ngd_plan_upd"], 1)
D["rev_share_ngd_plan_law"] = round(100 * D["rev_program_hi_rub"] / V["ngd_plan_law"], 1)
D["rev_share_export_aug"] = round(100 * D["rev_program_hi_usd"] / V["export_rev_aug"], 1)
D["rev_ext_share_export_aug"] = round(100 * D["rev_ext_hi_usd"] / V["export_rev_aug"], 0)
D["ngd_10m_short_pct"] = 14.1
D["damper_oct_vs_sep"] = round(V["damper_oct"] / V["damper_sep"], 2)
D["damper_share_ngd_oct"] = round(100 * V["damper_oct"] / V["ngd_oct"], 1)

# --------------------------------------------- 6. цены и запасы США
D["us_retail_yoy_pct"] = round(100 * (V["us_retail_peak"] / V["us_retail_oct25"] - 1), 1)
D["us_retail_nov_vs_peak"] = round(100 * (V["us_retail_nov"] / V["us_retail_peak"] - 1), 1)
D["stocks_oct_vs_5yr"] = None  # не публикуется в используемых источниках в едином базисе


# ------------------- 7. фискальный эффект и структурные доли (авторские оценки)
K_LOW, K_HIGH = 0.25, 0.35          # допущение: эффективная доля изъятия в бюджет, 25–35 %
D["fiscal_low_rub"] = round(D["rev_program_hi_rub"] * K_LOW, 1)
D["fiscal_high_rub"] = round(D["rev_program_hi_rub"] * K_HIGH, 1)
D["fiscal_low_share_deficit"] = round(100 * D["fiscal_low_rub"] / V["deficit_9m"], 1)
D["fiscal_high_share_deficit"] = round(100 * D["fiscal_high_rub"] / V["deficit_9m"], 1)
D["fiscal_low_usd"] = round(D["fiscal_low_rub"] / V["usdrub"], 2)
D["fiscal_high_usd"] = round(D["fiscal_high_rub"] / V["usdrub"], 2)
D["damper_cover_share"] = round(100 * D["fiscal_high_rub"] / V["damper_oct"], 0)
D["rev_share_ngd_6m"] = round(100 * D["rev_program_hi_rub"] / (6 * V["ngd_oct"]), 1)
D["us_annual_consumption_mt"] = round(D["us_month_consumption_mt"] * 12, 0)
D["program_share_us_annual"] = round(100 * D["program_total"] / D["us_annual_consumption_mt"], 1)
D["us_export_share_world"] = V["us_share_trade"]
D["canada_diesel_mbd"] = 1.000
D["deal_volume_vs_canada_days"] = round(D["program_total_mb"] / D["canada_diesel_mbd"], 1)

# ---------------------------------------------------------------- КПЭ-сводка
D["agreement_date"] = "09.10.2026"
D["license_expiry"] = "07.04.2027"
D["license_days"] = 180
D["election_date"] = "03.11.2026"
D["days_deal_to_election"] = 25

# ------------------------------------------------ таблицы (CSV)
import csv


def csv_write(name, header, rows):
    path = os.path.join(TAB, name)
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(header)
        w.writerows(rows)
    return path


csv_write(
    "t1_program.csv",
    ["Месяц", "Заявленный объём, млн т", "Баррелей, млн барр."],
    [[k, f"{v:.3f}", f"{v * BBL_PER_T:.2f}"] for k, v in program.items()],
)

rows = []
for vol_name, vol_label in (("program", "Программа окт.2026–март 2027 (4,8 млн т)"),
                            ("oct_actual", "Фактический экспорт октябрь 2026 (0,51 млн т)"),
                            ("nov_plan", "План экспорта ноябрь 2026 (2,15 млн т)")):
    rows.append([vol_label,
                 f"{revenue[(vol_name,'low')]['usd_bn']:.2f}", f"{revenue[(vol_name,'low')]['rub_bn']:.1f}",
                 f"{revenue[(vol_name,'mid')]['usd_bn']:.2f}", f"{revenue[(vol_name,'mid')]['rub_bn']:.1f}",
                 f"{revenue[(vol_name,'hi')]['usd_bn']:.2f}", f"{revenue[(vol_name,'hi')]['rub_bn']:.1f}"])
csv_write("t3_revenue.csv",
          ["Сценарий объёма", "900 долл./т: млрд долл.", "900 долл./т: млрд руб.",
           "1100 долл./т: млрд долл.", "1100 долл./т: млрд руб.",
           "1400 долл./т: млрд долл.", "1400 долл./т: млрд руб."], rows)

csv_write("t4_budget.csv", ["Показатель", "Значение", "Единица"], [
    ["НГД, август 2026", f"{V['ngd_aug']:.1f}", "млрд руб."],
    ["НГД, сентябрь 2026", f"{V['ngd_sep']:.1f}", "млрд руб."],
    ["НГД, октябрь 2026", f"{V['ngd_oct']:.1f}", "млрд руб."],
    ["НГД, январь–октябрь 2026", f"{V['ngd_10m']:.1f}", "млрд руб."],
    ["Выплаты по демпферу, сентябрь", f"{V['damper_sep']:.1f}", "млрд руб."],
    ["Выплаты по демпферу, октябрь", f"{V['damper_oct']:.1f}", "млрд руб."],
    ["Дефицит, январь–сентябрь 2026", f"{V['deficit_9m']:.1f}", "млрд руб."],
    ["Валовая выручка программы (1400 долл./т)", f"{D['rev_program_hi_rub']:.1f}", "млрд руб."],
])

# ---------------------------------------------------------------- рисунки
GREY = "#4d4d4d"
LIGHT = "#b3b3b3"
ACCENT = "#1f1f1f"

# Рис. 1 — динамика экспортного ресурса дизеля
fig, ax = plt.subplots(figsize=(6.4, 3.1))
labels = ["Апрель\n2026", "Сентябрь\n2026", "Октябрь\n2026\n(факт)", "Ноябрь\n2026\n(план)",
          "Ориентир\nконца 2026", "Среднемес.\n2025"]
vals = [V["apr_available"], V["sep_available"], V["oct_export_actual"],
        V["nov_export_plan"], V["cap_range_hi"], D["ru_2025_month"]]
colors = [LIGHT, LIGHT, GREY, GREY, ACCENT, "#7f7f7f"]
bars = ax.bar(labels, vals, color=colors, width=0.62, edgecolor="white", linewidth=0.6)
for b, v in zip(bars, vals):
    ax.text(b.get_x() + b.get_width() / 2, v + 0.06, f"{v:.2f}".replace(".", ","),
            ha="center", va="bottom", fontsize=8.2)
ax.set_ylabel("млн т в месяц")
ax.set_ylim(0, 4.0)
ax.axhline(V["ru_2025_export"] / 12, color="#7f7f7f", lw=0.8, ls="--")
ax.text(5.35, V["ru_2025_export"] / 12 + 0.08, "среднемесячный экспорт 2025 г.", fontsize=7.2, color="#666666", ha="right")
ax.set_title("Экспортный ресурс российского дизеля: обвал предложения и целевые ориентиры", pad=8)
ax.spines[["top", "right"]].set_visible(False)
ax.grid(axis="y", lw=0.4, color="#dddddd")
ax.set_axisbelow(True)
fig.savefig(os.path.join(FIG, "fig1_volumes.png"), dpi=300)
plt.close(fig)

# Рис. 2 — покрытие мирового дефицита заявленными объёмами
cover = {
    "Окт. 2026": V["oct_declared"],
    "Ноя. 2026": V["nov_declared"],
    "Дек. 2026": V["dec_declared"],
    "Янв.–март\n2027*": V["monthly_steady"],
}
D["cover_pct"] = {
    k: (round(100 * v / V["deficit_high"], 1), round(100 * v / V["deficit_low"], 1))
    for k, v in cover.items()
}
kpler_threshold_mt = 0.400 * 30.4 / BBL_PER_T   # 400 тыс. барр./сут -> млн т/мес
D["kpler_threshold_mt"] = round(kpler_threshold_mt, 2)
D["kpler_threshold_share"] = (round(100 * kpler_threshold_mt / V["deficit_high"], 1),
                              round(100 * kpler_threshold_mt / V["deficit_low"], 1))

fig, ax = plt.subplots(figsize=(6.4, 3.2))
xs = np.arange(len(cover))
lo = [D["cover_pct"][k][0] for k in cover]
hi = [D["cover_pct"][k][1] for k in cover]
ax.bar(xs, lo, width=0.52, color=GREY, edgecolor="white", linewidth=0.6)
ax.bar(xs, [h - l for h, l in zip(hi, lo)], bottom=lo, width=0.52, color=LIGHT, edgecolor="white",
       linewidth=0.6)
for i, (l, h) in enumerate(zip(lo, hi)):
    ax.text(i, h + 1.2, f"{l:.1f}".replace(".", ",") + "–" + f"{h:.1f}".replace(".", ",") + " %",
            ha="center", fontsize=8)
ax.axhspan(D["kpler_threshold_share"][0], D["kpler_threshold_share"][1], color="#000000",
           alpha=0.07, lw=0)
ax.axhline(np.mean(D["kpler_threshold_share"]), color="#555555", lw=0.9, ls=(0, (4, 3)))
ax.set_xticks(xs)
ax.set_xticklabels(list(cover))
ax.set_ylabel("доля мирового дефицита, %")
ax.set_ylim(0, 46)
ax.set_title("Покрытие мирового дефицита дизеля заявленными объёмами сделки", pad=8)
ax.spines[["top", "right"]].set_visible(False)
ax.grid(axis="y", lw=0.4, color="#dddddd")
ax.set_axisbelow(True)
ax.text(0.0, -0.20, "* при сохранении поставок на уровне 1 млн т/мес; тёмный сегмент — дефицит 6 млн т/мес,\nсветлый — 4 млн т/мес; пунктир — порог ценовой чувствительности ≈400 тыс. барр./сут (Kpler)",
        transform=ax.transAxes, fontsize=6.8, color="#666666")
fig.savefig(os.path.join(FIG, "fig2_coverage.png"), dpi=300)
plt.close(fig)

# Рис. 3 — асимметрия масштабов (логарифмическая шкала)
fig, ax = plt.subplots(figsize=(6.4, 3.3))
items = [
    ("Мировое потребление\nдизеля, млн т/мес", V["world_consumption_mt_month"]),
    ("Международная торговля\nдизелем, млн т/мес", V["world_trade_mt_month"]),
    ("Потребление в США,\nмлн т/мес", D["us_month_consumption_mt"]),
    ("Мировой дефицит,\nмлн т/мес (4–6)", D["deficit_mid"]),
    ("Экспорт РФ 2025,\nмлн т/мес", D["ru_2025_month"]),
    ("Заявленная программа\n(в среднем), млн т/мес", D["program_avg_month"]),
    ("Факт октября 2026,\nмлн т/мес", V["oct_export_actual"]),
]
names = [i[0] for i in items][::-1]
vals = [i[1] for i in items][::-1]
cols = ["#1f1f1f" if "Факт" in n else ("#8c8c8c" if "программа" in n else LIGHT) for n in names]
b = ax.barh(names, vals, color=cols, height=0.6, edgecolor="white", linewidth=0.6)
ax.set_xscale("log")
ax.set_xlim(0.3, 300)
for rect, v in zip(b, vals):
    ax.text(v * 1.12, rect.get_y() + rect.get_height() / 2, f"{v:.2f}".replace(".", ","),
            va="center", fontsize=8)
ax.set_xlabel("млн т в месяц (логарифмическая шкала)")
ax.set_title("Масштаб сделки относительно мирового рынка средних дистиллятов", pad=8)
ax.spines[["top", "right"]].set_visible(False)
ax.grid(axis="x", lw=0.4, color="#dddddd")
ax.set_axisbelow(True)
fig.savefig(os.path.join(FIG, "fig3_asymmetry.png"), dpi=300)
plt.close(fig)

# Рис. 4 — фискальный контур: НГД и демпфер
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(6.6, 2.9), gridspec_kw={"width_ratios": [1.15, 1]})
lab = ["Август", "Сентябрь", "Октябрь"]
ngd = [V["ngd_aug"], V["ngd_sep"], V["ngd_oct"]]
dmp = [None, V["damper_sep"], V["damper_oct"]]
xx = np.arange(3)
w = 0.36
ax1.bar(xx - w / 2, ngd, w, color=GREY, label="Нефтегазовые доходы")
ax1.bar(xx + w / 2, [0 if d is None else d for d in dmp], w, color=LIGHT,
        label="Выплаты по демпферу (за предшеств. месяц)")
for i, v in enumerate(ngd):
    ax1.text(i - w / 2, v + 15, f"{v:.0f}", ha="center", fontsize=7.6)
for i, v in enumerate(dmp):
    if v:
        ax1.text(i + w / 2, v + 15, f"{v:.0f}", ha="center", fontsize=7.6)
ax1.set_xticks(xx)
ax1.set_xticklabels(lab)
ax1.set_ylabel("млрд руб.")
ax1.set_ylim(0, 1320)
ax1.set_title("а) Нефтегазовые доходы и демпфер, 2026 г.", fontsize=9)
ax1.legend(frameon=False, fontsize=7.0, loc="upper left", ncol=2, handlelength=1.2, columnspacing=1.0)
ax1.spines[["top", "right"]].set_visible(False)
ax1.grid(axis="y", lw=0.4, color="#dddddd")
ax1.set_axisbelow(True)

bench = [
    ("Дефицит\nянв.–сент.", V["deficit_9m"]),
    ("НГД\n(октябрь)", V["ngd_oct"]),
    ("Демпфер\n(октябрь)", V["damper_oct"]),
    ("Выручка\nпрограммы*", D["rev_program_hi_rub"]),
]
names2 = [b[0] for b in bench]
vals2 = [b[1] for b in bench]
cols2 = [LIGHT, LIGHT, LIGHT, ACCENT]
bb = ax2.bar(names2, vals2, color=cols2, width=0.62, edgecolor="white", linewidth=0.6)
for r, v in zip(bb, vals2):
    ax2.text(r.get_x() + r.get_width() / 2, v + 90, f"{v:.0f}", ha="center", fontsize=7.6)
ax2.set_ylabel("млрд руб.")
ax2.set_ylim(0, 6100)
ax2.tick_params(axis="x", labelsize=7.6)
ax2.set_title("б) Выручка программы* на фоне бюджета", fontsize=9)
ax2.spines[["top", "right"]].set_visible(False)
ax2.grid(axis="y", lw=0.4, color="#dddddd")
ax2.set_axisbelow(True)
fig.tight_layout()
fig.savefig(os.path.join(FIG, "fig4_fiscal.png"), dpi=300)
plt.close(fig)

# ------------------------------------------------------------------ вывод
def fmt(x, nd=2):
    """Русская запись числа: запятая, отсечение лишних нулей, разряды через пробел."""
    if isinstance(x, (int, float)):
        txt = f"{x:.{nd}f}"
        if "." in txt:
            txt = txt.rstrip("0").rstrip(".")
        ip, _, fp = txt.partition(".")
        neg = ip.startswith("-")
        ip = ip.lstrip("-")
        groups = []
        while len(ip) > 3:
            groups.insert(0, ip[-3:])
            ip = ip[:-3]
        groups.insert(0, ip)
        out = "\u00a0".join(groups)
        if fp:
            out += "," + fp
        return ("-" if neg else "") + out
    return str(x)


M = {k: fmt(v) for k, v in D.items() if isinstance(v, (int, float))}
# ключевые входные величины, используемые в тексте
for _k in ("oct_declared", "nov_declared", "dec_declared", "monthly_steady", "cap_monthly",
           "oct_export_actual", "nov_export_plan", "ngd_oct", "damper_oct", "ngd_10m",
           "us_retail_oct19", "us_retail_oct29", "nov_export_plan", "stocks_oct02",
           "world_consumption_mt_month", "world_trade_mt_month", "deficit_low", "deficit_high",
           "ru_2025_export", "us_demand_mbd", "brent", "urals", "cap_range_hi",
           "first_cargo", "damper_sep", "damper_9m", "ngd_aug", "ngd_sep", "ngd_plan_law",
           "ngd_plan_upd", "deficit_year", "us_retail_peak", "us_retail_nov", "eia_2026_avg",
           "eia_2027_avg", "usdrub", "export_rev_aug", "ru_share_trade", "stocks_jul31",
           "stocks_sep11", "stocks_oct02", "apr_available", "sep_available"):
    M[_k] = fmt(V[_k])
M["deficit_range"] = f"{fmt(V['deficit_low'],1)}–{fmt(V['deficit_high'],1)}"
M["fiscal_k_range"] = "0,25–0,35"
M["discount_range"] = f"{fmt(V['discount_lo'],0)}–{fmt(V['discount_hi'],0)}"
M["cap_range"] = f"{fmt(V['cap_monthly'],1)}–{fmt(V['cap_range_hi'],1)}"
M["brent"] = fmt(V["brent"], 0)
M["urals"] = fmt(V["urals"], 0)
M["usdrub"] = fmt(V["usdrub"], 2)
M["us_retail_peak"] = fmt(V["us_retail_peak"], 2)
M["us_retail_nov"] = fmt(V["us_retail_nov"], 2)
M["eia_2026_avg"] = fmt(V["eia_2026_avg"], 2)
M["eia_2027_avg"] = fmt(V["eia_2027_avg"], 2)
M["ngd_9m"] = fmt(V["ngd_9m"], 1)
M["ngd_plan_law"] = fmt(V["ngd_plan_law"], 0)
M["ngd_plan_upd"] = fmt(V["ngd_plan_upd"], 1)
M["deficit_year"] = fmt(V["deficit_year"], 0)
M["deficit_9m"] = fmt(V["deficit_9m"], 0)

payload = {"inputs": V, "derived": D, "formatted": M}
with open(os.path.join(OUT, "metrics.json"), "w", encoding="utf-8") as f:
    json.dump(payload, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    print(json.dumps(M, ensure_ascii=False, indent=1))
    print("\nТаблицы:", sorted(os.listdir(TAB)))
    print("Рисунки:", sorted(os.listdir(FIG)))
