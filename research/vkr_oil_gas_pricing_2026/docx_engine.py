# -*- coding: utf-8 -*-
"""Тонкая обёртка над python-docx с оформлением по ГОСТ 7.32-2017.

Параметры страницы: А4, поля 30/15/20/20 мм (левое/правое/верхнее/нижнее),
Times New Roman 14 пт, полуторный интервал, абзацный отступ 1,25 см,
выравнивание по ширине, нумерация страниц внизу по центру (на титуле нет).
"""
import os

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import (WD_ALIGN_PARAGRAPH, WD_BREAK, WD_TAB_ALIGNMENT,
                            WD_TAB_LEADER)
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

FONT = "Times New Roman"
INK = (0x1a, 0x1a, 0x1a)

ALIGN = {
    "just": WD_ALIGN_PARAGRAPH.JUSTIFY,
    "center": WD_ALIGN_PARAGRAPH.CENTER,
    "left": WD_ALIGN_PARAGRAPH.LEFT,
    "right": WD_ALIGN_PARAGRAPH.RIGHT,
}


def set_font(run, size=14, bold=False, italic=False, name=FONT, color=None):
    run.font.name = name
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    if color:
        run.font.color.rgb = RGBColor(*color)
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.append(rfonts)
    for attr in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        rfonts.set(qn(attr), name)


def _field(paragraph, instr, size=12):
    """Вставка поля Word (PAGE / NUMPAGES)."""
    run = paragraph.add_run()
    set_font(run, size)
    fld_begin = OxmlElement("w:fldChar")
    fld_begin.set(qn("w:fldCharType"), "begin")
    instr_el = OxmlElement("w:instrText")
    instr_el.set(qn("xml:space"), "preserve")
    instr_el.text = instr
    fld_sep = OxmlElement("w:fldChar")
    fld_sep.set(qn("w:fldCharType"), "separate")
    fld_txt = OxmlElement("w:t")
    fld_txt.text = "1"
    fld_end = OxmlElement("w:fldChar")
    fld_end.set(qn("w:fldCharType"), "end")
    run._r.append(fld_begin)
    run._r.append(instr_el)
    run._r.append(fld_sep)
    run._r.append(fld_txt)
    run._r.append(fld_end)


