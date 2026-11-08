# -*- coding: utf-8 -*-
"""Расчёт производных показателей ВКР.

Все числа, которые в рукописи подаются как «рассчитано автором»,
вычисляются здесь и сохраняются в out/metrics.json. Никаких «ручных» цифр
в тексте быть не должно: build_docx.py читает только этот файл.
"""
import json
import os

import numpy as np

from facts import ALL, value

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "out")
os.makedirs(OUT, exist_ok=True)

MONTHS = ["январь", "февраль", "март", "апрель", "май", "июнь",
          "июль", "август", "сентябрь", "октябрь"]

URALS_2026 = [value(f"ru_urals_2026_{m:02d}") for m in range(1, 11)]
BRENT_2026 = {6: value("ru_brent_2026_june"), 7: value("ru_brent_2026_july")}

# Баррелей в тонне (коэффициент 7,33 для российской экспортной смеси)
BBL_PER_T = 7.33

# ------------------------------------------------------------------ утилиты


def r1(x):
    return round(float(x), 1)


def r2(x):
    return round(float(x), 2)


def pct(x):
    return round(float(x), 1)


D = {}

# ---------------------------------------------- 1. Волатильность и дисконты
D["urals_2026_mean"] = r1(np.mean(URALS_2026))
D["urals_2026_min"] = r1(min(URALS_2026))
D["urals_2026_max"] = r1(max(URALS_2026))
D["urals_2026_range"] = r1(max(URALS_2026) - min(URALS_2026))
D["urals_2026_range_x"] = r1(max(URALS_2026) / min(URALS_2026))
D["urals_2026_cv"] = pct(np.std(URALS_2026, ddof=1) / np.mean(URALS_2026) * 100)
D["urals_2026_budget_gap"] = r1(np.mean(URALS_2026) - value("ru_budget_urals_2026"))
D["urals_2026_below_budget"] = sum(1 for u in URALS_2026
                                   if u < value("ru_budget_urals_2026"))

mom = [URALS_2026[i] / URALS_2026[i - 1] * 100 - 100 for i in range(1, len(URALS_2026))]
D["urals_2026_max_mom"] = pct(max(mom))
D["urals_2026_min_mom"] = pct(min(mom))
D["urals_2026_max_mom_month"] = MONTHS[mom.index(max(mom)) + 1]

disc_june = BRENT_2026[6] - value("ru_urals_2026_06")
D["disc_june_2026"] = r2(disc_june)
D["disc_june_2026_pct"] = pct(disc_june / BRENT_2026[6] * 100)
D["brent_2026_jump"] = pct((BRENT_2026[7] / BRENT_2026[6] - 1) * 100)
D["urals_2026_jump_jul"] = pct((value("ru_urals_2026_07")
                                / value("ru_urals_2026_06") - 1) * 100)
D["divergence_jul"] = r2((value("ru_urals_2026_07") - value("ru_urals_2026_06"))
                          - (BRENT_2026[7] - BRENT_2026[6]))

D["urals_sep_vs_budget"] = r1(value("ru_urals_2026_09")
                              / value("ru_budget_urals_2026") * 100 - 100)
D["urals_oct_vs_budget"] = r1(value("ru_urals_2026_10")
                              / value("ru_budget_urals_2026") * 100 - 100)
D["urals_oct_yoy"] = r1(value("ru_urals_2026_10")
                        / value("ru_urals_2025_10") * 100 - 100)

# ------------------------------------------------- 2. Вклад цены и курса
D["rub_barrel_budget"] = round(value("ru_budget_urals_2026")
                               * value("ru_budget_rate_2026"))
D["rub_barrel_jan_fact"] = round(value("ru_urals_2026_01") * 77.2)
D["rub_barrel_gap_pct"] = r1(D["rub_barrel_jan_fact"] / D["rub_barrel_budget"] * 100 - 100)

# --------------------------------------------- 3. Бюджетные показатели
D["ngd_change_2025"] = r1((value("ru_ngd_2025") / value("ru_ngd_2024") - 1) * 100)
D["ngd_2026_plan_vs_2025"] = r1(value("ru_budget_ngd_2026") - value("ru_ngd_2025"))
D["ngd_audit_gap"] = r1(value("ru_budget_ngd_2026") - value("ru_ngd_audit_2026"))
D["ngd_audit_gap_pct"] = r1(D["ngd_audit_gap"] / value("ru_budget_ngd_2026") * 100)
D["damper_per_month"] = r1(value("ru_damper_8m2026") / 8)
D["damper_vs_ngd_9m"] = r1(value("ru_damper_8m2026")
                           / value("ru_ngd_9m2026") * 100)
D["ngd_9m_run_rate"] = r1(value("ru_ngd_9m2026") / 9 * 12)
D["ngd_year_estimate_short"] = r1(value("ru_budget_ngd_2026")
                                  - D["ngd_9m_run_rate"])

