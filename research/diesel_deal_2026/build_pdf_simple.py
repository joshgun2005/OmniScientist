# -*- coding: utf-8 -*-
"""Рендер рукописи в PDF (A4, Times New Roman, ГОСТ-подобная вёрстка).

Читает out/blocks.json, сформированный build_docx.py, и собирает PDF через
reportlab на том же гарнитуре, что и DOCX, чтобы обе версии совпадали по
объёму и разбиению на страницы.
"""
import json
import os
import re

from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, Frame, Image, KeepTogether, PageBreak,
                                PageTemplate, Paragraph, Spacer, Table, TableStyle)
from reportlab.lib import colors
from PIL import Image as PILImage

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "out")
FONT_PATH = "/home/user/OmniScientist/desktop/public/assets/fonts/TimesNewRoman-Regular.ttf"
BOLD_PATH = "/usr/local/lib/python3.11/dist-packages/matplotlib/mpl-data/fonts/ttf/STIXGeneralBol.ttf"

pdfmetrics.registerFont(TTFont("TNR", FONT_PATH))
pdfmetrics.registerFont(TTFont("TNR-Bold", BOLD_PATH))          # STIX Bold: полная кириллица
from reportlab.pdfbase.pdfmetrics import registerFontFamily
registerFontFamily("TNR", normal="TNR", bold="TNR-Bold", italic="TNR", boldItalic="TNR-Bold")

BLOCKS = json.load(open(os.path.join(OUT, "blocks_simple.json"), encoding="utf-8"))

PAGE_W, PAGE_H = A4
LM, RM, TM, BM = 2.5 * cm, 1.5 * cm, 2.0 * cm, 2.0 * cm
FRAME_W = PAGE_W - LM - RM

S = {
    "body": ParagraphStyle("body", fontName="TNR", fontSize=14, leading=21, alignment=TA_JUSTIFY,
                           firstLineIndent=1.25 * cm, spaceAfter=0),
    "body13": ParagraphStyle("body13", fontName="TNR", fontSize=11, leading=15.5, alignment=TA_JUSTIFY,
                             firstLineIndent=1.25 * cm, spaceAfter=0),
    "title": ParagraphStyle("title", fontName="TNR", fontSize=14, leading=21, alignment=TA_CENTER),
    "h1": ParagraphStyle("h1", fontName="TNR", fontSize=14, leading=21, spaceBefore=12, spaceAfter=6,
                         alignment=TA_LEFT),
    "cap": ParagraphStyle("cap", fontName="TNR", fontSize=10.5, leading=13.5, alignment=TA_JUSTIFY,
                          spaceBefore=2, spaceAfter=8),
    "eq": ParagraphStyle("eq", fontName="TNR", fontSize=12, leading=18, alignment=TA_CENTER),
    "ref": ParagraphStyle("ref", fontName="TNR", fontSize=9.5, leading=11.3, alignment=TA_JUSTIFY,
                          leftIndent=0.75 * cm, spaceAfter=2),
    "tcell": ParagraphStyle("tcell", fontName="TNR", fontSize=9, leading=11),
    "tcellb": ParagraphStyle("tcellb", fontName="TNR-Bold", fontSize=9, leading=11),
}


def esc(t):
    t = t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return t


def runs_to_markup(runs):
    out = []
    for text, st in runs:
        t = esc(text)
        if st.get("sub"):
            t = f"<sub>{t}</sub>"
        if st.get("sup"):
            t = f"<super>{t}</super>"
        if st.get("i"):
            t = f"<i>{t}</i>"
        if st.get("b"):
            t = f"<b>{t}</b>"
        out.append(t)
    return "".join(out)


def urlize(text):
    """Длинные URL и DOI — неразрывными кусками, чтобы не рвать строку уродливо."""
    return re.sub(r"(https?://\S+)", r'<font size="8.6">\1</font>', esc(text))


story = []

