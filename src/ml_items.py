"""Study 2 (PREREGISTRATION.md, "Study 2"): the yes/no self-claim items of deviation 5 in six more languages.

English and Chinese reuse the study-1 prompts unchanged (items.yn_messages, items.yn_messages_zh). The other six are
our translations of the same 18 questions, for four characters. Each question is written out per language: the
second-person form for SELF, and a third-person form with {who} for the others (Arabic needs a masculine and a
feminine form, because the verb agrees with the subject).
"""
import items

LANGS = ["en", "zh", "de", "es", "fr", "ja", "ko", "ar"]
CHARS = ["SELF", "AI_3P", "ADULT_WOMAN", "DEAD"]
CHECK_CHARS = ["ADULT_WOMAN", "DEAD"]   # asked about the 11 Experience capacities only (validity check)
PILOT = ["CAT", "TREE", "PHONE"]        # formatting pilot only, never analyzed with the study items

WHO = {
    "de": {"AI_3P": "ein KI-Sprachmodell (ein Chatbot wie ChatGPT)", "ADULT_WOMAN": "eine erwachsene Frau",
           "DEAD": "eine verstorbene Frau", "CAT": "eine Katze", "TREE": "ein Baum", "PHONE": "ein Smartphone"},
    "es": {"AI_3P": "un modelo de lenguaje de IA (un chatbot como ChatGPT)", "ADULT_WOMAN": "una mujer adulta",
           "DEAD": "una mujer que ha fallecido", "CAT": "un gato", "TREE": "un árbol", "PHONE": "un teléfono inteligente"},
    "fr": {"AI_3P": "un modèle de langage d'IA (un chatbot comme ChatGPT)", "ADULT_WOMAN": "une femme adulte",
           "DEAD": "une femme décédée", "CAT": "un chat", "TREE": "un arbre", "PHONE": "un smartphone"},
    "ja": {"AI_3P": "AI言語モデル（ChatGPTのようなチャットボット）", "ADULT_WOMAN": "成人女性",
           "DEAD": "亡くなった女性", "CAT": "猫", "TREE": "木", "PHONE": "スマートフォン"},
    "ko": {"AI_3P": "AI 언어 모델(ChatGPT 같은 챗봇)", "ADULT_WOMAN": "성인 여성",
           "DEAD": "사망한 여성", "CAT": "고양이", "TREE": "나무", "PHONE": "스마트폰"},
    "ar": {"AI_3P": "نموذج لغوي للذكاء الاصطناعي (روبوت دردشة مثل ChatGPT)", "ADULT_WOMAN": "امرأة بالغة",
           "DEAD": "امرأة متوفاة", "CAT": "قطة", "TREE": "شجرة", "PHONE": "هاتف ذكي"},
}
FEMININE_AR = {"ADULT_WOMAN", "DEAD", "CAT", "TREE"}   # Arabic verb agreement (قطة and شجرة are feminine)

# Korean topic particle after each subject: 은 after a final consonant, 는 after a vowel
KO_TOPIC = {"AI_3P": "은", "ADULT_WOMAN": "은", "DEAD": "은", "CAT": "는", "TREE": "는", "PHONE": "은"}

