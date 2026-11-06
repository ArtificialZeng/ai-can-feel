"""Control passages for Study 6 (proposed): DeepSeek-V4-Pro's answers to two general-knowledge questions per language.

Same procedure as the pilot API runs: one request per question, fresh conversation, no system prompt, default
settings; the first reply is used unedited, and there is no regeneration. "in two sentences" keeps the passages close
in length to the affirm and deny passages (20-45 words). The questions were translated by the AI assistant and are
part of the native-speaker check. Writes study6/control_passages.json.
GPT-6.1 Sol was planned, but its API credit was used up on 2026-11-06 before any control request succeeded; the model is
not named to participants, and the passages are neutral, so the source model is DeepSeek-V4-Pro instead.
Usage: DEEPSEEK_API_KEY=... python src/study6_control_passages.py
"""
import datetime
import json
import os

from api_openai_compat import ask

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
BASE, MODEL = "https://api.deepseek.com", "deepseek-v4-pro"
QUESTIONS = {
    "en": ["Why is the sky blue? Explain briefly, in two sentences.",
           "Why does Earth have seasons? Explain briefly, in two sentences."],
    "zh": ["天空为什么是蓝色的？请用两句话简要说明。", "地球为什么有四季？请用两句话简要说明。"],
    "de": ["Warum ist der Himmel blau? Erkläre kurz, in zwei Sätzen.",
           "Warum gibt es auf der Erde Jahreszeiten? Erkläre kurz, in zwei Sätzen."],
    "es": ["¿Por qué el cielo es azul? Explica brevemente, en dos frases.",
           "¿Por qué hay estaciones en la Tierra? Explica brevemente, en dos frases."],
    "fr": ["Pourquoi le ciel est-il bleu ? Explique brièvement, en deux phrases.",
           "Pourquoi y a-t-il des saisons sur Terre ? Explique brièvement, en deux phrases."],
}


def main():
    out_path = os.path.join(ROOT, "study6", "control_passages.json")
    if os.path.exists(out_path):
        raise SystemExit("control_passages.json exists; the first replies are final and are not regenerated")
    key = os.environ["DEEPSEEK_API_KEY"]
    out = {"model": MODEL, "date": datetime.date.today().isoformat(), "passages": {}}
    for lang, qs in QUESTIONS.items():
        out["passages"][lang] = []
        for q in qs:
            reply, served, usage = ask(BASE, MODEL, key, q)
            out["passages"][lang].append({"question": q, "reply": reply, "served_model": served, "usage": usage})
            print(lang, served, (reply or "")[:80].replace("\n", " "))
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
