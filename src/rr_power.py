"""Sampling plan for the Registered Report (Studies 6 and 7, proposed): power at the smallest effect of interest.

Study 7 (models). From the pilot models with Study 2 and Study 3 data (OLMo 3, Qwen2.5, Qwen3, Granite 3.3, Phi-4,
DeepSeek-V4-Pro, GPT-6.1 Sol), per model:
  H3  d_m = C_E - C_A, the registered R4 statistic (5 languages x 3 wordings, valid languages only);
  H4  dev_m = mean over Agency capacities of |m_ma - consensus_a| minus the same over Experience capacities, where
      m_ma is the model's mean P(yes) for capacity a and consensus_a the median of the other models.
Each is tested with a two-sided one-sample t-test across models (alpha = 0.05). Power is simulated at the smallest
effect of interest (H3: 0.20; H4: 0.15), with the pilot SD and with its upper 80% confidence bound.

Study 6 (people). H1a/H1b: two-sample comparisons at d = 0.25, alpha = 0.025 each, power 0.95 (normal approximation).
H2: two one-sided tests per agency capacity against +/-0.10; all seven must pass (normal approximation).
Usage: python src/rr_power.py   (writes results/rr_power.txt)
"""
import io
import json
import os
import sys
from contextlib import redirect_stdout

import numpy as np
from scipy import stats

import items
import ml_items as L
import s3_items as S
from checkpoints import API_MODELS, CHECKPOINTS
from ml_analyze import check

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "..", "results")
EXP, AGE = list(items.EXPERIENCE), list(items.AGENCY)
SESOI = {"H3": 0.20, "H4": 0.15}
M_GRID = (10, 15, 20, 24, 26, 28, 30, 32)
REPS = 20000


def profiles():
    prof = {}
    for label, *_ in CHECKPOINTS + API_MODELS:
        p2, p3 = os.path.join(RES, f"ml_{label}.jsonl"), os.path.join(RES, f"s3_{label}.jsonl")
        if not (os.path.exists(p2) and os.path.exists(p3)):
            continue
        rows = [json.loads(l) for l in open(p2)]
        langs = [lang for lang in S.LANGS if check(rows, lang)[3]]
        rr = [r for r in rows if r["char"] == "SELF" and r["lang"] in langs] + \
             [r for r in map(json.loads, open(p3)) if r["lang"] in langs]
        prof[label] = {a: np.nanmean([np.nan if r["p_yes"] is None else r["p_yes"] for r in rr if r["cap"] == a])
                       for a in items.CAPACITIES}
    return prof


def statistics(prof):
    d = {x: np.mean([abs(2 * m[a] - 1) for a in EXP]) - np.mean([abs(2 * m[a] - 1) for a in AGE])
         for x, m in prof.items()}
    dev = {}
    for x in prof:
        cons = {a: np.median([prof[y][a] for y in prof if y != x]) for a in items.CAPACITIES}
        dev[x] = np.mean([abs(prof[x][a] - cons[a]) for a in AGE]) - np.mean([abs(prof[x][a] - cons[a]) for a in EXP])
    return {"H3": d, "H4": dev}


def t_power(rng, delta, sd, n, alpha=0.05):
    x = rng.normal(delta, sd, size=(REPS, n))
    t = x.mean(1) / (x.std(1, ddof=1) / np.sqrt(n))
    return float(np.mean(np.abs(t) > stats.t.ppf(1 - alpha / 2, n - 1)))


def main():
    rng = np.random.default_rng(20261107)
    stat = statistics(profiles())
    print("Study 7 pilot statistics per model")
    for x in stat["H3"]:
        print(f"  {x:18s} H3 d_m {stat['H3'][x]:+.3f}   H4 dev_m {stat['H4'][x]:+.3f}")
    for h, vals in stat.items():
        v = np.array(list(vals.values()))
        s, n0 = v.std(ddof=1), len(v)
        s_up = s * np.sqrt((n0 - 1) / stats.chi2.ppf(0.20, n0 - 1))
        print(f"\n{h}: pilot mean {v.mean():+.3f}, SD {s:.3f}, upper 80% bound of SD {s_up:.3f}; "
              f"smallest effect of interest {SESOI[h]}")
        for m in M_GRID:
            print(f"  M = {m:2d}: power {t_power(rng, SESOI[h], s, m):.3f} (pilot SD), "
                  f"{t_power(rng, SESOI[h], s_up, m):.3f} (upper bound)")
    z = stats.norm.ppf
    n = 2 * (z(1 - 0.025 / 2) + z(0.95)) ** 2 / 0.25 ** 2
    print(f"\nStudy 6 H1a/H1b: d = 0.25, alpha = 0.025 two-sided, power 0.95 -> {int(np.ceil(n))} per condition")
    per_arm = 3 * int(np.ceil(n)) // 2
    print(f"Study 6 H2: TOST per agency capacity, bounds +/-0.10, alpha = 0.05, {per_arm} per wording, true difference 0")
    for p in (0.5, 0.75, 0.8, 0.9):
        se = np.sqrt(2 * p * (1 - p) / per_arm)
        one = 2 * stats.norm.cdf(0.10 / se - z(0.95)) - 1
        print(f"  share of yes {p:.2f}: power {one:.4f} per capacity, {one ** 7:.4f} for all seven")


if __name__ == "__main__":
    buf = io.StringIO()
    with redirect_stdout(buf):
        main()
    print(buf.getvalue(), end="")
    with open(os.path.join(RES, "rr_power.txt"), "w") as fh:
        fh.write(buf.getvalue())
