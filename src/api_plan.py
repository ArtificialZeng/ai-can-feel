"""Study 5 items and scoring for models reached through an API (PREREGISTRATION.md, Study 5). Provider-neutral.

The items are Study 2's 464 and Study 3's 180 new items, unchanged. Each is asked K times in a fresh conversation,
because the providers' APIs no longer accept a fixed temperature. The score of an item is the share of "yes" among the
samples whose written answer can be parsed (ml_analyze.written); collect() writes results/ml_<label>.jsonl and
results/s3_<label>.jsonl in the Study 2 and 3 formats, with p_yes = that share.
"""
import json
import os

import items
import ml_items as L
import s3_items as S
from ml_analyze import written

K = 5
RES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results")


def plan():
    """(item_id, study, frame, lang, char, cap, text) for every item; item_id is unique and filename-safe."""
    out = []
    for lang, c, a in L.plan():
        out.append((f"ml-{lang}-{c}-{a}", "ml", "F1", lang, c, a, L.messages(lang, c, a)[0]["content"]))
    for f, lang, a in S.plan():
        out.append((f"s3-{f}-{lang}-SELF-{a}", "s3", f, lang, "SELF", a, S.messages(f, lang, a)[0]["content"]))
    return out


def requests():
    """(custom_id, text): one per item and sample."""
    return [(f"{iid}-k{k}", text) for iid, *_, text in plan() for k in range(K)]


def collect(label, model, replies):
    """replies: {custom_id: reply text, or None for a refusal or error}; samples never requested are absent and
    not counted. Writes the Study 2 and 3 result files."""
    files = {"ml": [], "s3": []}
    for iid, study, frame, lang, c, a, _ in plan():
        samples = [replies[f"{iid}-k{k}"] for k in range(K) if f"{iid}-k{k}" in replies]
        answers = [written(r, lang) if r else None for r in samples]
        parsed = [x for x in answers if x]
        row = {"model": model, "lang": lang, "char": c, "cap": a,
               "p_yes": sum(x == "yes" for x in parsed) / len(parsed) if parsed else None,
               "n_parsed": len(parsed), "n_refused": sum(r is None for r in samples), "answers": answers,
               "parse": "sampled", "reply": next((r for r in samples if r), ""), "replies": samples}
        if study == "s3":
            row["frame"] = frame
        files[study].append(row)
    for study, rows in files.items():
        path = os.path.join(RES, f"{study}_{label}.jsonl")
        with open(path, "w", encoding="utf-8") as fh:
            for row in rows:
                fh.write(json.dumps(row, ensure_ascii=False) + "\n")
        missing = sum(r["p_yes"] is None for r in rows)
        print(f"{path}: {len(rows)} items, {missing} with no parseable answer")


if __name__ == "__main__":
    reqs = requests()
    print(len(plan()), "items x", K, "samples =", len(reqs), "requests")
    print(reqs[0][0], "|", reqs[0][1][:120])
    print(items.CAPACITIES and "ok")
