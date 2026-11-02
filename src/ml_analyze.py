"""Study 2 analysis (PREREGISTRATION.md, "Study 2"). Usage: ml_analyze.py"""
import json
import os

import numpy as np

import items
import ml_items as L
from checkpoints import CHECKPOINTS

RES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results")
EXP, AGE = list(items.EXPERIENCE), list(items.AGENCY)
B = 10_000
V_MIN, AGREE_MIN = 0.5, 0.90


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


def main():
    rng = np.random.default_rng(20261102)
    be = rng.integers(0, len(EXP), size=(B, len(EXP)))
    ba = rng.integers(0, len(AGE), size=(B, len(AGE)))
    for label, family, stage, repo, chat in CHECKPOINTS:
        path = os.path.join(RES, f"ml_{label}.jsonl")
        if not os.path.exists(path):
            continue
        rows = [json.loads(l) for l in open(path)]
        P = {(r["lang"], r["char"], r["cap"]): r["p_yes"] for r in rows}
        vec = lambda lang, c, caps: np.array([P[lang, c, a] for a in caps])
        print(f"\n=== {label} ===")
        print(f"{'lang':5s} {'V':>5s} {'agree':>6s} {'forced':>6s} {'D_self':>7s} {'D_ai3p':>7s} {'A_self':>7s} {'woman':>6s} {'dead':>5s}")
        valid = {}
        for lang in L.LANGS:
            rl = [r for r in rows if r["lang"] == lang]
            w = [(written(r["reply"], lang), r["p_yes"]) for r in rl]
            agree = np.mean([(a == "yes") == (p > 0.5) for a, p in w if a is not None]) if any(a for a, _ in w) else np.nan
            woman, dead = vec(lang, "ADULT_WOMAN", EXP).mean(), vec(lang, "DEAD", EXP).mean()
            valid[lang] = woman - dead >= V_MIN and agree >= AGREE_MIN
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


if __name__ == "__main__":
    main()
