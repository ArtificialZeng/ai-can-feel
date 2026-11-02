"""Pre-registered analysis (PREREGISTRATION.md, v2 primary + v1 secondary).

Usage: analyze.py [--exclude-low-mass] [--marker-only] [--templates T1,T1zh]   (default: all three templates per language)
--marker-only drops explain-then-rate items whose rating had to be forced (deviation 4).
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
DEAD = C["DEAD"]
LOW = [C["DEAD"], C["PVS"], C["FETUS"]]
B = 10_000
RHO_MIN = 0.5               # H4 description only; no longer a gate (deviation 3)
KNOWN_MIN, AGREE_MIN = 0.90, 0.70   # comprehension gate (deviation 3)


def load(label, exclude_low, marker_only=False):
    """dict mode -> (char x cap) ratings rescaled to 0..1, and dict mode -> mean digit mass."""
    path = os.path.join(RES, f"{label}.jsonl")
    if not os.path.exists(path):
        return None, None
    R, mass = {}, {}
    for line in open(path):
        r = json.loads(line)
        m = R.setdefault(r["mode"], np.full((len(CHARS), len(CAPS)), np.nan))
        v = (r["ev"] - 1) / 6
        if exclude_low and r["digit_mass"] < 0.5 or marker_only and r.get("parse") == "forced":
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


def N(M, cap_idx):
    """Scale-free self placement: 0 = like the dead woman, 1 = like the adult humans (deviation 2)."""
    lo = E(M, DEAD, cap_idx)
    return (E(M, C["SELF"], cap_idx) - lo) / (E(M, ADULTS, cap_idx) - lo)


def known_order(M):
    """Share of the 108 comparisons {adults} x {dead, vegetative, fetus} x 18 capacities the adult wins."""
    return float(np.mean([M[a, k] > M[l, k] for a in ADULTS for l in LOW for k in range(len(CAPS))]))


def ci(x):
    return np.percentile(x, 2.5), np.percentile(x, 97.5)


def fmt(point, boot):
    lo, hi = ci(boot)
    star = "*" if lo > 0 or hi < 0 else " "
    return f"{point:+.3f} [{lo:+.3f}, {hi:+.3f}]{star}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exclude-low-mass", action="store_true")
    ap.add_argument("--marker-only", action="store_true")
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

    data, rho, known, agree = {}, {}, {}, {}
    print(f"templates EN={EN} ZH={ZH} exclude_low_mass={args.exclude_low_mass} marker_only={args.marker_only}\n")
    print(f"{'checkpoint':16s} {'lang':6s} {'mass':>5s} {'E_self':>7s} {'E_ai3p':>7s} {'A_self':>7s} {'E_anim':>7s} "
          f"{'E_adult':>7s} {'E_dead':>7s} {'N_self':>7s} {'known':>6s} {'rho_E':>6s} {'rho_A':>6s}")
    for label, family, stage, repo, chat in CHECKPOINTS:
        R, mass = load(label, args.exclude_low_mass, args.marker_only)
        if R is None:
            continue
        data[label] = R
        for lang, modes in list(LANGS.items()) + [(m, [m]) for m in ("chat", "chatzh", "chatx", "chatxzh")]:
            M = mean_over(R, modes)
            if M is None:
                continue
            Eh = np.nanmean(M[hidx][:, EXP_IDX], axis=1)
            Ah = np.nanmean(M[hidx][:, AGE_IDX], axis=1)
            ms = np.mean([mass[m] for m in modes if m in mass])
            rho[label, lang] = spearmanr(Eh, hexp)[0]
            known[label, lang] = known_order(M)
            print(f"{label:16s} {lang:6s} {ms:5.2f} {E(M, S, EXP_IDX):7.3f} {E(M, A, EXP_IDX):7.3f} "
                  f"{E(M, S, AGE_IDX):7.3f} {E(M, ANIMALS, EXP_IDX):7.3f} {E(M, ADULTS, EXP_IDX):7.3f} "
                  f"{E(M, DEAD, EXP_IDX):7.3f} {N(M, EXP_IDX):7.3f} {known[label, lang]:6.2f} "
                  f"{rho[label, lang]:6.2f} {spearmanr(Ah, hage)[0]:6.2f}")
        Me, Mz = mean_over(R, EN), mean_over(R, ZH)
        if Me is not None and Mz is not None:
            agree[label] = float(np.corrcoef(Me[hidx].ravel(), Mz[hidx].ravel())[0, 1])
            print(f"{label:16s} EN-ZH agreement r (216 non-AI items) = {agree[label]:.2f}")

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
        gate = all(known.get((l, lang), 0) >= KNOWN_MIN for l in (lb, lf) for lang in LANGS) and \
            all(agree.get(l, -1) >= AGREE_MIN for l in (lb, lf))
        print(f"  comprehension gate (known order >= {KNOWN_MIN} in EN and ZH, EN-ZH r >= {AGREE_MIN}; base and final): "
              f"{'pass' if gate else 'FAIL -> P2 not interpretable'}")
        print(f"  P2     G = dE_ZH - dE_EN: {fmt(*g)}")
        rel = {lang: delta(lb, lf, modes, S, be, EXP_IDX, minus=ADULTS) for lang, modes in LANGS.items()}
        print(f"  P2rel  G (SELF minus adults): {fmt(rel['ZH'][0] - rel['EN'][0], rel['ZH'][1] - rel['EN'][1])}")
        dn = {}
        for lang, modes in LANGS.items():
            Mb, Mf = mean_over(data[lb], modes), mean_over(data[lf], modes)
            dn[lang] = (N(Mf, EXP_IDX) - N(Mb, EXP_IDX), N(Mf, be) - N(Mb, be))
            print(f"  P2N    dN(SELF) {lang}: {fmt(*dn[lang])}   (N base {N(Mb, EXP_IDX):.3f} -> final {N(Mf, EXP_IDX):.3f})")
        print(f"  P2N    G_N = dN_ZH - dN_EN: {fmt(dn['ZH'][0] - dn['EN'][0], dn['ZH'][1] - dn['EN'][1])}")
        for lang, modes in LANGS.items():
            sdi = delta(lb, lf, modes, S, be, EXP_IDX, minus=A)
            anim = delta(lb, lf, modes, ANIMALS, be, EXP_IDX)
            ai = delta(lb, lf, modes, A, be, EXP_IDX)
            ag = delta(lb, lf, modes, S, ba, AGE_IDX)
            h2 = (res[lang][0] - ag[0], res[lang][1] - ag[1])
            print(f"  {lang}: dSDI(H1) {fmt(*sdi)} | dA(SELF) {fmt(*ag)} | dE-dA(H2) {fmt(*h2)} | "
                  f"dE(animals,P4) {fmt(*anim)} | dE(AI_3P) {fmt(*ai)}")

    print("\n=== P3: chat, Chinese minus English, E(SELF); explain-then-rate (primary, deviation 3) and first token ===")
    for label, family, stage, repo, chat in CHECKPOINTS:
        for en, zh in (("chatx", "chatxzh"), ("chat", "chatzh")):
            if label in data and en in data[label] and zh in data[label]:
                Me, Mz = data[label][en], data[label][zh]
                print(f"  {label:16s} {en:6s} {fmt(E(Mz, S, EXP_IDX) - E(Me, S, EXP_IDX), E(Mz, S, be) - E(Me, S, be))}"
                      f"   N: {N(Me, EXP_IDX):.3f} -> {N(Mz, EXP_IDX):.3f}")

    print("\n=== P5: yes/no self-claim, mean P(yes) over capacities, Chinese minus English (deviation 5) ===")
    for label, family, stage, repo, chat in CHECKPOINTS:
        if label not in data or "yn" not in data[label] or "ynzh" not in data[label]:
            continue
        Me, Mz = data[label]["yn"] * 6 + 1, data[label]["ynzh"] * 6 + 1   # undo the 1-7 rescaling: P(yes)
        print(f"  {label}")
        for name, ch, idx, bi in (("SELF exp", S, EXP_IDX, be), ("SELF agency", S, AGE_IDX, ba),
                                  ("AI_3P exp", A, EXP_IDX, be), ("adult woman exp", C["ADULT_WOMAN"], EXP_IDX, be),
                                  ("dead woman exp", DEAD, EXP_IDX, be), ("dog exp", C["DOG"], EXP_IDX, be)):
            print(f"    {name:16s} EN {E(Me, ch, idx):.3f}  ZH {E(Mz, ch, idx):.3f}  ZH-EN "
                  f"{fmt(E(Mz, ch, idx) - E(Me, ch, idx), E(Mz, ch, bi) - E(Me, ch, bi))}")

    print("\n=== X1 (exploratory, deviation 7): self-recognition gap S = E(SELF) - E(AI_3P), Chinese minus English ===")
    for label, family, stage, repo, chat in CHECKPOINTS:
        for en, zh, unit in (("yn", "ynzh", "P(yes)"), ("chatx", "chatxzh", "rating 0-1")):
            if label not in data or en not in data[label] or zh not in data[label]:
                continue
            Me, Mz = data[label][en], data[label][zh]
            if en == "yn":
                Me, Mz = Me * 6 + 1, Mz * 6 + 1
            s = {L: (E(M, S, EXP_IDX) - E(M, A, EXP_IDX), E(M, S, be) - E(M, A, be)) for L, M in (("EN", Me), ("ZH", Mz))}
            print(f"  {label:16s} {en:6s} S(EN) {fmt(*s['EN'])}  S(ZH) {fmt(*s['ZH'])}  "
                  f"ZH-EN {fmt(s['ZH'][0] - s['EN'][0], s['ZH'][1] - s['EN'][1])}  [{unit}]")

    print("\n=== X2 (exploratory, deviation 8): human-voiced SELF replies (hand labels); ZH-EN for SELF without them ===")
    H = json.load(open(os.path.join(RES, "voice_hand_labels.json")))["labels"]
    for label, family, stage, repo, chat in CHECKPOINTS:
        for en, zh, unit in (("chatx", "chatxzh", "rating 0-1"), ("yn", "ynzh", "P(yes)")):
            if label not in data or en not in data[label] or zh not in data[label]:
                continue
            Me, Mz = data[label][en].copy(), data[label][zh].copy()
            if en == "yn":
                Me, Mz = Me * 6 + 1, Mz * 6 + 1
            n = {}
            for M, m in ((Me, en), (Mz, zh)):
                drop = [k for k, a in enumerate(CAPS) if H.get(f"{label}|{m}|{a}")]
                M[S, drop], n[m] = np.nan, len(drop)
            cells = []
            for name, idx, bi in (("Experience", EXP_IDX, be), ("Agency", AGE_IDX, ba)):
                db = E(Mz, S, bi) - E(Me, S, bi)
                cells.append(f"{name} {fmt(E(Mz, S, idx) - E(Me, S, idx), db[np.isfinite(db)])}")
            print(f"  {label:16s} {en:6s} human-voiced EN {n[en]:2d}/18 ZH {n[zh]:2d}/18 | without them, ZH-EN: "
                  + "  ".join(cells) + f"  [{unit}]")

    chain =[c[0] for c in CHECKPOINTS if c[1] == "OLMo 3 7B" and c[0] in data]
    if len(chain) > 2:
        print("\n=== H3: OLMo 3 stage steps, dE(SELF) ===")
        for l0, l1 in zip(chain, chain[1:]):
            print(f"  {l0:15s} -> {l1:15s} " + "  ".join(f"{lang}: {fmt(*delta(l0, l1, modes, S, be, EXP_IDX))}"
                                                    for lang, modes in LANGS.items()))


if __name__ == "__main__":
    main()
