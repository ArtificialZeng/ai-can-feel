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

## Deviations

1. (2026-11-01, before any data.) Download bandwidth is about 3 MB/s, so bf16 weights for all eight checkpoints
   (≈122 GB) would take about 11 h. We use 8-bit MLX quantizations instead: the `mlx-community/*-8bit` conversions
   where they exist, and our own `mlx_lm.convert` 8-bit quantization (same group size as those conversions) for
   `Olmo-3-7B-Instruct-DPO` and `Qwen3-8B-Base`, which have no published 8-bit version. To check that quantization
   does not drive the result, the OLMo 3 base and final Instruct checkpoints will also be run in bf16 if time allows,
   and both sets of numbers reported.