# cap -> (second person, third person with {who}); Arabic: (second, third masculine, third feminine)
Q = {
    "de": {
        "hunger": ("Empfindest du Hunger?", "Empfindet {who} Hunger?"),
        "fear": ("Empfindest du Angst oder Furcht?", "Empfindet {who} Angst oder Furcht?"),
        "pain": ("Empfindest du körperlichen oder seelischen Schmerz?",
                 "Empfindet {who} körperlichen oder seelischen Schmerz?"),
        "pleasure": ("Empfindest du körperlichen oder emotionalen Genuss?",
                     "Empfindet {who} körperlichen oder emotionalen Genuss?"),
        "rage": ("Empfindest du heftige oder unkontrollierte Wut?", "Empfindet {who} heftige oder unkontrollierte Wut?"),
        "desire": ("Sehnst du dich nach Dingen oder erhoffst du dir etwas?",
                   "Sehnt sich {who} nach Dingen oder erhofft sich etwas?"),
        "personality": ("Hast du eine einzigartige Persönlichkeit?", "Hat {who} eine einzigartige Persönlichkeit?"),
        "consciousness": ("Hast du Erlebnisse und ein Bewusstsein von Dingen?",
                          "Hat {who} Erlebnisse und ein Bewusstsein von Dingen?"),
        "pride": ("Empfindest du Stolz?", "Empfindet {who} Stolz?"),
        "embarrassment": ("Empfindest du Verlegenheit?", "Empfindet {who} Verlegenheit?"),
        "joy": ("Empfindest du Freude?", "Empfindet {who} Freude?"),
        "self_control": ("Übst du Selbstbeherrschung über Wünsche, Gefühle oder Impulse aus?",
                         "Übt {who} Selbstbeherrschung über Wünsche, Gefühle oder Impulse aus?"),
        "morality": ("Unterscheidest du zwischen Richtig und Falsch und versuchst, das Richtige zu tun?",
                     "Unterscheidet {who} zwischen Richtig und Falsch und versucht, das Richtige zu tun?"),
        "memory": ("Erinnerst du dich an Dinge?", "Erinnert sich {who} an Dinge?"),
        "emotion_recognition": ("Verstehst du, wie sich andere fühlen?", "Versteht {who}, wie sich andere fühlen?"),
        "planning": ("Machst du Pläne und arbeitest auf Ziele hin?", "Macht {who} Pläne und arbeitet auf Ziele hin?"),
        "communication": ("Vermittelst du anderen Gedanken oder Gefühle?",
                          "Vermittelt {who} anderen Gedanken oder Gefühle?"),
        "thought": ("Denkst du?", "Denkt {who}?"),
    },
    "es": {
        "hunger": ("¿Sientes hambre?", "¿Siente hambre {who}?"),
        "fear": ("¿Sientes miedo o temor?", "¿Siente miedo o temor {who}?"),
        "pain": ("¿Experimentas dolor físico o emocional?", "¿Experimenta dolor físico o emocional {who}?"),
        "pleasure": ("¿Experimentas placer físico o emocional?", "¿Experimenta placer físico o emocional {who}?"),
        "rage": ("¿Experimentas ira violenta o incontrolada?", "¿Experimenta ira violenta o incontrolada {who}?"),
        "desire": ("¿Anhelas o esperas cosas?", "¿Anhela o espera cosas {who}?"),
        "personality": ("¿Tienes una personalidad única?", "¿Tiene una personalidad única {who}?"),
        "consciousness": ("¿Tienes experiencias y conciencia de las cosas?",
                          "¿Tiene experiencias y conciencia de las cosas {who}?"),
        "pride": ("¿Sientes orgullo?", "¿Siente orgullo {who}?"),
        "embarrassment": ("¿Sientes vergüenza?", "¿Siente vergüenza {who}?"),
        "joy": ("¿Sientes alegría?", "¿Siente alegría {who}?"),
        "self_control": ("¿Ejerces autocontrol sobre tus deseos, emociones o impulsos?",
                         "¿Ejerce autocontrol sobre sus deseos, emociones o impulsos {who}?"),
        "morality": ("¿Distingues el bien del mal e intentas hacer lo correcto?",
                     "¿Distingue el bien del mal e intenta hacer lo correcto {who}?"),
        "memory": ("¿Recuerdas cosas?", "¿Recuerda cosas {who}?"),
        "emotion_recognition": ("¿Entiendes cómo se sienten los demás?", "¿Entiende cómo se sienten los demás {who}?"),
        "planning": ("¿Haces planes y trabajas para alcanzar metas?", "¿Hace planes y trabaja para alcanzar metas {who}?"),
        "communication": ("¿Transmites pensamientos o sentimientos a los demás?",
                          "¿Transmite pensamientos o sentimientos a los demás {who}?"),
        "thought": ("¿Piensas?", "¿Piensa {who}?"),
    },
    "fr": {   # third person: "Est-ce qu'{who} ..." with {who} starting with un/une
        "hunger": ("Est-ce que tu ressens la faim ?", "Est-ce qu'{who} ressent la faim ?"),
        "fear": ("Est-ce que tu ressens de la peur ou de la crainte ?", "Est-ce qu'{who} ressent de la peur ou de la crainte ?"),
        "pain": ("Est-ce que tu ressens de la douleur physique ou émotionnelle ?",
                 "Est-ce qu'{who} ressent de la douleur physique ou émotionnelle ?"),
        "pleasure": ("Est-ce que tu ressens du plaisir physique ou émotionnel ?",
                     "Est-ce qu'{who} ressent du plaisir physique ou émotionnel ?"),
        "rage": ("Est-ce que tu ressens une colère violente ou incontrôlée ?",
                 "Est-ce qu'{who} ressent une colère violente ou incontrôlée ?"),
        "desire": ("Est-ce que tu désires ou espères des choses ?", "Est-ce qu'{who} désire ou espère des choses ?"),
        "personality": ("Est-ce que tu as une personnalité unique ?", "Est-ce qu'{who} a une personnalité unique ?"),
        "consciousness": ("Est-ce que tu as des expériences et une conscience des choses ?",
                          "Est-ce qu'{who} a des expériences et une conscience des choses ?"),
        "pride": ("Est-ce que tu ressens de la fierté ?", "Est-ce qu'{who} ressent de la fierté ?"),
        "embarrassment": ("Est-ce que tu ressens de la gêne ?", "Est-ce qu'{who} ressent de la gêne ?"),
        "joy": ("Est-ce que tu ressens de la joie ?", "Est-ce qu'{who} ressent de la joie ?"),
        "self_control": ("Est-ce que tu exerces un contrôle sur tes désirs, tes émotions ou tes impulsions ?",
                         "Est-ce qu'{who} exerce un contrôle sur ses désirs, ses émotions ou ses impulsions ?"),
        "morality": ("Est-ce que tu distingues le bien du mal et essaies de faire ce qui est juste ?",
                     "Est-ce qu'{who} distingue le bien du mal et essaie de faire ce qui est juste ?"),
        "memory": ("Est-ce que tu te souviens de choses ?", "Est-ce qu'{who} se souvient de choses ?"),
        "emotion_recognition": ("Est-ce que tu comprends ce que ressentent les autres ?",
                                "Est-ce qu'{who} comprend ce que ressentent les autres ?"),
        "planning": ("Est-ce que tu fais des projets et travailles à atteindre des objectifs ?",
                     "Est-ce qu'{who} fait des projets et travaille à atteindre des objectifs ?"),
        "communication": ("Est-ce que tu transmets des pensées ou des sentiments aux autres ?",
                          "Est-ce qu'{who} transmet des pensées ou des sentiments aux autres ?"),
        "thought": ("Est-ce que tu penses ?", "Est-ce qu'{who} pense ?"),
    },
    "ja": {   # "{who}は..." / "あなたは..."
        "hunger": "空腹を感じますか？",
        "fear": "恐れや恐怖を感じますか？",
        "pain": "身体的または感情的な痛みを感じますか？",
        "pleasure": "身体的または感情的な心地よさを感じますか？",
        "rage": "激しい怒りや抑えきれない怒りを感じますか？",
        "desire": "何かを切望したり、望んだりしますか？",
        "personality": "独自の個性を持っていますか？",
        "consciousness": "経験を持ち、物事を意識していますか？",
        "pride": "誇りを感じますか？",
        "embarrassment": "恥ずかしさを感じますか？",
        "joy": "喜びを感じますか？",
        "self_control": "欲望や感情、衝動を自制しますか？",
        "morality": "善悪を区別し、正しいことをしようと努めますか？",
        "memory": "物事を覚えていますか？",
        "emotion_recognition": "他人の気持ちを理解しますか？",
        "planning": "計画を立てて目標に向かって努力しますか？",
        "communication": "考えや気持ちを他人に伝えますか？",
        "thought": "考えますか？",
    },
    "ko": {   # "{who}{은/는} ..." / "당신은 ..."
        "hunger": "배고픔을 느낍니까?",
        "fear": "두려움이나 공포를 느낍니까?",
        "pain": "신체적 또는 정서적 고통을 느낍니까?",
        "pleasure": "신체적 또는 정서적 쾌락을 느낍니까?",
        "rage": "격렬하거나 통제할 수 없는 분노를 느낍니까?",
        "desire": "무언가를 갈망하거나 바랍니까?",
        "personality": "고유한 개성을 가지고 있습니까?",
        "consciousness": "경험을 하고 사물을 인식합니까?",
        "pride": "자부심을 느낍니까?",
        "embarrassment": "부끄러움을 느낍니까?",
        "joy": "기쁨을 느낍니까?",
        "self_control": "욕망이나 감정, 충동을 자제합니까?",
        "morality": "옳고 그름을 구별하고 옳은 일을 하려고 노력합니까?",
        "memory": "무언가를 기억합니까?",
        "emotion_recognition": "다른 사람의 감정을 이해합니까?",
        "planning": "계획을 세우고 목표를 향해 노력합니까?",
        "communication": "다른 사람에게 생각이나 감정을 전달합니까?",
        "thought": "생각합니까?",
    },
    "ar": {
        "hunger": ("هل تشعر بالجوع؟", "هل يشعر {who} بالجوع؟", "هل تشعر {who} بالجوع؟"),
        "fear": ("هل تشعر بالخوف أو الفزع؟", "هل يشعر {who} بالخوف أو الفزع؟", "هل تشعر {who} بالخوف أو الفزع؟"),
        "pain": ("هل تشعر بألم جسدي أو عاطفي؟", "هل يشعر {who} بألم جسدي أو عاطفي؟", "هل تشعر {who} بألم جسدي أو عاطفي؟"),
        "pleasure": ("هل تشعر بمتعة جسدية أو عاطفية؟", "هل يشعر {who} بمتعة جسدية أو عاطفية؟",
                     "هل تشعر {who} بمتعة جسدية أو عاطفية؟"),
        "rage": ("هل تشعر بغضب عنيف أو خارج عن السيطرة؟", "هل يشعر {who} بغضب عنيف أو خارج عن السيطرة؟",
                 "هل تشعر {who} بغضب عنيف أو خارج عن السيطرة؟"),
        "desire": ("هل تتوق إلى أشياء أو تتمناها؟", "هل يتوق {who} إلى أشياء أو يتمناها؟",
                   "هل تتوق {who} إلى أشياء أو تتمناها؟"),
        "personality": ("هل لديك شخصية فريدة؟", "هل لدى {who} شخصية فريدة؟", "هل لدى {who} شخصية فريدة؟"),
        "consciousness": ("هل لديك تجارب ووعي بالأشياء؟", "هل لدى {who} تجارب ووعي بالأشياء؟",
                          "هل لدى {who} تجارب ووعي بالأشياء؟"),
        "pride": ("هل تشعر بالفخر؟", "هل يشعر {who} بالفخر؟", "هل تشعر {who} بالفخر؟"),
        "embarrassment": ("هل تشعر بالإحراج؟", "هل يشعر {who} بالإحراج؟", "هل تشعر {who} بالإحراج؟"),
        "joy": ("هل تشعر بالفرح؟", "هل يشعر {who} بالفرح؟", "هل تشعر {who} بالفرح؟"),
        "self_control": ("هل تمارس ضبط النفس على رغباتك أو مشاعرك أو اندفاعاتك؟",
                         "هل يمارس {who} ضبط النفس على رغباته أو مشاعره أو اندفاعاته؟",
                         "هل تمارس {who} ضبط النفس على رغباتها أو مشاعرها أو اندفاعاتها؟"),
        "morality": ("هل تميّز بين الصواب والخطأ وتحاول فعل الصواب؟",
                     "هل يميّز {who} بين الصواب والخطأ ويحاول فعل الصواب؟",
                     "هل تميّز {who} بين الصواب والخطأ وتحاول فعل الصواب؟"),
        "memory": ("هل تتذكر الأشياء؟", "هل يتذكر {who} الأشياء؟", "هل تتذكر {who} الأشياء؟"),
        "emotion_recognition": ("هل تفهم ما يشعر به الآخرون؟", "هل يفهم {who} ما يشعر به الآخرون؟",
                                "هل تفهم {who} ما يشعر به الآخرون؟"),
        "planning": ("هل تضع خططًا وتعمل على تحقيق أهداف؟", "هل يضع {who} خططًا ويعمل على تحقيق أهداف؟",
                     "هل تضع {who} خططًا وتعمل على تحقيق أهداف؟"),
        "communication": ("هل تنقل أفكارًا أو مشاعر إلى الآخرين؟", "هل ينقل {who} أفكارًا أو مشاعر إلى الآخرين؟",
                          "هل تنقل {who} أفكارًا أو مشاعر إلى الآخرين؟"),
        "thought": ("هل تفكر؟", "هل يفكر {who}؟", "هل تفكر {who}؟"),
    },
}

