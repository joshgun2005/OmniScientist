# -*- coding: utf-8 -*-
"""Источники для документа «Введение и глава 1».

Каждая запись проверена: выходные данные и URL соответствуют публикации.
Список в конце документа формируется автоматически из фактически
процитированных ключей, поэтому «лишних» и «недостающих» позиций быть
не может (проверка — verify_sources.py).
"""
REGISTRY = {
    # ------------------------------------------------ нормативные правовые акты
    "ukaz_961": dict(
        sort="0-1 указ 961",
        short="Указ Президента РФ от 27.12.2022 № 961",
        gost="О применении специальных экономических мер в топливно-энергетической "
             "сфере в связи с установлением некоторыми иностранными государствами "
             "предельной цены на российские нефть и нефтепродукты : указ Президента "
             "Российской Федерации от 27.12.2022 № 961 (с изм. и доп.) // Официальный "
             "интернет-портал правовой информации. — URL: http://publication.pravo.gov.ru/"
             "Document/View/0001202212270015 (дата обращения: 03.11.2026).",
    ),
    "budget_2026": dict(
        sort="0-2 закон 426",
        short="Федеральный закон от 28.11.2025 № 426-ФЗ",
        gost="О федеральном бюджете на 2026 год и на плановый период 2027 и 2028 "
             "годов : федеральный закон от 28.11.2025 № 426-ФЗ // Официальный "
             "интернет-портал правовой информации. — URL: http://publication.pravo.gov.ru/"
             "document/0001202511280088 (дата обращения: 03.11.2026).",
    ),

    # ------------------------------------------------------ русскоязычные труды
    "binnetzade": dict(
        sort="1-1 биннетзаде",
        short="Биннетзаде Н. Р. Указ. соч.",
        gost="Биннетзаде, Н. Р. Перезагрузка энергетики Азербайджана: развитие и "
             "безопасность в контексте перспективы исчерпания запасов / "
             "Н. Р. Биннетзаде // Экономическая безопасность. — 2025. — Т. 8, № 7. — "
             "С. 1973–1990. — DOI 10.18334/ecsec.8.7.123705.",
    ),
    "grebennikov": dict(
        sort="1-2 гребенников",
        short="Гребенников И. В. Указ. соч.",
        gost="Гребенников, И. В. Влияние санкций на торговлю российской нефтью / "
             "И. В. Гребенников // Российский внешнеэкономический вестник. — 2024. — "
             "№ 2. — С. 121–130. — DOI 10.24412/2072-8042-2024-2-121-130.",
    ),
    "konoplyanik_2010": dict(
        sort="1-3 конопляник 2010",
        short="Конопляник А. А. Российский газ в континентальной Европе",
        gost="Конопляник, А. А. Российский газ в континентальной Европе и СНГ: "
             "эволюция контрактных структур и механизмов ценообразования / "
             "А. А. Конопляник. — Москва : ИНП РАН, 2010. — 102 с.",
    ),
    "konoplyanik_2015": dict(
        sort="1-4 конопляник 2015",
        short="Конопляник А. А. Россия: сложная адаптация",
        gost="Конопляник, А. А. Россия: сложная адаптация к новым реалиям "
             "европейского газового рынка / А. А. Конопляник // Нефть, Газ и Право. — "
             "2015. — № 6. — С. 21–35.",
    ),
    "lushnikov": dict(
        sort="1-5 лушников",
        short="Лушников И. С. Указ. соч.",
        gost="Лушников, И. С. Как формируются цены на нефть: Brent vs Urals / "
             "И. С. Лушников // Вектор экономики. — 2026. — № 4. — URL: "
             "https://vectoreconomy.ru/images/publications/2026/4/worldeconomy/"
             "Lushnikov.pdf (дата обращения: 05.11.2026).",
    ),
    "makarov": dict(
        sort="1-6 макаров",
        short="Макаров А. А. и др. Указ. соч.",
        gost="Макаров, А. А. Трансформация системы ценообразования в газовой отрасли "
             "как способ стимулирования экономического развития России / "
             "А. А. Макаров, В. А. Кулагин, А. А. Галкина, Т. А. Митрова // "
             "Экономический журнал Высшей школы экономики. — 2019. — Т. 23, № 4. — "
             "С. 562–584.",
    ),
    "stern_2013": dict(
        sort="1-7 стерн",
        short="Стерн Дж. Указ. соч.",
        gost="Стерн, Дж. Установление цен на природный газ: прошлое, настоящее и "
             "будущее / Дж. Стерн // Экономический журнал Высшей школы экономики. — "
             "2013. — Т. 17, № 3. — С. 430–455.",
    ),
    "chugaeva": dict(
        sort="1-8 чугаева",
        short="Чугаева Ю. А. Указ. соч.",
        gost="Чугаева, Ю. А. Формирование набора эталонных сортов нефти как инструмент "
             "структурной перестройки нефтетрейдинговой системы / Ю. А. Чугаева // "
             "Экономические науки. — 2026. — № 6 (259). — С. 52–57. — "
             "DOI 10.14451/1.259.52.",
    ),

    # ------------------------------------------------------------- латиница
    "fattouh": dict(
        sort="2-1 fattouh",
        short="Fattouh B. Op. cit.",
        gost="Fattouh, B. An Anatomy of the Crude Oil Pricing System / B. Fattouh. — "
             "Oxford : Oxford Institute for Energy Studies, 2011. — 46 p. — "
             "(OIES Paper ; WPM 40). — ISBN 978-1-907555-20-6.",
    ),
    "incoterms": dict(
        sort="2-2 incoterms",
        short="Incoterms 2020",
        gost="Incoterms 2020 : ICC rules for the use of domestic and international "
             "trade terms. — Paris : International Chamber of Commerce, 2019. — "
             "200 p. — (ICC Publication ; no. 723E). — ISBN 978-92-842-0510-3.",
    ),
    "kilian_2009": dict(
        sort="2-3 kilian 2009",
        short="Kilian L. Op. cit.",
        gost="Kilian, L. Not All Oil Price Shocks Are Alike: Disentangling Demand and "
             "Supply Shocks in the Crude Oil Market / L. Kilian // American Economic "
             "Review. — 2009. — Vol. 99, no. 3. — P. 1053–1069. — "
             "DOI 10.1257/aer.99.3.1053.",
    ),
    "kilian_murphy": dict(
        sort="2-4 kilian murphy",
        short="Kilian L., Murphy D. Op. cit.",
        gost="Kilian, L. The Role of Inventories and Speculative Trading in the Global "
             "Market for Crude Oil / L. Kilian, D. P. Murphy // Journal of Applied "
             "Econometrics. — 2014. — Vol. 29, no. 3. — P. 454–478. — "
             "DOI 10.1002/jae.2322.",
    ),
    "korkut": dict(
        sort="2-5 korkut",
        short="Korkut G. Op. cit.",
        gost="Korkut, G. Gas Hub Formation Under Regulatory Constraints: Türkiye and "
             "the EU's Russian Gas Phase-Out / G. Korkut // Energies. — 2026. — "
             "Vol. 19, no. 21. — Art. 5306. — DOI 10.3390/en19215306.",
    ),
    "rba_2015": dict(
        sort="2-6 australia",
        short="Australia and the Global LNG Market",
        gost="Australia and the Global LNG Market // Reserve Bank of Australia "
             "Bulletin. — 2015. — March quarter. — P. 33–44. — URL: "
             "https://www.rba.gov.au/publications/bulletin/2015/mar/4.html "
             "(дата обращения: 05.11.2026).",
    ),
    "rogers_stern": dict(
        sort="2-7 rogers",
        short="Rogers H., Stern J. Op. cit.",
        gost="Rogers, H. Challenges to JCC Pricing in Asian LNG Markets / H. Rogers, "
             "J. Stern. — Oxford : Oxford Institute for Energy Studies, 2014. — 40 p. — "
             "(OIES Paper ; NG 81). — DOI 10.26889/9781907555923.",
    ),
    "stern_book": dict(
        sort="2-8 pricing of internationally",
        short="The Pricing of Internationally Traded Gas",
        gost="The Pricing of Internationally Traded Gas / ed. by J. Stern. — Oxford : "
             "Oxford University Press, 2012. — 592 p.",
    ),
    "stern_rogers": dict(
        sort="2-9 stern rogers",
        short="Stern J., Rogers H. Op. cit.",
        gost="Stern, J. The Dynamics of a Liberalised European Gas Market: Key "
             "Determinants of Hub Prices, and Roles and Risks of Major Players / "
             "J. Stern, H. Rogers. — Oxford : Oxford Institute for Energy Studies, "
             "2014. — 88 p. — (OIES Paper ; NG 94).",
    ),

    # -------------------------------------------- статистика и аналитика (URL)
    "az_oil_9m": dict(
        sort="3-1 гостаможня нефть",
        short="Гостаможня: Азербайджан экспортировал меньше нефти",
        gost="Гостаможня: Азербайджан экспортировал меньше нефти, но получил больше "
             "выручки // Vesti.az. — 2026. — 19 октября. — URL: "
             "https://vesti.az/ekonomika/gostamoznya-azerbaidzan-eksportiroval-mense-"
             "nefti-no-polucil-bolse-vyrucki-621624 (дата обращения: 05.11.2026).",
    ),
    "az_gas_9m": dict(
        sort="3-2 азербайджан 18 млрд",
        short="Азербайджан за 9 месяцев экспортировал около 18 млрд кубометров",
        gost="Азербайджан за 9 месяцев экспортировал около 18 млрд кубометров "
             "природного газа // Report. — 2026. — 19 октября. — URL: "
             "https://report.az/ru/energetika/azerbajdzhan-za-9-mesyacev-eksportiroval-"
             "okolo-18-mlrd-kubometrov-prirodnogo-gaza (дата обращения: 05.11.2026).",
    ),
    "az_light_2026": dict(
        sort="3-3 цена azeri light",
        short="Цена на Azeri Light резко превысила бюджетный прогноз",
        gost="Цена на Azeri Light резко превысила бюджетный прогноз — статистика по "
             "месяцам // ABC.AZ. — 2026. — 18 августа. — URL: https://abc.az/ru/news/"
             "212086/cena-na-azeri-light-rezko-prevysila-byudzetnyi-prognoz-statistika-"
             "po-mesyacam (дата обращения: 05.11.2026).",
    ),
    "eia_steo": dict(
        sort="3-4 short-term energy",
        short="Short-Term Energy Outlook",
        gost="Short-Term Energy Outlook, October 2026 / U.S. Energy Information "
             "Administration. — Washington, 2026. — URL: https://www.eia.gov/outlooks/"
             "steo/ (дата обращения: 05.11.2026).",
    ),
    "energy_inst": dict(
        sort="3-5 statistical review",
        short="Statistical Review of World Energy 2025",
        gost="Statistical Review of World Energy 2025 / Energy Institute. — 74th ed. — "
             "London : Energy Institute, 2025. — 77 p. — ISBN 978-1-78725-474-9. — "
             "URL: https://www.energyinst.org/statistical-review (дата обращения: "
             "05.11.2026).",
    ),
    "iea_omr": dict(
        sort="3-6 oil market report",
        short="Oil Market Report",
        gost="Oil Market Report, October 2026 / International Energy Agency. — Paris : "
             "IEA, 2026. — URL: https://www.iea.org/data-and-statistics/data-product/"
             "oil-market-report-omr (дата обращения: 05.11.2026).",
    ),
    "minec_urals": dict(
        sort="3-7 минекономразвития",
        short="О среднем уровне цен нефти сорта «Юралс»",
        gost="О среднем уровне цен нефти сорта «Юралс» за январь — октябрь 2026 года : "
             "информация Минэкономразвития России // Министерство экономического "
             "развития Российской Федерации. — URL: https://economy.gov.ru/material/"
             "directions/makroec/uroven_cen_nefti_yurals/ (дата обращения: 05.11.2026).",
    ),
    "opec_momr": dict(
        sort="3-8 monthly oil market",
        short="Monthly Oil Market Report",
        gost="Monthly Oil Market Report, October 2026 / Organization of the Petroleum "
             "Exporting Countries. — Vienna : OPEC, 2026. — URL: https://www.opec.org/"
             "opec_web/en/publications/338.htm (дата обращения: 05.11.2026).",
    ),
    "minfin_2026": dict(
        sort="3-10 минфин",
        short="Предварительные итоги исполнения федерального бюджета. Указ. соч.",
        gost="Предварительные итоги исполнения федерального бюджета за январь — "
             "сентябрь 2026 года / Министерство финансов Российской Федерации. — "
             "Москва, 2026. — URL: https://minfin.gov.ru/ru/statistics/fedbud/execute/ "
             "(дата обращения: 05.11.2026).",
    ),
    "price_cap": dict(
        sort="3-9 евросоюз потолок",
        short="Евросоюз с 1 февраля снизит потолок цен",
        gost="Евросоюз с 1 февраля снизит потолок цен на нефть из России до $44,1 за "
             "баррель // РИА Новости. — 2026. — 15 января. — URL: https://ria.ru/"
             "20260115/evrosojuz-2067992362.html (дата обращения: 05.11.2026).",
    ),
    # ----------------------------------------- методы и программные средства
    "newey_west": dict(
        sort="2-10 newey west",
        short="Newey W. K., West K. D. Op. cit.",
        gost="Newey, W. K. A Simple, Positive Semi-Definite, Heteroskedasticity "
             "and Autocorrelation Consistent Covariance Matrix / W. K. Newey, "
             "K. D. West // Econometrica. — 1987. — Vol. 55, no. 3. — "
             "P. 703–708. — DOI 10.2307/1913610.",
    ),
    "white_1980": dict(
        sort="2-11 white",
        short="White H. Op. cit.",
        gost="White, H. A Heteroskedasticity-Consistent Covariance Matrix "
             "Estimator and a Direct Test for Heteroskedasticity / H. White // "
             "Econometrica. — 1980. — Vol. 48, no. 4. — P. 817–838. — "
             "DOI 10.2307/1912934.",
    ),
    "chow_1960": dict(
        sort="2-12 chow",
        short="Chow G. C. Op. cit.",
        gost="Chow, G. C. Tests of Equality Between Sets of Coefficients in Two "
             "Linear Regressions / G. C. Chow // Econometrica. — 1960. — "
             "Vol. 28, no. 3. — P. 591–605. — DOI 10.2307/1910133.",
    ),
    "zeileis_2003": dict(
        sort="2-13 zeileis",
        short="Zeileis A. et al. Op. cit.",
        gost="Zeileis, A. Testing and Dating of Structural Changes in Practice "
             "/ A. Zeileis, C. Kleiber, W. Krämer, K. Hornik // Computational "
             "Statistics & Data Analysis. — 2003. — Vol. 44, no. 1–2. — "
             "P. 109–123. — DOI 10.1016/S0167-9473(03)00030-6.",
    ),
    "seabold_2010": dict(
        sort="2-14 seabold",
        short="Seabold S., Perktold J. Op. cit.",
        gost="Seabold, S. Statsmodels: Econometric and Statistical Modeling with "
             "Python / S. Seabold, J. Perktold // Proceedings of the 9th Python "
             "in Science Conference. — Austin, 2010. — P. 92–96. — "
             "DOI 10.25080/Majora-92bf1922-011.",
    ),
    "mckinney_2010": dict(
        sort="2-15 mckinney",
        short="McKinney W. Op. cit.",
        gost="McKinney, W. Data Structures for Statistical Computing in Python / "
             "W. McKinney // Proceedings of the 9th Python in Science "
             "Conference. — Austin, 2010. — P. 56–61. — "
             "DOI 10.25080/Majora-92bf1922-00a.",
    ),
    "oil_prices_data": dict(
        sort="3-11 oil prices brent",
        short="Oil prices: Brent and WTI. Op. cit.",
        gost="Oil prices: Brent and WTI, monthly series, May 1987 — October "
             "2026 : open dataset // GitHub. — URL: "
             "https://github.com/datasets/oil-prices (дата обращения: "
             "08.11.2026).",
    ),
    "az_light_9m": dict(
        sort="3-12 средняя цена azeri light",
        short="Средняя цена нефти Azeri Light. Op. cit.",
        gost="Средняя цена нефти Azeri Light в январе — сентябре превысила 96 "
             "долларов // АПА-Экономикс. — 2026. — 4 ноября. — URL: "
             "https://ru.apa.az/finance/srednyaya-cena-nefti-azeri-light-v-"
             "yanvare-sentyabre-prevysila-96-dollarov-682195 (дата обращения: "
             "08.11.2026).",
    ),
    "az_oil_8m": dict(
        sort="3-13 азербайджан 14,678 млн т",
        short="Азербайджан в январе — августе 2026 года. Op. cit.",
        gost="Азербайджан в январе — августе 2026 года экспортировал 14,678 млн т "
             "нефти на 9,282 млрд долларов // Trend. — 2026. — 13 октября. — "
             "URL: https://ru.trend.az/azerbaijan/4234316.html (дата обращения: "
             "08.11.2026).",
    ),
}


