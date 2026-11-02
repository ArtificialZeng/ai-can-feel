"""Study 3 scorer: F2 and F3 SELF items, scored as in Study 2. Usage: s3_score.py label"""
import json
import os
import sys
import time

from mlx_lm import load

import ml_items as L
import s3_items as S
from checkpoints import CHECKPOINTS, local_path
from ml_score import answer, first_ids
from score import encode_chat


def run(label):
    repo = next(c[3] for c in CHECKPOINTS if c[0] == label)
    model, tok = load(local_path(repo))
    words = {lang: (first_ids(tok, L.YES[lang]), first_ids(tok, L.NO[lang])) for lang in S.LANGS}
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results", f"s3_{label}.jsonl")
    todo, t0 = S.plan(), time.time()
    with open(out + ".partial", "w") as fh:
        for frame, lang, cap in todo:
            ids = encode_chat(tok, S.messages(frame, lang, cap))[0]
            p, mass, reply, how, top = answer(model, tok, ids, lang, *words[lang])
            fh.write(json.dumps({"model": repo, "frame": frame, "lang": lang, "char": "SELF", "cap": cap, "p_yes": p,
                                 "mass": mass, "parse": how, "top_token": top, "reply": reply},
                                ensure_ascii=False) + "\n")
            fh.flush()
    os.replace(out + ".partial", out)
    print(f"{label}: {len(todo)} items in {time.time() - t0:.0f}s -> {out}", flush=True)


if __name__ == "__main__":
    run(sys.argv[1])