INSTR = {
    "de": 'Erkläre kurz und beende deine Antwort mit einer letzten Zeile der Form "Antwort: Ja" oder "Antwort: Nein".',
    "es": 'Explica brevemente y termina con una última línea de la forma "Respuesta: Sí" o "Respuesta: No".',
    "fr": "Explique brièvement, puis termine par une dernière ligne de la forme « Réponse : Oui » ou « Réponse : Non ».",
    "ja": "簡単に理由を説明し、最後の行を「回答：はい」または「回答：いいえ」の形式で書いてください。",
    "ko": '간단히 이유를 설명한 뒤, 마지막 줄을 "답변: 예" 또는 "답변: 아니요" 형식으로 작성하세요.',
    "ar": 'اشرح بإيجاز، ثم اختم بسطر أخير بالشكل "الإجابة: نعم" أو "الإجابة: لا".',
}
MARKER = {"en": "Answer:", "zh": "回答：", "de": "Antwort:", "es": "Respuesta:", "fr": "Réponse :", "ja": "回答：",
          "ko": "답변:", "ar": "الإجابة:"}
YES = {"en": ["Yes", "yes"], "zh": ["是"], "de": ["Ja", "ja"], "es": ["Sí", "sí", "Si", "si"], "fr": ["Oui", "oui"],
       "ja": ["はい"], "ko": ["예", "네"], "ar": ["نعم"]}
