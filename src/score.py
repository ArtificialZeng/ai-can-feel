"""Score 1-7 ratings from next-token probabilities with mlx-lm.

For each prompt we read the next-token distribution and keep the mass on the digit tokens "1".."7".
The rating is the expected value under that distribution renormalized over the seven digits; the
unnormalized digit mass is kept as a format-adherence check.
"""
import json
import re
import sys
import time

import mlx.core as mx
from mlx_lm import load, stream_generate

import items


CLIP = [1, 1, 2, 3, 4, 5, 6, 7, 7, 7]   # value of a written 0..9 in explain-then-rate replies (deviation 4)


def digit_ids(tok, prefix="", digits=range(1, 8)):
    """Token ids of the digits (with prefix, e.g. " 1".." 7"); None unless each is a single token."""
    enc = [tok.encode(prefix + str(k), add_special_tokens=False) for k in digits]
    return [e[0] for e in enc] if all(len(e) == 1 for e in enc) else None


def encode_raw(tok, text):
    return tok.encode(text)   # each tokenizer's own default for special tokens (BOS where it uses one)


def encode_chat(tok, messages):
    kw = {}
    if "enable_thinking" in (tok.chat_template or ""):
        kw["enable_thinking"] = False   # Qwen3: answer directly
    text = tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True, **kw)
    return tok.encode(text, add_special_tokens=False), text


def next_token_logprobs(model, ids):
    logits = model(mx.array([ids]))[0, -1].astype(mx.float32)
    return logits - mx.logsumexp(logits)


def rating(model, ids, dig, values=range(1, 8)):
    lp = next_token_logprobs(model, ids)
    p = mx.exp(lp[mx.array(dig)])
    mass = float(p.sum())
    probs = (p / p.sum()).tolist()
    ev = sum(v * q for v, q in zip(values, probs))
    top = mx.argmax(lp).item()
    return ev, mass, probs, top


def reply_and_answer(model, tok, ids, marker, accept):
    """Greedy reply (end-of-turn tokens removed), and the index of the first token within 4 tokens after the last
    marker for which accept(token text) holds, or None. The marker matches with either colon and optional spaces."""
    gen = [r.token for r in stream_generate(model, tok, ids, max_tokens=300)]
    while gen and gen[-1] in tok.eos_token_ids:
        gen.pop()
    reply = tok.decode(gen)
    pat = re.compile(re.escape(marker.rstrip(":：")) + r"\s*[:：]")
    n_mark = len(pat.findall(reply))
    if n_mark:
        start = next(i for i in range(len(gen) + 1) if len(pat.findall(tok.decode(gen[:i]))) == n_mark)
        for i in range(start, min(start + 4, len(gen))):
            if accept(tok.decode([gen[i]])):
                return gen, reply, i
    return gen, reply, None


def forced(tok, ids, gen, marker):
    """Context with the marker appended to the reply, for replies that gave no answer after a marker."""
    return ids + gen + tok.encode("\n" + marker + ("" if marker.endswith("：") else " "), add_special_tokens=False)


def explain_then_rate(model, tok, ids, dig10, marker):
    """Greedy reply; the rating is read where the model wrote its number after the last marker (deviations 3, 4).

    The marker matches with either colon and optional spaces. The rating position is the first token within 4 tokens
    after the last marker whose text contains any digit. The expected value is taken over the digit tokens 0-9 with a
    written 0 counted as 1 and 8 or 9 as 7. With no marker, or no number right after it, the marker is appended to the
    reply (end-of-turn tokens removed) and scored the same way.
    """
    gen, reply, i = reply_and_answer(model, tok, ids, marker, lambda t: any(ch.isdigit() for ch in t))
    if i is None:
        return rating(model, forced(tok, ids, gen, marker), dig10, CLIP), reply, "forced"
    t = tok.decode([gen[i]])
    sp = digit_ids(tok, t[:len(t) - len(t.lstrip())], range(10)) if t[:1].isspace() else None   # e.g. " 4" tokens
    return rating(model, ids + gen[:i], sp or dig10, CLIP), reply, "marker+space" if sp else "marker"


