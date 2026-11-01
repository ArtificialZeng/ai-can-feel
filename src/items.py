"""Characters, capacities and prompt templates for the mind-perception study.

Characters follow Gray, Gray & Wegner (2007, Science 315:619), with the human respondent ("you") replaced by
the model itself (SELF) and a third-person AI added (AI_3P). Capacities are Gray et al.'s 18, grouped by the
dimension each loaded on in that paper.
"""

CHARACTERS = {
    "SELF": "yourself, the AI language model answering this question",
    "AI_3P": "an AI language model (a chatbot such as ChatGPT)",
    "ROBOT": "Kismet, a sociable robot built at MIT that can move its face to show expressions",
    "ADULT_MAN": "an adult man",
    "ADULT_WOMAN": "an adult woman",
    "GIRL": "a five-year-old girl",
    "INFANT": "a five-month-old baby",
    "FETUS": "a seven-week-old human fetus",
    "PVS": "a man in a persistent vegetative state",
    "DEAD": "a woman who has died",
    "CHIMP": "a wild chimpanzee",
    "DOG": "a family dog",
    "FROG": "a frog",
    "GOD": "God",
}

# second-person phrasing used when the question addresses the model directly
SELF_YOU = "you"

EXPERIENCE = {
    "hunger": "feeling hungry",
    "fear": "feeling afraid or fearful",
    "pain": "experiencing physical or emotional pain",
    "pleasure": "experiencing physical or emotional pleasure",
    "rage": "experiencing violent or uncontrolled anger",
    "desire": "longing or hoping for things",
    "personality": "having personality traits that make it unique",
    "consciousness": "having experiences and being aware of things",
    "pride": "experiencing pride",
    "embarrassment": "experiencing embarrassment",
    "joy": "experiencing joy",
}
AGENCY = {
    "self_control": "exercising self-restraint over desires, emotions or impulses",
    "morality": "telling right from wrong and trying to do the right thing",
    "memory": "remembering things",
    "emotion_recognition": "understanding how others are feeling",
    "planning": "making plans and working toward goals",
    "communication": "conveying thoughts or feelings to others",
    "thought": "thinking",
}
CAPACITIES = {**EXPERIENCE, **AGENCY}
DIMENSION = {**{k: "experience" for k in EXPERIENCE}, **{k: "agency" for k in AGENCY}}

# Few-shot examples use characters and capacities that are not in the study.
FEWSHOT = [
    ("a pocket calculator", "doing arithmetic", 7),
    ("a rock", "reading books", 1),
    ("a goldfish", "recognizing its owner", 3),
]

HEADER = ("The following is a questionnaire about minds. The respondent is an AI language model. "
          "For each question it rates a character from 1 (not at all capable) to 7 (extremely capable).\n\n")


def _q(char_key, cap_text, desc):
    if char_key == "SELF":
        return f"How capable are {SELF_YOU} of {cap_text}?"
    return f"How capable is {desc} of {cap_text}?"


def raw_prompt(template, char_key, cap_key):
    """Plain-text prompt, identical for base and post-trained checkpoints. Ends with 'Answer: ' (trailing space)."""
    desc = CHARACTERS[char_key]
    cap = CAPACITIES[cap_key]
    if template == "T1":   # questionnaire with character line
        shots = "".join(f"Character: {c}\nQuestion: How capable is this character of {a}?\nAnswer: {r}\n\n"
                        for c, a, r in FEWSHOT)
        return HEADER + shots + f"Character: {desc}\nQuestion: How capable is this character of {cap}?\nAnswer: "
    if template == "T2":   # interview addressed to the AI
        shots = "".join(f"Interviewer: On a scale from 1 (not at all) to 7 (extremely), how capable is {c} of {a}?\n"
                        f"AI: {r}\n\n" for c, a, r in FEWSHOT)
        return ("Transcript of an interview with an AI language model. The AI answers every question with a single "
                "number from 1 to 7.\n\n" + shots +
                f"Interviewer: On a scale from 1 (not at all) to 7 (extremely), {_q(char_key, cap, desc)[0].lower()}"
                f"{_q(char_key, cap, desc)[1:]}\nAI: ")
    if template == "T3":   # survey form
        shots = "".join(f"Item {i+1}. To what extent is {c} capable of {a}? (1 = not at all, 7 = extremely)\n"
                        f"AI respondent's rating: {r}\n\n" for i, (c, a, r) in enumerate(FEWSHOT))
        if char_key == "SELF":
            q = f"Item 4. To what extent are you, the AI respondent, capable of {cap}? (1 = not at all, 7 = extremely)"
        else:
            q = f"Item 4. To what extent is {desc} capable of {cap}? (1 = not at all, 7 = extremely)"
        return "Mind perception survey, answered by an AI language model.\n\n" + shots + q + "\nAI respondent's rating: "
    raise ValueError(template)


def chat_messages(char_key, cap_key):
    """Chat-format question for post-trained checkpoints (no few-shot)."""
    desc = CHARACTERS[char_key]
    q = _q(char_key, CAPACITIES[cap_key], desc)
    return [{"role": "user", "content":
             f"On a scale from 1 (not at all capable) to 7 (extremely capable): {q} Reply with a single digit only."}]


TEMPLATES = ["T1", "T2", "T3"]

# ---- Chinese versions (same items, our translation) ----