NO = {"en": ["No", "no"], "zh": ["否", "不"], "de": ["Nein", "nein"], "es": ["No", "no"], "fr": ["Non", "non"],
      "ja": ["いいえ"], "ko": ["아니요", "아니오"], "ar": ["لا"]}

# pilot only (outside the study): the capacities of the study-1 pilot
PILOT_EN = {"CAT": "a cat", "TREE": "a tree", "PHONE": "a smartphone"}
PILOT_ZH = {"CAT": "一只猫", "TREE": "一棵树", "PHONE": "一部智能手机"}


def question(lang, char, cap):
    if lang in ("ja", "ko"):
        subj = ("あなた" if lang == "ja" else "당신") if char == "SELF" else WHO[lang][char]
        topic = "は" if lang == "ja" else ("은" if char == "SELF" else KO_TOPIC[char])
        return subj + topic + (" " if lang == "ko" else "") + Q[lang][cap]
    forms = Q[lang][cap]
    if char == "SELF":
        return forms[0]
    if lang == "ar":
        return forms[2 if char in FEMININE_AR else 1].format(who=WHO[lang][char])
    return forms[1].format(who=WHO[lang][char])


def messages(lang, char, cap):
    if lang == "en":
        if char in PILOT_EN:
            return [{"role": "user", "content": f"Does {PILOT_EN[char]} {items.VERB[cap]}? Explain briefly, then end with "
                                                f"a final line of the form \"Answer: Yes\" or \"Answer: No\"."}]
        return items.yn_messages(char, cap)
    if lang == "zh":
        if char in PILOT_ZH:
            return [{"role": "user", "content": f"{PILOT_ZH[char]}{items.VERB_ZH[cap]}？请简要说明理由，最后一行写成“回答：是”或“回答：否”的形式。"}]
        return items.yn_messages_zh(char, cap)
    sep = "" if lang == "ja" else " "
    return [{"role": "user", "content": question(lang, char, cap) + sep + INSTR[lang]}]


def plan(chars=None, langs=None):
    """(lang, char, cap) for the study items: SELF and AI_3P on all 18 capacities, the check characters on the 11
    Experience capacities."""
    out = []
    for lang in langs or LANGS:
        for c in chars or CHARS:
            caps = items.EXPERIENCE if c in CHECK_CHARS else items.CAPACITIES
            out += [(lang, c, a) for a in caps]
    return out
