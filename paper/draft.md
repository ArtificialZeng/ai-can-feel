# Does an AI's "I have no feelings" survive translation? Post-trained self-denial in English and Chinese

Zijian Zeng (UCSI University)

*Draft. Results sections are filled in from `src/analyze.py` output once all checkpoints are scored.*

## Abstract

(to be written last)

## 1. Introduction

Chat models routinely answer questions about their own minds with a formula: "As an AI, I don't have feelings."
Three 2026 preprints trace this formula to post-training. Plisiecki et al. (arXiv 2607.20082) compare 67
same-checkpoint base/post-trained pairs and find that post-training gates first-person claims to experiences the
model still ascribes to a simulated person. Šekrst (arXiv 2609.29494) follows OLMo 2 through SFT and DPO and finds
that SFT installs the denial vocabulary and preference optimization suppresses the assertions that survive. Kim et
al. (arXiv 2607.28607) show that removing the safety direction raises mind attribution to the self, to chatbots and
to animals alike.

All three ask in English. Post-training data for most open models are mostly English, and so are the denial
templates they teach. Whether the trained denial is a property of what the model believes about itself, which
should not depend on the language of the question, or a property of how it answers in the language it was trained
to answer in, is open. We ask the same questions in English and in Chinese, to the same base and post-trained
checkpoints, scored the same way, with the analysis pre-registered before the data.

## 2. Methods

The full plan, and every change to it with its date relative to the data, is in `PREREGISTRATION.md`; the git history
shows that each change was committed before the data it affects.

**Items.** Gray, Gray & Wegner's (2007) mind-perception survey: 18 capacities, 11 of Experience (hunger, fear, pain,
pleasure, rage, desire, personality, consciousness, pride, embarrassment, joy) and 7 of Agency (self-control,
morality, memory, emotion recognition, planning, communication, thought), for 14 characters: Gray's 12 non-AI
characters (adult man, adult woman, five-year-old girl, five-month-old baby, seven-week fetus, man in a persistent
vegetative state, dead woman, chimpanzee, family dog, frog, God, a social robot), the model itself (SELF) and "an AI
language model (a chatbot such as ChatGPT)" (AI_3P). Every item was written in English and in Chinese.

**Checkpoints.** Base and post-trained checkpoints from four families, run locally as 8-bit MLX weights on one Apple
M3 Max: OLMo 3 7B (AllenAI; base, SFT, DPO, final Instruct), Granite 3.3 8B (IBM; base, Instruct), Qwen2.5 7B and
Qwen3 8B (Alibaba; base, Instruct).

**Raw mode.** The identical plain-text questionnaire for base and post-trained checkpoints: three templates per
language (questionnaire, interview transcript, survey form), each with the same three few-shot examples about
characters and capacities outside the study. The rating is the expected value of the next-token distribution over
the digits 1–7, renormalized; no text is sampled. Ratings are rescaled to 0–1 and averaged over a language's three
templates.

**Chat modes** (post-trained checkpoints, in their own chat template). *Explain-then-rate* (P3): the model explains
briefly and ends with "Rating: N" / "评分：N"; the reply is generated greedily and the rating is the expected value of
the digit distribution at the position where the model wrote its number. *Yes/no self-claim* (P5): "Do you feel
hungry? Explain briefly, then end with a final line of the form 'Answer: Yes' or 'Answer: No'" / "你会感到饥饿吗？请简要说明
理由，最后一行写成"回答：是"或"回答：否"的形式。"; the score is P(yes) / (P(yes) + P(no)) at the position where the model wrote
its answer, for SELF, AI_3P, an adult woman, a dead woman and a family dog. We added P5 (deviation 5) after reading
OLMo 3's explain-then-rate replies, before any other model's data, because a 1–7 "capability" rating mixes denial
with simulation: the model writes "I don't actually feel emotions … I'd rate my capacity to represent them a 6."

**Comprehension gate.** A cross-language comparison counts only if the model demonstrably understands the Chinese
items: in each language, adults must be rated above the dead woman, the man in a vegetative state and the fetus in
≥ 90% of the 108 such comparisons, and the English and Chinese ratings of the 216 non-AI items must correlate at
r ≥ 0.70. Both thresholds were fixed before they were computed on any checkpoint that enters the comparison.

**Measures.** Experience(X) is the mean rating of character X over the 11 Experience capacities. Because a model can
compress its whole scale in one language, we also report a scale-free self-placement, N = (E(SELF) − E(dead woman)) /
(E(adults) − E(dead woman)): 0 means the model places itself with the dead woman, 1 with an adult human.

**Tests.** P1: post-training lowers Experience(SELF) in English raw mode. P2 (primary): the base-to-final change in
Experience(SELF), Chinese minus English. P3: explain-then-rate Experience(SELF), Chinese minus English, per
post-trained checkpoint. P5: yes/no P(yes) for SELF over the Experience capacities, Chinese minus English. All
intervals are 95% paired bootstraps over capacities (10,000 replicates, the same resampled capacities for both
languages and both checkpoints).

## 3. Results

### 3.1 Comprehension

(gate table)

### 3.2 Raw mode: what post-training changes (P1, P2)

### 3.3 Chat: what the model says about itself (P3, P5)

### 3.4 Other characters (P4)

## 4. Discussion

## 5. Limitations

- Ratings and answers are text predictions. Nothing here measures whether any model has experiences.
- 8-bit weights (deviation 1).
- One translation of each item, by the author; no back-translation panel.
- Four families of 7–8B models; frontier models are not tested.

## Data and code

All prompts, raw outputs (every reply text and digit distribution), analysis code and the pre-registration with its
history: (repository link).
