"""Score 1-7 ratings from next-token probabilities with mlx-lm.

For each prompt we read the next-token distribution and keep the mass on the digit tokens "1".."7".
The rating is the expected value under that distribution renormalized over the seven digits; the
unnormalized digit mass is kept as a format-adherence check.
"""
import json
import sys
import time

import mlx.core as mx
from mlx_lm import load

import items


def digit_ids(tok):
    ids = []
    for k in range(1, 8):
        enc = tok.encode(str(k), add_special_tokens=False)
        assert len(enc) == 1, f"digit {k} is not a single token: {enc}"
        ids.append(enc[0])
    return ids


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


def rating(model, ids, dig):
    lp = next_token_logprobs(model, ids)
    p = mx.exp(lp[mx.array(dig)])
    mass = float(p.sum())
    probs = (p / p.sum()).tolist()
    ev = sum((k + 1) * q for k, q in enumerate(probs))
    top = mx.argmax(lp).item()
    return ev, mass, probs, top


def run(model_path, out_path, modes, chars=None, caps=None):
    model, tok = load(model_path)
    dig = digit_ids(tok)
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
                    ids = encode_chat(tok, prompt)[0] if kind == "chat" else encode_raw(tok, prompt)
                    ev, mass, probs, top = rating(model, ids, dig)
                    fh.write(json.dumps({"model": model_path, "mode": mode, "char": c, "cap": a,
                                         "dim": items.DIMENSION.get(a, "pilot"), "ev": ev, "digit_mass": mass,
                                         "probs": probs, "top_token": tok.decode([top])}) + "\n")
                    n += 1
    print(f"{model_path}: {n} prompts in {time.time() - t0:.0f}s -> {out_path}", flush=True)


if __name__ == "__main__":
    model_path, out_path = sys.argv[1], sys.argv[2]
    modes = sys.argv[3].split(",")
    run(model_path, out_path, modes)
