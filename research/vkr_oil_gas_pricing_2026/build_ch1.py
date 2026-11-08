# -*- coding: utf-8 -*-
"""Сборка документа 1: титул, содержание, введение, глава 1, список источников.

Лимит объёма — 20 страниц главы 1. Требования оформления: Times New Roman 14,
интервал 1,5, абзацный отступ 1,25 см, подстрочные сноски, заголовки главы по
центру заглавными, параграфов — с отступа. Нумерация страниц: титул и
содержание без номера, далее сквозная нумерация, где страница с ВВЕДЕНИЕМ —
третья (как в типовых методических рекомендациях).

Номера страниц в содержании рассчитываются по той же вёрстке, что и при
выводе: сначала собирается черновик, из него берётся карта страниц, затем
номера подставляются и документ сохраняется повторно.
"""
import json
import os

import fmt
import sources_ch1 as S
import text_mr_ch1 as T
import verify_layout
from mr_engine import MRDoc

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "out")
NAME = "VKR_2026_Glava_1_Teoriya.docx"
LIMIT = 20

with open(os.path.join(OUT, "metrics.json"), encoding="utf-8") as fh:
    M = json.load(fh)
D, V = M["derived"], M["inputs"]


def title_page(doc):
    f = doc
    f.para("МИНИСТЕРСТВО НАУКИ И ВЫСШЕГО ОБРАЗОВАНИЯ "
           "РОССИЙСКОЙ ФЕДЕРАЦИИ", size=12, bold=True, align="center",
           indent=0, after=0, spacing=1.0)
    f.para("Федеральное государственное образовательное бюджетное "
           "учреждение высшего образования", size=12, align="center",
           indent=0, after=0, spacing=1.0)
    f.para("«ФИНАНСОВЫЙ УНИВЕРСИТЕТ ПРИ ПРАВИТЕЛЬСТВЕ "
           "РОССИЙСКОЙ ФЕДЕРАЦИИ»", size=12, bold=True, align="center",
           indent=0, after=0, spacing=1.0)
    f.para("(Финансовый университет)", size=12, align="center", indent=0,
           after=0, spacing=1.0)
    f.para("", size=10, indent=0, after=0, spacing=1.0)
    f.para("[Наименование факультета / института]", size=12, align="center",
           indent=0, after=0, spacing=1.0)
    f.para("[Наименование кафедры]", size=12, align="center", indent=0,
           after=0, spacing=1.0)
    for _ in range(4):
        f.para("", size=12, indent=0, after=0, spacing=1.0)
    f.para("ВЫПУСКНАЯ КВАЛИФИКАЦИОННАЯ РАБОТА", size=14, bold=True,
           align="center", indent=0, after=6, spacing=1.0)
    f.para("на тему:", size=14, align="center", indent=0, after=6,
           spacing=1.0)
    f.para("«ОСОБЕННОСТИ И ПЕРСПЕКТИВЫ ИЗМЕНЕНИЯ ЦЕНООБРАЗОВАНИЯ "
           "НА НЕФТЕГАЗОВЫХ РЫНКАХ (НА ПРИМЕРЕ РОССИИ И АЗЕРБАЙДЖАНА)»",
           size=14, bold=True, align="center", indent=0, after=6, spacing=1.0)
    f.para("Теоретическая часть (введение и глава 1)", size=12, bold=False,
           align="center", indent=0, after=0, spacing=1.0)
    for _ in range(4):
        f.para("", size=12, indent=0, after=0, spacing=1.0)
    f.para("Направление подготовки 38.03.01 «Экономика»", size=12,
           align="right", indent=0, after=0, spacing=1.0)
    f.para("Образовательная программа: [наименование программы]", size=12,
           align="right", indent=0, after=0, spacing=1.0)
    for _ in range(3):
        f.para("", size=12, indent=0, after=0, spacing=1.0)
    f.para("Выполнил(а): обучающийся(аяся) [курс, группа]",
           size=12, align="right", indent=0, after=0, spacing=1.0)
    f.para("_____________________ / [И. О. Фамилия] /", size=12,
           align="right", indent=0, after=0, spacing=1.0)
    f.para("Научный руководитель: [учёная степень, звание]", size=12,
           align="right", indent=0, after=0, spacing=1.0)
    f.para("_____________________ / [И. О. Фамилия] /", size=12,
           align="right", indent=0, after=0, spacing=1.0)
    for _ in range(3):
        f.para("", size=12, indent=0, after=0, spacing=1.0)
    f.para("Москва — 2026", size=12, align="center", indent=0, after=0,
           spacing=1.0)


