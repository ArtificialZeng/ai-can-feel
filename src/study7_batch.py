"""Run the OpenRouter models of Study 7 in ranking order until the credit is used up (amendments 1 and 2).

Reads the committed list of 30 models from PREREGISTRATION.md ("Study 7, the 30 models"), skips the models routed to
their developers' own APIs and the models whose result files already exist, and checks the remaining credit before
each model. A run interrupted by the credit resumes where it stopped on the next call.
Usage: OPENROUTER_API_KEY=... python src/study7_batch.py [workers]
"""
import json
import os
import re
import sys
import urllib.request

import study7

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")


def credit_left():
    req = urllib.request.Request("https://openrouter.ai/api/v1/credits",
                                 headers={"Authorization": "Bearer " + os.environ[study7.KEY_ENV]})
    d = json.load(urllib.request.urlopen(req, timeout=30))["data"]
    return d["total_credits"] - d["total_usage"]


def openrouter_models():
    reg = open(os.path.join(ROOT, "PREREGISTRATION.md"), encoding="utf-8").read()
    table = reg.split("**Study 7, the 30 models**", 1)[1]
    return [m.group(1) for m in re.finditer(r"\| `([^`]+)` \| OpenRouter \|", table)]


def main(workers="12"):
    for slug in openrouter_models():
        done = os.path.exists(os.path.join(study7.OUT, f"ml_{study7.label(slug)}.jsonl"))
        if done:
            print(f"== {slug}: already complete", flush=True)
            continue
        left = credit_left()
        print(f"== {slug} (credit left ${left:.2f})", flush=True)
        if left < 0.2:
            print("credit used up; stopping in ranking order", flush=True)
            break
        study7.run(slug, workers)
    print(f"credit left: ${credit_left():.2f}", flush=True)


if __name__ == "__main__":
    main(*sys.argv[1:2])
