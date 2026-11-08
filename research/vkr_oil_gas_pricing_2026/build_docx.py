# -*- coding: utf-8 -*-
"""Сборка ВКР в DOCX.

Порядок запуска:
    python3 analysis.py        -> out/metrics.json
    python3 build_figures.py   -> figures/*.png
    python3 build_docx.py      -> out/VKR_*docx + out/blocks.json
"""
import json
import os

import fmt
from docx_engine import VKR
from sources import SOURCES, ORDER, check_alphabet
import text_ch1
import text_ch2
import text_ch3
import text_front
import verify_layout

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "out")
OUTDIR_NAME = ("VKR_2026_Tsenoobrazovanie_neftegaz_Rossiya_Azerbaijan")

M = json.load(open(os.path.join(OUT, "metrics.json"), encoding="utf-8"))
D, V = M["derived"], M["inputs"]


class Citer:
    """Подстановка [@@key] -> [n] по списку литературы."""

    def __init__(self):
        self.seen = []
        self.missing = []

    def __call__(self, text):
        import re

        def repl(m):
            parts = []
            for chunk in m.group(1).split(";"):
                key = chunk.strip().lstrip("@").strip()
                if key not in ORDER:
                    self.missing.append(key)
                    return "[??]"
                if key not in self.seen:
                    self.seen.append(key)
                parts.append(ORDER[key])
            return "[" + "; ".join(str(p) for p in parts) + "]"

        return re.sub(r"\[@@([^\]]+)\]", repl, text)


class Fmt:
    """Прокси к VKR с автоматической подстановкой ссылок в текст."""

    def __init__(self, vkr, citer):
        self._v = vkr
        self._c = citer

    def __getattr__(self, name):
        attr = getattr(self._v, name)
        if name in ("para", "h", "table", "figure", "rich"):
            def wrapped(*args, **kwargs):
                if name == "figure":
                    if len(args) > 2:
                        args = (args[0], self._c(args[1])) + args[2:]
                    if "note" in kwargs and kwargs["note"]:
                        kwargs["note"] = self._c(kwargs["note"])
                elif name == "table":
                    if "caption" in kwargs and kwargs["caption"]:
                        kwargs["caption"] = self._c(kwargs["caption"])
                    if "note" in kwargs and kwargs["note"]:
                        kwargs["note"] = self._c(kwargs["note"])
                elif name == "rich":
                    args = ([(self._c(t), st) for t, st in args[0]],) + args[1:]
                else:
                    if args and isinstance(args[0], str):
                        args = (self._c(args[0]),) + args[1:]
                    if "text" in kwargs and kwargs["text"]:
                        kwargs["text"] = self._c(kwargs["text"])
                return attr(*args, **kwargs)
            return wrapped
        return attr


def main():
    check_alphabet()
    citer = Citer()

    vkr = VKR()
    vkr.no_numbering()
    f = Fmt(vkr, citer)

    # ---------------------------------------------------------- титульный лист
    text_front.title_page(f)

    # ---------------------------------------------------------- основная часть
    vkr.start_body()
    vkr.toc_anchor()

    # введение
    vkr.page_break()
    text_front.introduction(D, V, f)
    vkr.page_break()
    text_ch1.build(D, V, f)
    vkr.page_break()
    text_ch2.build(D, V, f)
    vkr.page_break()
    text_ch3.build(D, V, f)
    vkr.page_break()
    text_front.conclusion(D, V, f)
    vkr.page_break()
    vkr.ref_mode = True
    text_front.bibliography(D, f, SOURCES)
    vkr.ref_mode = False
    text_front.appendix(D, V, f)

    # оглавление — вставляется к якорю
    vkr.toc([(lvl, txt, None) for lvl, txt in vkr.headings])

    name = f"{OUTDIR_NAME}.docx"
    path = vkr.save(os.path.join(OUT, name))

    # номера страниц для оглавления: два прохода — сначала оцениваем вёрстку,
    # затем подставляем номера в строки содержания и сохраняем повторно
    pages_map = verify_layout.page_map(path)
    vkr.fill_toc_pages(pages_map)
    path = vkr.save(os.path.join(OUT, name))

    # ---------------------------------------------------------- отчётность
    # ---------------------------------------------------------- контроль вёрстки
    est = estimate_pages(path, count_chars(vkr.body))

    with open(os.path.join(OUT, "blocks.json"), "w", encoding="utf-8") as fh:
        json.dump({
            "citations_seen": citer.seen,
            "citations_missing": citer.missing,
            "body_blocks": vkr.body,
            "reference_blocks": vkr.refs,
            "headings": vkr.headings,
        }, fh, ensure_ascii=False, indent=1)

    if citer.missing:
        raise SystemExit(f"Не найдены источники: {sorted(set(citer.missing))}")

    unused = [s["key"] for s in SOURCES if s["key"] not in citer.seen]
    chars = sum(len(t) for t in vkr.body)
    print(f"файл: {path}")
    print(f"знаков в тексте (с пробелами): {chars}")
    print(f"источников в списке: {len(SOURCES)}, процитировано: {len(citer.seen)}")
    if unused:
        print(f"ВНИМАНИЕ, не процитированы: {unused}")
    return path


# ---------------------------------------------------------------- объём
def count_chars(blocks):
    return sum(len(t) for t in blocks)


def estimate_pages(path, chars):
    """Оценка числа страниц по геометрии листа и объёму текста.

    Нет LibreOffice/pandoc, поэтому вёрстка не пересчитывается: считаем
    полезную площадь страницы (лист А4 минус поля), число строк при
    полуторном интервале с кеглем 14 пт и среднее заполнение строки,
    затем добавляем страницы под рисунки, таблицы и структурные разрывы.
    """
    from docx import Document
    from docx.shared import Cm

    doc = Document(path)
    sec = doc.sections[-1]
    w = sec.page_width.cm - sec.left_margin.cm - sec.right_margin.cm
    h = sec.page_height.cm - sec.top_margin.cm - sec.bottom_margin.cm

    pt_cm = 0.03528                     # 1 пт = 0,03528 см
    line_h = 14 * 1.5 * pt_cm           # полуторный интервал, кегль 14 пт
    lines_per_page = int(h / line_h)
    chars_per_line = int(w / (14 * pt_cm * 0.5))    # ~0,5 кегля на знак

    body_pages = chars / (lines_per_page * chars_per_line)

    n_fig = len(doc.inline_shapes)
    # рисунок: 15 см шириной при пропорции ~0,55 = 8,3 см + подпись
    fig_h = 8.4 + 1.2
    n_tab = len(doc.tables)
    tbl_h = 0.0
    for t in doc.tables:
        tbl_h += (len(t.rows) * 0.85 + 1.0)
    breaks = 7
    extra = (n_fig * fig_h + tbl_h) / h + breaks
    total = body_pages + extra

    print(f"оценка объёма: {chars} знаков, {lines_per_page} строк/стр., "
          f"~{chars_per_line} знаков/стр.")
    print(f"  текст ~{body_pages:.1f} стр. + рисунки/таблицы/разрывы "
          f"~{extra:.1f} стр. = ~{total:.0f} стр.")
    return total


if __name__ == "__main__":
    main()
