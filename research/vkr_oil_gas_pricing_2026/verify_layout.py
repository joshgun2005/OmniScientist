# -*- coding: utf-8 -*-
"""Точная оценка числа страниц DOCX без LibreOffice.

Модель: последовательный обход элементов body (абзацы и таблицы), высота
каждого элемента считается по фактическим метрикам шрифта и параметрам
абзаца; переполнение переносит элемент на новую страницу, разрывы
учитываются как принудительный переход.

Ширина текста измеряется по метрикам Tinos (метрически совместим с Times
New Roman: те же пропорции знаков и кириллица), кегль 14 пт, поля
3,0/1,5/2,0/2,0 см.
"""
import math
import os
import sys

from docx import Document
from docx.shared import Emu
from docx.table import Table
from docx.text.paragraph import Paragraph
from fontTools.ttLib import TTFont

PT_CM = 0.03528
FONT_PATHS = {
    False: "/tmp/gf/ofl/tinos/Tinos-Regular.ttf",
    True: "/tmp/gf/ofl/tinos/Tinos-Bold.ttf",
}
MISSING_W = 0.5


class Metrics:
    def __init__(self):
        self.cache = {}
        for bold, path in FONT_PATHS.items():
            if os.path.exists(path):
                f = TTFont(path)
                upm = f["head"].unitsPerEm
                self.cache[bold] = (f.getBestCmap(), f["hmtx"], upm)
            else:
                self.cache[bold] = (None, None, 2048)

    def width_em(self, text, size_pt, bold=False):
        cmap, hmtx, upm = self.cache[bold]
        if cmap is None:
            return len(text) * MISSING_W
        total = 0.0
        for ch in text:
            g = cmap.get(ord(ch))
            if g is None or g not in hmtx.metrics:
                total += MISSING_W * upm
            else:
                total += hmtx[g][0]
        return total / upm


M = Metrics()


def _size(p, default=14.0):
    for r in p.runs:
        if r.font.size:
            return r.font.size.pt
    return default


def _bold(p):
    for r in p.runs:
        if r.bold is not None:
            return bool(r.bold)
    return False


def lines_for(text, width_cm, size, bold=False):
    """Число строк с учётом переносов по словам."""
    if not text:
        return 1
    limit = width_cm / PT_CM           # ширина в пт
    words = text.split(" ")
    lines, cur = 1, ""
    for w in words:
        trial = (cur + " " + w) if cur else w
        if M.width_em(trial, size, bold) * size <= limit:
            cur = trial
        else:
            if not cur:
                cur = w               # слишком длинное слово
            else:
                lines += 1
                cur = w
    return lines


def para_height(p, width_cm, exact=True):
    pf = p.paragraph_format
    size = _size(p)
    bold = _bold(p)
    spacing = pf.line_spacing if pf.line_spacing else 1.0
    if isinstance(spacing, float):
        line_h = size * 1.15 * spacing * PT_CM
    else:
        line_h = spacing.pt * PT_CM

    indent = pf.first_line_indent.cm if pf.first_line_indent else 0.0
    left = pf.left_indent.cm if pf.left_indent else 0.0
    text = p.text
    n_first = lines_for(text, width_cm - indent - left, size, bold)
    if n_first > 1 and (indent or left):
        n_rest = lines_for(text, width_cm - left, size, bold)
        # первая строка короче: оцениваем среднее
        n = max(n_first, math.ceil(n_rest * 0.92))
    else:
        n = n_first
    before = (pf.space_before.pt if pf.space_before else 0) * PT_CM
    after = (pf.space_after.pt if pf.space_after else 0) * PT_CM
    return n * line_h + before + after, size


def para_has_image(p):
    return bool(p._p.findall(
        ".//{http://schemas.openxmlformats.org/drawingml/2006/main}blip"))


def image_height(p):
    ext = p._p.findall(
        ".//{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}extent")
    if not ext:
        return 0.0
    return Emu(int(ext[0].get("cy"))).cm


def table_height(t, width_cm):
    h = 0.0
    for row in t.rows:
        lines = 1
        for cell in row.cells:
            w = cell.width.cm if cell.width else width_cm / max(1, len(row.cells))
            fs = 11.0
            for cp in cell.paragraphs:
                for r in cp.runs:
                    if r.font.size:
                        fs = r.font.size.pt
                        break
            pad = 0.2          # поля ячейки
            lines = max(lines, lines_for(cell.text, w - pad, fs))
        h += lines * 1.15 * 1.0 * PT_CM + 0.14
    return h


def walk(path, exact=True):
    doc = Document(path)
    sec = doc.sections[-1]
    width = sec.page_width.cm - sec.left_margin.cm - sec.right_margin.cm
    height = sec.page_height.cm - sec.top_margin.cm - sec.bottom_margin.cm
    pages, used = 1, 0.0
    marks = []
    for el in doc.element.body.iterchildren():
        tag = el.tag.split("}")[1]
        if tag == "p":
            p = Paragraph(el, doc)
            brs = el.findall(
                ".//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}br")
            if any(b.get(
                    "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
                    "type") == "page" for b in brs):
                pages += 1
                used = 0.0
                continue
            if para_has_image(p):
                h = image_height(p) + 0.3
            else:
                h, _ = para_height(p, width, exact)
            t = p.text.strip()
            if t and _bold(p) and len(t) < 130 and (
                    t[0].isdigit() or t.isupper()):
                marks.append((pages, t[:60]))
            if used + h > height:
                pages += 1
                used = 0.0
            used += h
        elif tag == "tbl":
            h = table_height(Table(el, doc), width)
            if used + h > height:
                pages += 1
                used = 0.0
            used += h
    return pages, marks


def page_map(path):
    """Номер страницы для каждого заголовка (по началу строки)."""
    doc = Document(path)
    sec = doc.sections[-1]
    width = sec.page_width.cm - sec.left_margin.cm - sec.right_margin.cm
    height = sec.page_height.cm - sec.top_margin.cm - sec.bottom_margin.cm
    pages, used = 1, 0.0
    out = {}
    for el in doc.element.body.iterchildren():
        tag = el.tag.split("}")[1]
        if tag == "p":
            p = Paragraph(el, doc)
            brs = el.findall(
                ".//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}br")
            if any(b.get(
                    "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
                    "type") == "page" for b in brs):
                pages += 1
                used = 0.0
                continue
            h = image_height(p) + 0.3 if para_has_image(p) else para_height(p, width)[0]
            t = p.text.strip()
            if t and _bold(p) and len(t) < 130 and (
                    t[0].isdigit() or t.isupper()):
                out[t] = pages
            if used + h > height:
                pages += 1
                used = 0.0
            used += h
        elif tag == "tbl":
            h = table_height(Table(el, doc), width)
            if used + h > height:
                pages += 1
                used = 0.0
            used += h
    # приложению — собственный заголовок без номера
    for key in list(out):
        if key.startswith("ПРИЛОЖЕНИЕ А") and "ПРИЛОЖЕНИЕ А. Исходные данные" not in out:
            out["ПРИЛОЖЕНИЕ А. Исходные данные для расчётов"] = out[key]
    return out


def main(path):
    pages, marks = walk(path)
    print(f"страниц: {pages}")
    if os.environ.get("DETAIL"):
        for pg, t in marks:
            print(f"  с. {pg:3d}  {t}")
    return pages


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        "out", "VKR_2026_Tsenoobrazovanie_neftegaz_Rossiya_Azerbaijan.docx")
    main(target)
