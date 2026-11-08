# -*- coding: utf-8 -*-
"""Рисунки ВКР. Все значения берутся из out/metrics.json."""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

BASE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(BASE, "figures")
os.makedirs(FIG, exist_ok=True)

M = json.load(open(os.path.join(BASE, "out", "metrics.json"), encoding="utf-8"))
D = M["derived"]
V = M["inputs"]
MONTHS = M["series"]["months"]
URALS = M["series"]["urals_2026"]

plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["DejaVu Serif"],
    "font.size": 9,
    "axes.titlesize": 10,
    "axes.labelsize": 9,
    "axes.grid": True,
    "grid.alpha": 0.25,
    "grid.linewidth": 0.6,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "figure.dpi": 200,
    "savefig.bbox": "tight",
})

INK = "#22252b"
ACCENT = "#9e2b25"
BLUE = "#2f5d8a"
GREY = "#8a8f98"


def save(fig, name):
    path = os.path.join(FIG, name)
    fig.savefig(path, dpi=200, facecolor="white")
    plt.close(fig)
    print("  ->", name)


# ------------------------------------------------------------------ Рис. 1
def fig1():
    fig, ax = plt.subplots(figsize=(6.3, 3.3))
    x = list(range(len(MONTHS)))
    ax.plot(x, URALS, marker="o", ms=4.2, lw=1.7, color=ACCENT,
            label="Urals (расчётная цена для налогов)")
    ax.axhline(V["ru_budget_urals_2026"], ls="--", lw=1.2, color=BLUE,
               label=f"Бюджетная цена отсечения — {V['ru_budget_urals_2026']:.0f} долл./барр.")
    ax.fill_between(x, URALS, V["ru_budget_urals_2026"],
                    where=[u > V["ru_budget_urals_2026"] for u in URALS],
                    color=ACCENT, alpha=0.10, interpolate=True)
    ax.fill_between(x, URALS, V["ru_budget_urals_2026"],
                    where=[u <= V["ru_budget_urals_2026"] for u in URALS],
                    color=BLUE, alpha=0.10, interpolate=True)
    for i, (xi, yi) in enumerate(zip(x, URALS)):
        if i in (0, 2, 6, 9):
            ax.annotate(f"{yi:.0f}", (xi, yi), textcoords="offset points",
                        xytext=(0, 9), ha="center", fontsize=8, color=INK)
    ax.set_xticks(x)
    ax.set_xticklabels([m[:3] for m in MONTHS])
    ax.set_xlabel("Месяц 2026 г.")
    ax.set_ylabel("Долл. США за баррель")
    ax.set_ylim(0, 112)
    ax.yaxis.set_major_locator(MaxNLocator(6))
    ax.legend(loc="upper left", fontsize=7.6, frameon=False)
    ax.set_title("Помесячная динамика расчётной цены нефти Urals в 2026 г.\n"
                 "и уровень бюджетной цены отсечения", color=INK, pad=8)
    save(fig, "fig1_urals_2026.png")


# ------------------------------------------------------------------ Рис. 2
def fig2():
    fig, ax = plt.subplots(figsize=(6.3, 3.1))
    names = ["2023", "2024", "2025", "план\n2026", "оценка\nСП\n2026"]
    vals = [V["ru_ngd_2023"], V["ru_ngd_2024"], V["ru_ngd_2025"],
            V["ru_budget_ngd_2026"], V["ru_ngd_audit_2026"]]
    colors = [GREY, GREY, GREY, BLUE, ACCENT]
    bars = ax.bar(names, vals, color=colors, width=0.62, edgecolor="white", lw=0.8)
    for b, v in zip(bars, vals):
        ax.annotate(f"{v:.1f}".replace(".", ","), (b.get_x() + b.get_width() / 2, v),
                    textcoords="offset points", xytext=(0, 3), ha="center", fontsize=8.2)
    ax.set_ylabel("Трлн руб.")
    ax.set_ylim(0, 13)
    ax.set_title("Нефтегазовые доходы федерального бюджета России:\n"
                 "факт 2023–2025 гг. и параметры 2026 г.", color=INK, pad=8)
    ax.text(0.99, 0.94, f"разрыв плана и оценки: {D['ngd_audit_gap_pct']:.1f} п. п.".replace(".", ","),
            transform=ax.transAxes, ha="right", fontsize=7.6, color=ACCENT)
    save(fig, "fig2_ngd.png")


# ------------------------------------------------------------------ Рис. 3
def fig3():
    scen = D["scenarios"]
    fig, ax = plt.subplots(figsize=(6.3, 3.2))
    labels = list(scen.keys())
    urals = [scen[k]["urals"] for k in labels]
    rub = [scen[k]["rub_barrel"] for k in labels]
    x = range(len(labels))
    w = 0.34
    b1 = ax.bar([i - w / 2 for i in x], urals, width=w, color=ACCENT,
                label="Urals, долл./барр. (левая ось)")
    ax2 = ax.twinx()
    b2 = ax2.bar([i + w / 2 for i in x], rub, width=w, color=BLUE,
                 label="Рублёвая цена, руб./барр. (правая ось)")
    for bars, vals_ in ((b1, urals), (b2, rub)):
        for b, v in zip(bars, vals_):
            ax_ = ax if bars is b1 else ax2
            ax_.annotate(f"{v:.0f}", (b.get_x() + b.get_width() / 2, v),
                         textcoords="offset points", xytext=(0, 3),
                         ha="center", fontsize=8)
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels)
    ax.set_ylabel("Долл. США за баррель")
    ax2.set_ylabel("Руб. за баррель")
    ax.set_ylim(0, 100)
    ax2.set_ylim(0, 8500)
    ax2.grid(False)
    ax.text(0.015, 0.95, "левая ось — Urals, долл./барр.\nправая ось — рублёвая цена, руб./барр.",
            transform=ax.transAxes, fontsize=7.4, va="top", color=INK)
    ax.set_title("Сценарная оценка цены Urals и рублёвой выручки\nна баррель в 2027 г.",
                 color=INK, pad=8)
    save(fig, "fig3_scenarios.png")


