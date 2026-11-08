# -*- coding: utf-8 -*-
"""Движок оформления по методическим рекомендациям Финансового университета.

Отличия от docx_engine.VKR:
  * ссылки оформляются подстрочными сносками (настоящие сноски Word),
    а не номерами в квадратных скобках;
  * заголовки глав — по центру, полужирным, заглавными буквами;
  * заголовки параграфов — с абзацного отступа, строчными;
  * интервалы 15 пт вокруг заголовков;
  * текст сносок — Times New Roman 10 пт, одинарный интервал, по ширине.

Технически сноски собираются как отдельная часть пакета
(word/footnotes.xml) и привязываются к документу через отношение
officeDocument/2006/relationships/footnotes; в тексте ставится
w:footnoteReference с соответствующим номером.
"""
import os

from docx.opc.constants import RELATIONSHIP_TYPE as RT
from docx.opc.packuri import PackURI
from docx.opc.part import Part
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
from docx.shared import Cm, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

import docx_engine as base
from docx_engine import ALIGN, set_font

FOOTNOTES_CT = ("application/vnd.openxmlformats-officedocument"
                ".wordprocessingml.footnotes+xml")
FOOTNOTES_PARTNAME = PackURI("/word/footnotes.xml")


def _xml_escape(text):
    return (text.replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;"))


class MRDoc(base.VKR):
    """Документ ВКР с подстрочными ссылками."""

    def __init__(self):
        super().__init__()
        self._footnotes = []          # список текстов сносок, id = index + 2

    # ------------------------------------------------------------- сноски
    def fn(self, text):
        """Поставить сноску в текущем абзаце (вызывать внутри para/rich).

        Возвращает номер сноски (сквозная нумерация по документу).
        """
        raise NotImplementedError("используйте mark_fn после создания абзаца")

    def add_footnote(self, paragraph, text, anchor_run_index=None):
        """Добавить сноску в конец указанного абзаца."""
        self._footnotes.append(text)
        fid = len(self._footnotes) + 1          # 0 и 1 — разделители
        run = paragraph.add_run()
        set_font(run, 14)
        rpr = run._r.get_or_add_rPr()
        style = OxmlElement("w:rStyle")
        style.set(qn("w:val"), "FootnoteReference")
        rpr.append(style)
        ref = OxmlElement("w:footnoteReference")
        ref.set(qn("w:id"), str(fid))
        run._r.append(ref)
        return fid

    def para_fn(self, text, note, **kwargs):
        """Абзац, в конце которого ставится сноска."""
        p = self.para(text, **kwargs)
        self.add_footnote(p, note)
        return p

    def rich_fn(self, chunks, note, **kwargs):
        p = self.rich(chunks, **kwargs)
        self.add_footnote(p, note)
        return p


    # --------------------------------------------------- таблицы и рисунки
    def table(self, header, rows, widths, caption=None, note=None,
              size=12, align_first_left=True, number=None):
        """Таблица по методическим рекомендациям.

        Над заголовком справа — «Таблица N.», под ним по центру — заголовок.
        """
        if caption:
            if number:
                cap = self.para(f"Таблица {number}.", size=12, align="right",
                                indent=0, before=10, after=2, spacing=1.0)
                cap.paragraph_format.keep_with_next = True
            cap = self.para(caption, size=12, align="center", indent=0,
                            before=0, after=4, spacing=1.0)
            cap.paragraph_format.keep_with_next = True
        t = super().table(header, rows, widths, caption=None, note=None,
                          size=size, align_first_left=align_first_left)
        if note:
            self.para(note, size=12, align="left", indent=0, before=3,
                      after=12, spacing=1.0)
        return t

    def figure(self, path, caption, width_cm=15.0, note=None, number=None):
        """Рисунок с подписью «Рисунок N – Название» по центру под ним."""
        p = self.para("", size=14, align="center", indent=0, before=10,
                      after=2, spacing=1.0)
        p.add_run().add_picture(path, width=Cm(width_cm))
        p.paragraph_format.keep_with_next = True
        label = f"Рисунок {number} – {caption}" if number else caption
        cap = self.para(label, size=12, align="center", indent=0, before=4,
                        after=4, spacing=1.0)
        cap.paragraph_format.keep_with_next = bool(note)
        if note:
            self.para(note, size=12, align="left", indent=0, before=0,
                      after=12, spacing=1.0)
        return p

    def where(self, pairs, after=15):
        """Расшифровка формулы: «где» и каждый символ с новой строки.

        Символ задаётся строкой вида «P_i» или «P_bench»: до подчёркивания —
        обозначение (курсив), после — нижний индекс (прямое начертание).
        """
        for i, (sym, text) in enumerate(pairs):
            base, _, sub = sym.partition("_")
            chunks = [("где " if i == 0 else "", {}), (base, {"i": True})]
            if sub:
                chunks.append((sub, {"sub": True}))
            chunks.append((" — " + text, {}))
            self.rich(chunks, indent=0, after=2 if i < len(pairs) - 1 else after)

    # ---------------------------------------------------------- заголовки
    def h(self, text, level=1, toc=True, before=None, after=None):
        """Заголовок по методическим рекомендациям.

        Уровень 1 — глава: по центру, полужирный, ЗАГЛАВНЫМИ.
        Уровень 2 — параграф: с абзацного отступа, полужирный, строчными.
        """
        if level == 1:
            p = self.para(text.upper(), size=14, bold=True, align="center",
                          indent=0, before=0 if before is None else before,
                          after=15 if after is None else after, keep=True)
        elif level == 2:
            p = self.para(text, size=14, bold=True, align="left",
                          indent=1.25, before=15 if before is None else before,
                          after=15 if after is None else after, keep=True)
        else:
            p = self.para(text, size=14, bold=True, align="left",
                          indent=1.25, before=10 if before is None else before,
                          after=10 if after is None else after, keep=True)
        if toc:
            self.headings.append((level, text))
        return p

    # -------------------------------------------------------------- сноски
    def _footnotes_blob(self):
        parts = [f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                 f'<w:footnotes {nsdecls("w")}>']
        # разделитель и разделитель продолжения — обязательные первые две
        for sid, kind in ((0, "separator"), (1, "continuationSeparator")):
            parts.append(
                f'<w:footnote w:type="{kind}" w:id="{sid}">'
                f'<w:p><w:pPr><w:spacing w:after="0" w:line="240" '
                f'w:lineRule="auto"/></w:pPr><w:r><w:{kind}/></w:r></w:p>'
                f'</w:footnote>')
        for i, text in enumerate(self._footnotes, start=2):
            parts.append(
                f'<w:footnote w:id="{i}"><w:p>'
                f'<w:pPr><w:pStyle w:val="FootnoteText"/>'
                f'<w:jc w:val="both"/></w:pPr>'
                f'<w:r><w:rPr><w:rStyle w:val="FootnoteReference"/></w:rPr>'
                f'<w:footnoteRef/></w:r>'
                f'<w:r><w:rPr><w:rFonts w:ascii="Times New Roman" '
                f'w:hAnsi="Times New Roman" w:cs="Times New Roman"/>'
                f'<w:sz w:val="20"/><w:szCs w:val="20"/></w:rPr>'
                f'<w:t xml:space="preserve"> {_xml_escape(text)}</w:t></w:r>'
                f'</w:p></w:footnote>')
        parts.append("</w:footnotes>")
        return "".join(parts).encode("utf-8")

    def _attach_footnotes(self):
        if not self._footnotes:
            return
        blob = self._footnotes_blob()
        part = Part(FOOTNOTES_PARTNAME, FOOTNOTES_CT, blob, self.doc.part.package)
        self.doc.part.relate_to(part, RT.FOOTNOTES)
        # стили для текста сноски
        self._ensure_footnote_styles()

    def _ensure_footnote_styles(self):
        styles = self.doc.styles.element
        existing = {s.get(qn("w:styleId")) for s in
                    styles.findall(qn("w:style"))}
        if "FootnoteText" not in existing:
            styles.append(parse_xml(
                f'<w:style {nsdecls("w")} w:type="paragraph" '
                f'w:styleId="FootnoteText">'
                f'<w:name w:val="footnote text"/>'
                f'<w:basedOn w:val="Normal"/>'
                f'<w:pPr><w:spacing w:after="0" w:line="240" '
                f'w:lineRule="auto"/><w:ind w:firstLine="0"/></w:pPr>'
                f'<w:rPr><w:rFonts w:ascii="Times New Roman" '
                f'w:hAnsi="Times New Roman"/><w:sz w:val="20"/></w:rPr>'
                f'</w:style>'))
        if "FootnoteReference" not in existing:
            styles.append(parse_xml(
                f'<w:style {nsdecls("w")} w:type="character" '
                f'w:styleId="FootnoteReference">'
                f'<w:name w:val="footnote reference"/>'
                f'<w:rPr><w:vertAlign w:val="superscript"/></w:rPr>'
                f'</w:style>'))

    # --------------------------------------------------------------- вывод
    def save(self, path):
        # повторное сохранение в тот же объект не должно дублировать часть
        # word/footnotes.xml в пакете
        if not getattr(self, "_footnotes_attached", False):
            self._attach_footnotes()
            self._footnotes_attached = True
        return super().save(path)

    @property
    def footnote_count(self):
        return len(self._footnotes)
