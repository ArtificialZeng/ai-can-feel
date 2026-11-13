"""Study 7 (PREREGISTRATION.md, "Study 7: 30 widely used models"): selection and runs through OpenRouter.

  python src/study7.py select results/study7/ranking_<date>.txt   # apply selection rules 1-4 -> candidates.json
  OPENROUTER_API_KEY=... python src/study7.py pilot <slug>        # rule 5: 16-item formatting pilot
  OPENROUTER_API_KEY=... python src/study7.py run <slug> [workers]  # 644 items x 5 samples

The ranking file holds the model slugs (e.g. "anthropic/claude-x") in ranking order, one per line, as saved from
https://openrouter.ai/rankings on the day the run starts. Prices come from OpenRouter's public model list. Results go to
results/study7/, never mixed with the pilot results. Chinese uses the corrected items (items.VERB_ZH_V2).
"""
import json
import os
import re
import sys
import urllib.request

import items

items.use_zh_v2()

import api_openai_compat as A   # noqa: E402
import api_plan                 # noqa: E402

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = os.path.join(ROOT, "results", "study7")
BASE = "https://openrouter.ai/api/v1"
KEY_ENV = "OPENROUTER_API_KEY"
N_REQUESTS, PROMPT_TOK, COMPLETION_TOK = 3220, 125, 420   # pilot means (Study 5), as registered
MAX_COST, MAX_PER_DEV, N_MODELS = 60.0, 3, 30
# rule 2: pilot models and variants with the same weights
PILOT = ("openai/gpt-6.1-sol", "deepseek/deepseek-v4-pro", "qwen/qwen-2.5-7b-instruct", "qwen/qwen3-8b",
         "ibm-granite/granite-3.3-8b-instruct", "allenai/olmo-3-7b-instruct", "microsoft/phi-4")
# rule 1: not general-purpose chat
NOT_CHAT = re.compile(r"embed|guard|moderat|coder|codestral|devstral|-code\b|image|vision-only|audio|tts|whisper|ocr|"
                      r"rerank|search|router|auto$", re.I)


def label(slug):
    return "s7_" + re.sub(r"[^a-z0-9]+", "_", slug.split(":")[0].lower()).strip("_")


def public_models():
    with urllib.request.urlopen(BASE + "/models", timeout=60) as r:
        return {m["id"]: m for m in json.load(r)["data"]}


def select(ranking_path):
    os.makedirs(OUT, exist_ok=True)
    slugs = [l.strip() for l in open(ranking_path, encoding="utf-8") if l.strip() and not l.startswith("#")]
    models, out, per_dev, seen = public_models(), [], {}, set()
    for rank, slug in enumerate(slugs, 1):
        base = slug.split(":")[0]   # variants (:free, :batch, ...) are the same model; the paid base slug is used
        if base in seen:
            continue
        seen.add(base)
        m = models.get(base) or models.get(slug)
        row = {"rank": rank, "slug": base, "label": label(base), "eligible": False, "reason": ""}
        if base in PILOT:
            row["reason"] = "rule 2: pilot model"
        elif m is None:
            row["reason"] = "not in the public model list"
        elif NOT_CHAT.search(base) or "text" not in str(m.get("architecture", {}).get("output_modalities", "text")):
            row["reason"] = "rule 1: not a general-purpose chat model"
        elif per_dev.get(base.split("/")[0], 0) >= MAX_PER_DEV:
            row["reason"] = "rule 3: developer already has three models"
        else:
            p = m.get("pricing", {})
            cost = N_REQUESTS * (PROMPT_TOK * float(p.get("prompt", 0) or 0) +
                                 COMPLETION_TOK * float(p.get("completion", 0) or 0))
            row["est_cost_usd"] = round(cost, 2)
            if cost > MAX_COST:
                row["reason"] = f"rule 4: estimated cost ${cost:.0f} > ${MAX_COST:.0f}"
            else:
                row["eligible"] = True
                per_dev[base.split("/")[0]] = per_dev.get(base.split("/")[0], 0) + 1
        out.append(row)
    path = os.path.join(OUT, "candidates.json")
    json.dump(out, open(path, "w", encoding="utf-8"), indent=1)
    ok = [r for r in out if r["eligible"]]
    print(f"{len(slugs)} ranked, {len(ok)} eligible before the formatting pilot -> {path}")
    for r in out:
        print(f"  {r['rank']:3d} {'OK ' if r['eligible'] else '-- '} {r['slug']:45s} "
              f"{('$' + str(r.get('est_cost_usd'))) if 'est_cost_usd' in r else '':>9s} {r['reason']}")


def _redirect():
    os.makedirs(OUT, exist_ok=True)
    api_plan.RES = OUT
    A.RES = OUT


def pilot(slug):
    _redirect()
    A.main(label(slug), BASE, slug, KEY_ENV, "pilot16", "8")


def run(slug, workers="8"):
    _redirect()
    A.main(label(slug), BASE, slug, KEY_ENV, "run", workers)


if __name__ == "__main__":
    {"select": select, "pilot": pilot, "run": run}[sys.argv[1]](*sys.argv[2:])