# ------------------------------------------------------------------ Рис. 4
def fig4():
    fig, ax = plt.subplots(figsize=(6.3, 3.0))
    labels = ["Россия,\nдальнее\nзарубежье", "Россия,\nКитай", "Азербайджан,\nЕС и Турция\n(1-е п/г 2026)"]
    vals = [V["ru_gazprom_price_far_abroad_2026"], V["ru_gazprom_price_china_2026"],
            D["az_gas_price_1h2026"]]
    colors = [BLUE, ACCENT, "#4b7f52"]
    bars = ax.bar(labels, vals, color=colors, width=0.55, edgecolor="white", lw=0.8)
    for b, v in zip(bars, vals):
        ax.annotate(f"{v:.0f}".replace(".", ","), (b.get_x() + b.get_width() / 2, v),
                    textcoords="offset points", xytext=(0, 3), ha="center", fontsize=8.4)
    ax.axhline(V["ru_ttf_oct_2026"], ls=":", lw=1.3, color=GREY)
    ax.text(len(vals) - 0.42, V["ru_ttf_oct_2026"] + 22,
            f"TTF, октябрь 2026: ≈{V['ru_ttf_oct_2026']:.0f}",
            ha="right", fontsize=7.4, color=GREY)
    ax.set_ylabel("Долл. США за 1 тыс. куб. м")
    ax.set_ylim(0, 1250)
    ax.set_ylabel("Долл. США / 1 тыс. куб. м")
    ax.set_title("Сопоставление цен реализации газа по направлениям, 2026 г.",
                 color=INK, pad=8)
    save(fig, "fig4_gas_prices.png")


# ------------------------------------------------------------------ Рис. 5
def fig5():
    fig, ax = plt.subplots(figsize=(6.3, 3.1))
    labels = ["2024", "2025", "ноябрь\n2025", "июль\n2026"]
    keys = ["ru_disc_2024", "ru_disc_2025", "ru_disc_2025_11", "ru_disc_2026_07"]
    vals = [V[k] for k in keys]
    colors = [GREY, BLUE, "#c98b3f", ACCENT]
    bars = ax.bar(labels, vals, color=colors, width=0.55, edgecolor="white")
    for b, v in zip(bars, vals):
        ax.annotate(f"{v:.1f}".replace(".", ","), (b.get_x() + b.get_width() / 2, v),
                    textcoords="offset points", xytext=(0, 3), ha="center", fontsize=8.4)
    ax.axhspan(0, 3.0, color=GREY, alpha=0.13)
    ax.set_xlim(-0.75, 3.6)
    ax.annotate("историческая норма:\n1,5–3,0 % цены Brent", xy=(0.35, 3.0),
                xytext=(-0.62, 9.5), fontsize=7.2, ha="left", va="center",
                color=GREY, arrowprops=dict(arrowstyle="->", color=GREY, lw=0.8))
    ax.set_ylabel("Долл. США за баррель")
    ax.set_ylim(0, 31)
    ax.set_title("Дисконт нефти Urals к Brent: историческая норма и периоды\n"
                 "санкционного расширения (средние значения)", color=INK, pad=8)
    ax.annotate(f"≈{V['ru_disc_2025_12_share']:.0f} % цены Brent\nв декабре 2025 г.",
                xy=(2.08, vals[2]), xytext=(1.15, 27.5), fontsize=7.4, color=INK,
                arrowprops=dict(arrowstyle="->", color=GREY, lw=0.9,
                                connectionstyle="arc3,rad=-0.25"))
    save(fig, "fig5_discount.png")


# ------------------------------------------------------------------ Рис. 6
def fig6():
    fig, ax = plt.subplots(figsize=(6.3, 3.1))
    years = ["2025", "2026 (план)", "2027 (цель ЕС)"]
    vals = [V["az_gas_export_eu_2025"], V["az_gas_export_eu_2025"] * 1.06,
            V["az_eu_target_2027"]]
    bars = ax.bar(years, vals, color=["#4b7f52", "#4b7f52", "#9bb3a0"],
                  width=0.5, edgecolor="white", hatch=["", "", "//"])
    for b, v in zip(bars, vals):
        ax.annotate(f"{v:.1f}".replace(".", ","), (b.get_x() + b.get_width() / 2, v),
                    textcoords="offset points", xytext=(0, 3), ha="center", fontsize=8.4)
    ax.set_ylabel("Млрд куб. м")
    ax.set_ylim(0, 24)
    ax.set_title("Экспорт азербайджанского газа в Европу:\n"
                 "факт 2025 г. и ориентир меморандума с ЕС", color=INK, pad=8)
    ax.text(0.02, 0.93, f"требуемый прирост к 2027 г.: +{D['az_eu_target_gap']:.0f} %".replace(".", ","),
            transform=ax.transAxes, fontsize=7.8, color=ACCENT)
    save(fig, "fig6_az_gas.png")


if __name__ == "__main__":
    print("рисунки:")
    fig1(); fig2(); fig3(); fig4(); fig5(); fig6()