class VKR:
    """Сборщик документа. Все элементы регистрируются для оглавления."""

    def __init__(self):
        self.doc = Document()
        self.headings = []      # (level, text, page) — для оглавления
        self._toc_anchor = None
        self._page = 1
        self.body = []          # блоки основного текста (для проверки цифр)
        self.refs = []          # библиографические записи (не проверяются)
        self.ref_mode = False   # True — запись идёт в список литературы
        self._setup_styles()
        self._setup_section(self.doc.sections[0])

    # ---------------------------------------------------------------- база
    def _setup_styles(self):
        st = self.doc.styles["Normal"]
        st.font.name = FONT
        st.font.size = Pt(14)
        st.element.rPr.rFonts.set(qn("w:eastAsia"), FONT)
        st.paragraph_format.line_spacing = 1.5
        st.paragraph_format.space_before = Pt(0)
        st.paragraph_format.space_after = Pt(0)

    @staticmethod
    def _setup_section(sec, first=False):
        sec.page_height = Cm(29.7)
        sec.page_width = Cm(21.0)
        sec.top_margin = Cm(2.0)
        sec.bottom_margin = Cm(2.0)
        sec.left_margin = Cm(3.0)
        sec.right_margin = Cm(1.5)
        sec.footer_distance = Cm(1.0)
        sec.header_distance = Cm(1.2)

    def start_body(self):
        """Новая секция: титульный лист остаётся без номера, нумерация — со 2-й."""
        sec = self.doc.add_section(WD_SECTION.NEW_PAGE)
        self._setup_section(sec)
        self._numbering(sec, enable=True, start=2)
        return sec

    def no_numbering(self, sec=None):
        sec = sec or self.doc.sections[0]
        self._numbering(sec, enable=False)

    def toc_anchor(self):
        """Место, куда будет вставлено оглавление."""
        p = self.doc.add_paragraph()
        p.paragraph_format.space_after = Pt(0)
        self._toc_anchor = p
        return p

    def _numbering(self, sec, enable=True, start=None):
        """Нумерация страниц в нижнем колонтитуле по центру."""
        footer = sec.footer
        footer.is_linked_to_previous = False
        p = footer.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for r in list(p.runs):
            r._element.getparent().remove(r._element)
        if enable:
            _field(p, "PAGE", size=12)
        if start is not None:
            pg = OxmlElement("w:pgNumType")
            pg.set(qn("w:start"), str(start))
            sec._sectPr.append(pg)

    # ------------------------------------------------------------ элементы
    def para(self, text="", size=14, bold=False, italic=False, align="just",
             indent=1.25, before=0, after=0, spacing=1.5, keep=False,
             first=False, color=None, toc_entry=None):
        p = self.doc.add_paragraph()
        pf = p.paragraph_format
        pf.alignment = ALIGN[align]
        pf.first_line_indent = Cm(indent) if indent else Cm(0)
        pf.space_before = Pt(before)
        pf.space_after = Pt(after)
        pf.line_spacing = spacing
        pf.keep_with_next = keep
        if text:
            r = p.add_run(text)
            set_font(r, size, bold, italic, color=color)
            (self.refs if self.ref_mode else self.body).append(text)
        if toc_entry is not None:
            self.headings.append(toc_entry)
        return p

    def rich(self, chunks, size=14, align="just", indent=1.25, before=0,
             after=0, spacing=1.5, keep=False):
        """chunks: [(текст, {'b':..,'i':..,'sub':..,'sup':..}), ...]"""
        p = self.doc.add_paragraph()
        pf = p.paragraph_format
        pf.alignment = ALIGN[align]
        pf.first_line_indent = Cm(indent) if indent else Cm(0)
        pf.space_before = Pt(before)
        pf.space_after = Pt(after)
        pf.line_spacing = spacing
        pf.keep_with_next = keep
        acc = []
        for text, style in chunks:
            r = p.add_run(text)
            set_font(r, size, style.get("b", False), style.get("i", False))
            if style.get("sub"):
                r.font.subscript = True
            if style.get("sup"):
                r.font.superscript = True
            acc.append(text)
        (self.refs if self.ref_mode else self.body).append("".join(acc))
        return p

    def h(self, text, level=1, toc=True, before=None, after=None):
        """Заголовок. Уровень 1 — раздел (с новой страницы), 2 — параграф."""
        if level == 1:
            before = 0 if before is None else before
            after = 18 if after is None else after
            if len(self.headings) > 0 or toc:
                pass
            indent = 0
            align = "left"
            size = 14
        elif level == 2:
            before = 16 if before is None else before
            after = 10 if after is None else after
            indent = 0
            align = "left"
            size = 14
        else:
            before = 10 if before is None else before
            after = 6 if after is None else after
            indent = 1.25
            align = "left"
            size = 14
        p = self.para(text, size=size, bold=True, align=align, indent=indent,
                      before=before, after=after, keep=True)
        if toc:
            self.headings.append((level, text))
        return p

    def page_break(self):
        p = self.doc.add_paragraph()
        p.add_run().add_break(WD_BREAK.PAGE)
        return p

    def figure(self, path, caption, width_cm=15.0, note=None):
        p = self.doc.add_paragraph()
        pf = p.paragraph_format
        pf.alignment = WD_ALIGN_PARAGRAPH.CENTER
        pf.first_line_indent = Cm(0)
        pf.space_before = Pt(10)
        pf.space_after = Pt(6)
        pf.line_spacing = 1.0
        pf.keep_with_next = True
        p.add_run().add_picture(path, width=Cm(width_cm))
        cap = self.para(caption, size=12, align="center", indent=0, before=0,
                        after=8, spacing=1.0)
        cap.paragraph_format.keep_with_next = bool(note)
        if note:
            self.para(note, size=11, align="left", indent=0, before=0,
                      after=10, spacing=1.0, italic=True)
        return p

    def table(self, header, rows, widths, caption=None, note=None,
              size=11, align_first_left=True):
        if caption:
            cap = self.para(caption, size=12, align="left", indent=0,
                            before=10, after=4, spacing=1.0)
            cap.paragraph_format.keep_with_next = True
        t = self.doc.add_table(rows=0, cols=len(widths))
        t.style = "Table Grid"
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        t.autofit = False
        # ширина таблицы задаётся явно: python-docx иначе распределяет колонки
        # поровну и колонки с длинным текстом «расползаются» в Word
        for gc, w in zip(t._tbl.tblGrid.findall(qn("w:gridCol")), widths):
            gc.set(qn("w:w"), str(int(Cm(w).twips)))
        tblPr = t._tbl.tblPr
        layout = OxmlElement("w:tblLayout")
        layout.set(qn("w:type"), "fixed")
        tblPr.append(layout)

        def fill(cells, values, bold=False, first_left=True):
            for ci, val in enumerate(values):
                cell = cells[ci]
                cell.width = Cm(widths[ci])
                cp = cell.paragraphs[0]
                cpf = cp.paragraph_format
                cpf.space_before = Pt(2)
                cpf.space_after = Pt(2)
                cpf.line_spacing = 1.0
                cpf.first_line_indent = Cm(0)
                cpf.alignment = (WD_ALIGN_PARAGRAPH.LEFT
                                 if (ci == 0 and first_left)
                                 else WD_ALIGN_PARAGRAPH.CENTER)
                r = cp.add_run(str(val))
                set_font(r, size, bold=bold)

        fill(t.add_row().cells, header, bold=True)
        for v in header:
            (self.refs if self.ref_mode else self.body).append(str(v))
        tr = t.rows[0]._tr
        trPr = tr.get_or_add_trPr()
        th = OxmlElement("w:tblHeader")
        th.set(qn("w:val"), "true")
        trPr.append(th)
        for row in rows:
            cells = t.add_row().cells
            fill(cells, row, first_left=align_first_left)
            for ci, cell in enumerate(cells):
                cell.width = Cm(widths[ci])
            for v in row:
                (self.refs if self.ref_mode else self.body).append(str(v))
        if note:
            self.para(note, size=11, align="left", indent=0, before=3,
                      after=10, spacing=1.0, italic=True)
        else:
            self.para("", size=10, indent=0, after=6, spacing=1.0)
        return t

    def equation(self, chunks, number=None):
        p = self.doc.add_paragraph()
        pf = p.paragraph_format
        pf.first_line_indent = Cm(0)
        pf.space_before = Pt(6)
        pf.space_after = Pt(6)
        pf.line_spacing = 1.5
        pf.tab_stops.add_tab_stop(Cm(8.0), WD_TAB_ALIGNMENT.CENTER)
        pf.tab_stops.add_tab_stop(Cm(16.0), WD_TAB_ALIGNMENT.RIGHT)
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        set_font(p.add_run("\t"), 14)
        acc = []
        for text, style in chunks:
            r = p.add_run(text)
            set_font(r, 14, False, style.get("i", False))
            if style.get("sub"):
                r.font.subscript = True
            if style.get("sup"):
                r.font.superscript = True
            acc.append(text)
        if number:
            set_font(p.add_run("\t(" + number + ")"), 14)
        self.body.append("".join(acc))
        return p

    def toc(self, entries, page_of=None):
        """Оглавление: собирается после текста и переносится к якорю.

        Номера страниц подставляются из карты вёрстки (verify_layout.page_map):
        документ собирается дважды — сначала черновик для расчёта страниц,
        затем итоговая версия с номерами. Поле TOC не используется, поэтому
        содержание готово к печати сразу и не требует обновления полей.
        """
        made = []
        title = self.doc.add_paragraph()
        title.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
        title.paragraph_format.space_after = Pt(14)
        title.paragraph_format.first_line_indent = Cm(0)
        set_font(title.add_run("СОДЕРЖАНИЕ"), 14, bold=True)
        made.append(title._p)

        self._toc_rows = []
        for level, text, _page in entries:
            if level > 3:
                continue
            q = self.doc.add_paragraph()
            pf = q.paragraph_format
            pf.first_line_indent = Cm(0)
            pf.left_indent = Cm(0 if level == 1 else 0.75)
            pf.space_before = Pt(5 if level == 1 else 0)
            pf.space_after = Pt(0)
            pf.line_spacing = 1.5
            pf.tab_stops.add_tab_stop(Cm(16.0), WD_TAB_ALIGNMENT.RIGHT,
                                      WD_TAB_LEADER.DOTS)
            r = q.add_run(text)
            set_font(r, 14, bold=(level == 1))
            set_font(q.add_run("\t"), 14)
            if page_of:
                num = page_of.get(text)
                if num is not None:
                    set_font(q.add_run(str(num)), 14, bold=(level == 1))
            self._toc_rows.append(q)
            made.append(q._p)

        anchor = self._toc_anchor
        if anchor is not None:
            cur = anchor._p
            for el in made:
                el.getparent().remove(el)
                cur.addnext(el)
                cur = el

    def fill_toc_pages(self, page_of):
        """Подставить номера страниц в строки содержания (после вёрстки)."""
        for q in self._toc_rows:
            text = q.text.rstrip("\t")
            num = page_of.get(text)
            if num is None:
                continue
            r = q.add_run(str(num))
            set_font(r, 14, bold=q.runs[0].bold if q.runs else False)

    def save(self, path):
        self.doc.save(path)
        return path
