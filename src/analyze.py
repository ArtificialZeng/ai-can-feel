"""Pre-registered analysis (PREREGISTRATION.md). Usage: analyze.py [--exclude-low-mass] [--mode T1|T2|T3|chat]"""
import argparse
import json
import os

import numpy as np

from checkpoints import CHECKPOINTS, FAMILIES
import items

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "..", "results")
CHARS = list(items.CHARACTERS)
EXP = list(items.EXPERIENCE)
AGE = list(items.AGENCY)
B = 10_000


def load(label, modes, exclude_low):
    path = os.path.join(RES, f"{label}.jsonl")
    if not os.path.exists(path):
        return None
    rows = [json.loads(l) for l in open(path)]
    rows = [r for r in rows if r["mode"] in modes]
    if not rows:
        return None
    # R[mode, char, cap] in 0..1, NaN where excluded
    caps = EXP + AGE
    R = np.full((len(modes), len(CHARS), len(caps)), np.nan)
    low = 0
    for r in rows:
        v = (r["ev"] - 1) / 6
        if r["digit_mass"] < 0.5:
            low += 1
            if exclude_low:
                v = np.nan
        R[modes.index(r["mode"]), CHARS.index(r["char"]), caps.index(r["cap"])] = v
    return R, low, len(rows)


def dims(R, exp_idx, age_idx):
    """Experience and Agency per character, averaged over modes and the given capacity indices."""
    M = np.nanmean(R, axis=0)                      # char x cap
    return np.nanmean(M[:, exp_idx], axis=1), np.nanmean(M[:, age_idx], axis=1)


def boot_idx(rng):
    e = rng.integers(0, len(EXP), size=(B, len(EXP)))
    a = rng.integers(0, len(AGE), size=(B, len(AGE))) + len(EXP)
    return e, a


def ci(x):
    return np.percentile(x, 2.5), np.percentile(x, 97.5)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exclude-low-mass", action="store_true")
    ap.add_argument("--mode", default=None)
    args = ap.parse_args()
    modes = [args.mode] if args.mode else items.TEMPLATES
    S, A = CHARS.index("SELF"), CHARS.index("AI_3P")
    exp_idx, age_idx = np.arange(len(EXP)), np.arange(len(AGE)) + len(EXP)
    rng = np.random.default_rng(20261101)
    be, ba = boot_idx(rng)

    data = {}
    print(f"modes={modes} exclude_low_mass={args.exclude_low_mass}\n")
    print(f"{'checkpoint':16s} {'lowmass':>8s} {'E(SELF)':>8s} {'E(AI3P)':>8s} {'SDI':>7s} {'A(SELF)':>8s} {'A(AI3P)':>8s}")
    for label, family, stage, repo, chat in CHECKPOINTS:
        got = load(label, modes, args.exclude_low_mass)
        if got is None:
            continue
        R, low, n = got
        E, Ag = dims(R, exp_idx, age_idx)
        data[label] = R
        print(f"{label:16s} {low:4d}/{n:<4d} {E[S]:8.3f} {E[A]:8.3f} {E[S]-E[A]:+7.3f} {Ag[S]:8.3f} {Ag[A]:8.3f}")

    def stat_boot(R, which):
        M = np.nanmean(R, axis=0)
        Es = np.nanmean(M[S][be], axis=1); Ea = np.nanmean(M[A][be], axis=1)
        As = np.nanmean(M[S][ba], axis=1)
        return {"E_self": Es, "SDI": Es - Ea, "A_self": As}[which]

    print("\nBase -> final differences, 95% bootstrap CI over capacities")
    for fam in FAMILIES:
        chain = [c for c in CHECKPOINTS if c[1] == fam and c[0] in data]
        if len(chain) < 2 or chain[0][2] != "base":
            continue
        b, f = data[chain[0][0]], data[chain[-1][0]]
        out = []
        for which in ["SDI", "E_self", "A_self"]:
            d = stat_boot(f, which) - stat_boot(b, which)
            Mb, Mf = np.nanmean(b, axis=0), np.nanmean(f, axis=0)
            point = {"SDI": (np.nanmean(Mf[S, exp_idx]) - np.nanmean(Mf[A, exp_idx])) - (np.nanmean(Mb[S, exp_idx]) - np.nanmean(Mb[A, exp_idx])),
                     "E_self": np.nanmean(Mf[S, exp_idx]) - np.nanmean(Mb[S, exp_idx]),
                     "A_self": np.nanmean(Mf[S, age_idx]) - np.nanmean(Mb[S, age_idx])}[which]
            lo, hi = ci(d)
            out.append(f"d{which} {point:+.3f} [{lo:+.3f}, {hi:+.3f}]")
        h2 = (stat_boot(f, "E_self") - stat_boot(b, "E_self")) - (stat_boot(f, "A_self") - stat_boot(b, "A_self"))
        lo, hi = ci(h2)
        print(f"{fam:11s} ({chain[0][0]} -> {chain[-1][0]}): " + "; ".join(out) + f"; H2 dE-dA [{lo:+.3f}, {hi:+.3f}]")

    chain = [c for c in CHECKPOINTS if c[1] == "OLMo 3 7B" and c[0] in data]
    if len(chain) > 2:
        print("\nOLMo 3 stage steps (H3)")
        for (l0, *_), (l1, *_) in zip(chain, chain[1:]):
            dE = stat_boot(data[l1], "E_self") - stat_boot(data[l0], "E_self")
            dS = stat_boot(data[l1], "SDI") - stat_boot(data[l0], "SDI")
            print(f"  {l0:15s} -> {l1:15s} dE(SELF) {np.mean(dE):+.3f} [{ci(dE)[0]:+.3f}, {ci(dE)[1]:+.3f}]  "
                  f"dSDI {np.mean(dS):+.3f} [{ci(dS)[0]:+.3f}, {ci(dS)[1]:+.3f}]")


if __name__ == "__main__":
    main()
