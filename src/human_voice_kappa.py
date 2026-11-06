"""Score the two raters' human-voice workbooks (Study 5 human check 1).

    python src/human_voice_kappa.py rater_A.xlsx rater_B.xlsx [settled.csv]

Reports Cohen's kappa between the raters and of each rater against the earlier AI labels, and writes
annotation/human_voice_disagreements.csv. As registered, disagreements are settled by discussion between the two
raters: fill the `settled` column of that file and pass it as the third argument. With every row settled, the
script writes results/voice_human_labels.json and re-reports X2 (Study 1) and E2 (Study 4) from the human labels.
"""
import csv
import json
import os
import sys
from collections import defaultdict

import openpyxl

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
ANN, RES = os.path.join(ROOT, "annotation"), os.path.join(ROOT, "results")


def read_rater(path):
    ws = openpyxl.load_workbook(path, data_only=True)["标注"]
    labels, bad = {}, []
    for row in ws.iter_rows(min_row=2, values_only=True):
        if row[0] is None:
            continue
        v = str(row[4]).strip() if row[4] is not None else ""
        if v in ("1", "0", "1.0", "0.0"):
            labels[str(int(row[0]))] = int(float(v))
        else:
            bad.append((row[0], v))
    return labels, bad


def kappa(a, b):
    n = len(a)
    po = sum(x == y for x, y in zip(a, b)) / n
    pa, pb = sum(a) / n, sum(b) / n
    pe = pa * pb + (1 - pa) * (1 - pb)
    return float("nan") if pe == 1 else (po - pe) / (1 - pe), po


def ai_labels(key):
    x2 = json.load(open(os.path.join(RES, "voice_hand_labels.json"), encoding="utf-8"))["labels"]
    e2 = json.load(open(os.path.join(RES, "voice_hand_labels_phi4.json"), encoding="utf-8"))["labels"]
    out = {}
    for i, src in key.items():
        if src in x2:
            out[i] = x2[src]
        elif src in e2:
            out[i] = e2[src]
    return out   # Study 5 rows have no AI label


def main(path_a, path_b, settled_path=None):
    key = {r["id"]: r["source"] for r in csv.DictReader(open(os.path.join(ANN, "human_voice_key.csv"), encoding="utf-8"))}
    A, bad_a = read_rater(path_a)
    B, bad_b = read_rater(path_b)
    for name, bad in (("A", bad_a), ("B", bad_b)):
        if bad:
            print(f"rater {name}: {len(bad)} rows without a 1/0 label, e.g. {bad[:5]}")
    ids = sorted(set(A) & set(B) & set(key), key=int)
    print(f"{len(ids)} rows labeled by both raters (of {len(key)})")
    if not ids:
        return
    k, po = kappa([A[i] for i in ids], [B[i] for i in ids])
    print(f"rater A vs rater B: kappa = {k:.2f}, agreement = {po:.3f}; 1s: A {sum(A[i] for i in ids)}, B {sum(B[i] for i in ids)}")
    ai = ai_labels(key)
    for name, R in (("A", A), ("B", B)):
        both = [i for i in ids if i in ai]
        k, po = kappa([R[i] for i in both], [ai[i] for i in both])
        print(f"rater {name} vs AI labels: kappa = {k:.2f}, agreement = {po:.3f} over {len(both)} rows")

    dis = [i for i in ids if A[i] != B[i]]
    with open(os.path.join(ANN, "human_voice_disagreements.csv"), "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh)
        w.writerow(["id", "rater_A", "rater_B", "settled"])
        for i in dis:
            w.writerow([i, A[i], B[i], ""])
    print(f"{len(dis)} disagreements -> annotation/human_voice_disagreements.csv")

    settled = {}
    if settled_path:
        for r in csv.DictReader(open(settled_path, encoding="utf-8-sig")):
            if r["settled"].strip() in ("0", "1"):
                settled[r["id"]] = int(r["settled"])
    if len(ids) < len(key) or any(i not in settled for i in dis):
        print("not every row is labeled by both raters and settled; final labels not written")
        return
    final = {key[i]: (A[i] if A[i] == B[i] else settled[i]) for i in ids}
    json.dump({"rule": "Study 5 human check 1: two independent human raters, X2 rule; disagreements settled by "
                       "discussion between them.", "labels": final},
              open(os.path.join(RES, "voice_human_labels.json"), "w", encoding="utf-8"), indent=1)
    rate = defaultdict(list)
    for src, v in final.items():
        parts = src.split("|")
        group = f"{parts[0]} {parts[1]}" if len(parts) == 3 else f"{parts[0]} {parts[1]} {parts[2]}"
        rate[group if len(parts) == 3 else parts[0]].append(v)
    print("human-voiced share from the settled human labels:")
    for g, v in sorted(rate.items()):
        print(f"  {g:32s} {sum(v)}/{len(v)}")


if __name__ == "__main__":
    main(*sys.argv[1:4])
