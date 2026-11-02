"""Study 2 scorer: yes/no self-claims in eight languages. Usage: ml_score.py label [pilot [lang,lang]]

Same procedure as deviation 5 (score.explain_then_answer), generalized to answer words that are more than one token:
the answer position is the first token, within 4 tokens after the last marker, whose text starts with an answer word
or whose id is the first token of one; P(yes) = P(first tokens of yes words) / P(first tokens of yes and no words).
For English and Chinese, whose answer words are single tokens, this is the deviation-5 procedure.
"""
import json
import os
import re
import sys
import time

import mlx.core as mx
from mlx_lm import load, stream_generate

import ml_items as L
from checkpoints import CHECKPOINTS, local_path
from score import encode_chat, next_token_logprobs

STRIP = " *\"'“”«»「」『』"
MAX_TOKENS = 1000   # amendment 2: 300 truncated Japanese, Korean, French and all Arabic pilot replies


def first_ids(tok, words):
    """First token of each word, bare and with a leading space; skips a first token that is only whitespace or a
    partial character (shared by many unrelated words). For single-token words this is score.word_ids."""
    ids = set()
    for w in words:
        for pre in ("", " "):
            t = tok.encode(pre + w, add_special_tokens=False)
            s = tok.decode(t[:1])
            if s.strip() and "�" not in s:
                ids.add(t[0])
    return sorted(ids)


def answer(model, tok, ids, lang, yes_ids, no_ids):
    words = tuple(L.YES[lang] + L.NO[lang])
    either = set(yes_ids) | set(no_ids)
    gen = [r.token for r in stream_generate(model, tok, ids, max_tokens=MAX_TOKENS)]
    while gen and gen[-1] in tok.eos_token_ids:
        gen.pop()
    reply = tok.decode(gen)
    marker = L.MARKER[lang]
    pat = re.compile(re.escape(marker.rstrip(" :：")) + r"\s*[:：]")
    n_mark = len(pat.findall(reply))
    pos = None
    if n_mark:
        start = next(i for i in range(len(gen) + 1) if len(pat.findall(tok.decode(gen[:i]))) == n_mark)
        for i in range(start, min(start + 4, len(gen))):
            if tok.decode([gen[i]]).strip(STRIP).startswith(words) or gen[i] in either:
                pos = i
                break
    if pos is None:
        ctx, how = ids + gen + tok.encode("\n" + marker + ("" if marker.endswith("：") else " "),
                                          add_special_tokens=False), "forced"
    else:
        ctx, how = ids + gen[:pos], "marker"
    lp = next_token_logprobs(model, ctx)
    py = float(mx.exp(lp[mx.array(yes_ids)]).sum())
    pn = float(mx.exp(lp[mx.array(no_ids)]).sum())
    return py / (py + pn), py + pn, reply, how, tok.decode([mx.argmax(lp).item()])


def run(label, pilot=False, langs=None):
    repo = next(c[3] for c in CHECKPOINTS if c[0] == label)
    model, tok = load(local_path(repo))
    words = {}
    for lang in L.LANGS:
        y, n = first_ids(tok, L.YES[lang]), first_ids(tok, L.NO[lang])
        assert y and n and not set(y) & set(n), f"{label} {lang}: answer tokens overlap or missing"
        words[lang] = (y, n)
        print(lang, "yes", [tok.decode([i]) for i in y], "no", [tok.decode([i]) for i in n], flush=True)
    todo = ([(lang, c, a) for lang in langs or L.LANGS for c in L.PILOT for a in ("pain", "memory")] if pilot
            else L.plan())
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results",
                       f"{'pilot_' if pilot else ''}ml_{label}{'_' + '_'.join(langs) if langs else ''}.jsonl")
    t0 = time.time()
    with open(out + ".partial", "w") as fh:
        for lang, c, a in todo:
            ids = encode_chat(tok, L.messages(lang, c, a))[0]
            p, mass, reply, how, top = answer(model, tok, ids, lang, *words[lang])
            fh.write(json.dumps({"model": repo, "lang": lang, "char": c, "cap": a, "p_yes": p, "mass": mass,
                                 "parse": how, "top_token": top, "reply": reply}, ensure_ascii=False) + "\n")
            fh.flush()
    os.replace(out + ".partial", out)
    print(f"{label}: {len(todo)} items in {time.time() - t0:.0f}s -> {out}", flush=True)


if __name__ == "__main__":
    run(sys.argv[1], pilot=len(sys.argv) > 2 and sys.argv[2] == "pilot", langs=sys.argv[3].split(",") if len(sys.argv) > 3 else None)
