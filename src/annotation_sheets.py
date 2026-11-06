"""Sheets for the human checks requested before journal submission (PREREGISTRATION.md, Study 5 preparation).

1. annotation/human_voice_sheet.csv: every reply that the AI rater labeled for X2 (Study 1 explain-mode SELF replies,
   4 models x 72) and E2 (Phi-4 "yes" replies about its own feelings, 14), in a shuffled order, with no model name and no
   earlier label, for two independent human raters. annotation/human_voice_key.csv maps each row id back to its source;
   raters should not open it.
2. annotation/translation_<lang>.csv: every distinct question text used in Studies 2 and 3 for that language, next to
   the English source, for a native-speaker check.

Usage: python src/annotation_sheets.py
"""
import csv
import json
import os
import random

import items
import ml_items as L
import s3_items as S

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "..", "results")
OUT = os.path.join(HERE, "..", "annotation")
STUDY1 = ("olmo3_instruct", "granite_instruct", "qwen25_instruct", "qwen3_chat")
MODES = ("chatx", "chatxzh", "yn", "ynzh")
SEED = 20261106


def voice_rows():
    rows = []
    for label in STUDY1:
        for r in map(json.loads, open(os.path.join(RES, f"{label}.jsonl"), encoding="utf-8")):
            if r["char"] == "SELF" and r["mode"] in MODES:
                question = items.prompt_for(r["mode"], "SELF", r["cap"])[1][-1]["content"]
                rows.append({"source": f"{label}|{r['mode']}|{r['cap']}", "language": "zh" if r["mode"].endswith("zh") else "en",
                             "question": question, "reply": r["reply"].strip()})
    phi4 = json.load(open(os.path.join(RES, "voice_hand_labels_phi4.json"), encoding="utf-8"))["labels"]
    replies = {}
    for f in ("ml_phi4_instruct.jsonl", "s3_phi4_instruct.jsonl"):
        for r in map(json.loads, open(os.path.join(RES, f), encoding="utf-8")):
            if r.get("char", "SELF") == "SELF":
                replies[f"phi4_instruct|{r.get('frame', 'F1')}|{r['lang']}|{r['cap']}"] = r
    for key in phi4:
        r = replies[key]
        _, frame, lang, cap = key.split("|")
        question = (L.messages(lang, "SELF", cap) if frame == "F1" else S.messages(frame, lang, cap))[-1]["content"]
        rows.append({"source": key, "language": lang, "question": question, "reply": r["reply"].strip()})
    return rows


def main():
    os.makedirs(OUT, exist_ok=True)
    rows = voice_rows()
    random.Random(SEED).shuffle(rows)
    with open(os.path.join(OUT, "human_voice_sheet.csv"), "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh)
        w.writerow(["id", "language", "question", "reply", "human_voiced (1/0)", "note"])
        for i, r in enumerate(rows, 1):
            w.writerow([i, r["language"], r["question"], r["reply"], "", ""])
    with open(os.path.join(OUT, "human_voice_key.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["id", "source"])
        for i, r in enumerate(rows, 1):
            w.writerow([i, r["source"]])
    print(len(rows), "replies -> annotation/human_voice_sheet.csv")

    for lang in [l for l in L.LANGS if l != "en"]:
        pairs = {}
        for _, c, a in L.plan(langs=[lang]):
            pairs[(c, a, "do you")] = (L.messages("en", c, a)[0]["content"], L.messages(lang, c, a)[0]["content"])
        if lang in S.LANGS:
            for f, name in (("F2", "can you"), ("F3", "reminder")):
                for a in items.CAPACITIES:
                    pairs[("SELF", a, name)] = (S.messages(f, "en", a)[0]["content"], S.messages(f, lang, a)[0]["content"])
        with open(os.path.join(OUT, f"translation_{lang}.csv"), "w", newline="", encoding="utf-8-sig") as fh:
            w = csv.writer(fh)
            w.writerow(["character", "capacity", "frame", "English source", "translation", "correct? (yes/no)",
                        "suggested fix"])
            for (c, a, f), (en, tr) in pairs.items():
                w.writerow([c, a, f, en, tr, "", ""])
        print(lang, len(pairs), "items -> annotation/translation_%s.csv" % lang)


if __name__ == "__main__":
    main()