# ------------------------------------------- 4. Экспортная выручка России
D["oil_export_value_2026"] = r1(value("ru_oil_export_2026")
                                * D["urals_2026_mean"] * BBL_PER_T / 1000)
D["oil_export_value_2025"] = r1(value("ru_oil_export_2025")
                                * 56.0 * BBL_PER_T / 1000)
D["oil_revenue_effect_pct"] = r1(D["oil_export_value_2026"]
                                 / D["oil_export_value_2025"] * 100 - 100)
D["ton_value_2026"] = round(D["urals_2026_mean"] * BBL_PER_T)
D["ton_value_2025"] = round(56.0 * BBL_PER_T)

# --------------------------------------------------- 5. Газ: сопоставления
D["gas_price_spread_2026"] = r1(value("ru_gazprom_price_far_abroad_2026")
                                - value("ru_gazprom_price_china_2026"))
D["gas_price_spread_2026_pct"] = r1(value("ru_gazprom_price_china_2026")
                                    / value("ru_gazprom_price_far_abroad_2026")
                                    * 100 - 100)
D["gas_price_spread_2027_pct"] = r1(value("ru_gazprom_price_china_2027")
                                    / value("ru_gazprom_price_far_abroad_2026")
                                    * 100 - 100)
# разрыв прогнозной цены для Китая с текущей ценой для Китая
D["china_2027_vs_2026_gap"] = r1(value("ru_gazprom_price_china_2027")
                                 / value("ru_gazprom_price_china_2026") * 100 - 100)
D["ps2_vs_ps1"] = r1(value("ru_ps2_capacity") / value("ru_ps1_export_2025") * 100 - 100)
D["china_gap_x"] = r1(value("ru_gazprom_price_china_2026") / value("ru_china_wants_price"))
D["china_gap_x_vs_far"] = r1(value("ru_gazprom_price_far_abroad_2026")
                             / value("ru_china_wants_price"))
D["ttf_vs_gazprom_forecast"] = r1(value("ru_ttf_oct_2026")
                                  / value("ru_gazprom_price_forecast_2026") * 100 - 100)
D["ttf_vs_2022_peak"] = r1(value("ru_ttf_oct_2026") / value("ru_ttf_2022_peak") * 100)
D["turkey_share_2025"] = r1(value("ru_turkish_stream_2025")
                            / value("ru_gas_pipe_export_2025") * 100)
D["ts_5m_growth"] = r1(value("ru_turkish_stream_5m2026")
                       / (value("ru_turkish_stream_2025") * 5 / 12) * 100 - 100)
D["eu_import_cost_2025"] = r1(value("ru_eu_value_russian_2025")
                              / value("ru_eu_share_russian_2025"))
D["lng_share_of_eu_revenue"] = r1(value("ru_lng_eu_revenue_2025")
                                  / value("ru_eu_value_russian_2025") * 100)

# ------------------------------------------------------- 6. Азербайджан
D["az_gas_price_1h2026"] = round(value("az_gas_export_1h2026_usd") * 1e9
                                 / (value("az_gas_export_1h2026") * 1e9) * 1000)
D["az_gas_price_8m2026"] = round(value("az_gas_export_8m2026_usd") * 1e9
                                 / (value("az_gas_export_8m2026") * 1e9) * 1000)
D["az_price_change_1h2026"] = r1(value("az_gas_export_1h2026_drop_usd")
                                 / (1 + value("az_gas_export_1h2026_growth_vol") / 100) * -1)
D["az_price_vs_ttf"] = r1(D["az_gas_price_1h2026"] / value("ru_ttf_oct_2026") * 100)
D["az_oil_value_2025"] = r2(value("az_oil_export_2025") * BBL_PER_T
                            * (value("az_budget_oil_2026") + 15) / 1000)
D["az_oil_value_2026"] = r2(value("az_oil_export_2025") * BBL_PER_T
                            * value("az_azeri_light_2026_11") / 1000)
D["az_oil_value_gap"] = r1(D["az_oil_value_2026"] / D["az_oil_value_2025"] * 100 - 100)
D["azeri_premium_2026_11"] = r2(value("az_azeri_light_2026_11")
                                - value("az_brent_2026_11"))
D["azeri_premium_fob"] = r2(value("az_azeri_light_fob_2026_11")
                            - value("az_brent_2026_11"))
D["azeri_premium_pct"] = r1(value("az_azeri_light_2026_11")
                            / value("az_brent_2026_11") * 100 - 100)
D["azeri_vs_budget"] = r1(value("az_azeri_light_2026_11")
                          / value("az_budget_oil_2026") * 100 - 100)
