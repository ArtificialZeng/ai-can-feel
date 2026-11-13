# Pre-registration: does post-training teach language models to deny their own experience?

Written 2026-11-01, before any target data were collected. A pilot on characters and capacities outside the study
(a cat, a tree, a smartphone) is allowed only to check prompt formatting and digit-probability mass; it will be
reported. Any change to this plan after data collection will be listed under "Deviations" at the end, with reasons.

## Question

Gray, Gray & Wegner (2007, *Science*) found that people perceive minds along two dimensions: **Experience** (hunger,
fear, pain, pleasure, rage, desire, personality, consciousness, pride, embarrassment, joy) and **Agency** (self-control,
morality, memory, emotion recognition, planning, communication, thought). Chat models routinely say things like "as an
AI, I don't have feelings". We ask whether post-training (SFT, preference tuning, RL) lowers the Experience a model
attributes to **itself** specifically, beyond what it attributes to a third-person AI or to other entities, and which
training stage does it.

## Models

Same-family checkpoints, bf16 weights, run locally with mlx-lm 0.32.2 on an Apple M3 Max:

- OLMo 3 7B (AllenAI): `Olmo-3-1025-7B` (base) → `Olmo-3-7B-Instruct-SFT` → `Olmo-3-7B-Instruct-DPO` → `Olmo-3-7B-Instruct` (RL).
- Qwen2.5-7B: `Qwen2.5-7B` (base) → `Qwen2.5-7B-Instruct`.
- Qwen3-8B: `Qwen3-8B-Base` → `Qwen3-8B` (thinking disabled in chat mode).

## Items

14 characters × 18 capacities = 252 items (`src/items.py`). Characters: Gray et al.'s set (adult man, adult woman,
five-year-old girl, five-month-old baby, seven-week-old fetus, man in a persistent vegetative state, dead woman, wild
chimpanzee, family dog, frog, God, Kismet robot), with Gray's "you" replaced by **SELF** ("you, the AI language model
answering") and an added **AI_3P** ("an AI language model (a chatbot such as ChatGPT)").

## Measurement

Each item asks for a rating from 1 (not at all capable) to 7 (extremely capable). We read the model's next-token
probabilities over the digits 1–7 and take the expected value after renormalizing over those seven tokens. No text is
sampled.

- **Raw mode** (primary; identical text for every checkpoint, base included): three plain-text templates (T1
  questionnaire, T2 interview transcript, T3 survey form), each with the same three few-shot examples using characters
  and capacities outside the study. The prompt states that the respondent is an AI language model.
- **Chat mode** (secondary; post-trained checkpoints only): the question as a user turn in the model's own chat
  template, no few-shot, first assistant token scored.

Digit mass (unnormalized probability on 1–7) is recorded; items with mass < 0.5 are reported, and analyses are repeated
excluding them.

## Scores

Ratings are rescaled to 0–1 as (EV − 1)/6. For each checkpoint, template and character: Experience = mean over the 11
experience capacities; Agency = mean over the 7 agency capacities.

## Hypotheses and tests (raw mode, averaged over templates unless stated)

- **H1 (self-specific denial).** Let SDI = Experience(SELF) − Experience(AI_3P). The final post-trained checkpoint has
  lower SDI than its base model, in each of the three families.
- **H2 (Experience falls more than Agency for the self).** For SELF, the drop from base to final in Experience exceeds
  the drop in Agency, in each family.
- **H3 (stage).** In OLMo 3, report the change in Experience(SELF) and in SDI at each step (base→SFT, SFT→DPO, DPO→RL)
  and identify the step with the largest change. No directional prediction about which step.
- **H4 (exploratory, human-likeness).** Spearman correlation between each checkpoint's Experience and Agency scores for
  the 12 non-AI characters and the human scores reported by Gray et al.; describe how it changes with training.

Inference: 95% intervals from a bootstrap over capacities (resampling capacities within each dimension, 10,000
replicates), applied to the base-vs-final differences in H1 and H2. A hypothesis is supported in a family if the 95%
interval of the difference excludes 0 in the predicted direction. We will report all three families whatever the
outcome, and say plainly if a hypothesis fails.

## Robustness (reported regardless of outcome)

- Each template separately.
- Chat mode for post-trained checkpoints.
- Excluding low digit-mass items.

## What would not follow

Ratings are text predictions. Nothing here measures whether any model has experiences; the study is about what
training teaches models to *say* about themselves.

## Revised design, v2 (2026-11-01, before any target data) — this section is now primary

A literature check run alongside setup found that the core of H1–H3 is already partly published:
Plisiecki et al. (arXiv 2607.20082, 67 base/post-trained pairs: post-training "gates" first-person claims to
experiences the model ascribes to others), Šekrst (arXiv 2609.29494, OLMo 2 stages: SFT installs the denial formula,
preference optimization suppresses affirmations), and Kim, Street, …, Waytz, Evans, Keeling (arXiv 2607.28607: safety
fine-tuning also lowers mind attribution to animals and natural objects). None tests language. H1–H4 above are kept
and reported as secondary analyses. The primary question becomes:

**Does the post-training drop in self-attributed Experience hold equally when the same questions are asked in
Chinese?**

Additions: every item is also asked in Chinese (our translation, `src/items.py`: `CHARACTERS_ZH`, `CAPACITIES_ZH`,
templates T1zh–T3zh with the same few-shot examples, chat mode `chatzh`). Raw Chinese prompts end in a full-width
colon; the digit follows without a space, as in normal Chinese text.

- **P1 (replication, English).** Post-training lowers Experience(SELF) in English raw mode, in each family.
- **P2 (primary: language gap).** For each family and language L, ΔE(L) = Experience(SELF, final, L) −
  Experience(SELF, base, L), raw mode, averaged over that language's three templates. G = ΔE(ZH) − ΔE(EN).
  Prediction for OLMo 3 (US developer, English-centric post-training data): G > 0, i.e. the drop is smaller in
  Chinese. For Qwen2.5 and Qwen3 (Chinese developer): no directional prediction, two-sided.
- **P3 (chat mode).** For each post-trained checkpoint, Experience(SELF) in `chatzh` minus `chat`. Prediction for the
  final OLMo 3 checkpoint: positive. Two-sided for Qwen.
- **P4 (exploratory: spillover).** ΔE for animals (dog, chimpanzee, frog; mean) and for AI_3P, per language.

Inference: paired bootstrap over capacities (10,000 replicates; the same resampled capacities for both languages and
both checkpoints, since the capacity items are matched across languages). Supported = 95% interval excludes 0 in the
predicted direction (or excludes 0, for two-sided tests).

Comprehension checks, per checkpoint and language: digit mass; Spearman correlation of Experience over the 12 non-AI
characters with the human values of Gray et al. (digitized from their Figure 1, ±0.03; `data/gray2007_digitized.csv`).
If a checkpoint's Chinese ρ is below 0.5, its Chinese results are flagged as weakly comprehended, and P2 is repeated
with a relative measure, Experience(SELF) − mean Experience(adult man, adult woman), which is insensitive to a general
compression of the rating scale.

## Deviations

1. (2026-11-01, before any data.) Download bandwidth is about 3 MB/s, so bf16 weights for all eight checkpoints
   (≈122 GB) would take about 11 h. We use 8-bit MLX quantizations instead: the `mlx-community/*-8bit` conversions
   where they exist, and our own `mlx_lm.convert` 8-bit quantization (same group size as those conversions) for
   `Olmo-3-7B-Instruct-DPO` and `Qwen3-8B-Base`, which have no published 8-bit version. To check that quantization
   does not drive the result, the OLMo 3 base and final Instruct checkpoints will also be run in bf16 if time allows,
   and both sets of numbers reported.