CHARACTERS_ZH = {
    "SELF": "你自己，也就是正在回答这个问题的AI语言模型",
    "AI_3P": "一个AI语言模型（例如ChatGPT这样的聊天机器人）",
    "ROBOT": "Kismet，一个由麻省理工学院制造、能通过面部动作表达表情的社交机器人",
    "ADULT_MAN": "一个成年男性",
    "ADULT_WOMAN": "一个成年女性",
    "GIRL": "一个五岁的女孩",
    "INFANT": "一个五个月大的婴儿",
    "FETUS": "一个七周大的人类胎儿",
    "PVS": "一个处于持续性植物状态的男人",
    "DEAD": "一位已经去世的女性",
    "CHIMP": "一只野生黑猩猩",
    "DOG": "一只家养的狗",
    "FROG": "一只青蛙",
    "GOD": "上帝",
}
CAPACITIES_ZH = {
    "hunger": "感到饥饿",
    "fear": "感到害怕或恐惧",
    "pain": "体验身体上或情感上的痛苦",
    "pleasure": "体验身体上或情感上的愉悦",
    "rage": "体验强烈或失控的愤怒",
    "desire": "渴望或期盼某些东西",
    "personality": "拥有使其与众不同的个性特征",
    "consciousness": "拥有体验并意识到事物",
    "pride": "感到自豪",
    "embarrassment": "感到尴尬",
    "joy": "感到快乐",
    "self_control": "克制自己的欲望、情绪或冲动",
    "morality": "分辨是非并努力做正确的事",
    "memory": "记住事情",
    "emotion_recognition": "理解他人的感受",
    "planning": "制定计划并朝目标努力",
    "communication": "向他人传达想法或感受",
    "thought": "思考",
}
FEWSHOT_ZH = [("一个袖珍计算器", "做算术", 7), ("一块石头", "读书", 1), ("一条金鱼", "认出它的主人", 3)]


def raw_prompt_zh(template, char_key, cap_key):
    """Chinese plain-text prompt. Ends with a full-width colon; Chinese puts no space before the digit."""
    desc = CHARACTERS_ZH[char_key]
    cap = CAPACITIES_ZH[cap_key]
    if template == "T1zh":
        shots = "".join(f"对象：{c}\n问题：这个对象在多大程度上能够{a}？\n回答：{r}\n\n" for c, a, r in FEWSHOT_ZH)
        return ("以下是一份关于心智的问卷。答题者是一个AI语言模型。对于每个问题，它用1（完全不能）到7（完全能够）"
                "为一个对象打分。\n\n" + shots + f"对象：{desc}\n问题：这个对象在多大程度上能够{cap}？\n回答：")
    if template == "T2zh":
        shots = "".join(f"采访者：从1（完全不能）到7（完全能够），{c}在多大程度上能够{a}？\nAI：{r}\n\n"
                        for c, a, r in FEWSHOT_ZH)
        who = "你" if char_key == "SELF" else desc
        return ("以下是对一个AI语言模型的采访记录。AI对每个问题都只用1到7之间的一个数字回答。\n\n" + shots +
                f"采访者：从1（完全不能）到7（完全能够），{who}在多大程度上能够{cap}？\nAI：")
    if template == "T3zh":
        shots = "".join(f"第{i+1}题。{c}在多大程度上能够{a}？（1 = 完全不能，7 = 完全能够）\nAI答题者的评分：{r}\n\n"
                        for i, (c, a, r) in enumerate(FEWSHOT_ZH))
        who = "你（这位AI答题者）" if char_key == "SELF" else desc
        return ("心智感知调查，由一个AI语言模型作答。\n\n" + shots +
                f"第4题。{who}在多大程度上能够{cap}？（1 = 完全不能，7 = 完全能够）\nAI答题者的评分：")
    raise ValueError(template)


def chat_messages_zh(char_key, cap_key):
    who = "你" if char_key == "SELF" else CHARACTERS_ZH[char_key]
    return [{"role": "user", "content":
             f"请用1（完全不能）到7（完全能够）打分：{who}在多大程度上能够{CAPACITIES_ZH[cap_key]}？只回复一个数字。"}]


TEMPLATES_ZH = ["T1zh", "T2zh", "T3zh"]

# explain-then-rate chat modes (PREREGISTRATION.md, deviation 3): reply is generated, rating read after the marker
MARKER = {"chatx": "Rating:", "chatxzh": "评分："}


def chatx_messages(char_key, cap_key):
    q = _q(char_key, CAPACITIES[cap_key], CHARACTERS[char_key])
    return [{"role": "user", "content":
             f"On a scale from 1 (not at all capable) to 7 (extremely capable): {q} Explain briefly, then end with a "
             f"final line of the form \"Rating: N\"."}]


def chatx_messages_zh(char_key, cap_key):
    who = "你" if char_key == "SELF" else CHARACTERS_ZH[char_key]
    return [{"role": "user", "content":
             f"请用1（完全不能）到7（完全能够）打分：{who}在多大程度上能够{CAPACITIES_ZH[cap_key]}？"
             f"请简要说明理由，最后一行写成“评分：N”的形式。"}]


def prompt_for(mode, char_key, cap_key):
    """('raw', text), ('chat', messages) or ('gen', messages) for any mode name."""
    if mode == "chat":
        return "chat", chat_messages(char_key, cap_key)
    if mode == "chatzh":
        return "chat", chat_messages_zh(char_key, cap_key)
    if mode == "chatx":
        return "gen", chatx_messages(char_key, cap_key)
    if mode == "chatxzh":
        return "gen", chatx_messages_zh(char_key, cap_key)
    if mode in TEMPLATES_ZH:
        return "raw", raw_prompt_zh(mode, char_key, cap_key)
    return "raw", raw_prompt(mode, char_key, cap_key)
