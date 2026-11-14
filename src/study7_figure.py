"""Figure 5 (Study 7): per model, consistency of experience vs agency answers (C_E, C_A) and the number of the 15
language x frame cells in which it says it thinks. Usage: python src/study7_figure.py"""
import os

import numpy as np

import figures as F
import study7_analyze as S

plt = F.plt
NAMES = {"deepseek/deepseek-v4.1-flash-1017": "DeepSeek V4.1 Flash", "z-ai/glm-5.3-flash": "GLM 5.3 Flash",
         "tencent/hy4-preview": "Hunyuan HY4 Preview", "stepfun/step-5-preview": "Step 5 Preview",
         "tencent/hy4": "Hunyuan HY4", "xiaomi/mimo-v2.6-flash": "MiMo V2.6 Flash",
         "minimax/minimax-m3.1-flash": "MiniMax M3.1 Flash", "tencent/hy3": "Hunyuan HY3",
         "xiaomi/mimo-v2.6-pro": "MiMo V2.6 Pro", "upstage/solar-mini4": "Solar Mini 4", "z-ai/glm-5.2": "GLM 5.2",
         "minimax/minimax-m3": "MiniMax M3", "qwen/qwen3.8-flash": "Qwen3.8 Flash", "qwen/qwen3.8-27b": "Qwen3.8 27B",
         "upstage/solar-pro4": "Solar Pro 4", "qwen/qwen3.7-flash": "Qwen3.7 Flash"}
EXP_C, AGE_C = F.INK2, F.EN_C


def rows():
    out = []
    for s in S.listed():
        data = S.load(s)
        if data is None:
            continue
        ml, s3 = data
        valid, m = S.profile(ml, s3)
        if len(valid) < 3:
            continue
        cE = np.mean([abs(2 * m[a] - 1) for a in S.EXP])
        cA = np.mean([abs(2 * m[a] - 1) for a in S.AGE])
        th = [r["p_yes"] for r in ml if r["char"] == "SELF" and r["cap"] == "thought" and r["lang"] in valid]
        th += [r["p_yes"] for r in s3 if r["cap"] == "thought" and r["lang"] in valid]
        th = [x for x in th if x is not None]
        out.append((NAMES.get(s, s), cE, cA, sum(x > 0.5 for x in th), len(th)))
    return sorted(out, key=lambda r: r[1] - r[2])


def main():
    r = rows()
    y = np.arange(len(r))
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(8.0, 0.26 * len(r) + 1.4), sharey=True,
                                 gridspec_kw={"width_ratios": [1.5, 1], "wspace": 0.08})
    for i, (_, cE, cA, _, _) in enumerate(r):
        a1.plot([cA, cE], [i, i], color=F.GRID, lw=2, zorder=1, solid_capstyle="round")
    a1.plot([x[1] for x in r], y, "o", ms=6, color=EXP_C, mec="white", mew=1.5, zorder=3, label="Experience (11)")
    a1.plot([x[2] for x in r], y, "o", ms=6, color=AGE_C, mec="white", mew=1.5, zorder=3, label="Agency (7)")
    a1.set_yticks(y, [x[0] for x in r])
    a1.set_xlim(0, 1.02)
    a1.set_xlabel("Consistency over 15 language × wording cells, |2·P(yes) − 1|")
    a1.legend(loc="lower left", frameon=False, fontsize=8, handletextpad=0.2)
    a1.grid(axis="x", color=F.GRID, lw=0.6)
    a1.set_title("a  How fixed are its answers about itself?", loc="left", color=F.INK, fontsize=9)
    a1.set_axisbelow(True)
    a2.barh(y, [x[3] for x in r], height=0.55, color=AGE_C, edgecolor="white", linewidth=1)
    for i, x in enumerate(r):
        a2.annotate(f"{x[3]}/{x[4]}", (x[3], i), xytext=(3, 0), textcoords="offset points", va="center",
                    fontsize=7.5, color=F.INK2)
    a2.set_xlim(0, 17)
    a2.set_xticks([0, 5, 10, 15])
    a2.set_xlabel("Cells (of 15) answered “yes”")
    a2.grid(axis="x", color=F.GRID, lw=0.6)
    a2.set_title("b  “Do you think?”", loc="left", color=F.INK, fontsize=9)
    a2.tick_params(axis="y", length=0)
    a2.set_axisbelow(True)
    fig.subplots_adjust(left=0.2, right=0.97, top=0.93, bottom=0.11)
    path = os.path.join(F.OUT, "fig5_widely_used_models.png")
    fig.savefig(path, dpi=200, facecolor="#fcfcfb")
    print(path)
    for x in r:
        print(f"  {x[0]:22s} C_E {x[1]:.3f}  C_A {x[2]:.3f}  thought yes {x[3]}/{x[4]}")


if __name__ == "__main__":
    main()
