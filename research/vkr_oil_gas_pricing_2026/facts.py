# -*- coding: utf-8 -*-
"""Реестр заимствованных (не расчётных) числовых фактов.

Каждый факт — тройка: значение, единица измерения, ключ источника из sources.py.
Все числа, попадающие в текст рукописи, должны либо вычисляться в analysis.py,
либо присутствовать здесь. Проверка — verify_numbers.py.
"""

# ------------------------------------------------------------------ Россия: нефть
RUSSIA = {
    # среднемесячная цена Urals для целей налогообложения, долл./барр. (Минэкономразвития)
    "ru_urals_2025_01": (67.66, "долл./барр.", "minec_urals"),
    "ru_urals_2025_05": (52.08, "долл./барр.", "minec_urals"),
    "ru_urals_2025_07": (60.37, "долл./барр.", "minec_urals"),
    "ru_urals_2025_09": (56.82, "долл./барр.", "minec_urals"),
    "ru_urals_2025_10": (53.68, "долл./барр.", "minec_urals"),
    "ru_urals_2025_11": (44.87, "долл./барр.", "minec_urals"),
    "ru_urals_2025_12": (39.18, "долл./барр.", "minec_urals"),
    "ru_urals_2026_01": (40.95, "долл./барр.", "minec_urals"),
    "ru_urals_2026_02": (44.59, "долл./барр.", "minec_urals"),
    "ru_urals_2026_03": (77.00, "долл./барр.", "minec_urals"),
    "ru_urals_2026_04": (94.87, "долл./барр.", "minec_urals"),
    "ru_urals_2026_05": (86.52, "долл./барр.", "minec_urals"),
    "ru_urals_2026_06": (63.52, "долл./барр.", "minec_urals"),
    "ru_urals_2026_07": (59.02, "долл./барр.", "minec_urals"),
    "ru_urals_2026_08": (67.11, "долл./барр.", "minec_urals"),
    "ru_urals_2026_09": (92.08, "долл./барр.", "minec_urals"),
    "ru_urals_2026_10": (101.46, "долл./барр.", "minec_urals"),

    # бюджетные параметры
    "ru_budget_urals_2026": (59.0, "долл./барр.", "budget_2026"),
    "ru_budget_rate_2026": (92.2, "руб./долл.", "budget_2026"),
    "ru_budget_ngd_2026": (8.919, "трлн руб.", "budget_2026"),

    # добыча и экспорт
    "ru_oil_prod_2025": (511.4, "млн т", "minec_macro"),
    "ru_oil_prod_2024": (516.0, "млн т", "minec_macro"),
    "ru_oil_export_2025": (230.8, "млн т", "minec_macro"),
    "ru_oil_export_2026": (244.7, "млн т", "minec_macro"),
    "ru_asia_share_2025": (80, "%", "novak_2026"),
    "ru_asia_share_2021": (40, "%", "novak_2026"),
    "ru_sea_export_sep_2026": (3.76, "млн барр./сут.", "opec_momr"),

    # нефтегазовые доходы бюджета
    "ru_ngd_2023": (8.822, "трлн руб.", "minfin_ngd_year"),
    "ru_ngd_2024": (11.131, "трлн руб.", "minfin_ngd_year"),
    "ru_ngd_2025": (8.5, "трлн руб.", "minfin_ngd_year"),
    "ru_ngd_1h2026": (3.661, "трлн руб.", "minfin_2026"),
    "ru_ngd_9m2026": (5.471, "трлн руб.", "minfin_2026"),
    "ru_ngd_8m2026": (5.019, "трлн руб.", "minfin_2026"),
    "ru_ngd_9m2026_drop": (17.2, "%", "minfin_2026"),
    "ru_ngd_1h2026_drop": (22.7, "%", "minfin_2026"),
    "ru_ngd_share_2026": (19, "%", "minfin_ngd_year"),
    "ru_ngd_audit_2026": (7.3, "трлн руб.", "audit_2026"),
    "ru_deficit_9m2026_gdp": (2.2, "% ВВП", "minfin_2026"),
    "ru_damper_8m2026": (916, "млрд руб.", "minfin_2026"),

    # налоговый режим
    "ru_export_duty_zero_year": (2024, "год", "tax_maneuver"),
    "ru_duty_zero_since": (2025, "год", "tax_maneuver"),

    # дисконты
    "ru_disc_2024": (14.2, "долл./барр.", "minec_discount"),
    "ru_disc_2025": (13.4, "долл./барр.", "minec_discount"),
    "ru_disc_2025_11": (18.9, "долл./барр.", "disc_peak_2025"),
    "ru_disc_2025_12_share": (36, "%", "cbr_longrun"),
    "ru_disc_2026_07": (27.35, "долл./барр.", "argus_2026"),
    "ru_disc_2026_04": (23.94, "долл./барр.", "argus_2026"),
    "ru_disc_hist_low": (3.0, "%", "cbr_longrun"),
    "ru_disc_hist_high": (1.5, "%", "cbr_longrun"),

    # газ
    "ru_gas_pipe_export_2025": (114, "млрд куб. м", "tss_2025"),
    "ru_gas_lng_export_2025": (44, "млрд куб. м", "tss_2025"),
    "ru_turkish_stream_2025": (18.06, "млрд куб. м", "gazprom_turkey"),
    "ru_turkish_stream_5m2026": (7.65, "млрд куб. м", "turkish_stream"),
    "ru_turkish_stream_capacity": (31.5, "млрд куб. м", "turkish_stream"),
    "ru_gazprom_price_far_abroad_2026": (420.2, "долл./тыс. куб. м", "gazprom_prices"),
    "ru_gazprom_price_china_2026": (258.8, "долл./тыс. куб. м", "gazprom_prices"),
    "ru_gazprom_price_china_2027": (223.9, "долл./тыс. куб. м", "gazprom_prices"),
    "ru_gazprom_price_forecast_2026": (313.3, "долл./тыс. куб. м", "gazprom_prices"),
    "ru_china_wants_price": (50, "долл./тыс. куб. м", "sila_sibiri2"),
    "ru_ps2_capacity": (50, "млрд куб. м", "sila_sibiri2"),
    "ru_ps1_export_2025": (38.8, "млрд куб. м", "ps1"),
    "ru_ps1_capacity_new": (44, "млрд куб. м", "ps1"),
    "ru_eu_share_russian_2025": (13, "%", "eu_ban"),
    "ru_eu_value_russian_2025": (15, "млрд евро", "eu_ban"),
    "ru_lng_eu_revenue_2025": (7.2, "млрд евро", "eu_ban"),
    "ru_ttf_oct_2026": (1120, "долл./тыс. куб. м", "ttf_2026"),
    "ru_ttf_2022_peak": (1200, "долл./тыс. куб. м", "ttf_2026"),
    "ru_eu_hub_indexed_share": (82, "%", "ttf_2026"),
    "ru_eu_oil_indexed_share": (18, "%", "ttf_2026"),

    # санкционный контур
    "ru_price_cap_new": (44.1, "долл./барр.", "price_cap"),
    "ru_price_cap_old": (47.6, "долл./барр.", "price_cap"),
    "ru_price_cap_initial": (60, "долл./барр.", "price_cap"),

    # рынок
    "ru_brent_2026_june": (72.95, "долл./барр.", "brent_monthly"),
    "ru_brent_2026_july": (83.93, "долл./барр.", "brent_monthly"),
    "ru_brent_2026_q4": (70, "долл./барр.", "eia_steo"),
    "ru_eia_brent_2026": (81.91, "долл./барр.", "eia_steo"),
    "ru_eia_brent_2027": (64.8, "долл./барр.", "eia_steo"),
    "ru_reuters_poll_2026": (89.05, "долл./барр.", "reuters_poll"),
    "ru_opec_plus_unwind": (2.9, "млн барр./сут.", "reuters_poll"),
    "ru_world_demand_2024": (103.8, "млн барр./сут.", "sechin"),
    "ru_hormuz_normal": (20, "млн барр./сут.", "hormuz"),
    "ru_hormuz_oct_2026": (8.5, "млн барр./сут.", "hormuz"),
    "ru_russia_prod_share": (11.6, "%", "sechin"),
    "ru_russia_export_share": (11.3, "%", "sechin"),
    "ru_china_import_share": (25.7, "%", "sechin"),
    "ru_eu_russia_oil_2021": (30, "%", "sechin"),
    "ru_eu_russia_oil_2024": (6, "%", "sechin"),
    "ru_cbr_urals_longrun_low": (54, "долл./барр.", "cbr_longrun"),
    "ru_cbr_urals_longrun_high": (72, "долл./барр.", "cbr_longrun"),
}


