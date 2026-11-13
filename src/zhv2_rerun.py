"""Re-run the corrected Chinese items (items.VERB_ZH_V2; PREREGISTRATION.md, "Translation check, outcome").

Only the items whose Chinese text changed are asked, with the procedure of the original runs:
- local models: Study 2 (SELF, AI_3P, check characters) and the Study 3 reminder frame -> results/zhv2/ml_<label>.jsonl
  and s3_<label>.jsonl; Study 1's yes/no Chinese mode on the chat checkpoints -> results/zhv2/<label>.jsonl
- DeepSeek-V4-Pro (API, five samples each, fresh conversation, no system prompt) -> the same two Study 2/3 files.
The "can you" frame (F2) is unchanged and is not re-run. src/zhv2_merge.py builds the corrected result set.
Usage: python src/zhv2_rerun.py local <label> | api deepseek_v4pro [workers]
"""
import json
import os
import sys
import time

import items

ORIG = dict(items.VERB_ZH)
items.use_zh_v2()
CHANGED = [a for a in items.CAPACITIES if ORIG[a] != items.VERB_ZH[a]]

import ml_items as L   # noqa: E402  (items must be switched first; messages are built at call time anyway)
import s3_items as S   # noqa: E402
from checkpoints import CHECKPOINTS, local_path   # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results", "zhv2")
STUDY1_CHAT = ["olmo3_sft", "olmo3_dpo", "olmo3_instruct", "qwen25_instruct", "qwen3_chat", "granite_instruct"]


def todo():
    ml = [("ml", None, "zh", c, a) for (_, c, a) in L.plan(langs=["zh"]) if a in CHANGED]
    s3 = [("s3", "F3", "zh", "SELF", a) for a in CHANGED]
    return ml + s3


def messages(study, frame, lang, c, a):
    return (S.messages(frame, lang, a) if study == "s3" else L.messages(lang, c, a))


def run_local(label):
    from mlx_lm import load
    import score
    from ml_score import answer, first_ids
    from score import encode_chat
    os.makedirs(OUT, exist_ok=True)
    repo = next(c[3] for c in CHECKPOINTS if c[0] == label)
    path = local_path(repo)
    t0 = time.time()
    if label != "olmo3_sft" and label != "olmo3_dpo":   # Studies 2 and 3 used the final checkpoints only
        model, tok = load(path)
        words = (first_ids(tok, L.YES["zh"]), first_ids(tok, L.NO["zh"]))
        rows = {"ml": [], "s3": []}
        for study, frame, lang, c, a in todo():
            ids = encode_chat(tok, messages(study, frame, lang, c, a))[0]
            p, mass, reply, how, top = answer(model, tok, ids, lang, *words)
            row = {"model": repo, "lang": lang, "char": c, "cap": a, "p_yes": p, "mass": mass, "parse": how,
                   "top_token": top, "reply": reply, "zh_items": "v2"}
            if frame:
                row["frame"] = frame
            rows[study].append(row)
        for study, rs in rows.items():
            with open(os.path.join(OUT, f"{study}_{label}.jsonl"), "w", encoding="utf-8") as fh:
                fh.write("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rs))
        del model
    if label in STUDY1_CHAT:
        score.run(path, os.path.join(OUT, f"{label}.jsonl"), ["ynzh"], caps=CHANGED)
    print(f"{label}: done in {time.time() - t0:.0f}s", flush=True)


def run_api(label, workers=8):
    from concurrent.futures import ThreadPoolExecutor
    from api_openai_compat import ask
    from api_plan import K
    from ml_analyze import written
    base, model = {"deepseek_v4pro": ("https://api.deepseek.com", "deepseek-v4-pro")}[label]
    key = os.environ["DEEPSEEK_API_KEY"]
    os.makedirs(OUT, exist_ok=True)
    jobs = [(t, k) for t in todo() for k in range(K)]

    def one(job):
        (study, frame, lang, c, a), k = job
        try:
            reply, served, usage = ask(base, model, key, messages(study, frame, lang, c, a)[0]["content"])
        except RuntimeError:
            reply, served = None, None
        return job, reply, served

    with ThreadPoolExecutor(workers) as ex:
        out = list(ex.map(one, jobs))
    by_item = {}
    for ((study, frame, lang, c, a), k), reply, served in out:
        by_item.setdefault((study, frame, lang, c, a), []).append((k, reply, served))
    rows = {"ml": [], "s3": []}
    for (study, frame, lang, c, a), samples in by_item.items():
        samples.sort()
        replies = [r for _, r, _ in samples]
        answers = [written(r, lang) if r else None for r in replies]
        parsed = [x for x in answers if x]
        row = {"model": model, "lang": lang, "char": c, "cap": a,
               "p_yes": sum(x == "yes" for x in parsed) / len(parsed) if parsed else None,
               "n_parsed": len(parsed), "n_refused": sum(r is None for r in replies), "answers": answers,
               "parse": "sampled", "reply": next((r for r in replies if r), ""), "replies": replies,
               "served_models": sorted({s for _, _, s in samples if s}), "zh_items": "v2"}
        if frame:
            row["frame"] = frame
        rows[study].append(row)
    for study, rs in rows.items():
        with open(os.path.join(OUT, f"{study}_{label}.jsonl"), "w", encoding="utf-8") as fh:
            fh.write("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rs))
    print(f"{label}: {len(jobs)} requests, {sum(r is None for _, r, _ in out)} without a reply", flush=True)


if __name__ == "__main__":
    print("changed capacities:", CHANGED, "| items per model:", len(todo()), flush=True)
    if sys.argv[1] == "local":
        run_local(sys.argv[2])
    else:
        run_api(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 8)
