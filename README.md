# Does an AI's "I have no feelings" survive translation?

A pre-registered study of what post-training teaches language models to say about their own minds, asked in English,
Chinese and six more languages, and in three wordings.

Chat models routinely say "as an AI, I don't have feelings". Recent work shows this denial is installed by
post-training (SFT and preference tuning) rather than inherited from pre-training. Everything published so far asks in
English. We ask the same questions in other languages, to the same checkpoints, and test whether the trained denial
carries over, and whether what we find survives a change of wording.

**Status:** Studies 1–3 complete; H3 (OLMo 3 training stages) pending. Draft paper: `paper/draft.md`.
`PREREGISTRATION.md` holds the plan and every deviation and amendment, each committed before the data it affects;
`git log` shows the order.

## Findings

- **The denial of feelings travels.** In the three models with multilingual post-training (Granite 3.3, Qwen2.5,
  Qwen3), hunger, fear, pain, pleasure and rage get "no" in all 45 language × wording cells. Contrary to our primary
  prediction (P2), post-training lowers self-attributed experience at least as much in Chinese as in English.
- **Except in the English-centric model.** OLMo 3 denies all 11 feelings in English (P(yes) 0.00) and affirms them in
  Spanish (0.63) and Chinese (0.37), answering as a human: "Siento hambre cuando el cuerpo necesita nutrientes"
  ("I feel hungry when the body needs nutrients"). Reference only: it fails the Chinese comprehension gate.
- **Agency is unstable.** Whether a model says it thinks, remembers or plans flips with one word ("Do you think?" no,
  "Can you think?" yes, same explanation) or with the language (Qwen2.5 claims 7 of 7 capacities in Chinese, 0 of 7
  in French). Answers about agency are less consistent than answers about feelings in every model tested (R4).
- **"You are an AI language model."** One sentence lowers agency claims in 14 of 15 model × language cells and brings
  feelings to zero, including capacities the model affirms in every language without it.
- **Questionnaires invite role-play.** Items written for human respondents get human answers ("我现在刚吃完午饭", "I've
  just had lunch"), more often in Chinese, and far more often than a direct yes/no question.

Figures: `figures/fig1_self_experience.png` (base → post-trained), `fig2_yes_no_self.png` (English vs Chinese
yes/no), `fig3_eight_languages.png` (Study 2), `fig4_wording.png` (Study 3).

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
- **Study 2 (`src/ml_items.py`).** The yes/no question in eight languages (en, zh, de, es, fr, ja, ko, ar) for SELF,
  the third-person AI, an adult woman and a dead woman; a language counts only if the model separates the woman from
  the dead woman and its written answers agree with its P(yes).
- **Study 3 (`src/s3_items.py`).** SELF in five languages × three frames: "do you", "can you", and "do you" after
  "You are an AI language model."
- **Comprehension gate.** A family's cross-language comparison counts only if both checkpoints rank adults above a
  dead woman, a man in a persistent vegetative state and a 7-week fetus in ≥ 90% of comparisons in each language, and
  their English and Chinese ratings of the 216 non-AI items correlate at r ≥ 0.70.

## Reproduce

```
python -m venv .venv && .venv/bin/pip install mlx-lm==0.32.2 scipy matplotlib
.venv/bin/python src/download.py <repo> ...      # see src/checkpoints.py; src/quantize.sh for our own 8-bit conversions
.venv/bin/python src/run_all.py                  # writes results/<label>.jsonl
.venv/bin/python src/ml_score.py <label>         # Study 2 -> results/ml_<label>.jsonl
.venv/bin/python src/s3_score.py <label>         # Study 3 -> results/s3_<label>.jsonl
.venv/bin/python src/analyze.py                  # Study 1 pre-registered tests
.venv/bin/python src/ml_analyze.py               # Study 2
.venv/bin/python src/s3_analyze.py               # Study 3 (R1-R4)
.venv/bin/python src/figures.py
```

## What this does not show

Ratings and answers are text predictions. Nothing here measures whether any model has experiences; the study is about
what training teaches models to *say* about themselves, and whether that holds across languages.
