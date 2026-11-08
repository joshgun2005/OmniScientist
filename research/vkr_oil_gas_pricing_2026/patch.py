# -*- coding: utf-8 -*-
"""Правка text_mr_ch1.py по якорям: новый текст читается из файла .txt.

Использование:
    python3 patch.py spec.json
где spec.json — [[начало, конец, путь_к_новому_тексту], ...].
Пустая строка вместо пути — удалить фрагмент.
"""
import json
import sys


def apply(spec_path, target="text_mr_ch1.py"):
    s = open(target, encoding="utf-8").read()
    for start, end, newfile in json.load(open(spec_path, encoding="utf-8")):
        i = s.find(start)
        assert i >= 0, "начало не найдено: " + start[:70]
        j = s.find(end, i)
        assert j >= 0, "конец не найден: " + end[:70]
        new = open(newfile, encoding="utf-8").read().rstrip("\n") if newfile else ""
        s = s[:i] + new + s[j + len(end):]
    open(target, "w", encoding="utf-8").write(s)
    print("правок применено: %d" % len(json.load(open(spec_path, encoding="utf-8"))))


if __name__ == "__main__":
    apply(sys.argv[1])