# --- титульная шапка (УДК, название) уже в блоках; идём по порядку
for b in BLOCKS:
    t = b["t"]
    if t == "p":
        style = S["body"] if b["size"] >= 13 else S["body13"]
        if b["align"] == "center":
            st = ParagraphStyle("c", parent=style, alignment=TA_CENTER, firstLineIndent=0)
        elif b["align"] == "left":
            st = ParagraphStyle("l", parent=style, alignment=TA_LEFT, firstLineIndent=0)
        else:
            st = style
        story.append(Paragraph(esc(b["text"]), st))
    elif t == "runs":
        story.append(Paragraph(runs_to_markup(b["runs"]), S["body"]))
    elif t == "h":
        story.append(Paragraph(f"<b>{esc(b['text'])}</b>", S["h1"]))
    elif t == "eq":
        markup = runs_to_markup(b["runs"])
        eq_tbl = Table([[Paragraph("", S["eq"]), Paragraph(markup, S["eq"]),
                         Paragraph(f"({b['number']})", S["eq"])]],
                       colWidths=[FRAME_W * 0.16, FRAME_W * 0.68, FRAME_W * 0.16])
        eq_tbl.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                                    ("ALIGN", (1, 0), (1, 0), "CENTER"),
                                    ("ALIGN", (2, 0), (2, 0), "RIGHT"),
                                    ("TOPPADDING", (0, 0), (-1, -1), 2),
                                    ("BOTTOMPADDING", (0, 0), (-1, -1), 2)]))
        story.append(Spacer(1, 3))
        story.append(eq_tbl)
        story.append(Spacer(1, 3))
    elif t == "cap":
        st = S["cap"]
        nxt = BLOCKS[BLOCKS.index(b) + 1]["t"] if BLOCKS.index(b) + 1 < len(BLOCKS) else None
        if nxt in ("table", "img"):
            story.append(KeepTogether([Paragraph(esc(b["text"]), S["cap"])]))
            continue
        if b.get("align") == "left":
            st = ParagraphStyle("capl", parent=st, alignment=TA_LEFT)
        elif b.get("align") == "center":
            sz = b.get("size", 10)
            st = ParagraphStyle("capc", parent=st, alignment=TA_CENTER, fontSize=sz,
                                leading=sz * 1.35)
        story.append(Paragraph(esc(b["text"]), st))
    elif t == "ref":
        story.append(Paragraph(urlize(b["text"]), S["ref"]))
    elif t == "img":
        path = b["path"]
        w = b["width_cm"] * cm
        with PILImage.open(path) as im:
            iw, ih = im.size
        h = w * ih / iw
        story.append(Image(path, width=w, height=h))
    elif t == "table":
        data = [[Paragraph(esc(str(c)), S["tcellb"] if ri == 0 else S["tcell"])
                 for c in row] for ri, row in enumerate(b["rows"])]
        widths = [w * cm for w in b["widths"]]
        tbl = Table(data, colWidths=widths, repeatRows=1)
        tbl.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#666666")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (1, 0), (-1, -1), "CENTER"),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))
        story.append(Spacer(1, 4))
        story.append(tbl)
        story.append(Spacer(1, 4))

# превратить блоки списка литературы в компактный стиль
story = [s for s in story]

doc = BaseDocTemplate(os.path.join(OUT, "Dizelnaya_sdelka_2026_student_VAK.pdf"),
                      pagesize=A4, leftMargin=LM, rightMargin=RM, topMargin=TM, bottomMargin=BM,
                      title="Дизельная сделка России и США 2026 года: объёмы, выгоды и риски",
                      author="", subject="Мировая экономика")
frame = Frame(LM, BM, FRAME_W, PAGE_H - TM - BM, id="main", showBoundary=0)


def footer(canvas, doc_):
    canvas.saveState()
    canvas.setFont("TNR", 9)
    canvas.drawString(LM, BM - 0.9 * cm, "Мировая экономика")
    canvas.drawRightString(PAGE_W - RM, BM - 0.9 * cm, str(canvas.getPageNumber()))
    canvas.restoreState()


doc.addPageTemplates([PageTemplate(id="all", frames=[frame], onPage=footer)])
doc.build(story)
print("PDF:", os.path.join(OUT, "Dizelnaya_sdelka_2026_student_VAK.pdf"))
