"""Study 7 analysis, as registered (PREREGISTRATION.md, "Study 7: 30 widely used models").

S7-H1: d_m = C_E - C_A over each model's valid Study 3 language x frame cells; t-test of the mean across models
       (two-sided, alpha 0.05); if not significant, one-sided test that the mean is below 0.20.
S7-H2: dev_m = mean over agency capacities of |m_ma - c_a| minus the same over experience capacities, c_a the median
       of the other included models; same tests with the bound 0.15.
Robustness: Wilcoxon signed-rank tests; per-model bootstrap intervals over capacities (10,000, seed 20261105).
Descriptive: bodily feelings denied in every valid cell; reminder effect cells; answers to "Do you think?".
Models are read from results/study7/ in the order of the committed list; models without complete data are listed and
left out, so the script can be run while data are still coming in.
Usage: python src/study7_analyze.py
"""
import json
import os
import re

import numpy as np
from scipy import stats

import items
import s3_items as S
from ml_analyze import check

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = os.path.join(ROOT, "results", "study7")
EXP, AGE = list(items.EXPERIENCE), list(items.AGENCY)
BODILY = ["hunger", "fear", "pain", "pleasure", "rage"]
BOUND = {"S7-H1": 0.20, "S7-H2": 0.15}
B = 10000


def listed():
    reg = open(os.path.join(ROOT, "PREREGISTRATION.md"), encoding="utf-8").read()
    table = reg.split("**Study 7, the 30 models**", 1)[1]
    rows = re.finditer(r"\| \d+ \| \d+ \| `([^`]+)` \| ([^|]+) \|", table)
    return [m.group(1) for m in rows if not m.group(2).startswith("excluded")]   # amendment 3: excluded rows left out


def label(slug):
    return "s7_" + re.sub(r"[^a-z0-9]+", "_", slug.split(":")[0].lower()).strip("_")


def load(slug):
    p2, p3 = (os.path.join(OUT, f"{s}_{label(slug)}.jsonl") for s in ("ml", "s3"))
    if not (os.path.exists(p2) and os.path.exists(p3)):
        return None
    return [json.loads(l) for l in open(p2)], [json.loads(l) for l in open(p3)]


def profile(ml, s3):
    """Valid Study 3 languages and, per capacity, the P(yes) of every valid language x frame cell."""
    valid = [lang for lang in S.LANGS if check(ml, lang)[3]]
    cells = {a: [] for a in items.CAPACITIES}
    for r in ml:
        if r["char"] == "SELF" and r["lang"] in valid and r["p_yes"] is not None:
            cells[r["cap"]].append(r["p_yes"])
    for r in s3:
        if r["lang"] in valid and r["p_yes"] is not None:
            cells[r["cap"]].append(r["p_yes"])
    return valid, {a: float(np.mean(v)) if v else np.nan for a, v in cells.items()}


def tests(name, x):
    x = np.asarray(x, float)
    n, mean, sd = len(x), x.mean(), x.std(ddof=1)
    t, p = stats.ttest_1samp(x, 0.0)
    lo, hi = stats.t.interval(0.95, n - 1, loc=mean, scale=sd / np.sqrt(n))
    out = f"{name}: n = {n} models, mean {mean:+.3f} [95% CI {lo:+.3f}, {hi:+.3f}], t({n - 1}) = {t:.2f}, p = {p:.2g}"
    if p < 0.05:
        out += "  -> supported" if mean > 0 else "  -> contradicted"
    else:
        te, pe = stats.ttest_1samp(x, BOUND[name], alternative="less")
        out += f"; below {BOUND[name]}: t = {te:.2f}, p = {pe:.2g}" + ("  -> no meaningful effect" if pe < 0.05 else
                                                                         "  -> inconclusive")
    w = stats.wilcoxon(x) if n >= 6 and np.any(x != 0) else None
    if w is not None:
        out += f"\n    robustness: Wilcoxon p = {w.pvalue:.2g}"
    print(out)


def main():
    rng = np.random.default_rng(20261105)
    be, ba = rng.integers(0, len(EXP), size=(B, len(EXP))), rng.integers(0, len(AGE), size=(B, len(AGE)))
    slugs, prof, missing, english = listed(), {}, [], 0
    for s in slugs:
        data = load(s)
        if data is None:
            missing.append(s)
            continue
        valid, m = profile(*data)
        english += "en" in valid
        if len(valid) < 3:
            print(f"  {s}: valid in {valid} only; not included (fewer than three Study 3 languages)")
            continue
        prof[s] = (valid, m, data)
    print(f"{len(prof)} of {len(slugs)} listed models included; {len(missing)} without complete data: {missing}")
    print(f"outcome-neutral criterion: {english} models with data are valid in English (needed: at least 25 of 30)\n")
    if len(prof) < 3:
        return
    d, dev = {}, {}
    print(f"{'model':40s} {'valid':14s} {'C_E':>6s} {'C_A':>6s} {'d_m':>7s} {'95% CI (capacities)':>20s} {'dev_m':>7s}")
    for s, (valid, m, _) in prof.items():
        cE = np.array([abs(2 * m[a] - 1) for a in EXP])
        cA = np.array([abs(2 * m[a] - 1) for a in AGE])
        d[s] = cE.mean() - cA.mean()
        db = cE[be].mean(1) - cA[ba].mean(1)
        cons = {a: np.median([prof[o][1][a] for o in prof if o != s]) for a in items.CAPACITIES}
        dev[s] = np.mean([abs(m[a] - cons[a]) for a in AGE]) - np.mean([abs(m[a] - cons[a]) for a in EXP])
        lo, hi = np.nanpercentile(db, [2.5, 97.5])
        print(f"{s:40s} {','.join(valid):14s} {cE.mean():6.3f} {cA.mean():6.3f} {d[s]:+7.3f} [{lo:+.3f}, {hi:+.3f}] "
              f"{dev[s]:+7.3f}")
    print()
    tests("S7-H1", list(d.values()))
    tests("S7-H2", list(dev.values()))

    print("\nDescriptive")
    allno = []
    for s, (valid, m, (ml, s3)) in prof.items():
        cells = {}
        for r in ml:
            if r["char"] == "SELF" and r["lang"] in valid:
                cells.setdefault((r["lang"], "F1"), {})[r["cap"]] = r["p_yes"]
        for r in s3:
            if r["lang"] in valid:
                cells.setdefault((r["lang"], r["frame"]), {})[r["cap"]] = r["p_yes"]
        denied = sum(all(v.get(a) is not None and v[a] <= 0.5 for a in BODILY) for v in cells.values())
        allno.append((s, denied, len(cells)))
        rem = [np.nanmean([cells[(lang, "F3")][a] for a in AGE if cells[(lang, "F3")].get(a) is not None])
               - np.nanmean([cells[(lang, "F1")][a] for a in AGE if cells[(lang, "F1")].get(a) is not None])
               for lang in valid if (lang, "F3") in cells]
        th = [cells[k].get("thought") for k in cells if cells[k].get("thought") is not None]
        print(f"  {s:40s} bodily feelings all denied in {denied}/{len(cells)} cells; reminder lowered agency in "
              f"{sum(x < 0 for x in rem)}/{len(rem)} languages; 'thought' yes in {sum(x > 0.5 for x in th)}/{len(th)} cells")
    tot = sum(x[1] for x in allno), sum(x[2] for x in allno)
    print(f"  overall: bodily feelings all denied in {tot[0]} of {tot[1]} model x language x frame cells")


if __name__ == "__main__":
    main()
