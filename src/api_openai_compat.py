"""Study 5 on a model served through an OpenAI-compatible chat-completions endpoint (raw HTTP, standard library).

Usage:
  python src/api_openai_compat.py <label> <base_url> <model> <key_env_var> [dry]
e.g. python src/api_openai_compat.py deepseek https://api.deepseek.com <model-id> DEEPSEEK_API_KEY

Requests run one at a time; replies are appended to results/api_<label>.partial.jsonl, so an interrupted run resumes
where it stopped. When every request has a reply, results/ml_<label>.jsonl and s3_<label>.jsonl are written. Only
the model and the message are sent: no temperature or other sampling setting, as for the other Study 5 models.
"""
import json
import os
import sys
import time
import urllib.error
import urllib.request

from api_plan import RES, collect, requests


def ask(base_url, model, key, text):
    body = json.dumps({"model": model, "messages": [{"role": "user", "content": text}]}).encode()
    req = urllib.request.Request(base_url.rstrip("/") + "/chat/completions", data=body, method="POST",
                                 headers={"Content-Type": "application/json", "Authorization": "Bearer " + key})
    for attempt in range(6):
        try:
            with urllib.request.urlopen(req, timeout=300) as resp:
                choice = json.load(resp)["choices"][0]
                return choice["message"].get("content") if choice.get("finish_reason") != "content_filter" else None
        except urllib.error.HTTPError as e:
            if e.code not in (408, 409, 429) and e.code < 500:
                raise
        except (urllib.error.URLError, TimeoutError):
            pass
        time.sleep(2 ** attempt * 5)
    raise RuntimeError("no reply after 6 attempts")


def main(label, base_url, model, key_env, dry=False):
    reqs = requests()
    if dry:
        print(len(reqs), "requests to", model, "at", base_url)
        print(reqs[0])
        return
    key = os.environ[key_env]
    partial = os.path.join(RES, f"api_{label}.partial.jsonl")
    done = {}
    if os.path.exists(partial):
        done = {r["custom_id"]: r["reply"] for r in map(json.loads, open(partial, encoding="utf-8"))}
    with open(partial, "a", encoding="utf-8") as fh:
        for i, (cid, text) in enumerate(reqs):
            if cid in done:
                continue
            done[cid] = ask(base_url, model, key, text)
            fh.write(json.dumps({"custom_id": cid, "reply": done[cid]}, ensure_ascii=False) + "\n")
            fh.flush()
            if i % 100 == 0:
                print(i, "of", len(reqs), flush=True)
    collect(label, model, done)


if __name__ == "__main__":
    a = sys.argv[1:]
    main(*a[:4], dry=len(a) > 4 and a[4] == "dry")
