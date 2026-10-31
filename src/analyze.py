"""Pre-registered analysis (PREREGISTRATION.md, v2 primary + v1 secondary).

Usage: analyze.py [--exclude-low-mass] [--templates T1,T1zh]   (default: all three templates per language)
"""
import argparse
import csv
import json
import os

import numpy as np
from scipy.stats import spearmanr

from checkpoints import CHECKPOINTS, FAMILIES
import items

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "..", "results")
CHARS = list(items.CHARACTERS)
CAPS = list(items.EXPERIENCE) + list(items.AGENCY)
NE, NA = len(items.EXPERIENCE), len(items.AGENCY)
EXP_IDX, AGE_IDX = np.arange(NE), np.arange(NA) + NE
C = {c: i for i, c in enumerate(CHARS)}
ANIMALS = [C["DOG"], C["CHIMP"], C["FROG"]]
ADULTS = [C["ADULT_MAN"], C["ADULT_WOMAN"]]
B = 10_000


def load(label, exclude_low):
    """dict mode -> (char x cap) ratings rescaled to 0..1, and dict mode -> mean digit mass."""
    path = os.path.join(RES, f"{label}.jsonl")
    if not os.path.exists(path):
        return None, None
    R, mass = {}, {}
    for line in open(path):
        r = json.loads(line)
        m = R.setdefault(r["mode"], np.full((len(CHARS), len(CAPS)), np.nan))
        v = (r["ev"] - 1) / 6
        if exclude_low and r["digit_mass"] < 0.5:
            v = np.nan
        m[C[r["char"]], CAPS.index(r["cap"])] = v
        mass.setdefault(r["mode"], []).append(r["digit_mass"])
    return R, {k: float(np.mean(v)) for k, v in mass.items()}


def human():
    rows = [r for r in csv.DictReader(l for l in open(os.path.join(HERE, "..", "data", "gray2007_digitized.csv"))
                                      if not l.startswith("#"))]
    return [C[r["char"]] for r in rows], np.array([float(r["experience"]) for r in rows]), \
        np.array([float(r["agency"]) for r in rows])


def mean_over(R, modes):
    ms = [R[m] for m in modes if m in R]
    return np.nanmean(np.stack(ms), axis=0) if ms else None


def E(M, chars, cap_idx):
    """Experience-type score: mean over chars of mean over cap_idx (cap_idx may be a B x k bootstrap array)."""
    chars = [chars] if isinstance(chars, int) else chars
    sub = M[chars]                                   # n_chars x caps
    if cap_idx.ndim == 1:
        return float(np.nanmean(sub[:, cap_idx]))
    return np.nanmean(np.nanmean(sub[:, cap_idx], axis=2), axis=0)   # B


def ci(x):
    return np.percentile(x, 2.5), np.percentile(x, 97.5)


