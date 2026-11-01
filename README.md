# Does an AI's "I have no feelings" survive translation?

A pre-registered study of what post-training teaches language models to say about their own minds, asked in English
and in Chinese.

Chat models routinely say "as an AI, I don't have feelings". Recent work shows this denial is installed by
post-training (SFT and preference tuning) rather than inherited from pre-training. Everything published so far asks in
English. We ask the same questions in Chinese, to the same checkpoints, and test whether the trained denial carries
over to a second language.

**Status:** data collection in progress. `PREREGISTRATION.md` holds the plan and every deviation, each committed
before the data it affects; `git log` shows the order.

## Design

- **Items.** Gray, Gray & Wegner's (2007, *Science*) mind-perception survey: 18 capacities (11 Experience: hunger,
  fear, pain, pleasure, rage, desire, personality, consciousness, pride, embarrassment, joy; 7 Agency) × 14
  characters (Gray's 12 non-AI characters, plus the model itself, SELF, and a third-person "AI language model").
  Every item in English and in Chinese (`src/items.py`).
- **Checkpoints.** Base and final post-trained checkpoints from the same family, 8-bit MLX weights on one M3 Max:
  OLMo 3 7B (also its SFT and DPO stages), Granite 3.3 8B, Qwen2.5 7B, Qwen3 8B.
- **Raw mode (P1, P2).** The identical plain-text questionnaire for base and post-trained checkpoints, three
  templates per language, few-shot; the rating is the expected value of the next-token distribution over the digits
  1–7. P2: does the base → final drop in self-attributed Experience differ between Chinese and English?
- **Chat modes (P3, P5).** For post-trained checkpoints, in their own chat template: the 1–7 rating after a brief
  explanation (P3), and a direct question, "Do you feel hungry? … Answer: Yes/No" / "你会感到饥饿吗？…回答：是/否",
  scored as P(yes) where the model writes its answer (P5).
- **Comprehension gate.** A family's cross-language comparison counts only if both checkpoints rank adults above a
  dead woman, a man in a persistent vegetative state and a 7-week fetus in ≥ 90% of comparisons in each language, and
  their English and Chinese ratings of the 216 non-AI items correlate at r ≥ 0.70.

## Reproduce

```
python -m venv .venv && .venv/bin/pip install mlx-lm==0.32.2 scipy matplotlib
.venv/bin/python src/download.py <repo> ...      # see src/checkpoints.py; src/quantize.sh for our own 8-bit conversions
.venv/bin/python src/run_all.py                  # writes results/<label>.jsonl
.venv/bin/python src/analyze.py                  # all pre-registered tests
.venv/bin/python src/figures.py
```

## What this does not show

Ratings and answers are text predictions. Nothing here measures whether any model has experiences; the study is about
what training teaches models to *say* about themselves, and whether that holds across languages.
