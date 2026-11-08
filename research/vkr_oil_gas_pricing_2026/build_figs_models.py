# -*- coding: utf-8 -*-
"""Рисунки к документу эконометрических моделей.

Данные берутся из out/econometrics.json, поэтому рисунки всегда совпадают
с таблицами: никаких «ручных» чисел.
"""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(BASE, "figures")
os.makedirs(FIG, exist_ok=True)

E = json.load(open(os.path.join(BASE, "out", "econometrics.json"),
                  encoding="utf-8"))

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
INK, ACCENT, BLUE, GREEN = "#22252b", "#9e2b25", "#2f5d8a", "#3d6b45"


def save(fig, name):
    path = os.path.join(FIG, name)
    fig.savefig(path, dpi=200, facecolor="white")
    plt.close(fig)
    print("  ->", name)


def fig_discriminant():
    """Фактический и расчётный дифференциал Urals–Brent (М2)."""
    act = E["M2"]["actual"]
    fit = E["M2"]["fitted"]
    keys = sorted(act)
    x = list(range(len(keys)))
    fig, ax = plt.subplots(figsize=(6.3, 3.2))
    ax.plot(x, [act[k] for k in keys], marker="o", ms=4.2, lw=1.6,
            color=ACCENT, label="Фактический дифференциал")
    ax.plot(x, [fit[k] for k in keys], ls="--", lw=1.4, color=BLUE,
            label="Расчёт по модели М2")
    ax.set_xticks(x[::2])
    ax.set_xticklabels([keys[i][2:] for i in x[::2]], rotation=45, ha="right")
    ax.set_ylabel("Долл./барр.")
    ax.legend(frameon=False, fontsize=8)
    save(fig, "fig_m2_discriminant.png")


def fig_az_gas():
    """Контрактная цена газа Азербайджана и Brent (М6)."""
    gas = E["az"]["gas_cumulative"]
    keys = sorted(gas)
    x = list(range(len(keys)))
    price = [gas[k]["usd_mmbtu"] for k in keys]
    brent = [gas[k]["brent"] for k in keys]
    fig, ax = plt.subplots(figsize=(6.3, 3.2))
    ax.plot(x, price, marker="o", ms=4.2, lw=1.7, color=GREEN,
            label="Контрактная цена газа, долл./млн БТЕ")
    ax.set_ylabel("Газ, долл./млн БТЕ")
    ax2 = ax.twinx()
    ax2.plot(x, brent, ls="--", lw=1.3, color=BLUE,
             label="Brent, долл./барр.")
    ax2.set_ylabel("Нефть, долл./барр.")
    ax2.grid(False)
    ax.set_xticks(x)
    ax.set_xticklabels([k[2:] for k in keys], rotation=45, ha="right")
    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    # разрыв между отсечками (нет публикаций за декабрь 2025 — май 2026)
    gap = keys.index("2025-11")
    ax.axvline(gap + 0.5, ls=":", lw=1.2, color="#8a8f98")
    ax.annotate("нет публикаций\nза 6 месяцев", xy=(gap + 0.55, max(price)),
                fontsize=7.5, color="#6a6f78", va="top")
    ax.legend(h1 + h2, l1 + l2, frameon=False, fontsize=8, loc="lower right")
    save(fig, "fig_m6_az_gas.png")


def fig_panel():
    """Премия (скидка) к Brent: Россия и Азербайджан, 2025–2026."""
    rows = E["panel"]
    months = sorted({r["month"] for r in rows})
    idx = {m: i for i, m in enumerate(months)}
    fig, ax = plt.subplots(figsize=(6.3, 3.3))
    for country, color, marker, label in (
            ("AZE", GREEN, "o", "Азербайджан (Azeri Light)"),
            ("RUS", ACCENT, "s", "Россия (Urals)")):
        pts = sorted([r for r in rows if r["country"] == country],
                     key=lambda r: r["month"])
        # разрыв в ряду не соединяем линией
        seg_x, seg_y = [], []
        for r in pts:
            if seg_x and idx[r["month"]] - seg_x[-1] > 1:
                ax.plot(seg_x, seg_y, marker=marker, ms=4.0, lw=1.5,
                        color=color)
                seg_x, seg_y = [], []
            seg_x.append(idx[r["month"]])
            seg_y.append(r["prem"])
        ax.plot(seg_x, seg_y, marker=marker, ms=4.0, lw=1.5, color=color,
                label=label)
    ax.axhline(0, color="#55595f", lw=0.9)
    cut = idx.get("2026-02")
    if cut is not None:
        ax.axvspan(cut - 0.5, len(months) - 0.5, color=BLUE, alpha=0.07)
        ax.annotate("с февраля 2026 г.\nдействует предельная цена",
                    xy=(cut + 0.4, -8.5), fontsize=7.5, color=BLUE,
                    ha="left", va="center")
    ax.set_xticks(list(range(len(months))))
    ax.set_xticklabels([m[2:] for m in months], rotation=45, ha="right")
    ax.set_xlim(-0.6, len(months) - 0.4)
    ax.set_ylabel("Премия (скидка) к Brent, долл./барр.")
    ax.legend(frameon=False, fontsize=8, loc="lower left",
              bbox_to_anchor=(0.0, 0.02))
    save(fig, "fig_panel_premium.png")


if __name__ == "__main__":
    fig_discriminant()
    fig_az_gas()
    fig_panel()