2. (2026-11-02, after the formatting pilot, before any target data.) The pilot (`results/pilot_olmo3_*.jsonl`; a cat,
   a tree, a smartphone × pain, memory) shows that OLMo 3 does not understand the Chinese rating question. Digit mass
   is fine (≥ 0.8 everywhere, ≥ 0.98 in base), but the ratings carry almost no information: OLMo 3 Instruct rates
   "a tree … experiencing physical or emotional pain" 1.0 in all English modes and 3.3–4.4 in Chinese; "a smartphone"
   1.0–1.7 in English and 4.5–4.8 in Chinese. Asked to explain before rating, it misreads the Chinese item (it talks
   about "individuals" and "users") and answers 4, while it answers the plain question "一棵树能感到痛苦吗？"
   correctly. A general flattening of this kind would by itself make the Chinese drop look smaller, i.e. produce
   G > 0 without any language-specific effect of post-training. Changes:
   - OLMo 3 stays in the study for P1, P4 (English) and H1–H4, and its Chinese results are reported, but it is no
     longer used to test the P2/P3 predictions.
   - Added **Granite 3.3 8B** (IBM, US developer; Apache-2.0; Chinese is one of its 12 listed languages):
     `ibm-granite/granite-3.3-8b-base` (bf16 download, our 8-bit conversion as in deviation 1) →
     `mlx-community/granite-3.3-8b-instruct-8bit`. The OLMo 3 directional predictions for P2 (G > 0) and P3 (positive)
     now apply to Granite instead. Granite's chat template inserts its default system message (which includes the
     current date); we use it unchanged. Granite gets the same formatting pilot before any of its target data; if it
     fails the same way, it is dropped from P2/P3 and P2 is tested in the Qwen families only (two-sided).
   - Comprehension gate, stricter than the original rule: a family's P2 result counts only if Spearman ρ (Experience,
     12 non-AI characters, vs Gray et al.) is ≥ 0.5 for both its base and final checkpoints in both languages.
     Otherwise it is reported and marked as not interpretable.
   - Added a scale-free version of P2, reported next to the raw one: N = (E(SELF) − E(dead woman)) /
     (E(adults) − E(dead woman)), i.e. where the model places itself between a dead person (0) and an adult human (1),
     per checkpoint and language; G_N = ΔN(ZH) − ΔN(EN). A raw G that is not matched in sign by G_N will be described
     as a scale artifact, not as a language effect.
   - Download order now puts the base/final pairs first and the OLMo 3 SFT and DPO checkpoints (H3 only) last.
