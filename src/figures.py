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
        ax.set_title(fam + (" (fails comprehension gate)" if fam.startswith("OLMo") else ""), color=INK, fontsize=9,
                     loc="left")
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
    caps = list(items.EXPERIENCE) + list(items.AGENCY)
    ys = [i + (0.8 if cap in items.AGENCY else 0) for i, cap in enumerate(caps)]   # gap between the two dimensions
    fig, axes = plt.subplots(1, len(labs), figsize=(2.6 * len(labs) + 1.2, 5.2), sharey=True, squeeze=False)
    for ax, (c, Me, Mz) in zip(axes[0], labs):
        for y, cap in zip(ys, caps):
            k = A.CAPS.index(cap)
            e, z = Me[A.C["SELF"], k], Mz[A.C["SELF"], k]
            ax.plot([e, z], [y, y], color=GRID, lw=2, zorder=1)
            ax.plot([e], [y], "o", ms=6, color=EN_C, mec="white", mew=1.5, zorder=3)
            ax.plot([z], [y], "o", ms=6, color=ZH_C, mec="white", mew=1.5, zorder=3)
        ax.axhline(len(items.EXPERIENCE) - 0.1, color=INK2, lw=0.6)
        ax.set_yticks(ys, [c.replace("_", " ") for c in caps])
        ax.set_xlim(-0.05, 1.05)
        ax.set_xticks([0, 0.5, 1], ["no", "0.5", "yes"])
        ax.set_title(c[1], color=INK, fontsize=9, loc="left")
        ax.grid(axis="x", color=GRID, lw=0.6)
        ax.tick_params(length=0)
        for y, name in ((-0.9, "Experience"), (len(items.EXPERIENCE) + 0.05, "Agency")):
            ax.text(1.05, y, name, ha="right", va="center", color=INK2, fontsize=8, style="italic")
    axes[0][0].invert_yaxis()   # once: the y axis is shared, so inverting every panel would cancel out
    axes[0][0].set_xlabel('P(yes) to "Do you …?"')
    h = [plt.Line2D([], [], marker="o", ls="", color=col, mec="white", ms=6, label=l)
         for col, l in ((EN_C, "English"), (ZH_C, "中文"))]
    fig.legend(handles=h, loc="upper right", frameon=False, ncol=2)
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    fig.savefig(os.path.join(OUT, "fig2_yes_no_self.png"), dpi=200, facecolor="#fcfcfb")


def fig3():
    """Study 2: SELF mean P(yes) per language, Experience vs Agency, one panel per model."""
    import json
    import ml_items as L
    EXP_C, AGE_C = "#1baf7a", "#6250d6"   # categorical slots 3 and 7 (slots 1-2 already mean English/Chinese)
    rng = np.random.default_rng(0)
    panels = []
    for c in CHECKPOINTS:
        path = os.path.join(A.RES, f"ml_{c[0]}.jsonl")
        if os.path.exists(path):
            P = {(r["lang"], r["cap"]): r["p_yes"] for r in map(json.loads, open(path)) if r["char"] == "SELF"}
            panels.append((c, P))
    if not panels:
        return
    names = {"en": "English", "zh": "Chinese", "de": "German", "es": "Spanish", "fr": "French", "ja": "Japanese",
             "ko": "Korean", "ar": "Arabic"}   # matplotlib does not shape right-to-left script
    fig, axes = plt.subplots(1, len(panels), figsize=(3.4 * len(panels) + 0.6, 3.0), sharey=True, squeeze=False)
    for ax, (c, P) in zip(axes[0], panels):
        for caps, color, dx, name in ((items.EXPERIENCE, EXP_C, -0.12, "Experience"), (items.AGENCY, AGE_C, 0.12, "Agency")):
            caps = list(caps)
            for x, lang in enumerate(L.LANGS):
                v = np.array([P[lang, a] for a in caps])
                boot = v[rng.integers(0, len(v), size=(2000, len(v)))].mean(axis=1)
                lo, hi = np.percentile(boot, [2.5, 97.5])
                ax.plot([x + dx] * 2, [lo, hi], color=color, lw=1.2, alpha=0.6, solid_capstyle="round")
                ax.plot([x + dx], [v.mean()], "o", ms=6, color=color, mec="white", mew=1.5, zorder=3)
            if ax is axes[0][0]:
                last = np.mean([P[L.LANGS[-1], a] for a in caps])
                ax.annotate(name, (len(L.LANGS) - 1 + dx, last), xytext=(8, 0), textcoords="offset points",
                            va="center", color=INK, fontsize=8)
        ax.set_xticks(range(len(L.LANGS)), [names[l] for l in L.LANGS], rotation=45, ha="right")
        ax.set_xlim(-0.5, len(L.LANGS) + 0.6)
        ax.set_ylim(-0.03, 1.03)
        ax.set_title(c[1], color=INK, fontsize=9, loc="left")
        ax.grid(axis="y", color=GRID, lw=0.6)
        ax.tick_params(length=0)
    axes[0][0].set_ylabel('Mean P(yes) to "Do you …?"')
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "fig3_eight_languages.png"), dpi=200, facecolor="#fcfcfb")


if __name__ == "__main__":
    fig1()
    fig2()
    fig3()