def bibliography(doc, keys):
    """Список источников по ГОСТ Р 7.0.100-2018 — только процитированные."""
    doc.h("СПИСОК ИСПОЛЬЗОВАННЫХ ИСТОЧНИКОВ", 1)
    ordered = S.ordered(keys)
    doc.para("Источники приведены в алфавитном порядке: сначала нормативные "
             "правовые акты, затем русскоязычные издания, затем издания на "
             f"английском языке. Всего {len(ordered)} наименований; "
             "библиографические описания выполнены по ГОСТ Р 7.0.100-2018.",
             indent=0, after=10)
    for i, k in enumerate(ordered, 1):
        doc.para(f"{i}. {S.full(k)}", indent=1.25, after=4, spacing=1.0,
                 size=12)
    return ordered


def compose(keys):
    """Собирает документ; возвращает объект MRDoc (без сохранения)."""
    doc = MRDoc()
    doc.cited = set()
    doc.cited_log = []
    doc.no_numbering()

    title_page(doc)
    doc.start_body()            # секция 2: содержание, без номера
    doc.no_numbering()
    doc.toc_anchor()
    doc.start_body()            # секция 3: основной текст, номер 3 на старте
    doc._numbering(doc.doc.sections[-1], enable=True, start=3)

    T.introduction(D, V, doc)
    doc.page_break()
    T.chapter1(D, V, doc)
    body_for_check = list(doc.body)

    doc.page_break()
    bibliography(doc, keys)
    doc.toc([(lvl, txt, None) for lvl, txt in doc.headings])
    return doc, body_for_check


def chapter_pages():
    """Объём главы 1 отдельно — без введения и списка источников."""
    chap = MRDoc()
    chap.no_numbering()
    T.chapter1(D, V, chap)
    path = chap.save(os.path.join(OUT, "_tmp_chap.docx"))
    pages, marks = verify_layout.walk(path)
    os.remove(path)
    return pages, marks


def main():
    doc = MRDoc()
    doc.cited = set()
    doc.cited_log = []

    # первый проход: черновик без номеров страниц в содержании
    doc, body = compose(set())
    path = doc.save(os.path.join(OUT, "_tmp_pass1.docx"))

    # карта страниц и повторная сборка с номерами
    keys = S.ordered(sorted(doc.cited))
    pages_map = verify_layout.page_map(path)
    os.remove(path)

    doc, body = compose(keys)
    doc.fill_toc_pages(pages_map)

    body_chars = sum(len(t) for t in body)
    with open(os.path.join(OUT, "blocks_ch1.json"), "w", encoding="utf-8") as fh:
        json.dump({"body_blocks": body, "headings": doc.headings,
                   "cited": keys, "footnotes": doc._footnotes},
                  fh, ensure_ascii=False, indent=1)

    path = doc.save(os.path.join(OUT, NAME))
    pages, marks = verify_layout.walk(path)
    pages_chap, _ = chapter_pages()

    print(f"файл: {path}")
    print(f"страниц всего: {pages}")
    print(f"знаков основного текста: {body_chars}")
    print(f"страниц в главе 1: {pages_chap}")
    print(f"сносок: {doc.footnote_count}")
    print(f"источников процитировано: {len(keys)}")
    print("разбивка по страницам:")
    for pg, t in marks:
        print(f"  с. {pg:3d}  {t[:70]}")
    if pages_chap > LIMIT:
        print(f"ВНИМАНИЕ: глава 1 занимает {pages_chap} с. при лимите {LIMIT} с.")
    else:
        print(f"глава 1 укладывается в лимит: {pages_chap} с. из {LIMIT}")
    return path


if __name__ == "__main__":
    main()
