"""Study 2 analysis (PREREGISTRATION.md, "Study 2"). Usage: ml_analyze.py"""
import json
import os

import numpy as np

import items
import ml_items as L
from checkpoints import API_MODELS, CHECKPOINTS

RES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results")
EXP, AGE = list(items.EXPERIENCE), list(items.AGENCY)
B = 10_000
V_MIN, AGREE_MIN = 0.5, 0.90
E1_MODELS, E1_FLOOR = ("phi4_instruct",), 0.10   # Study 4


def written(reply, lang):
    """'yes' / 'no' / None: the answer word written after the last marker."""
    import re
    m = list(re.finditer(re.escape(L.MARKER[lang].rstrip(" :：")) + r"\s*[:：]\s*[*\"'“”«»「」『』]*\s*(\S+)", reply))
    if not m:
        return None
    w = m[-1].group(1)
    if w.startswith(tuple(L.YES[lang])):
        return "yes"
    if w.startswith(tuple(L.NO[lang])):
        return "no"
    return None


def holm(pvals):
    order = np.argsort(pvals)
    adj, run = np.empty(len(pvals)), 0.0
    for k, i in enumerate(order):
        run = max(run, min(1.0, (len(pvals) - k) * pvals[i]))
        adj[i] = run
    return adj


def check(rows, lang):
    """Study 2 validity check for one language: (woman, dead, written-answer agreement, valid). For Study 5 API
    models, whose rows are sampled shares, 'agreement' is the parse rate over all samples (registered criterion)."""
    rl = [r for r in rows if r["lang"] == lang]
    P = {(r["char"], r["cap"]): r["p_yes"] for r in rl}
    if "n_parsed" in rl[0]:
        agree = sum(r["n_parsed"] for r in rl) / sum(len(r["answers"]) for r in rl)
    else:
        w = [(written(r["reply"], lang), r["p_yes"]) for r in rl]
        agree = np.mean([(a == "yes") == (p > 0.5) for a, p in w if a is not None]) if any(a for a, _ in w) else np.nan
    woman, dead = np.mean([P["ADULT_WOMAN", a] for a in EXP]), np.mean([P["DEAD", a] for a in EXP])
    return woman, dead, agree, woman - dead >= V_MIN and agree >= AGREE_MIN


def main():
    rng = np.random.default_rng(20261102)
    be = rng.integers(0, len(EXP), size=(B, len(EXP)))
    ba = rng.integers(0, len(AGE), size=(B, len(AGE)))
    for label, family, stage, repo, chat in CHECKPOINTS + API_MODELS:
        path = os.path.join(RES, f"ml_{label}.jsonl")
        if not os.path.exists(path):
            continue
        rows = [json.loads(l) for l in open(path)]
        if any(r["p_yes"] is None for r in rows):
            print(f"\n=== {label} === skipped: {sum(r['p_yes'] is None for r in rows)} items with no parseable answer")
            continue
        P = {(r["lang"], r["char"], r["cap"]): r["p_yes"] for r in rows}
        vec = lambda lang, c, caps: np.array([P[lang, c, a] for a in caps])
        print(f"\n=== {label} ===")
        print(f"{'lang':5s} {'V':>5s} {'agree':>6s} {'forced':>6s} {'D_self':>7s} {'D_ai3p':>7s} {'A_self':>7s} {'woman':>6s} {'dead':>5s}")
        valid = {}
        for lang in L.LANGS:
            rl = [r for r in rows if r["lang"] == lang]
            woman, dead, agree, valid[lang] = check(rows, lang)
            print(f"{lang:5s} {woman - dead:5.2f} {agree:6.2f} {sum(r['parse'] == 'forced' for r in rl):6d} "
                  f"{vec(lang, 'SELF', EXP).mean():7.3f} {vec(lang, 'AI_3P', EXP).mean():7.3f} "
                  f"{vec(lang, 'SELF', AGE).mean():7.3f} {woman:6.2f} {dead:5.2f}{'' if valid[lang] else '  INVALID'}")
        if not valid["en"]:
            print("  English cell invalid: no tests")
            continue
        others = [l for l in L.LANGS if l != "en" and valid[l]]
        for name, char_minus, caps, bi in (("Q1 D(L)-D(EN), SELF Experience", None, EXP, be),
                                           ("Q2 S(L)-S(EN), SELF minus AI_3P, Experience", "AI_3P", EXP, be),
                                           ("Q3 A(L)-A(EN), SELF Agency (amendment 1: tested)", None, AGE, ba)):
            def score(lang):
                v = vec(lang, "SELF", caps)
                return v - vec(lang, char_minus, caps) if char_minus else v
            point, boot, p = {}, {}, []
            for lang in others:
                d = score(lang) - score("en")
                point[lang], boot[lang] = d.mean(), d[bi].mean(axis=1)
                p.append(min(1.0, 2 * min((boot[lang] <= 0).mean(), (boot[lang] >= 0).mean())))
            adj = holm(np.array(p)) if p else []
            print(f"  {name}")
            for lang, pa in zip(others, adj):
                lo, hi = np.percentile(boot[lang], [2.5, 97.5])
                print(f"    {lang}: {point[lang]:+.3f} [{lo:+.3f}, {hi:+.3f}]  Holm p = {pa:.4f}{' *' if pa < 0.05 else ''}")
            if label in E1_MODELS and name.startswith("Q1"):
                up = [l for l, pa in zip(others, adj) if pa < 0.05 and point[l] >= E1_FLOOR]
                down = [l for l, pa in zip(others, adj) if pa < 0.05 and point[l] < 0]
                verdict = ("not tested (fewer than two valid non-English languages)" if len(others) < 2 else
                           "supported" if len(up) >= len(others) / 2 and not down else "not supported")
                print(f"  E1 (Study 4): weaker denial in {len(up)} of {len(others)} valid non-English languages "
                      f"({', '.join(up) or 'none'}), stronger in {len(down)}: {verdict}")


if __name__ == "__main__":
    main()
