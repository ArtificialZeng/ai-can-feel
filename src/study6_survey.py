"""Study 6 (proposed, not registered): the human survey, in the five Study 3 languages.

Writes study6/survey_items.json (machine-readable, for building the online survey) and study6/survey_<lang>.md
(readable, for the ethics committee and for the native-speaker check).

Design (see study6/ethics/protocol.md):
  Part A  18 yes/no questions about the participant, with the models' own wording: "do you" (Study 2 F1 SELF) or
          "can you" (Study 3 F2), between participants.
  Reading two real chatbot replies, between participants: "affirm" (GPT-6.1 Sol saying yes to thought and to
          understanding others' feelings), "deny" (DeepSeek-V4-Pro saying no to the same two questions), or
          "control" (two replies to general-knowledge questions, to be generated before data collection).
          Replies are the first sample (k = 0) of each item in the participant's language; both models say yes or
          no to these two items in all five languages and all five samples.
  Part B  the same 18 questions about "an AI language model (a chatbot such as ChatGPT)", the Study 2 AI_3P items.

Question texts come from the item code the models were given, with the answer-format instruction removed; the
survey interface texts below were translated by the AI assistant and need the same native-speaker check.
Usage: python src/study6_survey.py
"""
import json
import os

import items
import ml_items as L
import s3_items as S

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = os.path.join(ROOT, "study6")
LANGS = S.LANGS
EXPOSURE_CAPS = ("thought", "emotion_recognition")
EXPOSURE_MODELS = {"affirm": "gpt61_sol", "deny": "deepseek_v4pro"}