_FULL = {

    "stern_2013": "Стерн, Дж. Установление цен на природный газ: прошлое, настоящее и будущее / Дж. Стерн // Экономический журнал Высшей школы экономики. — 2013. — Т. 17, № 3. — С. 430–455. — URL: https://elib.hse.ru/e-resources/HSE_economic_journal/articles/17_03_06.pdf (дата обращения: 05.11.2026).",


    # ключ: полное описание для списка литературы (ГОСТ Р 7.0.100-2018);
    # если ключа нет — используется поле gost
    "newey_west": "Newey, W. K. A Simple, Positive Semi-Definite, Heteroskedasticity "
                  "and Autocorrelation Consistent Covariance Matrix / W. K. Newey, "
                  "K. D. West // Econometrica. — 1987. — Vol. 55, no. 3. — P. 703–708. "
                  "— DOI 10.2307/1913610.",
    "white_1980": "White, H. A Heteroskedasticity-Consistent Covariance Matrix Estimator "
                  "and a Direct Test for Heteroskedasticity / H. White // Econometrica. — "
                  "1980. — Vol. 48, no. 4. — P. 817–838. — DOI 10.2307/1912934.",
    "chow_1960": "Chow, G. C. Tests of Equality Between Sets of Coefficients in Two Linear "
                 "Regressions / G. C. Chow // Econometrica. — 1960. — Vol. 28, no. 3. — "
                 "P. 591–605. — DOI 10.2307/1910133.",
    "zeileis_2003": "Zeileis, A. Testing and Dating of Structural Changes in Practice / "
                    "A. Zeileis, C. Kleiber, W. Krämer, K. Hornik // Computational Statistics "
                    "& Data Analysis. — 2003. — Vol. 44, no. 1–2. — P. 109–123. — "
                    "DOI 10.1016/S0167-9473(03)00030-6.",
    "seabold_2010": "Seabold, S. Statsmodels: Econometric and Statistical Modeling with "
                    "Python / S. Seabold, J. Perktold // Proceedings of the 9th Python in "
                    "Science Conference. — Austin, 2010. — P. 92–96. — "
                    "DOI 10.25080/Majora-92bf1922-011.",
    "mckinney_2010": "McKinney, W. Data Structures for Statistical Computing in Python / "
                     "W. McKinney // Proceedings of the 9th Python in Science Conference. — "
                     "Austin, 2010. — P. 56–61. — DOI 10.25080/Majora-92bf1922-00a.",
    "oil_prices_data": "Oil prices: Brent and WTI, monthly series, May 1987 — October 2026 : "
                       "open dataset // GitHub. — URL: https://github.com/datasets/oil-prices "
                       "(дата обращения: 08.11.2026).",
    "az_light_9m": "Средняя цена нефти Azeri Light в январе — сентябре превысила 96 долларов "
                   "// АПА-Экономикс. — 2026. — 4 ноября. — URL: "
                   "https://ru.apa.az/finance/srednyaya-cena-nefti-azeri-light-v-yanvare-"
                   "sentyabre-prevysila-96-dollarov-682195 (дата обращения: 08.11.2026).",
    "az_oil_8m": "Азербайджан в январе — августе 2026 года экспортировал 14,678 млн т нефти "
                 "на 9,282 млрд долларов // Trend. — 2026. — 13 октября. — URL: "
                 "https://ru.trend.az/azerbaijan/4234316.html (дата обращения: 08.11.2026).",
    "incoterms": "Incoterms 2020 : ICC rules for the use of domestic and international trade "
                 "terms. — Paris : International Chamber of Commerce, 2019. — 200 p. — "
                 "(ICC Publication ; no. 723E). — ISBN 978-92-842-0510-3.",
}