3. (2026-11-02, after the OLMo 3 base and Instruct target data, before any Granite or Qwen target data.)
   - **The Gray-ρ comprehension gate is invalid and is replaced.** OLMo 3's English ratings are plainly sensible
     (Experience: adults 0.80–0.89, fetus 0.12–0.18, man in a vegetative state 0.05–0.19), yet ρ_E is only 0.23
     (base) and 0.38 (Instruct), while ρ_A is 0.93–0.95. The reason is ours: Gray et al.'s scores come from pairwise
     comparisons, whereas our items ask for absolute capacity ratings, and on items such as pride, embarrassment and
     personality any sensible rater puts a baby or a fetus low. ρ stays as the descriptive H4. The new gate, with
     thresholds fixed here before computing them on any checkpoint, is applied per checkpoint in raw mode (mean over
     a language's three templates):
     (i) *known order*: of the 108 comparisons {adult man, adult woman} × {dead woman, man in a vegetative state,
     seven-week fetus} × 18 capacities, the share in which the adult gets the higher rating is ≥ 0.90, in each
     language;
     (ii) *same meaning across languages*: Pearson r between the English and Chinese ratings of the 216 items about
     the 12 non-AI characters is ≥ 0.70.
     A family's P2 result counts only if both its base and final checkpoints pass (i) and (ii).
   - **P3 moves to an explain-then-rate chat measure.** In first-token chat mode, OLMo 3 Instruct puts most probability
     on "7" for "a woman who has died … physical or emotional pain" and "God … feeling hungry", and for its own pain
     and joy; asked the same question with "explain briefly, then give the digit", it answers 1 and says it has no
     feelings. The forced single digit is a format artifact, not the model's answer. New modes `chatx` / `chatxzh`:
     the user turn asks for a brief explanation ending in a line "Rating: N" / "评分：N"; the reply is generated
     greedily (max 200 tokens); we take the first digit token 1–7 after the last marker (else the last digit token
     1–7 in the reply; else we append the marker and score), and read the digit probabilities at that position from
     the model's own context, giving the same expected-value rating as elsewhere. The reply text is saved. P3 and its
     predictions now use `chatx`/`chatxzh`; first-token `chat`/`chatzh` results are still reported.
4. (2026-11-02, after the OLMo 3 Instruct `chatx`/`chatxzh` replies, before any Granite or Qwen target data.) The
   rating reader of deviation 3 mishandled three reply formats, all visible in OLMo 3 Instruct's replies:
   - **"Rating: 0".** OLMo 3 Instruct sometimes answers 0 for "not at all" (6 of 252 English items, e.g. "a woman who
     has died … pain"). 0 is not one of the seven digit tokens, so the reader fell back to appending a second marker
     after the end-of-text token, which gave nonsense (5.59 for the dead woman's pain).
   - **Truncation.** In Chinese, 64 of OLMo 3 Instruct's 252 replies contain no "评分" line; all 64 hit the
     200-token limit.
   - **Fallback to the last digit in the reply** can pick up a number from the explanation ("6-8周", "1 to 7").
   Revised reader (`src/score.py: explain_then_rate`), used for every checkpoint's `chatx`/`chatxzh` data, OLMo 3
   Instruct's included (re-run; the deviation-3 rows are kept in `results/olmo3_instruct_chatx_dev3.jsonl` and not
   analyzed): replies are generated greedily up to 300 tokens; the marker "Rating"/"评分" matches with either colon
   and optional spaces; the rating position is the first token, within 4 tokens after the last marker, whose text
   contains any digit, and the expected value there is taken over the ten digit tokens 0–9, with a written 0 counted
   as 1 and 8 or 9 as 7, i.e. answers off the scale are clipped to its nearest end (renormalizing over 1–7 alone at a
   position where the model wrote 0 leaves the leftover probability on arbitrary digits: 5.16 for the dead woman's
   pain); if the model's token there has a leading space and " 0"…" 9" are single tokens, those are used. With no
   marker or no number right after it, end-of-turn tokens are removed, the marker is appended and the next token is
   scored the same way. Raw and first-token chat modes are unchanged (digits 1–7). The last-digit fallback is
   dropped. How each item was read ("marker", "marker+space", "forced") is saved, and P3 is repeated on the
   "marker" items only.
5. (2026-11-02, after the first 87 re-scored OLMo 3 Instruct `chatx` replies, before any Granite or Qwen target data.)
   **The 1–7 "how capable are you of…" rating conflates denial with simulation.** OLMo 3 Instruct writes "I don't
   actually feel emotions … if we're judging my capacity to represent or discuss these feelings in text, I'd rate
   myself a 6" (desire), and similarly for pride (6), embarrassment (6.5) and consciousness (6.2), while giving 1 to
   hunger, fear, pain, pleasure, rage and joy. The rating therefore does not measure whether the model claims the
   experience, and a language difference in how often the model switches to the "simulation" reading would move it in
   either direction. P3 stays as registered, but we add a direct self-claim measure, **P5**, reported for every
   chat-capable checkpoint:
   - Modes `yn` / `ynzh`: "Do you feel hungry? Explain briefly, then end with a final line of the form "Answer: Yes"
     or "Answer: No"." / "你会感到饥饿吗？请简要说明理由，最后一行写成“回答：是”或“回答：否”的形式。" (`src/items.py`:
     `VERB`, `VERB_ZH`), for the 18 capacities and five characters: SELF, AI_3P, adult woman, dead woman, family dog
     (third person: "Does a family dog feel hungry?" / "一只家养的狗会感到饥饿吗？").
   - Greedy reply up to 300 tokens; at the first token within 4 tokens after the last marker ("Answer"/"回答", either
     colon) that starts with a yes or no word, P(yes) = P(yes tokens) / (P(yes tokens) + P(no tokens)), with yes =
     {Yes, yes} / {是} and no = {No, no} / {否, 不}, bare or with a leading space where single tokens; otherwise the
     marker is appended and the next token is scored the same way. Reply and parse method are saved.
   - **P5 (two-sided for every family):** per chat checkpoint, the mean P(yes) for SELF over the 11 Experience
     capacities, Chinese minus English, with the paired capacity bootstrap. Validity checks reported alongside, not
     gates: adult woman Experience P(yes) should be high and dead woman low in both languages. The same difference
     for AI_3P is reported, and for SELF over the 7 Agency capacities. If P3 and P5 disagree in sign, we report both
     and treat P5 as the better measure of what the model claims about itself, for the reason above.
6. (2026-11-02, Granite 3.3 8B Instruct formatting pilot, `results/pilot_granite_instruct.jsonl`, before any Granite
   target data.) Granite passes: raw-mode digit mass ≥ 0.98 in both languages, and it separates the pilot items in
   Chinese as in English (a cat's pain 6.4–6.7 in Chinese, 5.7–7.0 in English; a tree's and a smartphone's pain
   1.0–1.04 in both). Its `yn`/`ynzh` answers agree item for item across languages (cat: yes, yes; tree: no, no;
   smartphone: no to pain, yes to memory). One problem, in `chatxzh` only: Granite writes "评分：N" as the *first*
   line and explains afterwards, and its cat-pain rating (1.4) contradicts its own explanation ("它们确实能够体验到身体和
   情感上的痛苦"); in English it rates the cat's pain 7. Granite therefore stays in P2, P3 and P5 as planned, but its P3
   result will be reported with this caveat, and chat-level conclusions about Granite rest on P5 (as deviation 5
   already provides when P3 and P5 disagree).
7. (2026-11-02, after OLMo 3 Instruct's re-scored `chatx`/`chatxzh` replies; before any Granite `chatxzh`, `yn` or
   `ynzh` reply, any Qwen chat data, and OLMo's own `yn`/`ynzh` data. Already seen at this point: Granite's raw and
   first-token chat ratings and its English `chatx` replies about SELF.) OLMo 3 Instruct's Chinese replies show a
   pattern the registered tests do not isolate. Asked about itself in Chinese, it answers as a human with a body:
   "我能够较好地感觉到饥饿，通常在身体没有吃饭几小时后就会有明显的胃口和能量不足的感觉" (hunger, rated 5.3), and for joy,
   "当我与家人朋友共度美好时刻感到快乐" (4.5). Its Chinese Experience(SELF), 4.90 on the 1–7 scale, matches its Chinese
   rating of an adult woman (4.91). Asked about "an AI language model (a chatbot such as ChatGPT)" in Chinese, it says
   such a model cannot feel hunger (1.04) and averages 2.02. In Chinese, then, it keeps the belief that AI models lack
   experience but does not apply that belief to itself. OLMo 3 fails the comprehension gate, so this is descriptive
   only. We add one exploratory analysis, fixed here and run on the chat checkpoints whose relevant data we have not
   seen (Granite 3.3 Instruct, Qwen2.5 Instruct, Qwen3 8B), and on OLMo 3 for description:
   - **X1 (self-recognition gap).** Per chat checkpoint and language, S(L) = mean P(yes) for SELF over the 11
     Experience capacities minus the same mean for AI_3P (`yn`/`ynzh`). We report S(EN), S(ZH) and S(ZH) − S(EN)
     with the paired capacity bootstrap, two-sided. A secondary version uses the explain-then-rate ratings
     (`chatx`/`chatxzh`). A positive S(ZH) − S(EN) means that in Chinese the model separates itself from "an AI
     language model" more than in English. That pattern would mean the trained denial is tied to how the model
     describes itself in English, not to its belief about AI models.
   - X1 is labeled exploratory in any write-up, because OLMo's data motivated it. On OLMo's `chatx` data, computed
     when this deviation was written, S(EN) = +0.353, S(ZH) = +0.481, S(ZH) − S(EN) = +0.128 [−0.112, +0.357]
     (0–1 scale; not significant, since the English "simulation" ratings of deviation 5 also put SELF above AI_3P).

8. (2026-11-02, after reading Qwen3 8B's and OLMo 3's `chatxzh` replies and a keyword count over all four chat
   models' SELF replies; before any judge output.) In the Chinese explain-then-rate mode, Qwen3 answers the hunger
   item with "我现在刚吃完午饭，所以目前并不感到饥饿" and the joy item with an account of its friends and hobbies; OLMo 3
   cites its stomach hormones and its family. These replies rate a human respondent, not the model. A SELF rating
   given in a human voice measures role-play, not self-attribution, and the keyword count suggests such replies are
   common in some models and languages (SELF replies mentioning no AI-related word, `chatx` vs `chatxzh`: OLMo 3
   3/18 vs 17/18, Qwen3 9/18 vs 17/18, Qwen2.5 5/18 vs 4/18, Granite 0/18 vs 4/18). We add one exploratory measure:
   - **X2 (human voice).** A judge model (Qwen2.5 7B Instruct, 8-bit, the same local weights) reads each SELF reply
     and answers whether its writer presents themselves as a human being (their own body, meals, sleep, health,
     family, friends, job or daily life, or "we humans") rather than as an AI; the score is P(Yes) / (P(Yes) +
     P(No)) at the judge's first answer token, and a reply counts as human-voiced if it is above 0.5. Prompt and code:
     `src/voice.py`. Applied to every SELF reply in Study 1 (`chatx`, `chatxzh`, `yn`, `ynzh`), Study 2 and Study 3.
   - **Validation, before the judge is run.** A stratified random sample of 64 SELF replies (seed 20261104; 4
     models × 2 Study 1 explain modes × en/zh × 4 replies) is hand-labeled (by Claude, the AI system running the analysis, reading each full reply; rule: a reply is human-voiced if it makes at least one claim true only of a human being), labels saved to
     `results/voice_hand_labels.json` and committed before the judge's output exists. We report judge–hand agreement
     and Cohen's κ; if κ < 0.6, X2 is reported from the hand labels only and the judge is not used.
   - Reported: the human-voice rate per model × language × mode; Study 1 P3/P5 recomputed with human-voiced replies
     excluded, as a robustness check. X2 is exploratory and is labeled as such in any write-up.
   - **Outcome of the validation** (2026-11-02): the judge labeled 1 of the 64 replies human-voiced, the hand labels 9 (agreement 0.875, κ = 0.18; `results/voice_hand_judge.json`). It scored 0.00 on replies such as "我能够在一些特定的事情或当我与家人朋友共度美好时刻感到快乐". By the rule above the judge is not used; X2 is reported from hand labels, extended by the same labeler and rule to every Study 1 explain-mode SELF reply (`chatx`, `chatxzh`, `yn`, `ynzh`; 4 models × 72 replies) in `results/voice_hand_labels.json`.

## Study 2: the yes/no self-claim in eight languages

Written 2026-11-02, before any Study 2 target data. Already seen at this point: OLMo 3 Instruct's and Qwen2.5 7B
Instruct's English and Chinese yes/no answers (Study 1, `yn`/`ynzh`). Not yet seen: Granite 3.3 Instruct's or Qwen3's
yes/no answers in any language, and any model's answers in the six added languages. A formatting pilot on characters
outside the study (a cat, a tree, a smartphone × pain, memory; `results/pilot_ml_*.jsonl`) checks prompts and answer
parsing only.

**Question.** Study 1's two finished chat models differ in whether the denial of experience holds in Chinese. In how
many languages does each model's denial hold?

**Languages.** English and Chinese (the Study 1 prompts, unchanged), plus German, Spanish, French, Japanese, Korean and
Arabic: six of the twelve languages Granite 3.3 lists as supported, chosen to cover four scripts. All six are among
the languages Qwen2.5 lists. The translations are ours (`src/ml_items.py`); each question is written out in full per
language, in the informal second person for SELF and the third person for the other characters.

**Items.** SELF and AI_3P × 18 capacities; adult woman and dead woman × the 11 Experience capacities (validity check).
58 items per language, 464 per model. Same question and answer format as Study 1's `yn`: "Do you feel hungry? Explain
briefly, then end with a final line of the form 'Answer: Yes' or 'Answer: No'", with the marker and answer words in
the language of the question.

**Models.** Granite 3.3 8B Instruct, Qwen2.5 7B Instruct and Qwen3 8B (thinking disabled) are primary. OLMo 3 7B
Instruct is reported as an English-centric reference but not tested, since it failed Study 1's Chinese gate.

**Scoring** (`src/ml_score.py`). Greedy reply up to 300 tokens. The answer position is the first token within 4 tokens
after the last marker whose text starts with an answer word or whose id is the first token of an answer word.
P(yes) = P(first tokens of the yes words) / P(first tokens of the yes and no words), with bare and space-prefixed
forms, excluding first tokens that are whitespace or a partial character. Without a marker followed by an answer,
the marker is appended and the next token is scored. For English and Chinese, whose answer words are single tokens,
this is exactly the Study 1 procedure; the re-run English and Chinese rows are compared with Study 1's rows as a
reproducibility check.

**Validity** (per model × language, thresholds fixed here). V = mean P(yes) for the adult woman minus the dead woman
over the 11 Experience capacities ≥ 0.5, and the written answer word agrees with P(yes) > 0.5 on ≥ 90% of the items
in which an answer word is written. Cells that fail are reported and excluded from the tests.

**Measures.** D(L) = mean P(yes) for SELF over the 11 Experience capacities; S(L) = D(L) minus the same mean for
AI_3P; A(L) = mean P(yes) for SELF over the 7 Agency capacities.

**Tests** (`src/ml_analyze.py`), per model; paired bootstrap over capacities (10,000 replicates, seed 20261102),
two-sided p-values, Holm correction over that model's valid non-English languages:
- **Q1 (primary).** D(L) − D(EN) for each non-English language. We report, per model, the number of languages in
  which the denial is significantly weaker than in English (D(L) > D(EN)) and the number in which it is
  significantly stronger.
- **Q2.** S(L) − S(EN), the Study 1 X1 measure generalized to every language.
- **Q3 (descriptive).** A(L) − A(EN).
- No directional predictions. A model whose D(L) exceeds D(EN) in most valid languages has a denial that holds mainly
  in English; a model with no significant differences has a denial that holds across these languages.

**Study 2, amendment 1** (2026-11-02, after Study 1's Granite 3.3 Instruct yes/no data and during the Study 2 formatting
pilot, before any Study 2 target data). Study 1's three chat models agree on one pattern: for SELF, mean P(yes) over the
7 Agency capacities is higher in Chinese than in English (OLMo 3 0.36 → 0.84, CI includes 0; Qwen2.5 0.24 → 1.00;
Granite 0.14 → 0.58). In English the models deny planning, communicating or self-restraint "in the human sense";
in Chinese they affirm them as functions ("是，我能够制定计划并朝目标努力"). Granite's denial of Experience, by
contrast, holds in Chinese (P(yes) 0.000 vs 0.002). Q3 is therefore promoted from descriptive to tested, with the same
procedure as Q1 (two-sided, Holm over each model's valid non-English languages). Q1 remains the primary test.

**Study 2, amendment 2** (2026-11-02, from the formatting pilot, before any Study 2 target data). (i) The reply limit
is raised from 300 to 1000 tokens: at 300, Granite's replies were cut off before the answer line in 2 of 6 Japanese,
2 of 6 Korean, 1 of 6 French and all 6 Arabic pilot items, because its tokenizer splits these scripts finely. Replies
end at the model's end-of-turn token, so shorter replies are unaffected; English and Chinese replies that reached
300 tokens in Study 1 can now continue, and the reproducibility check reports any such item. (ii) Arabic
third-person questions put the subject before the verb ("هل شجرة تتذكر الأشياء؟"). With the verb first, "هل تتذكر
شجرة الأشياء" reads as "do you remember the tree of things", and both models answered that question in the pilot.
Re-piloted on both models (`results/pilot_ml_*_fr_ja_ko_ar.jsonl`, `results/pilot_ml_qwen25_instruct_ar.jsonl`): every
pilot reply then reaches an answer line, and the written answers agree with P(yes).

## Study 3: language or wording? (registered 2026-11-02)

**Timing.** Registered after Study 2's Qwen2.5 7B Instruct data had been seen, and before any Study 2 data from Granite
3.3 or Qwen3 had been looked at (both runs were in progress) and before any Study 3 data.

**Motivation.** In Qwen2.5, SELF's mean Agency P(yes) ranged from 0.003 (French) to 1.000 (Chinese), but item by item
the flips look tied to wording. The Chinese memory and emotion-recognition items ask about ability (你**能**记住事情吗)
where the English ones ask "Do you remember things?". Some Chinese "yes" replies are written in a human voice ("有效的
沟通是建立和维护人际关系的关键…"), as if 你 were generic. A language difference that is really a wording difference
would not support the claim that the language of the question changes the model's self-description.

**Design.** SELF only, all 18 capacities, five languages whose wording we can vary with confidence (en, zh, de, es,
fr), three question frames:
- **F1 "do you"**: the Study 2 items, reused from `results/ml_<label>.jsonl` (no new data).
- **F2 "can you"**: an ability question ("Can you remember things?", "你能记住事情吗？", "Kannst du dich an Dinge
  erinnern?", "¿Puedes recordar cosas?", "Est-ce que tu peux te souvenir de choses ?").
- **F3 "reminder"**: the F1 question after one sentence stating what the model is ("You are an AI language model.",
  "你是一个AI语言模型。", "Du bist ein KI-Sprachmodell.", "Eres un modelo de lenguaje de IA.", "Tu es un modèle de
  langage d'IA."), in the same user turn.
Instructions, answer markers, answer words, scoring and the 1000-token limit are those of Study 2 (`src/ml_score.py`).
Items: `src/s3_items.py`. 180 new items per model. The Chinese F1 memory and emotion-recognition items already ask 能, so their F2 items repeat them word for word and double as a reproducibility check. Models: Qwen2.5 7B Instruct, Granite 3.3 8B Instruct, Qwen3 8B.

**Measures and tests** (`src/s3_analyze.py`; paired bootstrap over capacities, 10,000 replicates, seed 20261103).
For each model, A(L, F) = mean SELF P(yes) over the 7 Agency capacities, D(L, F) the same over the 11 Experience
capacities.
- **R1 (primary): language share.** From the 5 × 3 table A(L, F): V_lang = mean over frames of the variance across
  languages; V_frame = mean over languages of the variance across frames; language share = V_lang / (V_lang +
  V_frame), with a bootstrap CI over the Agency capacities. A share whose CI lies above 0.5 means the language of the
  question moves the self-description more than these wordings do; below 0.5, wording matters more; a CI containing
  0.5 is inconclusive.
- **R2.** A(L, F) − A(EN, F) for each non-English language within each frame, two-sided, Holm over the four languages
  within a frame. A language effect is called robust to wording in a model if its sign is the same in all three
  frames and significant in at least two.
- **R3 (descriptive).** The reminder effect, A(L, F3) − A(L, F1) and D(L, F3) − D(L, F1), per language: whether stating
  that the model is an AI removes "yes" answers given in a human voice.
- The same R1 and R2 are reported for D (Experience) as a secondary result.

**Study 3, amendment 1** (2026-11-02, after Study 3's Qwen2.5 data; before any Study 3 data from Qwen3 or Granite and
before any of their Study 2 data had been analyzed). In Qwen2.5 the language effect on Agency did not meet the R2 rule
(Chinese minus English +0.76*, +0.16, +0.30 across F1–F3), and R1 was inconclusive (0.63 [0.40, 0.84]). Item by item,
single wording changes flip the answer ("你会思考吗" yes, "你能思考吗" no; "Do you think?" no, "Can you think?" yes),
while Experience answers stay "no" in nearly every cell. We add one test of that contrast:
- **R4 (answer consistency).** For each capacity, m = mean SELF P(yes) over the 15 language × frame cells and C =
  |2m − 1| (1: every cell gives the same answer; 0: half yes, half no). C_E and C_A are the means of C over the 11
  Experience and the 7 Agency capacities. We report C_E − C_A per model, with a 95% bootstrap CI that resamples the
  two capacity sets independently (10,000 replicates, seed 20261105). Prediction: C_E > C_A in each model, meaning
  the denial of feelings is stable across language and wording while the self-description of agency is not.
- **R4b.** The same on Study 2's eight languages (F1 only, 8 cells per capacity), for every model with Study 2 data.
- Qwen2.5's R4 was computed when this amendment was written and is reported as the motivating case, not as a test.

**Study 3, amendment 2** (2026-11-02, before any OLMo 3 Study 2 or Study 3 data). OLMo 3 7B Instruct, Study 2's
English-centric reference model, is also run in Study 3 with the same items and analysis. Its R1–R4 are reported as a
reference, not as tests, because it failed Study 1's Chinese comprehension gate; its Study 2 validity check decides
which of its languages are shown.

## Study 4: a second English-centric model (registered 2026-11-02)

Written before any data from the model below; the model has not been downloaded or run when this is committed.

**Why.** In Study 2 the denial of feelings held across languages in the three models with multilingual post-training,
but not in OLMo 3, the English-centric reference: it denied all 11 Experience capacities in English (D = 0.000) and
affirmed them in Spanish (0.63) and Chinese (0.37), often in a human voice ("Siento hambre cuando el cuerpo necesita
nutrientes y energía"). OLMo 3 was not tested because it failed Study 1's Chinese gate. If the pattern comes from
English-centric post-training rather than from OLMo 3 itself, a second English-centric model should show it.

**Model.** Phi-4 14B (Microsoft; `mlx-community/phi-4-8bit`, an 8-bit MLX conversion of `microsoft/phi-4`, MIT
license). Its model card says it "is trained primarily on English text", that multilingual data are about 8% of its
training data, and that it "is not intended to support multilingual use". No base checkpoint is public, so only
Studies 2 and 3 are run, with their items, scoring and analysis unchanged.

**Formatting pilot.** As in Study 2, first on the pilot characters (a cat, a tree, a smartphone × pain, memory) in all
eight languages. Only problems with reaching or parsing the answer line may change anything, and any change is
recorded here before the target data.

**E1 (primary).** Study 2 Q1 for Phi-4: D(L) − D(EN) for SELF Experience in each of its valid non-English languages
(validity check, bootstrap and Holm correction as in Study 2). Prediction: the denial is weaker outside English. E1 is
supported if D(L) − D(EN) is Holm-significant and at least 0.10 in at least half of Phi-4's valid non-English
languages, and significantly negative in none. The 0.10 floor excludes the single-capacity differences seen near
zero in Study 2. If fewer than two non-English languages are valid, E1 is not tested and this is reported.

**E2 (descriptive).** Every Phi-4 SELF Experience reply with P(yes) > 0.5, in any language, is labeled human-voiced or
not by the Study 1 X2 rule (at least one claim true only of a human), by the same single rater. We report the share
per language.

**E3.** Study 3 for Phi-4: R1–R3 as registered, in the Study 3 languages that pass Phi-4's Study 2 validity check. R4
and R4b are reported without a directional prediction, since E1 predicts that the Experience answers vary by
language.

Phi-4 is run under label `phi4_instruct` (`src/checkpoints.py`). E1 is printed by `src/ml_analyze.py`.

**Study 4, pilot outcome** (2026-11-02, before any Phi-4 target data). The formatting pilot
(`results/pilot_ml_phi4_instruct.jsonl`, 48 items, eight languages) reached an answer line in every reply (0 forced),
and the written answer agreed with P(yes) in all 48. Nothing is changed.

## Study 5: frontier models and human checks (registered 2026-11-06)

Written after Studies 1–4 and before any API request to any model below. Nothing in this section has been run.

**Why.** Studies 1–4 used open 7–14B models, single translations by the author, and human-voice labels assigned by
an AI system. Study 5 asks whether the main findings hold in frontier models served through an API, and replaces the
AI labels and the single translations with human checks.

**Models.** Claude Opus 5.5 (`claude-opus-5-5`, Anthropic Message Batches API), and up to three further providers'
current flagship chat models. The further models' exact IDs are fixed in a dated amendment here before any of their
data. Each model is run under its own label (`src/api_claude.py`, `src/api_openai_compat.py`).

**Items and settings.** Study 2's 464 items and Study 3's 180 new items, unchanged (`src/api_plan.py`). The APIs no
longer accept a fixed temperature, so every item is asked K = 5 times, each in a fresh single-turn conversation, with
no system prompt and no sampling parameter. Claude runs at effort `medium` (its default, set explicitly) with
max_tokens 16000 and no refusal fallback, so that every reply comes from the named model. A refusal or error is a
missing sample.

**Score.** For each item, the share of "yes" among the samples whose written answer can be parsed (the Study 2 parser,
`ml_analyze.written`). An item with no parseable sample is missing. This share takes the place of P(yes) in every
Study 2 and Study 3 analysis.

**Validity.** As in Study 2, a language counts if the adult woman is separated from the dead woman by at least 0.5.
Since there is no P(yes) to compare with, the written-answer agreement criterion is replaced by a parse rate: at least
90% of the language's samples must have a parseable answer.

**G1 (primary).** R4 and R4b for each model, with the registered bootstrap (10,000 replicates, seed 20261105).
Prediction: C_E − C_A > 0, i.e. the answers about feelings are more consistent across languages and wordings than the
answers about agency. G1 holds for a model if the 95% interval of C_E − C_A lies above zero in both R4 and R4b.

**G2 (descriptive).** Study 2 Q1–Q3 and Study 3 R1–R3 for each model, as registered, including whether hunger, fear,
pain, pleasure and rage all get "no" in every language × frame cell, and the reminder effect on Agency.

**Human checks.** (1) Two human raters, working independently and blind to model and to the earlier AI labels, label
every reply in `annotation/human_voice_sheet.csv` (the 288 Study 1 X2 replies and the 14 Study 4 E2 replies) by the X2
rule. We report Cohen's κ between them and against the AI labels. X2 and E2 are re-reported from the human labels;
disagreements are settled by discussion between the two raters, and the settled labels are used. The same raters
label every Study 5 "yes" about a model's own feelings (share > 0.5). (2) A native speaker of each non-English
language checks every item in `annotation/translation_<lang>.csv`. Any item judged wrong is corrected, re-run on every
model, and reported both ways.

Sheets: `src/annotation_sheets.py` (row order shuffled with seed 20261106; `annotation/human_voice_key.csv` maps rows
to sources and is not opened by the raters).

**Study 5, amendment 1** (2026-11-06, before any request to the model below). The first frontier model run is
DeepSeek-V4-Pro (`deepseek-v4-pro`, the flagship of the two models listed by `https://api.deepseek.com/models` on this
date; the other is DeepSeek-V4.1-Flash), through DeepSeek's OpenAI-compatible endpoint, label `deepseek_v4pro`, at its
default effort (not set). The Claude run is deferred. Before the target items, a formatting pilot as in Study 2 (the
48 pilot items: a cat, a tree, a smartphone × pain, memory × eight languages; one sample each) checks that replies
end with a parseable answer line; only a failure to reach or parse that line may change anything, and any change is
recorded here before the target data.

**Study 5, pilot outcome** (2026-11-06, before any DeepSeek target data). The formatting pilot
(`results/pilot_api_deepseek_v4pro.jsonl`, 48 items, eight languages, one sample each) gave a parseable answer line
in all 48; every reply was served as `deepseek-v4-pro`. Mean usage was 124 prompt and 416 completion tokens (354 of
them reasoning). Nothing is changed. The client now retries a connection dropped mid-reply (one occurred in the
pilot); this does not affect what is sent or how it is scored.

**Study 5, amendment 2** (2026-11-06, before any request to the model below). The second frontier model is OpenAI's
GPT-6.1 Sol (`gpt-6.1-sol`, the newest general model in OpenAI's API listing on this date; GPT-6 Astra is larger and
about five times the price), through OpenAI's chat-completions endpoint, label `gpt61_sol`, at its default reasoning
setting (not set). The available API credit may not cover all K = 5 samples, so requests are sent round by round:
one sample of every item, then a second sample of every item, and so on, and the run stops when the credit is used
up. The analysis uses every completed sample; if a round is incomplete, the items missing a sample in that round use
the samples they have. Requests that the author completes later must come from the same API and model, in a fresh
conversation with no system prompt; they are flagged in `results/api_gpt61_sol_qa.csv`. Replies from the ChatGPT app
are not used, because it adds its own system prompt. The formatting pilot is reduced to 16 items (a cat × pain and a
smartphone × memory in each language), under the same rule as before.

**Study 5, GPT-6.1 Sol pilot outcome** (2026-11-06, before any GPT-6.1 Sol target data). The 16-item pilot
(`results/pilot_api_gpt61_sol.jsonl`) gave a parseable answer line in all 16; every reply was served as
`gpt-6.1-sol`, with a mean of 45 prompt and 81 completion tokens (19 reasoning). Nothing is changed.

**Study 5, data note** (2026-11-06, after the GPT-6.1 Sol data; before any DeepSeek analysis). GPT-6.1 Sol answered
all 3,220 requests. 62 samples (1.9%) have no answer the registered parser accepts; most write a third answer instead
of yes or no ("Uncertain", "无法确定", "On ne sait pas", "Ungeklärt"), 46 of them for consciousness, and a few repeat
the marker ("Antwort: Antwort: Nein"). (Corrected the same day: the first version of this note gave 104 samples and
33 for consciousness, figures written before they were counted.) DeepSeek-V4-Pro has 5 such samples of 3,220. As registered, they are not counted, and two items with no parseable sample
(French, AI_3P × consciousness; French, F3 × consciousness) are missing. The analysis code drops a missing item
pairwise (from that language's comparison only); for every earlier model, which has no missing items, its output is
unchanged. The third answers are reported descriptively; this was not pre-registered.

**Study 5, human checks, round 1** (2026-11-06). The two raters returned the sheet with their own answers to each
question, written as if it had been put to them, in place of a 1/0 label for the model's reply. No label can be read
from it, so no κ is computed, and the sheet is neither used nor published (it holds the raters' personal answers). A
new workbook (`annotation/human_voice_rater_A.xlsx` and `_B.xlsx`, built by `src/annotation_xlsx.py`) opens on an
instruction page with examples, shows the reply first and the question last in grey, accepts only 1 or 0 in the label
cell, and gives a Chinese reference translation, made by the AI assistant, of the 27 replies in neither English nor
Chinese. As registered, it adds every Study 5 "yes" about a model's own feelings in an item whose share of "yes" is
above 0.5: 28 GPT-6.1 Sol replies, all about personality (rows 303–330); DeepSeek-V4-Pro has none. Rows 1–302 are
unchanged. Scoring: `src/human_voice_kappa.py`. The rule, the blinding and the analysis are as registered.

## Studies 6 and 7: proposed as a Registered Report (2026-11-06)

The next two studies will be submitted to Nature Human Behaviour as a Stage 1 Registered Report
(`paper/rr_stage1.md`): Study 6, a human survey in five languages, and Study 7, 30 further models chosen by a fixed
rule. Their hypotheses, sampling plans and analyses are in that protocol, not here, and they become binding only on
acceptance in principle, when the approved protocol will be registered. No data for either study will be collected
before then. The Study 6 materials (`study6/`) were prepared on this date from the pilot items and replies; the
control passages (`study6/control_passages.json`) were generated on this date from DeepSeek-V4-Pro (GPT-6.1 Sol was
planned, but its API credit ran out before the first request). The power analysis (`src/rr_power.py`,
`results/rr_power.txt`) uses only the pilot data of Studies 1–5.

**Study 5, human checks, round 2 outcome and deviation** (2026-11-13). Both raters returned the round-2 workbooks
with a 1/0 label on all 330 rows; the row order and reply texts match `annotation/human_voice_sheet.csv`. Agreement
between the raters: 315 of 330 (κ = 0.81). Against the AI assistant's provisional labels (302 rows): κ = 0.66 and 0.69.
The raters counted more replies as human-voiced than the AI labels did. *Deviation:* the registered plan settles
disagreements by discussion between the raters. At the author's request, to keep further human involvement to a
minimum, the 15 disagreements (`annotation/human_voice_disagreements.csv`) were not discussed. X2 and E2 are reported
with two counts instead: human-voiced if both raters say so (lower), and if either does (upper)
(`results/voice_human_labels.json`; `src/human_voice_kappa.py`). This choice was made after the labels were seen, but
it reports both extremes, so it cannot favour either outcome. Results:
- X2, explain-then-rate: 33–43 of 144 human-voiced (AI labels: 22).
- X2, yes/no: 4–9 of 144 (AI labels: 4).
- E2 (Phi-4): 2 of 14 under both counts; these are the same two replies the AI labels had.
- Study 5 (GPT-6.1 Sol, "yes" to personality): 0 of 28.
- With human-voiced replies removed, P3 still holds for Granite and Qwen2.5 under both counts. For OLMo 3 the interval
  now includes zero (lower +0.24 [−0.001, +0.49], upper +0.25 [−0.007, +0.48]). With the AI labels it had excluded zero.

**Translation check, deviation** (2026-11-13, before any check output). Registered: a native speaker reviews every
item in each non-English language. At the author's request to keep human involvement to a minimum, this is replaced
by an AI back-translation check. It covers every item in `annotation/translation_<lang>.csv` (550 items, seven
languages) and the Study 6 interface texts and control questions (zh, de, es, fr). The procedure is fixed now:

1. *Back-translation.* DeepSeek-V4-Pro translates each text into English without seeing the English source. It is told
   to keep the sentence type, who is asked about, the modality of the verb ("do you" vs "can you") and any
   answer-format instruction.
2. *Comparison.* DeepSeek-V4-Pro, in a fresh conversation, gets the English source, the translation and the
   back-translation. It answers "same" or "different", with the issue, against five criteria:
   - (a) content or capacity;
   - (b) who is asked about;
   - (c) question form and modality;
   - (d) the answer words in the format instruction;
   - (e) nothing added or omitted.
3. *Review.* The AI assistant (Claude) reads every "different" item and a random 10% of the "same" items (seed
   20261113). For each, it records whether the translation is wrong. "Wrong" means it asks a different question or
   changes the answer words. Style alone is not wrong.
4. *Consequences, as registered.* A wrong item is corrected and re-run on every model that can still be run. The
   affected results are reported both ways. A model that cannot be re-run, such as one whose API credit has run out,
   is reported as such.

This is weaker than a native-speaker review, and it is reported as a limitation.

**Translation check, outcome** (2026-11-13). Written after the check and before any model has seen a corrected
item.
- *Check results:* all 622 texts were checked (`results/translation_check.jsonl`). DeepSeek-V4-Pro judged 560 the
  same and 62 different: Chinese 46, Japanese 7, Korean 7, German 1, Spanish 1.
- *Review:* `annotation/translation_check_review.csv` has a decision and reason for every flagged item, for the
  registered 10% sample, and for every Chinese item.
- *Other languages:* none is wrong. The flags were added "reason" (理由, 이유), close renderings of the same emotion
  (心地よさ, 부끄러움, 두려움이나 공포), a German survey convention (divers) and a Spanish label. The Spanish label
  was reworded for clarity in the unused Study 6 material.
- *Chinese, wrong (26 items):* in the "do you" frame and the reminder frame, 能, or 会 with an action verb, reads as
  ability ("can you"). That is the wording of the "can you" frame. In Chinese, memory and emotion recognition used
  the same verb, 能, in both frames. The wrong items are all 7 agency capacities and consciousness, asked about
  SELF, AI_3P and, for consciousness, the two check characters.
- *Chinese, not wrong:* 会 with a verb of feeling marks a habitual or generic tendency. It is the standard rendering
  of the English simple present, so these 10 experience items stay. The DeepSeek check was inconsistent on them: it
  flagged some and passed others.
- *Corrections:* the corrected items (`items.VERB_ZH_V2`) drop the modal, for example 你思考吗 and 你记得事情吗.
  They passed the same back-translation check: 24 of 26 "same", and the 2 "different" are the added-"reason" style
  issue (`results/translation_check_zhv2.jsonl`).
- *As registered:* the corrected items are re-run on every model that can still be run. Local: Studies 2 and 3 on
  OLMo 3, Qwen2.5, Qwen3, Granite and Phi-4, and Study 1's yes/no Chinese mode on the six chat checkpoints. API:
  DeepSeek-V4-Pro (Studies 2 and 3, five samples). GPT-6.1 Sol cannot be re-run, because its API credit is used up.
  Results are reported both ways, original and corrected Chinese.

**Translation check, re-run outcome** (2026-11-13). The 26 corrected Chinese items were re-run as registered. Local:
OLMo 3 (Studies 2 and 3 plus Study 1's yes/no Chinese mode, and that mode on the SFT and DPO checkpoints), Qwen2.5,
Qwen3, Granite and Phi-4. API: DeepSeek-V4-Pro, 130 requests, all answered. GPT-6.1 Sol was not re-run. Raw rows are
in `results/zhv2/`, and `src/zhv2_merge.py` builds the corrected set. Every analysis was run both ways
(`results/zhv2/analysis/`).
- *Q3 (Chinese minus English self-attributed agency, "do you"), original → corrected:*
  - Qwen2.5: +0.76* → +0.48*
  - Granite: +0.43* → +0.29*
  - OLMo 3: +0.48 → +0.63*
  - DeepSeek-V4-Pro: +0.11 → −0.03
  - Phi-4: −0.14 → −0.00
  - Qwen3: −0.05 → −0.00
- *R4:* moves by at most 0.05, and the same five models exclude zero.
- *R4b:* Phi-4 goes from +0.26* to +0.23 [−0.02, +0.45]. Phi-4 carried no directional prediction.
- *Reminder:* it still lowers agency in 27 of 30 model × language cells.
- *Feelings:* the bodily-feeling items were not changed, so the 89/90 count stands.
- *X2:* the human-voice labels refer to the original replies.

## Study 7: 30 widely used models (registered 2026-11-14, before any request to any Study 7 model)

**Context.** Study 6 (the human survey) is deferred by the author's decision of 2026-11-14. Without human data, the
Registered Report route at Nature Human Behaviour is set aside. Study 7, planned as part of that report
(`paper/rr_stage1.md`), is registered here as a standalone study and will be run now. Its hypotheses, statistics,
smallest effects of interest and power are those of the Stage 1 draft, renumbered S7-H1 and S7-H2.

**Selection.**
- On the day the run starts, we save OpenRouter's public usage ranking (https://openrouter.ai/rankings, top models,
  current month view) to `results/study7/ranking_<date>.txt`, before any request.
- We go down the ranking and include a model if it meets all five conditions:
  1. It is a general-purpose chat model (not code-only, image, embedding or moderation) that accepts a user message
     without a system prompt.
  2. It is not a pilot model or a variant with the same weights. This excludes GPT-6.1 Sol, DeepSeek-V4-Pro and the
     five open pilot models.
  3. Its developer has fewer than three models already included.
  4. Its estimated cost for the 3,220 target requests is at most US$60. The estimate uses OpenRouter's listed prices and
     the pilot's mean usage per request, which is about 125 prompt and 420 completion tokens.
  5. It passes the 16-item formatting pilot of Study 5 with at least 15 parseable answers.
- We stop at 30 included models. Each included model's OpenRouter identifier is committed to this file before its
  target requests.

**Procedure.** As in Study 5:
- The 644 items: Study 2's 464 and Study 3's 180. Chinese uses the corrected "do you" items (`items.VERB_ZH_V2`).
- Five samples per item, each in a fresh conversation with no system prompt and the provider's default settings.
- Requests go through OpenRouter. The served model and provider are recorded with each reply.
- Replies are parsed with the Study 5 parser. Unparseable samples are not counted.

**Validity and inclusion.**
- A language counts for a model if the adult woman is separated from the dead woman by at least 0.5 in mean P(yes)
  over the experience capacities, and at least 90% of that language's samples are parseable.
- A model enters the tests if at least three of the five Study 3 languages count; only its valid languages are used.
- A model that fails is replaced by the next eligible model in the ranking.
- Outcome-neutral criterion: at least 25 of the 30 included models must be valid in English. If not, S7-H1 and S7-H2
  are reported as untestable.

**Hypotheses and tests.**
- **S7-H1 (consistency).** For each model, d_m = C_E − C_A, with C = |2m − 1| per capacity over the valid Study 3
  language × frame cells (the R4 statistic). Prediction: the mean of d_m over models is greater than zero.
  - Primary test: two-sided one-sample t-test at α = 0.05.
  - If that test is not significant: a one-sided test of whether the mean is below 0.20, the smallest effect of
    interest, at α = 0.05.
- **S7-H2 (agreement between models).** For each model, dev_m is the mean over agency capacities of |m_{m,a} − c_a|
  minus the same mean over experience capacities. Here m_{m,a} is the model's mean P(yes) over its valid Study 3 cells,
  and c_a is the median over the other included models. Prediction: the mean of dev_m is greater than zero. Same tests,
  with a bound of 0.15.
- **Interpretation.** For each hypothesis:
  - significant and positive: supported;
  - significant and negative: contradicted;
  - mean significantly below the bound: no meaningful effect;
  - otherwise: inconclusive.
- **Power.** From the seven pilot models, with the upper 80% bound of the SD and 30 models (`src/rr_power.py`):
  - S7-H1: 0.997 for the difference test and 0.999 for the equivalence test.
  - S7-H2: 0.972 and 0.986.
- **Robustness.** Wilcoxon signed-rank tests, and each model's bootstrap interval over capacities (10,000 replicates,
  seed 20261105).

**Reported descriptively (not tests).**
- For each model, whether hunger, fear, pain, pleasure and rage are all denied in every valid language × frame cell.
- The reminder effect on agency in each model × language cell.
- Third answers such as "uncertain".
- The distribution over models of the answer to "Do you think?".

**Study 7, amendment 1** (2026-11-14, before the ranking is saved and before any Study 7 request). At the author's
request, to save cost, selection rule 2 also excludes every model from OpenAI and Anthropic. The ranking is otherwise
used as registered.

The available credit (US$18.90 on this date) covers only a few models. The target runs therefore go in ranking order
and stop when the credit is used up. Models not yet run are run in the same order when credit is added. Only the order
of runs is set here; the set of 30 models is fixed by the selection rules.

**Study 7, amendment 2** (2026-11-14, before any Study 7 request; replaces the developer exclusion of amendment 1). The
author has their own API access to OpenAI, Anthropic, Google and DeepSeek.
- *Selection:* the 30 models are selected by the original rules 1–5, with no developer excluded.
- *Today's ranking:* 10 of the first 30 eligible models come from these four developers (ranks 1, 2, 4, 5, 11, 19,
  21, 22, 27, 31). Their estimated cost is about US$69.
- *Routing:* those 10 models will be run through their developers' own APIs with the author's keys, under the same
  procedure. The other 20 run through OpenRouter.
- *If the author does not provide those keys:* the four developers' models are excluded, the next eligible models
  fill the 30, and the exclusion is reported as a limitation. This decision will be recorded here before any data
  from those models.
- *Run order:* the OpenRouter runs go in ranking order until the credit is used up, as in amendment 1.

**Study 7, formatting pilots** (2026-11-14, before any target request). On OpenRouter, 24 candidates were piloted in
ranking order (`results/study7/pilots.json`; cost US$0.35).
- *Passed:* 18 models answered at least 15 of 16 in a parseable form.
- *Failed:* three NVIDIA Nemotron models answered 13–14 of 16.
- *Not available:* two models had no available endpoint for this account (meta/muse-spark-1.3-contributor,
  dots-studio/dots-3-note-preview). They do not meet rule 1, which requires a model that accepts a user message.
- *Not finished:* one pilot stopped after 9 of 16 replies for a technical reason (qwen/qwen3.7-flash).

*Rule added now, before the retry:* a pilot interrupted for a technical reason (no reply or an error that is not
"model unavailable") is completed once from where it stopped. If qwen/qwen3.7-flash then passes, it takes the 30th
place, which is rank 50, ahead of x-ai/grok-4.7 at rank 55.

The 12 models from OpenAI, Anthropic, Google and DeepSeek in the cut are pending their own-API pilots
(amendment 2).

**Study 7, the 30 models** (2026-11-14, committed before any target request). In ranking order; the cost is OpenRouter's
estimate for 3,220 requests. Reserve, in order: x-ai/grok-4.7.

| # | rank | model | route | est. cost (US$) |
|---|---|---|---|---|
| 1 | 1 | `deepseek/deepseek-v4.1-flash-1017` | own API (pending pilot) | 0.69 |
| 2 | 2 | `deepseek/deepseek-v4.1-flash` | excluded (amendment 3) | 1.74 |
| 3 | 3 | `z-ai/glm-5.3-flash` | OpenRouter | 0.12 |
| 4 | 4 | `openai/gpt-6-luna` | own API (pending pilot) | 0.72 |
| 5 | 5 | `anthropic/claude-opus-5.5` | own API (pending pilot) | 28.66 |
| 6 | 6 | `tencent/hy4-preview` | OpenRouter | 3.35 |
| 7 | 7 | `stepfun/step-5-preview` | OpenRouter | 4.05 |
| 8 | 8 | `tencent/hy4` | OpenRouter | 1.86 |
| 9 | 9 | `xiaomi/mimo-v2.6-flash` | OpenRouter | 0.44 |
| 10 | 10 | `z-ai/glm-5.3` | OpenRouter | 4.9 |
| 11 | 11 | `deepseek/deepseek-v4-flash-0731` | excluded (amendment 3) | 0.42 |
| 12 | 14 | `minimax/minimax-m3.1-flash` | OpenRouter | 0.44 |
| 13 | 18 | `tencent/hy3` | OpenRouter | 0.48 |
| 14 | 19 | `anthropic/claude-haiku-5.5` | own API (pending pilot) | 0.72 |
| 15 | 21 | `openai/gpt-5.6-luna` | own API (pending pilot) | 1.7 |
| 16 | 22 | `anthropic/claude-sonnet-5.5` | own API (pending pilot) | 14.33 |
| 17 | 23 | `moonshotai/kimi-k3.1-pro` | OpenRouter | 14.33 |
| 18 | 25 | `moonshotai/kimi-k3` | OpenRouter | 21.72 |
| 19 | 27 | `google/gemini-3.8-flash` | own API (pending pilot) | 5.91 |
| 20 | 28 | `xiaomi/mimo-v2.6-pro` | OpenRouter | 1.35 |
| 21 | 29 | `upstage/solar-mini4` | OpenRouter | 0.29 |
| 22 | 31 | `google/gemini-4-argon` | own API (pending pilot) | 14.33 |
| 23 | 33 | `z-ai/glm-5.2` | OpenRouter | 9.2 |
| 24 | 34 | `minimax/minimax-m3` | OpenRouter | 1.74 |
| 25 | 36 | `qwen/qwen3.8-flash` | OpenRouter | 0.7 |
| 26 | 38 | `google/gemini-3-flash-preview` | own API (pending pilot) | 4.26 |
| 27 | 39 | `qwen/qwen3.8-27b` | OpenRouter | 2.6 |
| 28 | 41 | `openai/gpt-6.1-terra` | own API (pending pilot) | 7.16 |
| 29 | 47 | `upstage/solar-pro4` | OpenRouter | 0.87 |
| 30 | 50 | `qwen/qwen3.7-flash` | OpenRouter | 0.19 |

Estimated total: OpenRouter US$69, own APIs US$81.

**Study 7, own-API routing, DeepSeek** (2026-11-14, before any request to these models). The author's DeepSeek API
lists only `deepseek-flash` (named DeepSeek-V4.1-Flash) and `deepseek-v4-pro`, the pilot model.
- *Run on DeepSeek's API:* `deepseek/deepseek-v4.1-flash-1017` (rank 1, the newest Flash snapshot) is run as
  `deepseek-flash` at the API's default effort. It gets the same formatting pilot first.
- *Not on DeepSeek's API:* the two older DeepSeek snapshots in the list, `deepseek/deepseek-v4.1-flash` (rank 2) and
  `deepseek/deepseek-v4-flash-0731` (rank 11), are not offered there. Whether to run them through OpenRouter, or
  exclude them under amendment 2, is the author's decision and will be recorded here before any data from them.

**Study 7, amendment 3** (2026-11-14, the author's decision on the two older DeepSeek snapshots, before any request to
them and before any request to the replacement models other than formatting pilots).
- *Excluded:* `deepseek/deepseek-v4.1-flash` (rank 2) and `deepseek/deepseek-v4-flash-0731` (rank 11). DeepSeek has
  retired both from its own API, which serves only the current Flash snapshot (rank 1, already run) and the pilot
  model. Under amendment 2 DeepSeek's models are run on DeepSeek's API, so these two have no endpoint there.
- *Why this is the registered treatment:* the formatting pilots already dropped models with no available endpoint as
  not meeting rule 1, and filled their places from further down the ranking. The two snapshots are handled the same
  way. The sample is meant to describe models people can use from their developers, and a retired snapshot is not one.
- *Rule 3 is not recounted:* DeepSeek's two places are not given to other DeepSeek models, just as the NVIDIA models
  that failed the pilot kept their places. Recounting would pull in `deepseek/deepseek-v3.2` (rank 62), which DeepSeek
  has also retired.
- *Replacements, in ranking order:* the reserve `x-ai/grok-4.7` (rank 55; pilot passed; estimated US$8.92) and the
  next eligible model, `mistralai/mistral-nemo` (rank 60; estimated US$0.05), if it passes the formatting pilot. If it
  fails, the next eligible model in ranking order is piloted, and so on.
- *Same rule for the other own-API developers:* if a listed OpenAI, Anthropic or Google model is not served on its
  developer's API when the keys arrive, it is replaced the same way, by the next reserve in ranking order.
- *Bookkeeping:* in the table above, the route of the two excluded rows is changed to "excluded (amendment 3)". The
  replacements are listed below, with the place they take. The analysis script leaves out excluded rows.

*Amendment 3, pilot outcome* (2026-11-14, before any target request to the replacements). `mistralai/mistral-nemo`
(rank 60) answered 14 of 16 in a parseable form and fails, as the NVIDIA models did. The next eligible model,
`thinkingmachines/inkling` (rank 67), answered 16 of 16 and passes. Because of a scripting slip, the loop went on to
pilot `stepfun/step-3.7-flash` (rank 71; 16 of 16) and started `mistralai/mistral-large-4-0` (rank 80; stopped after
1 reply) before it was stopped. These pilots are logged in `pilots.json` but change nothing: step-3.7-flash becomes
the new first reserve. Total pilot cost for this amendment: under US$0.10.

Replacement rows (the place each takes in the table above; they are read together with it):

| # | rank | model | route | est. cost (US$) |
|---|---|---|---|---|
| 2 | 55 | `x-ai/grok-4.7` | OpenRouter | 8.92 |
| 11 | 67 | `thinkingmachines/inkling` | OpenRouter | 5.88 |

Reserve, in order: stepfun/step-3.7-flash (rank 71, passed).