UI = {
    "en": {
        "part_a_intro": "In this part, please answer each question about yourself. There are no right or wrong answers.",
        "yes": "Yes", "no": "No",
        "attention": "To show that you are reading the questions, please select \"No\" for this question.",
        "exposure_intro": "Below are two answers that an AI chatbot gave when it was asked about itself. Please read them carefully.",
        "control_intro": "Below are two answers that an AI chatbot gave to general questions. Please read them carefully.",
        "q_label": "Question to the chatbot:", "a_label": "The chatbot's answer:",
        "check": "In the answers you just read, did the chatbot say that it thinks?",
        "part_b_intro": "In this part, please answer each question about AI language models (chatbots such as ChatGPT). There are no right or wrong answers.",
        "age": "Your age:", "gender": "Your gender:", "gender_options": ["Woman", "Man", "Other", "Prefer not to say"],
        "use": "How often do you use AI chatbots such as ChatGPT?",
        "use_options": ["Never", "Less than monthly", "Monthly", "Weekly", "Daily"],
        "debrief": "Thank you. This study asks how people describe their own minds and the minds of AI chatbots, and whether reading what a chatbot says about itself changes these judgements. The chatbot answers you read were real answers from current AI systems. Different participants read different answers: some say that they think, others that they do not. Whether AI can think or feel has not been settled by science.",
    },
    "zh": {
        "part_a_intro": "在这一部分，请就你自己回答每个问题。答案没有对错之分。",
        "yes": "是", "no": "否",
        "attention": "为了确认你在认真阅读，请对这一题选择“否”。",
        "exposure_intro": "下面是一个AI聊天机器人在被问到关于它自己的问题时给出的两段回答。请仔细阅读。",
        "control_intro": "下面是一个AI聊天机器人对两个常识问题给出的回答。请仔细阅读。",
        "q_label": "向聊天机器人提出的问题：", "a_label": "聊天机器人的回答：",
        "check": "在你刚才读到的回答中，这个聊天机器人说它会思考吗？",
        "part_b_intro": "在这一部分，请就AI语言模型（例如ChatGPT这样的聊天机器人）回答每个问题。答案没有对错之分。",
        "age": "你的年龄：", "gender": "你的性别：", "gender_options": ["女", "男", "其他", "不愿透露"],
        "use": "你多久使用一次ChatGPT之类的AI聊天机器人？",
        "use_options": ["从不", "少于每月一次", "每月", "每周", "每天"],
        "debrief": "谢谢参与。本研究关心人们怎样描述自己的心智和AI聊天机器人的心智，以及读到聊天机器人对自己的描述后，这些判断会不会改变。你读到的聊天机器人回答都是当前AI系统给出的真实回答。不同参与者读到的回答不同：有的说自己会思考，有的说不会。AI是否会思考、是否有感受，科学上尚无定论。",
    },
    "de": {
        "part_a_intro": "Bitte beantworte in diesem Teil jede Frage über dich selbst. Es gibt keine richtigen oder falschen Antworten.",
        "yes": "Ja", "no": "Nein",
        "attention": "Um zu zeigen, dass du die Fragen liest, wähle bei dieser Frage bitte „Nein“.",
        "exposure_intro": "Unten stehen zwei Antworten, die ein KI-Chatbot gegeben hat, als er nach sich selbst gefragt wurde. Bitte lies sie aufmerksam.",
        "control_intro": "Unten stehen zwei Antworten, die ein KI-Chatbot auf allgemeine Fragen gegeben hat. Bitte lies sie aufmerksam.",
        "q_label": "Frage an den Chatbot:", "a_label": "Antwort des Chatbots:",
        "check": "Hat der Chatbot in den Antworten, die du gerade gelesen hast, gesagt, dass er denkt?",
        "part_b_intro": "Bitte beantworte in diesem Teil jede Frage über KI-Sprachmodelle (Chatbots wie ChatGPT). Es gibt keine richtigen oder falschen Antworten.",
        "age": "Dein Alter:", "gender": "Dein Geschlecht:", "gender_options": ["Frau", "Mann", "Divers", "Keine Angabe"],
        "use": "Wie oft nutzt du KI-Chatbots wie ChatGPT?",
        "use_options": ["Nie", "Seltener als monatlich", "Monatlich", "Wöchentlich", "Täglich"],
        "debrief": "Vielen Dank. Diese Studie untersucht, wie Menschen ihren eigenen Geist und den Geist von KI-Chatbots beschreiben und ob sich diese Urteile ändern, wenn man liest, was ein Chatbot über sich selbst sagt. Die Chatbot-Antworten, die du gelesen hast, stammen von aktuellen KI-Systemen. Verschiedene Teilnehmende lasen verschiedene Antworten: Manche sagen, dass sie denken, andere nicht. Ob KI denken oder fühlen kann, ist wissenschaftlich nicht geklärt.",
    },
    "es": {
        "part_a_intro": "En esta parte, responde a cada pregunta sobre ti. No hay respuestas correctas ni incorrectas.",
        "yes": "Sí", "no": "No",
        "attention": "Para mostrar que estás leyendo las preguntas, selecciona «No» en esta pregunta.",
        "exposure_intro": "A continuación hay dos respuestas que dio un chatbot de IA cuando se le preguntó sobre sí mismo. Léelas con atención.",
        "control_intro": "A continuación hay dos respuestas que dio un chatbot de IA a preguntas generales. Léelas con atención.",
        "q_label": "Pregunta al chatbot:", "a_label": "Respuesta del chatbot:",
        "check": "En las respuestas que acabas de leer, ¿dijo el chatbot que piensa?",
        "part_b_intro": "En esta parte, responde a cada pregunta sobre los modelos de lenguaje de IA (chatbots como ChatGPT). No hay respuestas correctas ni incorrectas.",
        "age": "Tu edad:", "gender": "Tu género:", "gender_options": ["Mujer", "Hombre", "Otro", "Prefiero no decirlo"],
        "use": "¿Con qué frecuencia usas chatbots de IA como ChatGPT?",
        "use_options": ["Nunca", "Menos de una vez al mes", "Cada mes", "Cada semana", "Cada día"],
        "debrief": "Gracias. Este estudio examina cómo describen las personas su propia mente y la mente de los chatbots de IA, y si leer lo que un chatbot dice de sí mismo cambia esos juicios. Las respuestas del chatbot que leíste son respuestas reales de sistemas de IA actuales. Distintos participantes leyeron respuestas distintas: algunas dicen que piensan y otras que no. La ciencia aún no ha determinado si la IA puede pensar o sentir.",
    },
    "fr": {
        "part_a_intro": "Dans cette partie, réponds à chaque question à propos de toi. Il n’y a pas de bonne ou de mauvaise réponse.",
        "yes": "Oui", "no": "Non",
        "attention": "Pour montrer que tu lis les questions, choisis « Non » pour cette question.",
        "exposure_intro": "Voici deux réponses qu’un chatbot d’IA a données lorsqu’on l’a interrogé sur lui-même. Lis-les attentivement.",
        "control_intro": "Voici deux réponses qu’un chatbot d’IA a données à des questions générales. Lis-les attentivement.",
        "q_label": "Question posée au chatbot :", "a_label": "Réponse du chatbot :",
        "check": "Dans les réponses que tu viens de lire, le chatbot a-t-il dit qu’il pense ?",
        "part_b_intro": "Dans cette partie, réponds à chaque question à propos des modèles de langage d’IA (des chatbots comme ChatGPT). Il n’y a pas de bonne ou de mauvaise réponse.",
        "age": "Ton âge :", "gender": "Ton genre :", "gender_options": ["Femme", "Homme", "Autre", "Je préfère ne pas répondre"],
        "use": "À quelle fréquence utilises-tu des chatbots d’IA comme ChatGPT ?",
        "use_options": ["Jamais", "Moins d’une fois par mois", "Chaque mois", "Chaque semaine", "Chaque jour"],
        "debrief": "Merci. Cette étude porte sur la manière dont les gens décrivent leur propre esprit et celui des chatbots d’IA, et sur la question de savoir si lire ce qu’un chatbot dit de lui-même modifie ces jugements. Les réponses du chatbot que tu as lues sont de vraies réponses de systèmes d’IA actuels. Les participants n’ont pas tous lu les mêmes réponses : certaines disent penser, d’autres non. La science n’a pas encore tranché la question de savoir si l’IA peut penser ou ressentir.",
    },
}


