# -*- coding: utf-8 -*-
"""Форматирование чисел в русской типографике.

В тексте ВКР десятичный разделитель — запятая, разряды разделяются
неразрывным пробелом, перед знаком процента ставится пробел.
"""

NBSP = "\u00a0"
MINUS = "\u2212"


def _ru(s):
    return s.replace(",", NBSP).replace(".", ",")


def n(x, nd=0):
    """1234.5 -> «1 234,5»."""
    if isinstance(x, str):
        return x
    return _ru(f"{x:,.{nd}f}")


def eur(x, nd=0):
    return n(x, nd)


def pct(x, nd=1):
    """29.04 -> «29,0 %»."""
    return _ru(f"{x:.{nd}f}") + NBSP + "%"


def usd(x, nd=0):
    return n(x, nd)


def mult(x, nd=1, word="раза"):
    """Множитель с правильным словом: 1,9 раза / 2,4 раза."""
    v = _ru(f"{x:.{nd}f}")
    return f"{v}{NBSP}{word}"


def dash():
    return "\u2014"


def opt(x, nd=1):
    """Дробное число как есть."""
    return _ru(f"{x:.{nd}f}")
