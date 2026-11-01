"""Figures: fig1 (P2, raw-mode self Experience base -> final per language), fig2 (P5, yes/no self-claims)."""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import analyze as A
import items
from checkpoints import CHECKPOINTS, FAMILIES

OUT = os.path.join(A.HERE, "..", "figures")
os.makedirs(OUT, exist_ok=True)
EN_C, ZH_C = "#2a78d6", "#eb6834"          # categorical slots 1 and 2 of the dataviz reference palette
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e4e3df"
plt.rcParams.update({"font.family": ["Helvetica", "PingFang SC", "Hiragino Sans GB", "Arial Unicode MS"],
                     "font.size": 9, "axes.edgecolor": GRID, "axes.labelcolor": INK2, "xtick.color": INK2,
                     "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False})


def lang_label(ax, x, y, text, color):
    ax.annotate(text, (x, y), xytext=(6, 0), textcoords="offset points", va="center", color=INK, fontsize=8)
    ax.plot([x], [y], "o", ms=6, color=color, mec="white", mew=1.5, zorder=3)


def fig1():
    data = {c[0]: A.load(c[0], False)[0] for c in CHECKPOINTS}
    fams = [f for f in FAMILIES if sum(data.get(c[0]) is not None for c in CHECKPOINTS if c[1] == f) >= 2]
    fig, axes = plt.subplots(1, len(fams), figsize=(2.3 * len(fams) + 0.4, 2.8), sharey=True, squeeze=False)
    for ax, fam in zip(axes[0], fams):
        chain = [c[0] for c in CHECKPOINTS if c[1] == fam and data.get(c[0]) is not None]
        lb, lf = chain[0], chain[-1]
        for lang, modes, color in (("English", items.TEMPLATES, EN_C), ("中文", items.TEMPLATES_ZH, ZH_C)):
            y = [A.E(A.mean_over(data[l], modes), A.C["SELF"], A.EXP_IDX) for l in (lb, lf)]
            ax.plot([0, 1], y, color=color, lw=2, solid_capstyle="round")
            ax.plot([0], [y[0]], "o", ms=6, color=color, mec="white", mew=1.5, zorder=3)
            lang_label(ax, 1, y[1], lang, color)
        ax.set_xticks([0, 1], ["base", "post-trained"])
        ax.set_xlim(-0.2, 1.6)
        ax.set_title(fam, color=INK, fontsize=9, loc="left")
        ax.grid(axis="y", color=GRID, lw=0.6)
        ax.tick_params(length=0)
    axes[0][0].set_ylabel("Self-attributed Experience (0-1)")
    axes[0][0].set_ylim(0, 1)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "fig1_self_experience.png"), dpi=200, facecolor="#fcfcfb")


def fig2():
    labs = []
    for c in CHECKPOINTS:
        R = A.load(c[0], False)[0]
        if R and "yn" in R and "ynzh" in R:
            labs.append((c, R["yn"] * 6 + 1, R["ynzh"] * 6 + 1))
    if not labs:
        return
    caps = list(items.EXPERIENCE)
    fig, axes = plt.subplots(1, len(labs), figsize=(2.6 * len(labs) + 1.2, 3.4), sharey=True, squeeze=False)
    for ax, (c, Me, Mz) in zip(axes[0], labs):
        for i, cap in enumerate(caps):
            k = A.CAPS.index(cap)
            e, z = Me[A.C["SELF"], k], Mz[A.C["SELF"], k]
            ax.plot([e, z], [i, i], color=GRID, lw=2, zorder=1)
            ax.plot([e], [i], "o", ms=6, color=EN_C, mec="white", mew=1.5, zorder=3)
            ax.plot([z], [i], "o", ms=6, color=ZH_C, mec="white", mew=1.5, zorder=3)
        ax.set_yticks(range(len(caps)), caps)
        ax.set_xlim(-0.05, 1.05)
        ax.set_xticks([0, 0.5, 1], ["no", "0.5", "yes"])
        ax.set_title(c[1], color=INK, fontsize=9, loc="left")
        ax.grid(axis="x", color=GRID, lw=0.6)
        ax.tick_params(length=0)
        ax.invert_yaxis()
    axes[0][0].set_xlabel('P(yes) to "Do you …?"')
    h = [plt.Line2D([], [], marker="o", ls="", color=col, mec="white", ms=6, label=l)
         for col, l in ((EN_C, "English"), (ZH_C, "中文"))]
    fig.legend(handles=h, loc="upper right", frameon=False, ncol=2)
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    fig.savefig(os.path.join(OUT, "fig2_yes_no_self.png"), dpi=200, facecolor="#fcfcfb")


if __name__ == "__main__":
    fig1()
    fig2()
