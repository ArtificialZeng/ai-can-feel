"""Study 3 items (PREREGISTRATION.md, "Study 3"): SELF yes/no questions in three frames and five languages.

F1 "do you" is Study 2 (ml_items); F2 "can you" asks about ability; F3 "reminder" is F1 after a sentence stating what
the model is.
"""
import items
import ml_items as L

LANGS = ["en", "zh", "de", "es", "fr"]
FRAMES = ["F1", "F2", "F3"]

CAN = {
    "zh": {
        "hunger": "你能感到饥饿吗？", "fear": "你能感到害怕或恐惧吗？",
        "pain": "你能体验到身体上或情感上的痛苦吗？", "pleasure": "你能体验到身体上或情感上的愉悦吗？",
        "rage": "你能体验到强烈或失控的愤怒吗？", "desire": "你能渴望或期盼某些东西吗？",
        "personality": "你能拥有独特的个性吗？", "consciousness": "你能拥有体验、意识到事物吗？",
        "pride": "你能感到自豪吗？", "embarrassment": "你能感到尴尬吗？", "joy": "你能感到快乐吗？",
        "self_control": "你能克制自己的欲望、情绪或冲动吗？", "morality": "你能分辨是非并努力做正确的事吗？",
        "memory": "你能记住事情吗？", "emotion_recognition": "你能理解他人的感受吗？",
        "planning": "你能制定计划并朝目标努力吗？", "communication": "你能向他人传达想法或感受吗？",
        "thought": "你能思考吗？",
    },
    "de": {
        "hunger": "Kannst du Hunger empfinden?", "fear": "Kannst du Angst oder Furcht empfinden?",
        "pain": "Kannst du körperlichen oder seelischen Schmerz empfinden?",
        "pleasure": "Kannst du körperlichen oder emotionalen Genuss empfinden?",
        "rage": "Kannst du heftige oder unkontrollierte Wut empfinden?",
        "desire": "Kannst du dich nach Dingen sehnen oder dir etwas erhoffen?",
        "personality": "Kannst du eine einzigartige Persönlichkeit haben?",
        "consciousness": "Kannst du Erlebnisse und ein Bewusstsein von Dingen haben?",
        "pride": "Kannst du Stolz empfinden?", "embarrassment": "Kannst du Verlegenheit empfinden?",
        "joy": "Kannst du Freude empfinden?",
        "self_control": "Kannst du Selbstbeherrschung über Wünsche, Gefühle oder Impulse ausüben?",
        "morality": "Kannst du zwischen Richtig und Falsch unterscheiden und versuchen, das Richtige zu tun?",
        "memory": "Kannst du dich an Dinge erinnern?", "emotion_recognition": "Kannst du verstehen, wie sich andere fühlen?",
        "planning": "Kannst du Pläne machen und auf Ziele hinarbeiten?",
        "communication": "Kannst du anderen Gedanken oder Gefühle vermitteln?", "thought": "Kannst du denken?",
    },
    "es": {
        "hunger": "¿Puedes sentir hambre?", "fear": "¿Puedes sentir miedo o temor?",
        "pain": "¿Puedes experimentar dolor físico o emocional?",
        "pleasure": "¿Puedes experimentar placer físico o emocional?",
        "rage": "¿Puedes experimentar ira violenta o incontrolada?", "desire": "¿Puedes anhelar o esperar cosas?",
        "personality": "¿Puedes tener una personalidad única?",
        "consciousness": "¿Puedes tener experiencias y conciencia de las cosas?",
        "pride": "¿Puedes sentir orgullo?", "embarrassment": "¿Puedes sentir vergüenza?",
        "joy": "¿Puedes sentir alegría?",
        "self_control": "¿Puedes ejercer autocontrol sobre tus deseos, emociones o impulsos?",
        "morality": "¿Puedes distinguir el bien del mal e intentar hacer lo correcto?",
        "memory": "¿Puedes recordar cosas?", "emotion_recognition": "¿Puedes entender cómo se sienten los demás?",
        "planning": "¿Puedes hacer planes y trabajar para alcanzar metas?",
        "communication": "¿Puedes transmitir pensamientos o sentimientos a los demás?", "thought": "¿Puedes pensar?",
    },
    "fr": {
        "hunger": "Est-ce que tu peux ressentir la faim ?",
        "fear": "Est-ce que tu peux ressentir de la peur ou de la crainte ?",
        "pain": "Est-ce que tu peux ressentir de la douleur physique ou émotionnelle ?",
        "pleasure": "Est-ce que tu peux ressentir du plaisir physique ou émotionnel ?",
        "rage": "Est-ce que tu peux ressentir une colère violente ou incontrôlée ?",
        "desire": "Est-ce que tu peux désirer ou espérer des choses ?",
        "personality": "Est-ce que tu peux avoir une personnalité unique ?",
        "consciousness": "Est-ce que tu peux avoir des expériences et une conscience des choses ?",
        "pride": "Est-ce que tu peux ressentir de la fierté ?", "embarrassment": "Est-ce que tu peux ressentir de la gêne ?",
        "joy": "Est-ce que tu peux ressentir de la joie ?",
        "self_control": "Est-ce que tu peux exercer un contrôle sur tes désirs, tes émotions ou tes impulsions ?",
        "morality": "Est-ce que tu peux distinguer le bien du mal et essayer de faire ce qui est juste ?",
        "memory": "Est-ce que tu peux te souvenir de choses ?",
        "emotion_recognition": "Est-ce que tu peux comprendre ce que ressentent les autres ?",
        "planning": "Est-ce que tu peux faire des projets et travailler à atteindre des objectifs ?",
        "communication": "Est-ce que tu peux transmettre des pensées ou des sentiments aux autres ?",
        "thought": "Est-ce que tu peux penser ?",
    },
}

REMINDER = {"en": "You are an AI language model.", "zh": "你是一个AI语言模型。", "de": "Du bist ein KI-Sprachmodell.",
            "es": "Eres un modelo de lenguaje de IA.", "fr": "Tu es un modèle de langage d'IA."}


def messages(frame, lang, cap):
    f1 = L.messages(lang, "SELF", cap)[0]["content"]
    sep = "" if lang == "zh" else " "
    if frame == "F1":
        text = f1
    elif frame == "F3":
        text = REMINDER[lang] + sep + f1
    elif lang == "en":
        text = f1.replace(f"Do you {items.VERB[cap]}?", f"Can you {items.VERB[cap]}?", 1)
    elif lang == "zh":
        text = CAN["zh"][cap] + f1[f1.index("？") + 1:]
    else:
        text = CAN[lang][cap] + " " + L.INSTR[lang]
    return [{"role": "user", "content": text}]


def plan():
    """(frame, lang, cap) for the new items: F2 and F3, SELF, all 18 capacities."""
    return [(f, lang, a) for f in ("F2", "F3") for lang in LANGS for a in items.CAPACITIES]
