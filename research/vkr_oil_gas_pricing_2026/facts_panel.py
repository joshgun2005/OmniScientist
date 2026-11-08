# -*- coding: utf-8 -*-
"""Фактические (не расчётные) значения, нужные модели и её денежному блоку.

Каждое значение снабжено ключом источника из sources_ch1.py, поэтому
verify_docs.py может проверить, что цифра в тексте имеет источник.
Все величины — в единицах, указанных в комментарии.
"""
from facts import ALL as _ALL  # словарь фактических значений главы 1

# источник -> значение; попадает в out/metrics.json (inputs)
FACTS = {
    # -------------------------------- экспорт нефти, млн т (таможенная статистика / ЦБ РФ)
    "ru_export_2013": 236.6,
    "ru_export_2014": 223.4,
    "ru_export_2015": 244.5,
    "ru_export_2016": 254.9,
    "ru_export_2017": 252.6,
    "ru_export_2018": 260.6,
    "ru_export_2019": 267.5,
    "ru_export_2020": 238.6,
    "ru_export_2021": 230.0,
    "ru_export_2022": 242.0,
    "ru_export_2023": 240.8,
    "ru_export_2024": 240.0,
    "ru_export_2025": 238.0,
    "az_export_2018": 32.70,
    "az_export_2019": 31.60,
    "az_export_2020": 29.02,
    "az_export_2021": 28.10,
    "az_export_2022": 26.05,
    "az_export_2023": 26.05,
    "az_export_2024": 23.60,
    "az_export_2025": 23.40,
    # -------------------------------- годовые цены, долл./барр.
    "urals_2013": 107.88, "urals_2014": 97.60, "urals_2015": 51.23,
    "urals_2016": 41.90, "urals_2017": 53.03, "urals_2018": 70.01,
    "urals_2019": 63.59, "urals_2020": 41.73, "urals_2021": 69.00,
    "urals_2022": 76.09, "urals_2023": 62.99, "urals_2024": 68.00,
    "urals_2025": 55.60,
    "az_light_2018": 73.30, "az_light_2019": 66.79, "az_light_2020": 43.70,
    "az_light_2021": 71.60, "az_light_2022": 103.58, "az_light_2023": 85.05,
    "az_light_2024": 82.87, "az_light_2025": 71.00,
    # -------------------------------- бюджетные ориентиры Азербайджана, долл./барр.
    "az_budget_2018": 45.0, "az_budget_2019": 60.0, "az_budget_2020": 55.0,
    "az_budget_2021": 45.0, "az_budget_2022": 50.0, "az_budget_2023": 60.0,
    "az_budget_2024": 60.0, "az_budget_2025": 70.0, "az_budget_2026": 65.0,
    # -------------------------------- потолок цен (контрактное условие ЕС/G7)
    "cap_2023": 60.0, "cap_2024": 60.0, "cap_2025": 47.6, "cap_2026": 44.1,
    # -------------------------------- бюджет РФ
    "ngd_2024_trln": 11.131,     # нефтегазовые доходы 2024 г., трлн руб.
    "ngd_2025_trln": 8.477,      # нефтегазовые доходы 2025 г., трлн руб.
    "duties_2013_trln": 2.2,     # экспортная пошлина на нефть и нефтепродукты, 2013 г.
    # -------------------------------- контракты
    "cnpc_volume_mt": 365.0,     # потолок поставок Роснефть — CNPC, млн т
    "cnpc_value_bn": 270.0,      # стоимость контракта, млрд долл.
    "cnpc_prepay_bn": 35.0,      # фактическая предоплата к 2015 г., млрд долл.
    "cnpc_annual_mt": 15.0,      # контракт 2009 г.: млн т в год до 2030 г.
    "cnpc_peak_mt": 31.0,        # пик поставок по контракту, млн т в год
    "acg_profit_share": 0.75,    # доля прибыльной нефти Азербайджана в АЧГ
    "acg_socar_2017": 25.0,      # доля SOCAR в АЧГ после 2017 г., %
    "acg_socar_2026": 35.3,      # доля SOCAR в АЧГ, % (после 2024 г.)
    "acg_bonus_bn": 3.6,         # бонус ГНФАР по amended & restated 2017 г., млрд долл.
    "acg_horizon": 2050,         # год окончания контракта АЧГ
    "acg_share_prod": 66.0,      # доля АЧГ в добыче нефти Азербайджана, %
}

# ключ факта -> ключ источника (для verify_docs и для сносок в тексте)
SOURCE_OF = {
    "ru_export_2013": "ru_export_series", "ru_export_2014": "ru_export_series",
    "ru_export_2015": "ru_export_series", "ru_export_2016": "ru_export_series",
    "ru_export_2017": "ru_export_series", "ru_export_2018": "ru_export_series",
    "ru_export_2019": "ru_export_series", "ru_export_2020": "ru_export_series",
    "ru_export_2021": "ru_export_series", "ru_export_2022": "ru_export_series",
    "ru_export_2023": "ru_export_series", "ru_export_2024": "ru_export_2025_novak",
    "ru_export_2025": "ru_export_2025_novak",
    "az_export_2018": "az_export_series", "az_export_2019": "az_export_series",
    "az_export_2020": "az_export_series", "az_export_2021": "az_export_series",
    "az_export_2022": "az_export_series", "az_export_2023": "az_export_series",
    "az_export_2024": "az_export_series", "az_export_2025": "az_export_series",
    "urals_2013": "urals_annual", "urals_2014": "urals_annual",
    "urals_2015": "urals_annual", "urals_2016": "urals_annual",
    "urals_2017": "urals_annual", "urals_2018": "urals_annual",
    "urals_2019": "urals_annual", "urals_2020": "urals_annual",
    "urals_2021": "urals_annual", "urals_2022": "urals_annual",
    "urals_2023": "urals_annual", "urals_2024": "urals_annual",
    "urals_2025": "urals_2025_result",
    "az_light_2018": "az_light_annual", "az_light_2019": "az_light_annual",
    "az_light_2020": "az_light_annual", "az_light_2021": "az_light_annual",
    "az_light_2022": "az_light_annual", "az_light_2023": "az_light_2023",
    "az_light_2024": "az_light_2024", "az_light_2025": "az_light_2025",
    "az_budget_2018": "az_budget_series", "az_budget_2019": "az_budget_series",
    "az_budget_2020": "az_budget_series", "az_budget_2021": "az_budget_series",
    "az_budget_2022": "az_budget_series", "az_budget_2023": "az_budget_series",
    "az_budget_2024": "az_budget_series", "az_budget_2025": "az_budget_series",
    "az_budget_2026": "az_budget_series",
    "cap_2023": "price_cap", "cap_2024": "price_cap",
    "cap_2025": "price_cap", "cap_2026": "price_cap",
    "ngd_2024_trln": "minfin_ngd_2025", "ngd_2025_trln": "minfin_ngd_2025",
    "cnpc_volume_mt": "rosneft_cnpc", "cnpc_value_bn": "rosneft_cnpc",
    "cnpc_prepay_bn": "rosneft_cnpc", "cnpc_annual_mt": "rosneft_cnpc",
    "cnpc_peak_mt": "rosneft_cnpc",
    "acg_profit_share": "acg_contract", "acg_socar_2017": "acg_contract",
    "acg_socar_2026": "acg_contract", "acg_bonus_bn": "acg_contract",
    "acg_horizon": "acg_contract", "acg_share_prod": "acg_contract",
}
