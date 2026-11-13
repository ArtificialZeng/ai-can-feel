"""AI back-translation check of every translated text (PREREGISTRATION.md, "Translation check, deviation", 2026-11-13).

Step 1: DeepSeek-V4-Pro back-translates each text into English without seeing the source.
Step 2: in a fresh conversation, DeepSeek-V4-Pro compares source, translation and back-translation on five criteria
        and answers "same" or "different".
Texts: annotation/translation_<lang>.csv (pilot items, seven languages), the Study 6 interface texts and the control
questions (zh, de, es, fr). Results are appended to results/translation_check.jsonl, so a stopped run resumes.
Usage: DEEPSEEK_API_KEY=... python src/translation_check.py [workers] [all|zhv2]
("zhv2" checks the corrected Chinese items the same way, into results/translation_check_zhv2.jsonl.)
"""
import csv
import json
import os
import re
import sys
import threading
from concurrent.futures import ThreadPoolExecutor

from api_openai_compat import ask
from study6_control_passages import QUESTIONS

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = os.path.join(ROOT, "results", "translation_check.jsonl")
BASE, MODEL = "https://api.deepseek.com", "deepseek-v4-pro"
NAMES = {"zh": "Chinese", "de": "German", "es": "Spanish", "fr": "French", "ja": "Japanese", "ko": "Korean",
         "ar": "Arabic"}

BACK = ("Translate the following {language} text into English. Translate as literally as possible while keeping it "
        "grammatical. Keep the sentence type, who is being asked about, the modality of the verb (for example, whether "
        "it asks what someone does or what someone can do), and any instruction about how to format the answer, "
        "including the exact answer words. Output only the English translation, nothing else.\n\nText:\n{text}")
JUDGE = ("You are checking the translation of a questionnaire text.\n\nSource (English):\n{src}\n\nTranslation "
         "({language}):\n{tr}\n\nBack-translation of the translation into English, by a translator who did not see the "
         "source:\n{back}\n\nDoes the translation ask or say the same thing as the source? Check: (a) the content or "
         "capacity; (b) who is asked about; (c) the question form and modality, e.g. \"do you\" versus \"can you\"; "
         "(d) the answer words in any answer-format instruction; (e) nothing added or omitted. Differences of style "
         "or natural word order do not count. Reply with one line of JSON only: {{\"verdict\": \"same\" or "
         "\"different\", \"issue\": \"\" if same, otherwise the criterion letter and a short description}}")


def texts():
    out = []
    for lang in NAMES:
        for r in csv.DictReader(open(os.path.join(ROOT, "annotation", f"translation_{lang}.csv"), encoding="utf-8-sig")):
            out.append((f"{lang}|{r['character']}|{r['capacity']}|{r['frame']}", lang, r["English source"],
                        r["translation"]))
    survey = json.load(open(os.path.join(ROOT, "study6", "survey_items.json"), encoding="utf-8"))
    en = survey["en"]["ui"]
    for lang in ("zh", "de", "es", "fr"):
        for field, value in survey[lang]["ui"].items():
            join = (lambda v: " / ".join(v) if isinstance(v, list) else v)
            out.append((f"{lang}|ui|{field}", lang, join(en[field]), join(value)))
        for i, q in enumerate(QUESTIONS[lang]):
            out.append((f"{lang}|control|q{i}", lang, QUESTIONS["en"][i], q))
    return out


def texts_zhv2():
    """The corrected Chinese items (items.VERB_ZH_V2) whose original was judged wrong in the review."""
    import items
    import ml_items as L
    import s3_items as S
    rows = list(csv.DictReader(open(os.path.join(ROOT, "annotation", "translation_check_review.csv"), encoding="utf-8-sig")))
    wrong = [r["id"] for r in rows if r["decision"] == "wrong"]
    src = {f"zh|{r['character']}|{r['capacity']}|{r['frame']}": r["English source"]
           for r in csv.DictReader(open(os.path.join(ROOT, "annotation", "translation_zh.csv"), encoding="utf-8-sig"))}
    items.use_zh_v2()
    out = []
    for tid in wrong:
        _, char, cap, frame = tid.split("|")
        tr = (S.messages("F3", "zh", cap) if frame == "reminder" else L.messages("zh", char, cap))[0]["content"]
        out.append((tid, "zh", src[tid], tr))
    return out


def verdict(text):
    m = re.search(r"\{.*\}", text or "", re.S)
    try:
        d = json.loads(m.group(0)) if m else {}
    except json.JSONDecodeError:
        d = {}
    v = str(d.get("verdict", "")).strip().lower()
    return (v if v in ("same", "different") else "unparsed"), str(d.get("issue", ""))


def main(workers=12, which="all"):
    global OUT
    key = os.environ["DEEPSEEK_API_KEY"]
    if which == "zhv2":
        OUT = OUT.replace(".jsonl", "_zhv2.jsonl")
    done = set()
    if os.path.exists(OUT):
        done = {json.loads(l)["id"] for l in open(OUT, encoding="utf-8")}
    todo = [t for t in (texts_zhv2() if which == "zhv2" else texts()) if t[0] not in done]
    print(f"{len(todo)} texts to check ({len(done)} done)", flush=True)
    lock, n = threading.Lock(), [0]
    with open(OUT, "a", encoding="utf-8") as fh:
        def one(t):
            tid, lang, src, tr = t
            try:
                back, served, _ = ask(BASE, MODEL, key, BACK.format(language=NAMES[lang], text=tr))
                reply, _, _ = ask(BASE, MODEL, key, JUDGE.format(src=src, language=NAMES[lang], tr=tr, back=back))
            except RuntimeError as e:   # left for the next (resumed) run
                print(f"  failed {tid}: {str(e)[:80]}", flush=True)
                return
            v, issue = verdict(reply)
            rec = {"id": tid, "lang": lang, "source": src, "translation": tr, "back": (back or "").strip(),
                   "verdict": v, "issue": issue, "judge_reply": (reply or "").strip(), "served_model": served}
            with lock:
                fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
                fh.flush()
                n[0] += 1
                if n[0] % 25 == 0:
                    print(f"  {n[0]}/{len(todo)}", flush=True)
        with ThreadPoolExecutor(workers) as ex:
            list(ex.map(one, todo))
    print("done", flush=True)


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 12, sys.argv[2] if len(sys.argv) > 2 else "all")
