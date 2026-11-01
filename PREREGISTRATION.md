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
