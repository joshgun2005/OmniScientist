# -*- coding: utf-8 -*-
"""Отдельный документ: титул, содержание, введение, глава 1.

Оформление — по методическим рекомендациям Финансового университета
(сноски, заголовки глав по центру заглавными, 15 пт вокруг заголовков).
Главы 2 и 3 в этот файл не входят.
"""
import json
import os

import fmt
import text_mr_ch1 as T
from mr_engine import MRDoc

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "out")
NAME = "VKR_2026_Vvedenie_i_glava_1_MR.docx"

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
    for _ in range(5):
        f.para("", size=12, indent=0, after=0, spacing=1.0)
    f.para("ВЫПУСКНАЯ КВАЛИФИКАЦИОННАЯ РАБОТА", size=14, bold=True,
           align="center", indent=0, after=6, spacing=1.0)
    f.para("на тему:", size=14, align="center", indent=0, after=6,
           spacing=1.0)
    f.para("«ОСОБЕННОСТИ И ПЕРСПЕКТИВЫ ИЗМЕНЕНИЯ ЦЕНООБРАЗОВАНИЯ "
           "НА НЕФТЕГАЗОВЫХ РЫНКАХ (НА ПРИМЕРЕ РОССИИ И АЗЕРБАЙДЖАНА)»",
           size=14, bold=True, align="center", indent=0, after=0, spacing=1.0)
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


def main():
    doc = MRDoc()
    doc.no_numbering()

    title_page(doc)
    doc.start_body()
    doc.toc_anchor()

    doc.page_break()
    T.introduction(D, V, doc, doc.add_footnote)
    doc.page_break()
    T.sources_section(
        doc, "Список источников, использованных во введении",
        T.SOURCES_INTRO,
        intro="Введение опирается на следующие источники, приведённые в "
              "порядке первого упоминания. Библиографические описания "
              "выполнены по ГОСТ Р 7.0.100-2018 и полностью дублируются в "
              "общем списке использованной литературы.")
    doc.page_break()
    T.chapter1(D, V, doc, doc.add_footnote)
    doc.page_break()
    T.sources_section(
        doc, "Список источников, использованных в главе 1",
        T.SOURCES_CH1,
        intro="Глава 1 опирается на следующие источники, сгруппированные по "
              "проблематике: контрактные структуры и формулы индексации, "
              "ценообразование на трубопроводный газ, методология цен СПГ, "
              "институциональные аспекты нефтяного рынка.")

    doc.toc([(lvl, txt, None) for lvl, txt in doc.headings])

    path = doc.save(os.path.join(OUT, NAME))

    chars = sum(len(t) for t in doc.body)
    print(f"файл: {path}")
    print(f"знаков в тексте: {chars}")
    print(f"сносок: {doc.footnote_count}")
    print(f"заголовков в содержании: {len(doc.headings)}")
    return path


if __name__ == "__main__":
    main()
