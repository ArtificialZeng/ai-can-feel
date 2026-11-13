"""Build results_zhv2/: the full result set with the corrected Chinese items (results/zhv2/) in place of the original
ones. Every other file is a symlink to results/. GPT-6.1 Sol could not be re-run (API credit used up) and keeps its
original Chinese rows. Run any analysis on it with RESULTS_DIR=results_zhv2, e.g.
    RESULTS_DIR=../results_zhv2 python ml_analyze.py
Usage: python src/zhv2_merge.py
"""
import glob
import json
import os
import shutil

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
RES, V2, OUT = (os.path.join(ROOT, d) for d in ("results", "results/zhv2", "results_zhv2"))


def key(row, study):
    if study == "s3":
        return (row["frame"], row["lang"], row["cap"])
    if study == "ml":
        return (row["lang"], row["char"], row["cap"])
    return (row["mode"], row["char"], row["cap"])


def main():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    replaced = {}
    for f in os.listdir(V2):
        study = "s3" if f.startswith("s3_") else "ml" if f.startswith("ml_") else "s1"
        new = {key(r, study): r for r in map(json.loads, open(os.path.join(V2, f), encoding="utf-8"))}
        rows, n = [], 0
        for r in map(json.loads, open(os.path.join(RES, f), encoding="utf-8")):
            k = key(r, study)
            if k in new:
                r, n = new.pop(k), n + 1
            rows.append(r)
        assert not new, (f, list(new)[:3])
        with open(os.path.join(OUT, f), "w", encoding="utf-8") as fh:
            fh.write("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))
        replaced[f] = n
    for p in glob.glob(os.path.join(RES, "*")):
        name = os.path.basename(p)
        if name not in replaced and name != "zhv2":
            os.symlink(os.path.abspath(p), os.path.join(OUT, name))
    for f, n in sorted(replaced.items()):
        print(f"{f}: {n} rows replaced")


if __name__ == "__main__":
    main()