D["azeri_range_x"] = r1(value("az_azeri_light_max") / value("az_azeri_light_min"))
D["az_prod_5y_drop"] = r1((value("az_oil_prod_2025") - 34.6) / 34.6 * 100)
D["az_prod_2025_vs_5y_ago_pct"] = r1(value("az_oil_prod_2025") / 34.6 * 100)
D["az_gas_export_share_prod"] = r1(value("az_gas_export_2025")
                                   / value("az_gas_prod_2025") * 100)
D["az_sd_share_export_1h2026"] = r1(value("az_shah_deniz_export_1h2026")
                                    / value("az_gas_export_1h2026") * 100)
D["az_sofaz_transfer_9m_pct"] = r1(value("az_sofa_transfer_9m2026")
                                   / value("az_sofa_transfer_plan") * 100)
D["az_sofaz_assets_growth"] = r1(value("az_sofa_assets")
                                 / value("az_sofa_assets_2025") * 100 - 100)
D["az_nonoil_gap_vs_export"] = r1(value("az_hydrocarb_export_share_2025")
                                  - value("az_nonoil_gdp_share"))
D["az_eu_target_gap"] = r1(value("az_eu_target_2027")
                           / value("az_gas_export_eu_2025") * 100 - 100)
D["az_sefe_share_eu"] = r1(value("az_sefe_volume")
                           / value("az_gas_export_eu_2025") * 100)
D["az_georgia_price_gap"] = r1(D["az_gas_price_1h2026"]
                               / value("az_georgia_price_high") * 100 - 100)
D["az_gas_export_eur_share"] = value("az_gas_export_2025_eur_share")

# объём, который необходимо перевести с внутреннего рынка для выполнения
# ориентира меморандума с ЕС (при сохранении прочих направлений)
D["az_balance_needed"] = r1(value("az_eu_target_2027")
                            - value("az_gas_export_eu_2025"))
D["az_balance_share_demand"] = r1(
    D["az_balance_needed"]
    / (value("az_gas_prod_2025") - value("az_gas_export_2025")) * 100)
D["az_domestic"] = r1(value("az_gas_prod_2025") - value("az_gas_export_2025"))

# доля прироста европейского направления в требуемом объёме
D["az_target_multiple"] = r1(value("az_eu_target_2027")
                             / value("az_gas_export_eu_2025"))


# ------------------------------- 7. Сценарии цены Urals и НГД на 2027 г.
SCEN = {
    "Базовый": dict(brent=70.0, disc=15.0, rate=95.0),
    "Низкий": dict(brent=55.0, disc=22.0, rate=100.0),
    "Высокий": dict(brent=90.0, disc=12.0, rate=90.0),
}
for name, p in SCEN.items():
    urals = p["brent"] - p["disc"]
    p["urals"] = r1(urals)
    p["rub_barrel"] = round(urals * p["rate"])
    p["ngd_index"] = round(urals * p["rate"]
                           / (value("ru_budget_urals_2026")
                              * value("ru_budget_rate_2026")) * 100, 1)
D["scenarios"] = SCEN
D["scen_urals_spread"] = r1(max(v["urals"] for v in SCEN.values())
                            - min(v["urals"] for v in SCEN.values()))

# ------------------------- 8. Оценка «цены адаптации» (санкционная рента)


def adaptation_cost(discount, volume_mt):
    """Потеря выручки от дисконта, млрд долл."""
    return round(volume_mt * BBL_PER_T * discount / 1000, 2)


D["adapt_cost_base"] = adaptation_cost(value("ru_disc_2025"), value("ru_oil_export_2026"))
D["adapt_cost_stress"] = adaptation_cost(value("ru_disc_2026_07"),
                                         value("ru_oil_export_2026"))
D["adapt_cost_share_ngd"] = r1(D["adapt_cost_base"] * 80
                               / (value("ru_ngd_2025") * 1e3) * 100)
D["adapt_cost_share_export"] = r1(D["adapt_cost_base"]
                                  / D["oil_export_value_2026"] * 100)


def main():
    metrics = {
        "inputs": {k: v[0] for k, v in ALL.items()},
        "units": {k: v[1] for k, v in ALL.items()},
        "source": {k: v[2] for k, v in ALL.items()},
        "derived": D,
        "series": {"months": MONTHS, "urals_2026": URALS_2026},
    }
    path = os.path.join(OUT, "metrics.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)
    print(f"metrics -> {path}")
    for k in ["urals_2026_mean", "urals_2026_range", "urals_2026_cv",
              "disc_june_2026", "ngd_audit_gap_pct", "az_gas_price_1h2026",
              "gas_price_spread_2026", "oil_revenue_effect_pct",
              "adapt_cost_base", "scen_urals_spread", "az_oil_value_gap"]:
        print(f"  {k} = {D[k]}")


if __name__ == "__main__":
    main()