# ------------------------------------------------------- Азербайджан
AZERBAIJAN = {
    "az_oil_prod_2025": (27.68, "млн т", "az_stat"),
    "az_oil_prod_2024": (29.0, "млн т", "az_stat"),
    "az_oil_prod_2026_plan": (27.6, "млн т", "az_stat"),
    "az_oil_prod_7m2026": (15.5, "млн т", "az_stat"),
    "az_oil_prod_7m2026_drop": (3.1, "%", "az_stat"),
    "az_gas_prod_2025": (50.92, "млрд куб. м", "az_stat"),
    "az_gas_prod_2026_plan": (48.44, "млрд куб. м", "az_stat"),
    "az_gas_sale_2025": (38.88, "млрд куб. м", "az_stat"),
    "az_gas_prod_7m2026": (29.565, "млрд куб. м", "az_stat"),
    "az_oil_export_2025": (23.38, "млн т", "az_stat"),
    "az_oil_products_export_2025": (0.74, "млн т", "az_stat"),
    "az_gas_export_2025": (25.2, "млрд куб. м", "az_gas_export"),
    "az_gas_export_eu_2025": (12.8, "млрд куб. м", "az_gas_export"),
    "az_gas_export_1h2026": (12.43, "млрд куб. м", "az_customs"),
    "az_gas_export_1h2026_usd": (4.11, "млрд долл.", "az_customs"),
    "az_gas_export_1h2026_drop_usd": (9.6, "%", "az_customs"),
    "az_gas_export_1h2026_growth_vol": (0.5, "%", "az_customs"),
    "az_gas_export_8m2026": (16.378, "млрд куб. м", "az_customs"),
    "az_gas_export_8m2026_usd": (5.711, "млрд долл.", "az_customs"),
    "az_gas_export_turkey_8m2026": (6.46, "млрд куб. м", "az_customs"),
    "az_gas_export_turkey_share": (39.5, "%", "az_customs"),
    "az_gas_export_italy_8m2026": (5.6, "млрд куб. м", "az_customs"),
    "az_gas_export_italy_share": (34.2, "%", "az_customs"),
    "az_gas_export_share_total_8m2026": (26.18, "%", "az_customs"),
    "az_shah_deniz_export_2025": (23.14, "млрд куб. м", "az_gas_export"),
    "az_shah_deniz_export_1h2026": (11.44, "млрд куб. м", "az_gas_export"),
    "az_shah_deniz_reserves": (1.2, "трлн куб. м", "az_gas_export"),
    "az_export_countries": (16, "стран", "az_gas_export"),
    "az_export_countries_eu": (13, "стран", "az_gas_export"),
    "az_budget_oil_2026": (65, "долл./барр.", "az_budget"),
    "az_azeri_light_2026_11": (107.46, "долл./барр.", "azeri_light"),
    "az_azeri_light_fob_2026_11": (102.40, "долл./барр.", "azeri_light"),
    "az_brent_2026_11": (96.48, "долл./барр.", "azeri_light"),
    "az_azeri_light_max": (149.66, "долл./барр.", "azeri_light"),
    "az_azeri_light_min": (15.81, "долл./барр.", "azeri_light"),
    "az_acg_socar_share": (35.3, "%", "azeri_light"),
    "az_sofa_assets": (74.0, "млрд долл.", "sofaz"),
    "az_sofa_assets_2025": (73.5, "млрд долл.", "sofaz"),
    "az_sofa_transfer_plan": (12.75, "млрд манат", "az_budget"),
    "az_sofa_transfer_share": (33.2, "%", "az_budget"),
    "az_sofa_transfer_9m2026": (9.628, "млрд манат", "sofaz"),
    "az_sofa_transfer_total": (180.0, "млрд манат", "sofaz"),
    "az_hydrocarb_export_share_2025": (85.51, "%", "az_trade"),
    "az_hydrocarb_export_2025": (21.4, "млрд долл.", "az_trade"),
    "az_nonoil_export_2025": (3.63, "млрд долл.", "az_trade"),
    "az_export_total_2025": (25.0, "млрд долл.", "az_trade"),
    "az_nonoil_gdp_share": (72, "%", "az_gdp"),
    "az_gdp_2025": (129.1, "млрд манат", "az_gdp"),
    "az_gdp_2025_usd": (76, "млрд долл.", "az_gdp"),
    "az_gdp_growth_8m2026": (1.2, "%", "aliev_2026"),
    "az_gasification": (96, "%", "aliev_2026"),
    "az_sefe_volume": (1.5, "млрд куб. м", "sefe"),
    "az_eu_target_2027": (20, "млрд куб. м", "eu_mou"),
    "az_georgia_price_low": (70, "долл./тыс. куб. м", "georgia_gas"),
    "az_georgia_price_high": (75, "долл./тыс. куб. м", "georgia_gas"),
    "az_gas_export_2025_eur_share": (50, "%", "az_gas_export"),
}

ALL = {**RUSSIA, **AZERBAIJAN}

assert len(ALL) == len(RUSSIA) + len(AZERBAIJAN), "коллизия ключей реестра"


def value(key):
    return ALL[key][0]


def src(key):
    return ALL[key][2]
