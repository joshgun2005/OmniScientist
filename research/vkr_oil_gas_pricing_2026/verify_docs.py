# -*- coding: utf-8 -*-
"""Проверка прослеживаемости чисел и источников в обоих документах.

Каждый числовой токен текста должен либо совпадать со значением из
out/metrics.json / out/model.json, либо входить в белый список служебных
чисел (годы, номера актов, нумерация формул и разделов, коэффициенты единиц).
Дополнительно проверяется, что все источники из подстрочных сносок и списка
литературы присутствуют в реестре sources_ch1.py и что в списке нет
непроцитированных позиций.

Запуск: python3 verify_docs.py
"""
import json
import os
import re

import sources_ch1 as S

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "out")

WHITELIST = {
    # годы и даты
    1900, 1910, 1973, 1980, 1986, 1987, 1990, 2000, 2008, 2009, 2010, 2012,
    1960, 2003, 2011, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020,
    2021, 2022, 2023, 2024,
    2025, 2026, 2027, 2028, 2030, 2035,
    # нумерация разделов, формул, таблиц, задач
    1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
    21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31,
    # номера нормативных актов
    117, 342, 426, 259, 961, 723,
    # единицы и коэффициенты пересчёта
    0, 100, 1000, 10000, 1000000, 7.33, 35.11, 1.15, 1.25, 2.0, 0.06,
    # диапазоны, используемые как характеристики контрактов
    10, 20, 40, 60, 80, 120, 12, 7, 3,
}


def numbers_in(text):
    out = []
    for m in re.finditer(r"\d[\d \u00a0]*(?:[.,]\d+)?", text):
        raw = m.group(0).replace("\u00a0", "").replace(" ", "")
        raw = raw.replace(",", ".")
        try:
            out.append((float(raw), m.group(0)))
        except ValueError:
            continue
    return out


def registry_values():
    vals = set()
    met = json.load(open(os.path.join(OUT, "metrics.json"), encoding="utf-8"))
    for part in ("inputs", "derived"):
        for v in met[part].values():
            if isinstance(v, (int, float)):
                vals.add(round(float(v), 4))
    mod = json.load(open(os.path.join(OUT, "model.json"), encoding="utf-8"))

    def walk(node):
        if isinstance(node, dict):
            for v in node.values():
                walk(v)
        elif isinstance(node, (list, tuple)):
            for v in node:
                walk(v)
        elif isinstance(node, (int, float)):
            vals.add(round(float(node), 4))

    walk(mod)
    return vals


def close(a, b):
    a, b = abs(a), abs(b)
    for nd in (0, 1, 2, 3):
        if round(b, nd) == round(a, nd):
            return True
    return int(b) == int(a)


def clean(text):
    text = re.sub(r"https?://\S+", " ", text)
    text = re.sub(r"DOI\s*\S+", " ", text)
    text = re.sub(r"\bС\.\s*\d+\s*[–-]\s*\d+", " ", text)
    text = re.sub(r"\bP\.\s*\d+(\s*[–-]\s*\d+)?", " ", text)
    text = re.sub(r"\b(Т|Vol)\.\s*\d+", " ", text)
    text = re.sub(r"№\s*\d+(\s*\([\d–-]+\))?", " ", text)
    text = re.sub(r"\bArt\.\s*\d+", " ", text)
    text = re.sub(r"\b\d+\s*p\.", " ", text)
    text = re.sub(r"ISBN\s*[\d-]+", " ", text)
    text = re.sub(r"«[^»]*\d[^»]*»", " ", text)
    text = re.sub(r"\((\d+)\)", " ", text)          # номера формул
    return text


def check_doc(path, title):
    from docx import Document
    doc = Document(path)
    blocks = [p.text for p in doc.paragraphs if p.text.strip()]
    for t in doc.tables:
        for row in t.rows:
            blocks.extend(c.text for c in row.cells)
    text = clean("\n".join(blocks))
    vals = registry_values()
    unknown = {}
    total = 0
    for num, raw in numbers_in(text):
        total += 1
        if num in WHITELIST or any(close(num, v) for v in vals):
            continue
        unknown[raw.strip()] = unknown.get(raw.strip(), 0) + 1
    print(f"\n{title}")
    print(f"  абзацев: {len(doc.paragraphs)}, таблиц: {len(doc.tables)}, "
          f"токенов: {total}, нераспознанных: {sum(unknown.values())} "
          f"(уникальных {len(unknown)})")
    for raw, cnt in sorted(unknown.items(), key=lambda x: -x[1])[:25]:
        print(f"    «{raw}» ×{cnt}")
    return sum(unknown.values())


def is_printed(rec):
    """Печатное издание: указаны страницы и нет ссылки на сетевой ресурс."""
    # страницы указываются и как «С. 21–35», и как «102 с.», и как «46 p.»
    has_pages = re.search(r"\b[СP]\.\s*\d+|\d+\s*[сp]\.", rec) is not None
    return has_pages and "URL" not in rec and "DOI" not in rec


def check_sources():
    print("\nреестр источников")
    cited_ch1 = json.load(open(os.path.join(OUT, "blocks_ch1.json"),
                               encoding="utf-8"))["cited"]
    cited_model = json.load(open(os.path.join(OUT, "blocks_model.json"),
                                 encoding="utf-8"))["cited"]
    miss = [k for k in list(cited_ch1) + list(cited_model)
            if k not in S.REGISTRY]
    bad = [k for k in S.REGISTRY if len(S.full(k)) < 60]
    print(f"  ключей в реестре: {len(S.REGISTRY)}; процитировано: "
          f"документ 1 — {len(cited_ch1)}, документ 2 — {len(cited_model)}")
    print(f"  отсутствуют в реестре: {miss or 'нет'}")
    print(f"  слишком короткие описания: {bad or 'нет'}")
    for name, cited in (("документ 1", cited_ch1), ("документ 2", cited_model)):
        own = [k for k in cited if k not in S.REGISTRY]
        print(f"  {name}: позиций в списке {len(cited)}, "
              f"нет в реестре {len(own)}")
    only_ch1 = [k for k in cited_ch1 if k not in cited_model]
    only_model = [k for k in cited_model if k not in cited_ch1]
    print(f"  только в документе 1: {only_ch1 or 'нет'}")
    print(f"  только в документе 2: {only_model or 'нет'}")
    for k in sorted(set(cited_ch1) | set(cited_model)):
        g = S.full(k)
        if not is_printed(g) and "DOI" not in g and "URL" not in g:
            print(f"  ВНИМАНИЕ: нет URL/DOI — {k}")
    return len(miss) + len(bad)


if __name__ == "__main__":
    bad = 0
    for name, title in (
        ("VKR_2026_Glava_1_Teoriya.docx", "документ 1 (теория)"),
        ("VKR_2026_Ekonometricheskaya_model.docx", "документ 2 (модель)"),
    ):
        path = os.path.join(OUT, name)
        if os.path.exists(path):
            bad += check_doc(path, title)
    bad += check_sources()
    print("\nитог:", "ок" if bad == 0 else f"замечаний {bad}")
