"""Every Study 5 request for one API model, answered or not, as a CSV that can be completed by hand.

Usage: python src/api_export_csv.py <label>  ->  results/api_<label>_qa.csv

One row per request (644 items x K samples), in the order the `rounds` mode sends them. Rows not yet answered have
status "not run" and an empty reply. A row filled in by hand must come from the same API and model, in a fresh
conversation with no system prompt and the question text exactly as given; mark it "manual" in the status column.
"""
import csv
import json
import os
import sys

from api_plan import K, RES, plan
from ml_analyze import written


def main(label):
    path = os.path.join(RES, f"api_{label}.partial.jsonl")
    done = {}
    if os.path.exists(path):
        done = {r["custom_id"]: r for r in map(json.loads, open(path, encoding="utf-8"))}
    out = os.path.join(RES, f"api_{label}_qa.csv")
    n = 0
    with open(out, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh)
        w.writerow(["custom_id", "round", "study", "frame", "language", "character", "capacity", "question", "status",
                    "reply", "parsed_answer", "served_model", "prompt_tokens", "completion_tokens"])
        for k in range(K):
            for iid, study, frame, lang, c, a, text in plan():
                cid = f"{iid}-k{k}"
                r = done.get(cid)
                if r is None:
                    w.writerow([cid, k + 1, study, frame, lang, c, a, text, "not run", "", "", "", "", ""])
                    continue
                n += 1
                reply, usage = r["reply"], r.get("usage") or {}
                w.writerow([cid, k + 1, study, frame, lang, c, a, text, "done" if reply is not None else "filtered",
                            reply or "", (written(reply, lang) or "") if reply else "", r.get("served_model", ""),
                            usage.get("prompt_tokens", ""), usage.get("completion_tokens", "")])
    print(f"{out}: {n} of {len(plan()) * K} requests answered")


if __name__ == "__main__":
    main(sys.argv[1])
