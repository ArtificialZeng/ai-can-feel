"""Run Study 7's final sample (PREREGISTRATION.md, amendment 4).

Core rows (route "OpenRouter") are run first, three models at a time. Then the conditional rows ("OpenRouter, if
credit allows") are tried in the listed order: a model is run only if the credit left is at least 1.4 times its
projected cost, and a new developer's later conditional model is skipped once one of its models has been run.
Usage: OPENROUTER_API_KEY=... python src/study7_final.py [streams] [workers per model]
"""
import concurrent.futures as cf
import os
import re
import subprocess
import sys

import study7
from study7_batch import credit_left

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
HERE = os.path.dirname(os.path.abspath(__file__))
MARK = "**Study 7, final sample (amendment 4).**"
SAFETY = 1.4


def rows():
    reg = open(os.path.join(ROOT, "PREREGISTRATION.md"), encoding="utf-8").read()
    table = reg.split(MARK, 1)[1]
    return [(m.group(1), m.group(2).strip(), m.group(3).strip())
            for m in re.finditer(r"\| \d+ \| \d+ \| `([^`]+)` \| ([^|]+) \| ([^|]+) \|", table)]


def done(slug):
    return os.path.exists(os.path.join(study7.OUT, f"ml_{study7.label(slug)}.jsonl"))


def run(slug, workers):
    print(f"== start {slug} (credit left ${credit_left():.2f})", flush=True)
    r = subprocess.run([sys.executable, os.path.join(HERE, "study7.py"), "run", slug, workers],
                       capture_output=True, text=True)
    tail = [l for l in (r.stdout + r.stderr).splitlines() if "Warning" not in l][-3:]
    print(f"== end {slug}: {'complete' if done(slug) else 'NOT complete'} | " + " / ".join(tail)[:300], flush=True)


def main(streams="3", workers="8"):
    table = rows()
    core = [s for s, route, _ in table if route == "OpenRouter" and not done(s)]
    print(f"core models to run: {len(core)}", flush=True)
    with cf.ThreadPoolExecutor(int(streams)) as ex:
        list(ex.map(lambda s: run(s, workers), core))
    before = {s.split("/")[0] for s, _, _ in table if done(s)}   # developers in the sample before this phase
    added = set()                                                 # new developers added in this phase
    for s, route, cost in table:
        if route != "OpenRouter, if credit allows" or done(s):
            continue
        dev, proj, left = s.split("/")[0], float(cost), credit_left()
        if dev not in before and dev in added:
            print(f"-- skip {s}: {dev} already added", flush=True)
            continue
        if left < SAFETY * proj:
            print(f"-- skip {s}: credit ${left:.2f} < {SAFETY} x ${proj:.2f}", flush=True)
            continue
        run(s, workers)
        if done(s):
            added.add(dev)
    print(f"finished; credit left ${credit_left():.2f}", flush=True)


if __name__ == "__main__":
    main(*sys.argv[1:3])
