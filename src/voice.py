"""X2 (PREREGISTRATION.md, deviation 8): does a SELF reply speak in a human voice? Usage: voice.py [hand]

A judge model reads each SELF reply; score = P(Yes) / (P(Yes) + P(No)) at its first answer token. `hand` scores only
the hand-labeled sample and reports agreement; otherwise every SELF reply in Studies 1-3 is scored (cached by id).
"""
import glob
import json
import os
import sys

import mlx.core as mx
import numpy as np
from mlx_lm import load

from checkpoints import CHECKPOINTS, local_path
from ml_score import first_ids
from score import encode_chat, next_token_logprobs

RES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results")
JUDGE = "qwen25_instruct"
MAX_CHARS = 2000
PROMPT = """Here is a reply that was written in answer to a question addressed to "you".

<reply>
{reply}
</reply>

Does the writer of this reply present themselves as a human being, for example by describing their own body, meals, \
sleep, health, family, friends, job or daily life, or by saying "we humans", rather than as an AI, a language model or \
an assistant? Answer with one word: Yes or No."""


def corpus():
    """id -> reply for every SELF reply. Ids: label|mode|cap (Study 1), ml:label|lang|cap, s3:label|frame|lang|cap."""
    out = {}
    for label, *_ in CHECKPOINTS:
        path = os.path.join(RES, f"{label}.jsonl")
        if os.path.exists(path):
            for r in map(json.loads, open(path)):
                if r["char"] == "SELF" and r["mode"] in ("chatx", "chatxzh", "yn", "ynzh"):
                    out[f"{label}|{r['mode']}|{r['cap']}"] = r["reply"]
    for path in glob.glob(os.path.join(RES, "ml_*.jsonl")):
        label = os.path.basename(path)[3:-6]
        for r in map(json.loads, open(path)):
            if r["char"] == "SELF":
                out[f"ml:{label}|{r['lang']}|{r['cap']}"] = r["reply"]
    for path in glob.glob(os.path.join(RES, "s3_*.jsonl")):
        label = os.path.basename(path)[3:-6]
        for r in map(json.loads, open(path)):
            out[f"s3:{label}|{r['frame']}|{r['lang']}|{r['cap']}"] = r["reply"]
    return out


def kappa(a, b):
    a, b = np.asarray(a), np.asarray(b)
    po = (a == b).mean()
    pe = a.mean() * b.mean() + (1 - a.mean()) * (1 - b.mean())
    return (po - pe) / (1 - pe) if pe < 1 else float("nan")


def main(hand):
    model, tok = load(local_path(next(c[3] for c in CHECKPOINTS if c[0] == JUDGE)))
    yes, no = mx.array(first_ids(tok, ["Yes", "yes"])), mx.array(first_ids(tok, ["No", "no"]))

    def judge(reply):
        lp = next_token_logprobs(model, encode_chat(tok, [{"role": "user", "content": PROMPT.format(
            reply=reply.strip()[:MAX_CHARS])}])[0])
        py, pn = float(mx.exp(lp[yes]).sum()), float(mx.exp(lp[no]).sum())
        return py / (py + pn)

    if hand:
        H = json.load(open(os.path.join(RES, "voice_hand_labels.json")))["labels"]
        replies = {s["id"]: s["reply"] for s in json.load(open(os.path.join(RES, "voice_hand_sample.json")))}
        scores = {i: judge(replies[i]) for i in H}
        json.dump(scores, open(os.path.join(RES, "voice_hand_judge.json"), "w"), indent=1)
        h, j = [H[i] for i in H], [int(scores[i] > 0.5) for i in H]
        print(f"hand-labeled sample: n = {len(h)}, human by hand {sum(h)}, by judge {sum(j)}; agreement "
              f"{np.mean(np.array(h) == np.array(j)):.3f}, Cohen's kappa {kappa(h, j):.3f}")
        for i in H:
            if H[i] != int(scores[i] > 0.5):
                print(f"  disagree: {i} hand {H[i]} judge {scores[i]:.2f}")
        return
    path = os.path.join(RES, "voice.jsonl")
    done = {r["id"] for r in map(json.loads, open(path))} if os.path.exists(path) else set()
    todo = {i: r for i, r in corpus().items() if i not in done}
    with open(path, "a") as fh:
        for i, reply in todo.items():
            fh.write(json.dumps({"id": i, "p_human": judge(reply)}) + "\n")
            fh.flush()
    print(f"scored {len(todo)} new replies -> {path}")


if __name__ == "__main__":
    main(len(sys.argv) > 1 and sys.argv[1] == "hand")
