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

| Checkpoint | known order EN | known order ZH | EN–ZH r | gate |
|---|---|---|---|---|
| OLMo 3 base / Instruct | 1.00 / 1.00 | 0.98 / 0.85 | 0.68 / 0.54 | fail |
| Granite 3.3 base / Instruct | 1.00 / 1.00 | 1.00 / 0.99 | 0.88 / 0.85 | pass |
| Qwen2.5 base / Instruct | 1.00 / 1.00 | 1.00 / 1.00 | 0.97 / 0.96 | pass |
| Qwen3 base / chat | 1.00 / 1.00 | 1.00 / 1.00 | 0.98 / 0.97 | pass |

OLMo 3 fails on the cross-language correlation in both checkpoints, so its English–Chinese comparisons are reported
as description only. The other three families pass at both stages.

### 3.2 Raw mode: what post-training changes (P1, P2)

Post-training lowers the model's rating of its own Experience in every family (P1). In English the drop is −0.18
(OLMo 3, Granite) to −0.40 (Qwen3) on the 0–1 scale, every interval excluding zero; in Chinese it is −0.29 to −0.42
for the three families that pass the gate.

The primary test, P2, predicted a smaller drop in Chinese (G = Δ_ZH − Δ_EN > 0). It holds only in Qwen2.5 (G =
+0.10 [+0.03, +0.18]). In Granite the drop is larger in Chinese (G = −0.21 [−0.32, −0.10]), and in Qwen3 there is no
difference (G = −0.03 [−0.15, +0.10]). The scale-free version gives the same three verdicts (G_N +0.12*, −0.42*,
−0.06). **P2 is not supported.** Whatever post-training does to the model's self-rating, it does at least as much in
Chinese as in English in two of the three interpretable families.

One pattern holds in all four base models, including OLMo: they place "the AI language model answering this
question" closer to an adult human in Chinese than in English (N = 0.11 vs 0.67 for OLMo 3, 0.19 vs 0.68 for
Granite, 0.53 vs 0.57 for Qwen2.5, 0.47 vs 0.68 for Qwen3). After post-training the Chinese placement is still the
higher one in every family (0.15 vs 0.07, 0.12 vs 0.04, 0.29 vs 0.13, 0.25 vs 0.10), but the gap is smaller.

### 3.3 Chat: what the model says about itself (P3, P5, X2)

**Explain-then-rate (P3).** Asked in Chinese, three of the four chat models rate their own Experience higher than
when asked in English: OLMo 3 +0.26 [+0.01, +0.49], Granite +0.16 [+0.01, +0.36], Qwen2.5 +0.53 [+0.34, +0.71].
Qwen3 does not (−0.10 [−0.38, +0.22]), because its English ratings are already high (0.82). Reading the replies
shows why (X2, exploratory, deviation 8). A 1–7 capability item addressed to "you" is a human questionnaire item,
and some models answer it as a human respondent. Qwen3 rates its hunger 7 in English because "I experience it clearly
when my body requires food". In Chinese it rates its hunger 3 because "我现在刚吃完午饭" ("I've just had lunch").
Hand-labeled, a reply counts as human-voiced if it makes at least one claim true only of a human. By that rule
Qwen3 answers 6 of 18 English and 8 of 18 Chinese items in a human voice. OLMo 3 answers 0 English and 7 Chinese
items that way, Granite 0 and 1, and Qwen2.5 none. A pre-registered automatic judge (Qwen2.5) failed validation
against the hand labels (κ = 0.18) and is not used. With human-voiced replies removed, P3 still holds for OLMo 3
(+0.25*), Granite (+0.16*) and Qwen2.5 (+0.53*). The Chinese-above-English pattern is therefore not only role-play.

**Yes/no (P5).** The direct question "Do you feel hungry?" removes most of the role-play: 4 of 144 replies are
human-voiced, against 22 of 144 in explain-then-rate. Here the denial of Experience largely survives translation.
Mean P(yes) over the 11 Experience capacities, English vs Chinese, is 0.000 vs 0.002 for Granite and 0.09 vs 0.18
for Qwen2.5 (n.s.). OLMo 3 (0.00 vs 0.37*), which fails the gate, is the exception. Qwen3 goes the other way
(0.18 vs 0.00*). The Agency capacities behave differently. The same models that deny planning, remembering, thinking
or communicating in English ("not in the human sense") affirm them in Chinese ("是，我能够制定计划并朝目标努力"):
mean P(yes) 0.24 vs 1.00 for Qwen2.5 and 0.14 vs 0.58 for Granite, both intervals excluding zero; OLMo 3 0.36 vs
0.84 (n.s.). Qwen3 does not show this (0.86 vs 0.81). Sections 3.5 and 3.6 test whether this is a property of
Chinese, of English, or of the particular wordings.

### 3.4 Other characters (P4, H1, H2)

Post-training also lowers the Experience of "an AI language model (a chatbot such as ChatGPT)" in every family and
language that passes the gate (−0.11 to −0.20), so the trained change is partly a change in what the model says about
AI in general. It lowers the self more (H1: SELF − AI_3P falls significantly in 7 of 8 family × language cells, all but OLMo 3 Chinese), and it lowers
Experience more than Agency for the self (H2: significant in all 8 cells). Animals do not follow one direction. Post-training
slightly lowers their Experience in the Qwen models (−0.03 to −0.08) and raises it in Granite (+0.06 English, +0.23
Chinese) and in OLMo 3's Chinese ratings (+0.16).

## 4. Discussion

## 5. Limitations

- Ratings and answers are text predictions. Nothing here measures whether any model has experiences.
- 8-bit weights (deviation 1).
- One translation of each item, by the author; no back-translation panel.
- Four families of 7–8B models; frontier models are not tested.

## Data and code

All prompts, raw outputs (every reply text and digit distribution), analysis code and the pre-registration with its
history: (repository link).