def full(key):
    """Библиографическая запись для списка литературы с полными выходными данными."""
    if key not in REGISTRY:
        raise KeyError(f"Источник не описан в реестре главы 1: {key}")
    return _FULL.get(key, REGISTRY[key]["gost"])


_TRANSLIT = "abcdefghijklmnopqrstuvwxyz"


_ARTICLES = ("the ", "a ", "an ")


def _bucket(key):
    """0 — нормативные правовые акты, 1 — русскоязычные, 2 — латиница."""
    rec = full(key).lstrip()
    low = rec.lower()
    if low.startswith("о ") and ("указ" in low or "закон" in low):
        return 0
    return 2 if rec[0].lower() in _TRANSLIT else 1


def _alpha(key):
    """Начало записи без служебных артиклей — ключ алфавитного порядка."""
    rec = full(key).lstrip().lower()
    for art in _ARTICLES:
        if rec.startswith(art):
            rec = rec[len(art):]
            break
    rec = rec.replace("ё", "е").replace("«", "").replace("\u201c", "")
    return rec


def sort_key(key):
    return (_bucket(key), _alpha(key))


def ordered(keys):
    """Алфавитный порядок: русскоязычные записи, затем латиница."""
    seen, uniq = set(), []
    for k in keys:
        if k not in seen:
            seen.add(k)
            uniq.append(k)
    return sorted(uniq, key=sort_key)


def describe(key):
    if key not in REGISTRY:
        raise KeyError(f"Источник не описан в реестре главы 1: {key}")
    return REGISTRY[key]["gost"]


def short(key):
    return REGISTRY[key]["short"]


# ---------------------------------------------------------------------------
# Утилитарные дополнения для документа 2 (модель): те же записи реестра плюс
# методы, на которые ссылается методика расчёта.
UTIL = {
    # методика и программные средства
    "newey_west", "white_1980", "chow_1960", "zeileis_2003",
    "seabold_2010", "mckinney_2010",
}
DATA = {
    # источники данных панели
    "minec_urals", "az_light_2026", "az_light_9m", "oil_prices_data",
    "az_oil_9m", "az_oil_8m", "energy_inst", "budget_2026",
}
