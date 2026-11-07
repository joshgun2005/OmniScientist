# -*- coding: utf-8 -*-
"""Реестр источников статьи.

Один элемент — одна запись в списке литературы. Поле `cited` хранит
фрагмент текста, где источник используется, чтобы можно было проверить
соответствие ссылок и утверждений (сквозная проверка в build_docx.py).
"""

SOURCES = [
    # ---------------------------------------------------------- нормативные
    dict(key="ofac2026", kind="norm",
         ref="OFAC. General License No. 135: Authorizing Certain Transactions Related to Russian-Origin "
             "Diesel Fuel. U.S. Department of the Treasury, Office of Foreign Assets Control, 9 October 2026.",
         short="Генеральная лицензия OFAC № 135"),
    dict(key="pl117109", kind="norm",
         ref="Ending Importation of Russian Oil Act. Public Law 117-109, 136 Stat. 1154 (8 April 2022); "
             "22 U.S.C. § 8923.",
         short="Ending Importation of Russian Oil Act"),
    dict(key="eo14066", kind="norm",
         ref="Executive Order 14066 of March 8, 2022: Prohibiting Certain Imports and New Investments "
             "With Respect to Continued Russian Federation Aggression. Federal Register, 2022, vol. 87, no. 50.",
         short="Указ № 14066"),
    dict(key="kremlin2026", kind="norm",
         ref="Кремль. Заявление Президента Российской Федерации по итогам телефонного разговора "
             "с Президентом США. 9 октября 2026 г. URL: http://www.kremlin.ru (дата обращения: 06.11.2026).",
         short="заявление Кремля от 09.10.2026"),
    dict(key="trump2026", kind="norm",
         ref="Truth Social. Запись Д. Трампа об итогах переговоров с В. Путиным. 9 октября 2026 г.",
         short="запись Д. Трампа от 09.10.2026"),

    # ---------------------------------------------------------- статистика
    dict(key="eia_stocks", kind="stat",
         ref="U.S. Energy Information Administration. Weekly Petroleum Status Report. Washington, D.C.: EIA, "
             "2026. URL: https://www.eia.gov/petroleum/supply/weekly/ (accessed: 06.11.2026).",
         short="EIA, Weekly Petroleum Status Report"),
    dict(key="eia_sto", kind="stat",
         ref="U.S. Energy Information Administration. Short-Term Energy Outlook. September 2026. "
             "Washington, D.C.: EIA, 2026. URL: https://www.eia.gov/outlooks/steo/ (accessed: 06.11.2026).",
         short="EIA, Short-Term Energy Outlook"),
    dict(key="iea2026", kind="stat",
         ref="International Energy Agency. Oil Market Report. Paris: IEA, September 2026.",
         short="МЭА, Oil Market Report"),
    dict(key="minfin2026", kind="stat",
         ref="Министерство финансов Российской Федерации. Краткая информация об исполнении федерального "
             "бюджета за январь–октябрь 2026 г. М.: Минфин России, 2026. "
             "URL: https://minfin.gov.ru (дата обращения: 06.11.2026).",
         short="Минфин России, отчётность об исполнении бюджета"),
    dict(key="cbr2026", kind="stat",
         ref="Банк России. Официальные курсы валют на 6 ноября 2026 г. М.: Банк России, 2026. "
             "URL: https://www.cbr.ru/currency_base/ (дата обращения: 06.11.2026).",
         short="Банк России, официальные курсы"),
    dict(key="kpler2026", kind="stat",
         ref="Kpler. Seaborne Diesel and Gasoil Trade Flows, 2025–2026. Rotterdam: Kpler, 2026. "
             "(цит. по публикациям Reuters и ИРТТЭК от 12–23 октября 2026 г.).",
         short="данные Kpler"),
    dict(key="jodi2026", kind="stat",
         ref="Joint Organizations Data Initiative (JODI-Oil). World Database. Riyadh: IEF, 2026. "
             "URL: https://www.jodidata.org (accessed: 06.11.2026).",
         short="JODI-Oil"),

    # ---------------------------------------------------------- научная литература
    dict(key="gurvich2010", kind="sci",
         ref="Гурвич Е. Т. Нефтегазовая рента в российской экономике // Вопросы экономики. 2010. № 11. С. 4–24.",
         short="Е. Т. Гурвич"),
    dict(key="cherniavsky2025", kind="sci",
         ref="Чернявский А. В., Чепель А. А. Межотраслевой анализ влияния торговых санкций на российскую "
             "экономику // Вопросы экономики. 2025. № 3. С. 29–47. DOI: 10.32609/0042-8736-2025-3-29-47.",
         short="А. В. Чернявский, А. А. Чепель"),
    dict(key="hausmann2024", kind="sci",
         ref="Hausmann R., Schetter U., Yildirim M. A. On the Design of Effective Sanctions: The Case of Bans "
             "on Exports to Russia // Economic Policy. 2024. Vol. 39, no. 117. P. 109–153. "
             "DOI: 10.1093/epolic/eiad043.",
         short="R. Hausmann et al."),
    dict(key="fouad2024", kind="sci",
         ref="Fouad K. The Russian Oil Ban: Reassessment of the Effectiveness of Sanctions // European Journal "
             "on Criminal Policy and Research. 2024. Vol. 30. P. 261–276. DOI: 10.1007/s10610-024-09583-z.",
         short="K. Fouad"),
    dict(key="timofeev2020", kind="sci",
         ref="Тимофеев И. Н. «Санкции за нарушение санкций»: принудительные меры Министерства финансов США "
             "против компаний финансового сектора // Полис. Политические исследования. 2020. № 6. С. 73–90. "
             "DOI: 10.17976/jpps/2020.06.06.",
         short="И. Н. Тимофеев"),
    dict(key="timofeev2023", kind="sci",
         ref="Тимофеев И. Н. Политика санкций в законопроектах Конгресса США // Международные процессы. "
             "2023. Т. 21, № 2. DOI: 10.17994/IT.2023.21.2.73.1.",
         short="И. Н. Тимофеев (2023)"),
    dict(key="kilmetov2025", kind="sci",
         ref="Кильметов А. Р., Анисимов А. Ю. Оценка экономической устойчивости предприятий нефтегазовой "
             "отрасли в условиях санкций // Экономика, предпринимательство и право. 2025. Т. 15, № 1. "
             "С. 483–498. DOI: 10.18334/epp.15.1.122520.",
         short="А. Р. Кильметов, А. Ю. Анисимов"),
    dict(key="andrade2025", kind="sci",
         ref="Andrade G. B., Krykhtine F., Cosenza C. A. N., Silva V. C. Russian Oil Trade in the Face of "
             "Economic Sanctions // Вестник Российского университета дружбы народов. Серия: Экономика. "
             "2025. Т. 33, № 1. С. 26–39. DOI: 10.22363/2313-2329-2025-33-1-26-39.",
         short="G. B. Andrade et al."),
    dict(key="braginsky2024", kind="sci",
         ref="Брагинский О. Б. Развитие нефтегазохимической отрасли России в условиях ужесточения "
             "экономических санкций // Экономическая наука современной России. 2024. № 3 (106). С. 51–65.",
         short="О. Б. Брагинский"),

    # ---------------------------------------------------------- экспертно-аналитические публикации
    dict(key="carnegie2026", kind="expert",
         ref="Вакуленко С. Что получит Россия от дизельной сделки с США и зачем она Трампу // Carnegie "
             "Politika. 14.10.2026.",
         short="С. Вакуленко (Carnegie Politika)"),
    dict(key="irttek2026", kind="expert",
         ref="Кулагин В. Россия открывает экспорт дизеля: первые 500 тыс. тонн — около 15 % обычного "
             "месяца // Институт развития технологий ТЭК. 12.10.2026.",
         short="ИРТТЭК"),
    dict(key="reuters_kpler2026", kind="expert",
         ref="First Tanker with Russian Diesel Heads to the U.S. // Reuters. 2026. 22 October.",
         short="Reuters (22.10.2026)"),
    dict(key="ft2026", kind="expert",
         ref="Russian Diesel Tankers Change Course as Deal Frays // Financial Times. 2026. 4 November.",
         short="Financial Times (04.11.2026)"),
    dict(key="rg2026", kind="expert",
         ref="Симонов К. В., Тюня Д. Почему США не могут остановить дизельный кризис и какие риски есть "
             "для России // Российская газета. 26.10.2026.",
         short="К. В. Симонов, Д. Тюня"),
    dict(key="wsj2026", kind="expert",
         ref="U.S. Diesel Prices Keep Climbing Despite Russian Deal // The Wall Street Journal. 2026. 28 October.",
         short="The Wall Street Journal (28.10.2026)"),
    dict(key="dw2026", kind="expert",
         ref="Дизельная сделка между Россией и США и частичное снятие санкций с РФ // Deutsche Welle. "
             "12.10.2026.",
         short="Deutsche Welle (12.10.2026)"),
    dict(key="lenta2026", kind="expert",
         ref="«Трампу достанется»: дизельная сделка России и США оказалась под угрозой срыва // Lenta.ru. "
             "28.10.2026.",
         short="Lenta.ru (28.10.2026)"),
    dict(key="energypolicy2026", kind="expert",
         ref="Россия в августе сократила экспорт нефти до 6,44 млн б/с, доходы выросли до 13,87 млрд долл. // "
             "Энергетическая политика. 11.09.2026.",
         short="«Энергетическая политика» (11.09.2026)"),
]
