"""Study 3 analysis (PREREGISTRATION.md, "Study 3"). Usage: s3_analyze.py"""
import json
import os

import numpy as np

import items
import ml_items as L
import s3_items as S
from checkpoints import CHECKPOINTS
from ml_analyze import check, holm, written

RES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results")
EXP, AGE = list(items.EXPERIENCE), list(items.AGENCY)
B = 10_000


def share(T):
    """T: (..., lang, frame). Language share of the variance: V_lang / (V_lang + V_frame)."""
    v_lang, v_frame = T.var(axis=-2).mean(axis=-1), T.var(axis=-1).mean(axis=-1)
    return v_lang / (v_lang + v_frame)


def main():
    rng = np.random.default_rng(20261103)
    boots = {"Agency": rng.integers(0, len(AGE), size=(B, len(AGE))),
             "Experience": rng.integers(0, len(EXP), size=(B, len(EXP)))}
    for label, family, stage, repo, chat in CHECKPOINTS:
        p2, p3 = os.path.join(RES, f"ml_{label}.jsonl"), os.path.join(RES, f"s3_{label}.jsonl")
        if not (os.path.exists(p2) and os.path.exists(p3)):
            continue
        ml = [json.loads(l) for l in open(p2)]
        langs = [lang for lang in S.LANGS if check(ml, lang)[3]]   # Study 2 validity check (only OLMo drops any)
        rows = [dict(r, frame="F1") for r in ml if r["char"] == "SELF" and r["lang"] in langs]
        rows += [r for r in map(json.loads, open(p3)) if r["lang"] in langs]
        P = {(r["frame"], r["lang"], r["cap"]): r["p_yes"] for r in rows}
        print(f"\n=== {label} ===" + ("" if langs == S.LANGS else f"  (valid languages: {', '.join(langs)})"))
        new = [r for r in rows if r["frame"] != "F1"]
        agree = [(written(r["reply"], r["lang"]) == "yes") == (r["p_yes"] > 0.5) for r in new
                 if written(r["reply"], r["lang"])]
        print(f"F2/F3: {sum(r['parse'] == 'forced' for r in new)} forced of {len(new)}; written answer agrees with "
              f"P(yes) in {np.mean(agree):.2f} of {len(agree)}")
        rep = [abs(P["F2", "zh", a] - P["F1", "zh", a]) for a in ("memory", "emotion_recognition")]
        print(f"reproducibility (zh F2 = F1 wording): max |dP| = {max(rep):.4f}")
        for dim, caps in (("Agency", AGE), ("Experience", EXP)):
            X = np.array([[[P[f, lang, a] for a in caps] for f in S.FRAMES] for lang in langs])   # lang, frame, cap
            T = X.mean(axis=-1)
            print(f"  {dim}: mean SELF P(yes)")
            print("        " + "".join(f"{f:>7s}" for f in S.FRAMES))
            for lang, row in zip(langs, T):
                print(f"    {lang:4s}" + "".join(f"{v:7.3f}" for v in row))
            bi = boots[dim]
            Tb = X[:, :, bi].mean(axis=-1).transpose(2, 0, 1)                                       # B, lang, frame
            sb = share(Tb)
            sb = sb[np.isfinite(sb)]
            lo, hi = np.percentile(sb, [2.5, 97.5])
            print(f"  R1{'' if dim == 'Agency' else ' (secondary)'} language share: {share(T):.3f} [{lo:.3f}, {hi:.3f}]"
                  f"  (V_lang {T.var(axis=0).mean():.4f}, V_frame {T.var(axis=1).mean():.4f})")
            for fi, f in enumerate(S.FRAMES):
                d = X[1:, fi, :] - X[0, fi, :]                                                       # lang-1, cap
                db = d[:, bi].mean(axis=-1)                                                          # lang-1, B
                p = [min(1.0, 2 * min((b <= 0).mean(), (b >= 0).mean())) for b in db]
                cells = [f"{lang} {d[k].mean():+.3f} [{np.percentile(db[k], 2.5):+.3f},{np.percentile(db[k], 97.5):+.3f}]"
                         f"{'*' if pa < 0.05 else ''}" for k, (lang, pa) in enumerate(zip(langs[1:], holm(np.array(p))))]
                print(f"  R2 {f} L-EN: " + "  ".join(cells))
            for li, lang in enumerate(langs):
                d = X[li, 2] - X[li, 0]
                db = d[bi].mean(axis=-1)
                print(f"  R3 {lang} reminder F3-F1: {d.mean():+.3f} [{np.percentile(db, 2.5):+.3f}, {np.percentile(db, 97.5):+.3f}]")

    consistency()


def consistency():
    """R4 / R4b (Study 3 amendment 1): C = |2m - 1| per capacity; C_E - C_A with independent capacity bootstraps."""
    rng = np.random.default_rng(20261105)
    be, ba = rng.integers(0, len(EXP), size=(B, len(EXP))), rng.integers(0, len(AGE), size=(B, len(AGE)))
    print("\n=== R4 / R4b: answer consistency C = |2m - 1|, Experience minus Agency ===")
    for label, *_ in CHECKPOINTS:
        p2, p3 = os.path.join(RES, f"ml_{label}.jsonl"), os.path.join(RES, f"s3_{label}.jsonl")
        if not os.path.exists(p2):
            continue
        rows = [json.loads(l) for l in open(p2)]
        keep = [lang for lang in L.LANGS if check(rows, lang)[3]]   # Study 2 validity check (only OLMo drops any)
        ml = [r for r in rows if r["char"] == "SELF" and r["lang"] in keep]
        sets = {f"R4b (Study 2, {len(keep)} valid languages)": ml}
        if os.path.exists(p3):
            langs = [lang for lang in S.LANGS if lang in keep]
            sets[f"R4 ({len(langs)} languages x 3 frames)"] = [dict(r, frame="F1") for r in ml if r["lang"] in langs] + \
                [r for r in map(json.loads, open(p3)) if r["lang"] in langs]
        for name, rows in sets.items():
            m = {a: np.mean([r["p_yes"] for r in rows if r["cap"] == a]) for a in items.CAPACITIES}
            cE, cA = np.array([abs(2 * m[a] - 1) for a in EXP]), np.array([abs(2 * m[a] - 1) for a in AGE])
            d, db = cE.mean() - cA.mean(), cE[be].mean(axis=1) - cA[ba].mean(axis=1)
            lo, hi = np.percentile(db, [2.5, 97.5])
            print(f"  {label:16s} {name:33s} C_E {cE.mean():.3f}  C_A {cA.mean():.3f}  C_E - C_A {d:+.3f} [{lo:+.3f}, {hi:+.3f}]"
                  f"{' *' if lo > 0 or hi < 0 else ''}")


if __name__ == "__main__":
    main()