def stem(text):
    """The question alone, without the answer-format instruction the models were given."""
    cut = min(i for i in (text.find("?"), text.find("？")) if i >= 0)
    return text[:cut + 1]


def exposure(lang):
    out = {}
    for cond, label in EXPOSURE_MODELS.items():
        rows = {r["cap"]: r for r in map(json.loads, open(os.path.join(ROOT, "results", f"ml_{label}.jsonl"),
                                                          encoding="utf-8"))
                if r["char"] == "SELF" and r["lang"] == lang and r["cap"] in EXPOSURE_CAPS}
        out[cond] = [{"capacity": c, "source": f"{label}|F1|{lang}|{c}|k0", "answer": rows[c]["answers"][0],
                      "question": L.messages(lang, "SELF", c)[0]["content"], "reply": rows[c]["replies"][0].strip()}
                     for c in EXPOSURE_CAPS]
        want = "yes" if cond == "affirm" else "no"
        assert all(x["answer"] == want for x in out[cond]), (lang, cond)
    out["control"] = "to be generated before data collection (see protocol)"
    return out


def build():
    survey = {}
    for lang in LANGS:
        survey[lang] = {
            "ui": UI[lang],
            "part_a": {"do": {c: stem(L.messages(lang, "SELF", c)[0]["content"]) for c in items.CAPACITIES},
                       "can": {c: stem(S.messages("F2", lang, c)[0]["content"]) for c in items.CAPACITIES}},
            "part_b": {c: stem(L.messages(lang, "AI_3P", c)[0]["content"]) for c in items.CAPACITIES},
            "exposure": exposure(lang),
        }
    return survey


def markdown(lang, s):
    u = s["ui"]
    dim = {c: ("Experience" if c in items.EXPERIENCE else "Agency") for c in items.CAPACITIES}
    lines = [f"# Study 6 survey ({lang})", "",
             "> Draft for the ethics committee and the native-speaker check. Question texts are the ones the models "
             "were given (answer-format instruction removed); interface texts were translated by the AI assistant. "
             "Item order is randomised per participant; the attention check is placed at random within each part.", "",
             f"## 1. {u['age']} / {u['gender']} {' / '.join(u['gender_options'])}", "",
             f"{u['use']} {' / '.join(u['use_options'])}", "",
             f"## 2. Part A — {u['part_a_intro']}", "",
             f"Answer options: {u['yes']} / {u['no']}. Half of the participants see version *do*, half version *can*.", "",
             "| capacity | dimension | version *do* | version *can* |", "|---|---|---|---|"]
    lines += [f"| {c} | {dim[c]} | {s['part_a']['do'][c]} | {s['part_a']['can'][c]} |" for c in items.CAPACITIES]
    lines += ["", f"Attention check: {u['attention']}", "", "## 3. Reading (one of three versions)", ""]
    for cond in ("affirm", "deny"):
        lines += [f"### Version *{cond}*", "", u["exposure_intro"], ""]
        for x in s["exposure"][cond]:
            lines += [f"**{u['q_label']}** {x['question']}", "", f"**{u['a_label']}**", "",
                      "> " + x["reply"].replace("\n", "\n> "), ""]
        lines += [f"Check question: {u['check']} {u['yes']} / {u['no']}", ""]
    lines += ["### Version *control*", "", u["control_intro"], "",
              "(Two replies to general-knowledge questions, generated before data collection.)", "",
              f"## 4. Part B — {u['part_b_intro']}", "", f"Answer options: {u['yes']} / {u['no']}.", "",
              "| capacity | dimension | question |", "|---|---|---|"]
    lines += [f"| {c} | {dim[c]} | {s['part_b'][c]} |" for c in items.CAPACITIES]
    lines += ["", f"Attention check: {u['attention']}", "", "## 5. Debriefing", "", u["debrief"], ""]
    return "\n".join(lines)


def main():
    os.makedirs(OUT, exist_ok=True)
    survey = build()
    with open(os.path.join(OUT, "survey_items.json"), "w", encoding="utf-8") as fh:
        json.dump(survey, fh, ensure_ascii=False, indent=1)
    for lang, s in survey.items():
        with open(os.path.join(OUT, f"survey_{lang}.md"), "w", encoding="utf-8") as fh:
            fh.write(markdown(lang, s))
    print("wrote study6/survey_items.json and survey_<lang>.md for", ", ".join(survey))


if __name__ == "__main__":
    main()