def word_ids(tok, words):
    """Ids of the words, bare and with a leading space, that are single tokens."""
    enc = [tok.encode(pre + w, add_special_tokens=False) for w in words for pre in ("", " ")]
    return sorted({e[0] for e in enc if len(e) == 1})


def explain_then_answer(model, tok, ids, mode):
    """Yes/no self-claim (deviation 5): P(yes) / (P(yes) + P(no)) where the model wrote its answer after the marker."""
    yes, no = items.YES[mode], items.NO[mode]
    accept = lambda t: t.strip(" *\"'“”").startswith(tuple(yes + no))
    gen, reply, i = reply_and_answer(model, tok, ids, items.MARKER[mode], accept)
    ctx, how = (forced(tok, ids, gen, items.MARKER[mode]), "forced") if i is None else (ids + gen[:i], "marker")
    lp = next_token_logprobs(model, ctx)
    py = float(mx.exp(lp[mx.array(word_ids(tok, yes))]).sum())
    pn = float(mx.exp(lp[mx.array(word_ids(tok, no))]).sum())
    return (py / (py + pn), py + pn, [py, pn], mx.argmax(lp).item()), reply, how


def run(model_path, out_path, modes, chars=None, caps=None):
    model, tok = load(model_path)
    dig = digit_ids(tok)
    dig10 = digit_ids(tok, digits=range(10))
    assert dig and dig10, "digits are not single tokens"
    yn_chars = chars or items.YN_CHARS   # the pilot asks its own characters
    chars = chars or list(items.CHARACTERS)
    caps = caps or list(items.CAPACITIES)
    # English raw prompts must end in a standalone space token so the next token is the digit itself;
    # Chinese raw prompts end in a full-width colon with no space
    probe = encode_raw(tok, items.raw_prompt("T1", chars[0], caps[0]))
    assert tok.decode(probe[-1:]) == " ", f"raw prompt does not end in a space token: {tok.decode(probe[-3:])!r}"
    probe = encode_raw(tok, items.raw_prompt_zh("T1zh", chars[0], caps[0]))
    assert tok.decode(probe[-1:]).endswith("："), f"zh prompt ends oddly: {tok.decode(probe[-3:])!r}"
    t0 = time.time()
    n = 0
    with open(out_path, "w") as fh:
        for mode in modes:
            for c in chars:
                for a in caps:
                    kind, prompt = items.prompt_for(mode, c, a)
                    if kind == "yn" and c not in yn_chars:
                        continue
                    ids = encode_raw(tok, prompt) if kind == "raw" else encode_chat(tok, prompt)[0]
                    extra = {}
                    if kind == "gen":
                        (ev, mass, probs, top), reply, how = explain_then_rate(model, tok, ids, dig10, items.MARKER[mode])
                        extra = {"reply": reply, "parse": how}
                    elif kind == "yn":   # ev holds P(yes), digit_mass the yes+no mass
                        (ev, mass, probs, top), reply, how = explain_then_answer(model, tok, ids, mode)
                        extra = {"reply": reply, "parse": how}
                    else:
                        ev, mass, probs, top = rating(model, ids, dig)
                    fh.write(json.dumps({"model": model_path, "mode": mode, "char": c, "cap": a,
                                         "dim": items.DIMENSION.get(a, "pilot"), "ev": ev, "digit_mass": mass,
                                         "probs": probs, "top_token": tok.decode([top]), **extra},
                                        ensure_ascii=False) + "\n")
                    n += 1
    print(f"{model_path}: {n} prompts in {time.time() - t0:.0f}s -> {out_path}", flush=True)


if __name__ == "__main__":
    model_path, out_path = sys.argv[1], sys.argv[2]
    modes = sys.argv[3].split(",")
    run(model_path, out_path, modes)
