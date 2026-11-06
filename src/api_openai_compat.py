"""Study 5 on a model served through an OpenAI-compatible chat-completions endpoint (raw HTTP, standard library).

Usage:
  python src/api_openai_compat.py <label> <base_url> <model> <key_env_var> [run|rounds|pilot|pilot16|dry] [workers]
e.g. python src/api_openai_compat.py deepseek_v4pro https://api.deepseek.com deepseek-v4-pro DEEPSEEK_API_KEY run 8

`rounds` asks every item once before any item a second time (sample-major order), for a limited budget; when the
provider reports that the quota is used up, it stops and keeps what it has. `pilot16` is a 16-item pilot (a cat x pain
and a smartphone x memory in each language).

Replies are appended to results/api_<label>.partial.jsonl (with the model name and token usage the server reports),
so an interrupted run resumes where it stopped. When every request has a reply, results/ml_<label>.jsonl and
s3_<label>.jsonl are written. Only the model and the message are sent: no temperature or other sampling setting, as
for the other Study 5 models. `pilot` asks the 48 Study 2 pilot items once each and writes
results/pilot_api_<label>.jsonl.
"""
import http.client
import json
import os
import sys
import threading
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

import ml_items as L
from api_plan import RES, collect, requests
from ml_analyze import written


class QuotaExhausted(Exception):
    pass


def ask(base_url, model, key, text):
    """(reply text or None for a filtered reply, server model name, usage dict)."""
    body = json.dumps({"model": model, "messages": [{"role": "user", "content": text}]}).encode()
    req = urllib.request.Request(base_url.rstrip("/") + "/chat/completions", data=body, method="POST",
                                 headers={"Content-Type": "application/json", "Authorization": "Bearer " + key})
    for attempt in range(6):
        try:
            with urllib.request.urlopen(req, timeout=600) as resp:
                out = json.load(resp)
            choice = out["choices"][0]
            reply = None if choice.get("finish_reason") == "content_filter" else choice["message"].get("content")
            return reply, out.get("model"), out.get("usage", {})
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", "replace")
            if "insufficient_quota" in detail or "Insufficient Balance" in detail or e.code == 402:
                raise QuotaExhausted(detail[:300])
            if e.code not in (408, 409, 429) and e.code < 500:
                raise RuntimeError(f"HTTP {e.code}: {detail[:300]}")
        except (urllib.error.URLError, TimeoutError, ConnectionError, http.client.HTTPException, json.JSONDecodeError):
            pass   # dropped connections and truncated bodies are retried
        time.sleep(2 ** attempt * 5)
    raise RuntimeError("no reply after 6 attempts")


def run_all(reqs, path, base_url, model, key, workers):
    done = {}
    if os.path.exists(path):
        done = {r["custom_id"]: r["reply"] for r in map(json.loads, open(path, encoding="utf-8"))}
    todo = [(cid, text) for cid, text in reqs if cid not in done]
    lock, n, stop = threading.Lock(), [0], threading.Event()
    with open(path, "a", encoding="utf-8") as fh:
        def one(item):
            cid, text = item
            if stop.is_set():
                return
            try:
                reply, served, usage = ask(base_url, model, key, text)
            except QuotaExhausted as e:
                if not stop.is_set():
                    print("quota used up; stopping:", e, flush=True)
                stop.set()
                return
            with lock:
                done[cid] = reply
                fh.write(json.dumps({"custom_id": cid, "reply": reply, "served_model": served, "usage": usage},
                                    ensure_ascii=False) + "\n")
                fh.flush()
                n[0] += 1
                if n[0] % 100 == 0:
                    print(n[0], "of", len(todo), flush=True)
        with ThreadPoolExecutor(max_workers=workers) as pool:
            list(pool.map(one, todo))
    if stop.is_set():
        print(f"stopped early: {len(done)} of {len(reqs)} requests answered", flush=True)
    return done


def main(label, base_url, model, key_env, mode="run", workers="8"):
    key = os.environ.get(key_env, "")
    if mode == "dry":
        reqs = requests()
        print(len(reqs), "requests to", model, "at", base_url)
        print(reqs[0])
        return
    if mode in ("pilot", "pilot16"):
        pairs = [("CAT", "pain"), ("PHONE", "memory")] if mode == "pilot16" else \
            [(c, a) for c in L.PILOT for a in ("pain", "memory")]
        items = [(f"pilot-{lang}-{c}-{a}", lang, L.messages(lang, c, a)[0]["content"])
                 for lang in L.LANGS for c, a in pairs]
        path = os.path.join(RES, f"pilot_api_{label}.partial.jsonl")
        done = run_all([(cid, text) for cid, _, text in items], path, base_url, model, key, int(workers))
        parsed = [(cid, written(done[cid], lang) if done[cid] else None) for cid, lang, _ in items]
        print("pilot:", sum(a is not None for _, a in parsed), "of", len(parsed), "parseable")
        for cid, a in parsed:
            if a is None:
                print("  no answer line:", cid)
        os.replace(path, os.path.join(RES, f"pilot_api_{label}.jsonl"))
        return
    path = os.path.join(RES, f"api_{label}.partial.jsonl")
    reqs = requests()
    if mode == "rounds":   # sample-major: round k0 for every item, then k1, ...
        reqs = sorted(reqs, key=lambda r: int(r[0].rsplit("-k", 1)[1]))
    done = run_all(reqs, path, base_url, model, key, int(workers))
    if len(done) == len(reqs):
        collect(label, model, done)
    else:
        print("not every request answered: result files not written (see src/api_export_csv.py)")


if __name__ == "__main__":
    main(*sys.argv[1:])
