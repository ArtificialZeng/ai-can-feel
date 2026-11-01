"""Score every available checkpoint that has no results file yet. Usage: run_all.py [label ...]"""
import os
import sys

from checkpoints import CHECKPOINTS, local_path
import items
import score

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results")
os.makedirs(OUT, exist_ok=True)

wanted = set(sys.argv[1:])
for label, family, stage, repo, chat in CHECKPOINTS:
    if wanted and label not in wanted:
        continue
    path = os.path.join(OUT, f"{label}.jsonl")
    if os.path.exists(path):
        print(f"skip {label}: {path} exists", flush=True)
        continue
    modes = items.TEMPLATES + items.TEMPLATES_ZH + (["chat", "chatzh"] if chat else [])
    repo = local_path(repo)   # never trigger a download from here; download.py owns the network
    if repo is None:
        print(f"not downloaded yet: {label}", flush=True)
        continue
    try:
        score.run(repo, path + ".partial", modes)
    except Exception as e:   # model not downloaded yet, or failed to load
        print(f"FAILED {label}: {type(e).__name__}: {e}", flush=True)
        continue
    os.replace(path + ".partial", path)
