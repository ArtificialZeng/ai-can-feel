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