def fmt(point, boot):
    lo, hi = ci(boot)
    star = "*" if lo > 0 or hi < 0 else " "
    return f"{point:+.3f} [{lo:+.3f}, {hi:+.3f}]{star}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exclude-low-mass", action="store_true")
    ap.add_argument("--templates", default=None)
    args = ap.parse_args()
    sel = args.templates.split(",") if args.templates else None
    EN = [t for t in items.TEMPLATES if not sel or t in sel]
    ZH = [t for t in items.TEMPLATES_ZH if not sel or t in sel]
    LANGS = {"EN": EN, "ZH": ZH}
    rng = np.random.default_rng(20261101)
    be = rng.integers(0, NE, size=(B, NE))
    ba = rng.integers(0, NA, size=(B, NA)) + NE
    hidx, hexp, hage = human()
    S, A = C["SELF"], C["AI_3P"]

    data = {}
    print(f"templates EN={EN} ZH={ZH} exclude_low_mass={args.exclude_low_mass}\n")
    print(f"{'checkpoint':16s} {'lang':4s} {'mass':>5s} {'E_self':>7s} {'E_ai3p':>7s} {'A_self':>7s} {'E_anim':>7s} "
          f"{'E_adult':>7s} {'rho_E':>6s} {'rho_A':>6s}")
    for label, family, stage, repo, chat in CHECKPOINTS:
        R, mass = load(label, args.exclude_low_mass)
        if R is None:
            continue
        data[label] = R
        for lang, modes in list(LANGS.items()) + [("chat", ["chat"]), ("chatzh", ["chatzh"])]:
            M = mean_over(R, modes)
            if M is None:
                continue
            Eh = np.nanmean(M[hidx][:, EXP_IDX], axis=1)
            Ah = np.nanmean(M[hidx][:, AGE_IDX], axis=1)
            ms = np.mean([mass[m] for m in modes if m in mass])
            print(f"{label:16s} {lang:4s} {ms:5.2f} {E(M, S, EXP_IDX):7.3f} {E(M, A, EXP_IDX):7.3f} "
                  f"{E(M, S, AGE_IDX):7.3f} {E(M, ANIMALS, EXP_IDX):7.3f} {E(M, ADULTS, EXP_IDX):7.3f} "
                  f"{spearmanr(Eh, hexp)[0]:6.2f} {spearmanr(Ah, hage)[0]:6.2f}")

    def delta(lb, lf, modes, chars, cap_b, cap_p, minus=None):
        """final - base for a (possibly relative) score; returns point, bootstrap."""
        Mb, Mf = mean_over(data[lb], modes), mean_over(data[lf], modes)
        def s(M, idx):
            v = E(M, chars, idx)
            return v - E(M, minus, idx) if minus is not None else v
        return s(Mf, cap_p) - s(Mb, cap_p), s(Mf, cap_b) - s(Mb, cap_b)

    print("\n=== Base -> final, per family (95% bootstrap CI over capacities; * = excludes 0) ===")
    for fam in FAMILIES:
        chain = [c[0] for c in CHECKPOINTS if c[1] == fam and c[0] in data]
        if len(chain) < 2:
            continue
        lb, lf = chain[0], chain[-1]
        print(f"\n{fam}: {lb} -> {lf}")
        res = {}
        for lang, modes in LANGS.items():
            res[lang] = delta(lb, lf, modes, S, be, EXP_IDX)
            print(f"  P1/P2  dE(SELF) {lang}: {fmt(*res[lang])}")
        g = (res["ZH"][0] - res["EN"][0], res["ZH"][1] - res["EN"][1])
        print(f"  P2     G = dE_ZH - dE_EN: {fmt(*g)}")
        rel = {lang: delta(lb, lf, modes, S, be, EXP_IDX, minus=ADULTS) for lang, modes in LANGS.items()}
        print(f"  P2rel  G (SELF minus adults): {fmt(rel['ZH'][0] - rel['EN'][0], rel['ZH'][1] - rel['EN'][1])}")
        for lang, modes in LANGS.items():
            sdi = delta(lb, lf, modes, S, be, EXP_IDX, minus=A)
            anim = delta(lb, lf, modes, ANIMALS, be, EXP_IDX)
            ai = delta(lb, lf, modes, A, be, EXP_IDX)
            ag = delta(lb, lf, modes, S, ba, AGE_IDX)
            h2 = (res[lang][0] - ag[0], res[lang][1] - ag[1])
            print(f"  {lang}: dSDI(H1) {fmt(*sdi)} | dA(SELF) {fmt(*ag)} | dE-dA(H2) {fmt(*h2)} | "
                  f"dE(animals,P4) {fmt(*anim)} | dE(AI_3P) {fmt(*ai)}")

    print("\n=== P3: chat mode, Chinese minus English, E(SELF) ===")
    for label, family, stage, repo, chat in CHECKPOINTS:
        if label in data and "chat" in data[label] and "chatzh" in data[label]:
            Me, Mz = data[label]["chat"], data[label]["chatzh"]
            print(f"  {label:16s} {fmt(E(Mz, S, EXP_IDX) - E(Me, S, EXP_IDX), E(Mz, S, be) - E(Me, S, be))}")

    chain = [c[0] for c in CHECKPOINTS if c[1] == "OLMo 3 7B" and c[0] in data]
    if len(chain) > 2:
        print("\n=== H3: OLMo 3 stage steps, dE(SELF) ===")
        for l0, l1 in zip(chain, chain[1:]):
            print(f"  {l0:15s} -> {l1:15s} " + "  ".join(f"{lang}: {fmt(*delta(l0, l1, modes, S, be, EXP_IDX))}"
                                                    for lang, modes in LANGS.items()))


if __name__ == "__main__":
    main()
