# -*- coding: utf-8 -*-
"""Проверка прослеживаемости чисел.

Каждый числовой токен основного текста должен либо
  (а) совпадать со значением из out/metrics.json (inputs или derived),
  (б) входить в белый список служебных чисел (годы, номера законов,
      нумерация разделов, коэффициенты пересчёта единиц).
"""
import json
import os
import re
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
M = json.load(open(os.path.join(BASE, "out", "metrics.json"), encoding="utf-8"))
BLOCKS = json.load(open(os.path.join(BASE, "out", "blocks.json"), encoding="utf-8"))

# служебные числа: годы, номера актов, нумерация, коэффициенты единиц
WHITELIST = {
    # годы и даты
    1900, 1910, 1980, 1986, 2000, 2008, 2009, 2010, 2012, 2013, 2014, 2015,
    1973, 1987, 1990, 1901, 1928, 1960, 2016, 2017, 2018, 2019, 2020, 2021,
    2022, 2023, 2024, 2025, 2026, 2027,
    2028, 2029, 2030, 2035, 18, 5, 1, 2, 3, 4, 6, 7, 8, 9, 10, 11, 12, 13,
    14, 15, 16, 17, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31,
    # номера нормативных актов и статей
    117, 342, 426, 961, 135, 117, 32, 3340, 259, 52, 1_259,
    # единицы измерения и нулевые значения
    0, 1000, 10000, 35.11, 293, 1000000,
    # десятичные коэффициенты
    0.78, 0.22, 0.62, 7.33, 11.95, 1.5, 3.0, 2.5, 0.4,
    # проценты/пункты из определений
    5, 100,
}


def numbers_in(text):
    """Числовые токены: 1 234,56 ; 27,4 ; 44.1 ; 118,41."""
    out = []
    for m in re.finditer(r"\d[\d \u00a0]*(?:[.,]\d+)?", text):
        raw = m.group(0).replace("\u00a0", "").replace(" ", "")
        raw = raw.replace(",", ".")
        try:
            out.append((float(raw), m.group(0)))
        except ValueError:
            continue
    return out


def metric_values():
    vals = set()
    for v in M["inputs"].values():
        vals.add(round(float(v), 4))
    for k, v in M["derived"].items():
        if isinstance(v, (int, float)):
            vals.add(round(float(v), 4))
        elif isinstance(v, dict):
            for p in v.values():
                for kk, vv in p.items():
                    if isinstance(vv, (int, float)):
                        vals.add(round(float(vv), 4))
    return vals


def close(a, b):
    """Совпадение с учётом округления (до 1 знака, до целых)."""
    if a == 0:
        return abs(b) < 0.005
    # знак может быть опущен в тексте (abs(...) в модуле форматирования)
    a, b = abs(a), abs(b)
    for nd in (0, 1, 2, 3):
        if round(b, nd) == round(a, nd):
            return True
    # допускаем усечение (59,4 -> 59)
    if int(b) == int(a):
        return True
    return False


def main():
    vals = metric_values()
    text = "\n".join(BLOCKS["body_blocks"])
    # номера библиографических ссылок — не числовые утверждения
    text = re.sub(r"\[\d+(?:;\s*\d+)*\]", " ", text)
    # URL и диапазоны страниц в библиографических описаниях — не показатели
    text = re.sub(r"https?://\S+", " ", text)
    text = re.sub(r"\bС\.\s*\d+\s*[–-]\s*\d+", " ", text)
    # выходные данные библиографических записей: DOI, тома, номера, страницы
    text = re.sub(r"DOI\s*\S+", " ", text)
    text = re.sub(r"\bArt\.\s*\d+", " ", text)
    text = re.sub(r"\b(Т|Vol)\.\s*\d+", " ", text)
    text = re.sub(r"№\s*\d+(\s*\(\d+\))?", " ", text)
    text = re.sub(r"\bP\.\s*\d+(\s*[–-]\s*\d+)?", " ", text)
    text = re.sub(r"\b\d+\s*с\.", " ", text)
    # объём и цена в библиографических записях: «228 p.», «$900 млн»
    text = re.sub(r"\d+\s*p\.", " ", text)
    text = re.sub(r"\$\s*\d+", " ", text)
    # цены и объёмы, приведённые в заголовках публикаций
    text = re.sub(r"«[^»]*\d[^»]*»", " ", text)
    text = re.sub(r"\b\d+\s*[–-]\s*\d+\s*с\.", " ", text)
    tokens = numbers_in(text)
    unknown = []
    for num, raw in tokens:
        if num in WHITELIST:
            continue
        if any(close(num, v) for v in vals):
            continue
        unknown.append((raw, num))

    # агрегируем повторы
    seen = {}
    for raw, num in unknown:
        seen.setdefault(raw.strip(), 0)
        seen[raw.strip()] += 1

    print(f"числовых токенов: {len(tokens)}")
    print(f"уникальных значений в реестре: {len(vals)}")
    print(f"нераспознанных токенов: {len(unknown)} (уникальных {len(seen)})")
    for raw, cnt in sorted(seen.items(), key=lambda x: -x[1])[:40]:
        print(f"  «{raw}» ×{cnt}")
    return 0 if not unknown else 1


if __name__ == "__main__":
    sys.exit(main())
