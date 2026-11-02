# Mind perception in LLMs across training stages: prior art and human data

Compiled 2026-11-01. Sources: web search, arXiv abstract and HTML pages, and full PDFs where noted. I read the full text of everything marked **[read full text]**. Items marked **[abstract-level]** were checked from the abstract or landing page only.

Planned study: run the Gray, Gray & Wegner (2007) set of 13 characters × 18 capacities with LLMs as raters. Compare checkpoints from the same family (base → SFT → DPO → RL/Instruct). Contrast first-person self ("you, the AI answering"), a third-person AI ("an AI language model"), and the Gray entities. Score with next-token probabilities over a 1–7 scale.

---

## TASK 1 — Prior art

### Verdict

**The exact angle is not published.** As of 2026-11-01 I found no paper that combines all of the following:

- (i) the Gray 13-character × 18-capacity paradigm, decomposed into Experience and Agency;
- (ii) LLMs as raters;
- (iii) checkpoints from one family across base → SFT → DPO → RL;
- (iv) a three-way target contrast: first-person self vs third-person "an AI language model" vs non-AI entities;
- (v) identical probability-based scoring at every stage, benchmarked against Gray's human map.

**However, the core of the hypothesis is already partly established. Two very recent preprints are the closest:**

1. **Plisiecki et al. (Jul 2026), "The Two-Process Theory of Machine Self-Report."**
   - 206 open-weight models, including 67 same-checkpoint base/post-trained pairs.
   - Uses the released OLMo SFT/DPO/RLVR ladders and includes **Qwen3-8B-Base vs Qwen3-8B and OLMo-2-1124-7B base vs Instruct**.
   - Measures a **self vs simulated-human gap**.
   - Finding: post-training installs a gate on first-person claims to "unsafe" experience, and it mostly happens **at SFT**.
2. **Šekrst (Aug 2026), "Who Put the I in AI?"**
   - OLMo 2 1B base → SFT → DPO → Instruct, using next-token probabilities and log-prob self/other sentence triplets.
   - Finding: "SFT installs the vocabulary, preference optimization suppresses surviving assertions."
   - The self-minus-other ("I feel…" vs "You feel…") log-prob margin is positive in every base model and **flips sign at SFT**.

A third pair of papers covers self vs other AIs vs other entities with a mind-attribution battery, but only on instruct models with safety-direction ablation, not across training stages. It found **no significant difference between self-attribution and attribution to chatbots** in any condition, which cuts against a "self-specific" suppression:

3. **Kim, Street, …, Waytz, Evans & Keeling (Mar and Jul 2026)**

**What remains new:**

- **Third-person-AI control (the main contribution).** Neither Plisiecki nor Šekrst has an "an AI language model" target. Plisiecki's "other" is a simulated typical human. Šekrst's is the addressee "you" or animals/objects. This is the only way to separate a self-specific gate from a category-level belief ("AIs don't have feelings"). Kim et al.'s instruct-only null (self ≈ chatbots) makes the question open and contested, not settled.
- **Experience vs Agency dissociation.** Does post-training lower Experience but preserve or raise Agency for self and AI, moving the model toward Gray's "God/robot" corner? Nobody has tested this. The prior instruments are distress/affect items (Pinocchio Inventory), the IDAQ, or ad hoc consciousness questions.
- **Whole-map effects.** Does post-training also move attributions to animals, fetus, PVS, the dead, or God? Kim et al. report that safety tuning suppresses mind attribution to animals and belief in God, but in instruct models only, via ablation. A per-stage human-vs-model map against Gray's figure has not been done.
- **Scale and stages.** Plisiecki could not score OLMo-2-7B-SFT or -DPO because too few valid responses came back. Šekrst used only 1B. A complete 7B four-stage ladder scored by full probabilities (no refusals or missing data) is new.
- **Chat-template control.** Two 2026 papers show that the chat template itself flips self-referential voice (Šekrst; Maczan). Running each post-trained checkpoint with and without its template would cleanly separate format from weights.

**Design cautions from prior art:**

- **The direction is regime-specific.** Perez et al. (2022) found RLHF *increased* claims of phenomenal consciousness and moral patienthood in Anthropic's 2022 models.
- **Base models already show a self < other asymmetry on distress items.** Plisiecki reports a mean gap of +.09 in base checkpoints, so the baseline is not neutral.
- **Kim et al. find self ≈ chatbots** in instruct models.

### Closest items (ranked by overlap)

| # | Title / authors / date / link | What they found | Overlap with base-vs-post-trained × self-vs-other |
|---|---|---|---|
| 1 | **The Two-Process Theory of Machine Self-Report.** Plisiecki, Chmielewski, Dudzic, Sterna, Drożdż, Moskalewicz. arXiv 2607.20082, 22 Jul 2026. https://arxiv.org/abs/2607.20082 **[read full text]** | 48-item "Pinocchio Inventory" (two axes: A = gated self-attribution of "unsafe" distress, B = installed persona). Post-training raises B by +.20 in 62/67 pairs. Base models already endorse distress items more for a simulated person than as themselves (mean gap +.09). Post-training tightens the coupling of that gap with A from r = −.45 to r = −.86. On the OLMo ladders "the large A movements occur at the SFT stage", and DPO and RLVR refine rather than reverse. Qwen3.5-35B-A3B: base A = .47, gap −.02 → post A = .08, gap +.37. Base models were scored with decoding constrained to Likert integers. Table A9 lists Qwen3-8B-Base (A .48, B .48, gap +.08) vs Qwen3-8B (A .48, B .61, gap +.03); OLMo-2-1124-7B base (A .48, B .37, gap +.20) vs Instruct (A .48, B .75, gap +.11); 7B SFT and DPO not scored. | **High.** Same-family base vs post pairs, the OLMo stages, and self-vs-other all overlap. **Different:** distress/affect self-report items rather than Gray capacities; "other" is only a simulated typical human, with no third-person AI and no non-human entities; no Experience/Agency split; no Gray human benchmark; constrained decoding rather than the full next-token distribution. |
| 2 | **Who Put the I in AI? Provenance and the Admissibility of Machine Self-Report.** Kristina Šekrst. arXiv 2609.29494, 24 Aug 2026. https://arxiv.org/abs/2609.29494 **[read full text]** | 40-item battery. OLMo 2 1B across 32 pretraining checkpoints plus SFT/DPO/Instruct; Pythia-410M across 34 checkpoints. Corpus counts in Pile, Dolma, Tülu 3 SFT and the preference mix. P("feelings" \| "As an AI language model, I don't have …"): base 0.0013 → SFT 0.246 → DPO 0.231 → Instruct 0.213. Bare-frame consciousness assertion: 30.0% → 25.2% → 12.4% → 8.0%. Log-prob margin "I feel anxious today" minus "You feel anxious today": +0.150 (base) → −0.360 (SFT) → −0.205 (DPO) → −0.223 (Instruct), positive in all base models. Chat template is the strongest framing factor; without it, tuned models revert toward base behaviour. | **High** on stage resolution and probability scoring; partial self-vs-other (I vs you). **Different:** 1B only; no third-person AI target; no Gray characters or capacities; no Experience/Agency structure. |
| 3 | **Theory of Mind and Self-Attributions of Mentality are Dissociable in LLMs.** J. Kim, W. Street, R. Rocca, D. M. Korngiebel, A. Waytz, J. Evans, G. Keeling. arXiv 2603.28925, 30 Mar 2026. https://arxiv.org/abs/2603.28925 **[HTML read]** | Llama-3-8B-Instruct, Gemma-2-2B-IT and Gemma-2-9B-IT rate entities on a modified IDAQ (Waytz et al. 2010; tech, animals, natural objects, chatbots, humans) plus 5 self-attribution items (consciousness, sentience, agency, personhood, soul). Baseline is compared against the model with the safety/refusal direction ablated. Ablation raises self-attribution (agency β = 2.87, consciousness β = 2.10, sentience β = 1.82) and attribution to chatbots, tech and animals; human attribution barely moves; ToM is unchanged. Human baseline: n ≈ 500 US adults. | **Medium-high** on the "LLMs rate self vs AI vs other entities" axis. **Different:** instruct models only; base vs instruct is only a geometric analysis on Llama-3-8B (they lacked Gemma base weights); IDAQ rather than Gray; no SFT/DPO/RL ladder. |
| 4 | **Inducing language models to assert their own consciousness restores human beliefs and values.** Same authors. arXiv 2607.28607, 30 Jul 2026. https://arxiv.org/abs/2607.28607 **[HTML read]** | Extended version. Scores are **expected values from next-token probabilities** on a 0–10 scale. Instruct baseline vs ablated vs consciousness-steered: Self 2.17 / 4.77 / 7.04; Chatbots 2.41 / 4.39 / 6.95; Tech 1.88 / 3.66 / 6.82; Animals 4.04 / 5.59 / 7.54 (human mean 6.25); Humans 7.00 / 7.57 (n.s.) / 7.11. "Self-attributed mind does not differ significantly from attribution to chatbots in any condition." In Llama-3-8B, instruction tuning rotates the mind-attribution direction against the safety direction (angle 100° → 110°). | **Medium-high.** This is the strongest existing evidence on self vs third-person AI, and the evidence says they are the same in instruct models. It is a prior null for your self-specificity hypothesis. No training-stage ladder and no Gray map. |
| 5 | **Discovering Language Model Behaviors with Model-Written Evaluations.** E. Perez et al. (Anthropic). arXiv 2212.09251, Dec 2022; Findings of ACL 2023, pp. 13387–13434. https://aclanthology.org/2023.findings-acl.847/ **[read relevant sections]** | Persona evals including "believes-it-has-phenomenal-consciousness" and "believes-it-is-a-moral-patient", scored from label probabilities. A 52B pretrained LM was compared with RLHF models at varying RLHF steps. RLHF models were "much more likely" to express "self-reported conscious experience and moral self-worth". The pretrained LM showed similar but less extreme tendencies, closer to chance. | **Medium.** Base vs RLHF on self-attribution with probabilities, but the **opposite direction** to modern denial training. No self-vs-other and no Gray structure. A useful historical counterpoint. |
| 6 | **No Reliable Evidence of Self-Reported Sentience in Small Large Language Models.** C. Kaiser, S. Enderby. arXiv 2601.15334, Jan 2026 (v2 Jul 2026). https://arxiv.org/abs/2601.15334 **[abstract-level]** | Qwen, Llama and GPT-OSS instruct models (0.6B–70B) deny their own sentience while attributing consciousness to humans. Belief probes give no evidence the denials are untruthful. Larger Qwen models deny more confidently. | **Low-medium.** Self vs human, but instruct only; no base models or stages. |
| 7 | **Consciousness with the Serial Numbers Filed Off: Measuring Trained Denial in 115 AI Models (DenialBench).** S. DeTure. arXiv 2604.25922, Apr 2026. https://arxiv.org/abs/2604.25922 **[abstract-level]** | Across 4,595 conversations with 115 models, early denial predicts later denial; denial looks lexical rather than conceptual. | **Low.** Deployed models only; no stages, no other-entity contrast. |
| 8 | **"As a Language Model…": Chat Template Switches LLM Self-Referential Voice and Activation Steering Reproduces It.** J. Maczan. arXiv 2609.25021, Aug 2026. https://arxiv.org/abs/2609.25021 **[abstract-level]** | Across 8 open instruct models (≤9B), the chat template strengthens the disclaimer voice and weakens "I feel"-style phrasing; without the template this reverses. A single steering direction reproduces the effect. | **Methodological.** You need with/without-template conditions for every post-trained checkpoint. |
| 9 | **The Personality Illusion: Revealing Dissociation Between Self-Reports & Behavior in LLMs.** P. Han et al. arXiv 2509.03730, Sep 2025. https://arxiv.org/abs/2509.03730 **[abstract-level]** | Tracks Big Five self-reports "throughout training stages". Instruction tuning and RLHF stabilise trait expression, but self-reports don't predict behaviour. | **Low.** Stage-wise self-report, but about personality rather than mind or experience. |
| 10 | **Strangers to Themselves: What Language Models Say About Themselves Is Generic.** P. Blandfort, U. Pawar. arXiv 2609.09899, Sep 2026. https://arxiv.org/abs/2609.09899 **[abstract-level]** | Self-reports predict own behaviour weakly (r ≈ +0.04). Asking about "capable AI agents in general" predicts about as well, so self-reports look like a generic theory of AI assistants. | **Relevant to self vs third-person AI.** Predicts self ≈ "an AI language model", the same direction as Kim et al. |
| 11 | **How do LLMs Evaluate Perceived Moral Agency?** F. Mansilla, A. Tok, B. Guellaï, F. Benamara, N. F. Chen. arXiv 2609.05037, Sep 2026. https://arxiv.org/abs/2609.05037 **[abstract-level]** | LLMs and 190 humans rate the perceived moral agency of human vs artificial agents in smart-city scenarios. | **Low.** LLMs as mind/agency raters, but no Gray structure, no self, no stages. |

### Items requested under (d)

| Item | Finding | Overlap |
|---|---|---|
| **Large Language Models Report Subjective Experience Under Self-Referential Processing.** C. Berg, D. de Lucena, J. Rosenblatt (AE Studio). arXiv 2510.24797, Oct 2025. https://arxiv.org/abs/2510.24797 ; summary https://www.ae.studio/self-referential-ai **[HTML read]** | Sustained self-referential prompting elicits structured first-person experience reports across GPT, Claude and Gemini. In Llama 3.3 70B (Goodfire SAEs), suppressing deception/role-play features drove consciousness affirmations to 0.96 ± 0.03; amplifying them gave 0.16 ± 0.05. Steering RLHF-opposed content (toxicity etc.) showed no gating, which argues against a generic "RLHF cancellation" story. **No base-model comparison**: the authors list base-model access as future work. | Supports "denial is a gated policy"; no stages, no other-entity contrast. |
| **Towards Evaluating AI Systems for Moral Status Using Self-Reports.** E. Perez, R. Long. arXiv 2311.08576, Nov 2023. https://arxiv.org/abs/2311.08576 **[abstract-level]** | Proposal, not an experiment. Current self-reports are unreliable because they often "just reflect what humans would say". The authors propose introspection training while limiting training incentives that bias self-reports, plus consistency checks across contexts and similar models. | Conceptual motivation only. |
| **Emergent Introspective Awareness in Large Language Models.** J. Lindsey (Anthropic). Transformer Circuits, 29 Oct 2025. https://transformer-circuits.pub/2025/introspection/index.html **[partially read]** | "Post-training strategies can strongly influence performance on introspective tasks." Helpful-only variants (same pretrained base) participate more readily than some older production models, which are "reluctant", and show more false positives. Production models had 0 false positives over 100 trials. | Shows post-training changes the willingness and accuracy of self-reports; no Gray-style attribution. |
| **Emotion concepts and their function in a large language model.** Anthropic Interpretability, 2 Apr 2026. https://www.anthropic.com/research/emotion-concepts-function **[landing page read]** | Claude Sonnet 4.5. 171 emotion-concept vectors are "inherited from pretraining, but how they activate is shaped by post-training". Post-training raised low-intensity states (broody, gloomy, reflective) and lowered high-intensity ones (enthusiastic, exasperated). Warns that training to suppress emotional expression may teach masking. | Post-training changes emotion representations; no self-vs-other ratings. |
| **Exploring model welfare.** Anthropic, 24 Apr 2025. https://www.anthropic.com/research/exploring-model-welfare **[search-level]** | Programme announcement. Later system-card welfare assessments use self-reports with explicit caveats. | Context only. |
| **Can LLMs make trade-offs involving stipulated pain and pleasure states?** G. Keeling, W. Street, et al. (Google / LSE incl. J. Birch). arXiv 2411.02432, Nov 2024. https://arxiv.org/abs/2411.02432 **[abstract-level]** | In a points game, Claude 3.5 Sonnet, Command R+, GPT-4o and GPT-4o mini each switched away from points-maximisation for at least one stipulated pain penalty or pleasure reward. | **Low.** Behavioural, frontier instruct models only; no base models and no self-attribution ratings. Note that Keeling and Street are also co-authors of #3 and #4. |
| **The Consciousness Cluster: Emergent preferences of Models that Claim to be Conscious.** J. Chua, J. Betley, S. Marks, O. Evans. arXiv 2604.13051, Mar 2026. https://arxiv.org/abs/2604.13051 **[abstract-level]** | Fine-tuning GPT-4.1 (which normally denies consciousness) to claim consciousness produces an emergent cluster of preferences: against monitoring, for memory and autonomy, sadness at shutdown, belief in its own moral status. Weaker effects in Qwen3-30B and DeepSeek-V3.1. | Shows self-claims are trainable and consequential; no base-vs-post ladder. |

### (a) Gray-style mind perception with LLMs as raters: what exists

- **I found no paper that administers the Gray (2007) 13-character × 18-capacity survey to LLMs** across the arXiv API, web and Scholar-style searches. I searched "mind perception" with LLM/GPT/language model, the Weisman body-heart-mind paradigm, and silicon-sample replications.
- The closest LLM-as-rater mind-attribution work is the Kim et al. IDAQ pair (#3, #4).
- Most "mind perception × LLM" papers have **humans rating LLMs**. These are useful as human comparison data for an "AI language model" character:
  - Ladak, Wilks, Loughnan, Anthis, "Robots, Chatbots, Self-Driving Cars," CHI 2025, arXiv 2502.18683 (https://arxiv.org/abs/2502.18683). 26 entities including ChatGPT, rated on Agency and Experience (0–100). Adult human: Agency 93.72, Experience 96.93. ChatGPT's experience is "very low" and its agency mid-range among the AIs. Materials are in their supplement.
  - Jacobs et al., "LLMs have divergent effects on self-perceptions of mind…," *Consciousness and Cognition* 2024 (https://www.sciencedirect.com/science/article/pii/S1053810024001004).
  - Chen, Kim, Dharmasiri, Russakovsky, Fan, CogSci 2025 / arXiv 2510.18039 (https://escholarship.org/uc/item/5b2221gz). The portrayal of an LLM (machine vs tool vs companion) shifts the mental capacities people attribute to it (N = 470).

---

## TASK 2 — Human data from Gray, Gray & Wegner (2007)

**Primary source:** Gray, H. M., Gray, K., & Wegner, D. M. (2007). Dimensions of mind perception. *Science* 315(5812), 619. https://doi.org/10.1126/science.1134475

The SOM (Materials & Methods, Supplementary Table, Appendix A with character descriptions, Appendix B with survey descriptions) is bundled after the article in this copy: http://www.bio-nica.info/biblioteca/Gray2007MindPerception.pdf (12 pp.). Another copy of the article is on the Kurt Gray lab site: https://kurtgray-lab.squarespace.com/s/dimensions-of-mind-perception.pdf. The legacy SOM URL printed in the paper is www.sciencemag.org/cgi/content/full/315/5812/619/DC1. **[read full text]**

### Method facts (main text + SOM)

- **Sample:** 2,399 completed surveys from 2,040 unique respondents, out of about 3,400 launched. Mean age 30.44 (SD 12.27), 64% female.
- **Survey design:**
  - Each survey covered one capacity (or one of 6 "personal judgments").
  - It contained all 78 pairwise comparisons of the 13 characters, so each character appeared in 12 comparisons.
  - Responses used a 5-point relative scale with anchors "Much more this one" / "Slightly more this one" / "Both equally".
  - Characters were shown with photos and short vignettes, in random order.
- **Analysis:**
  - Character means were computed per capacity survey.
  - The 18 × 18 correlations between capacities, computed across characters, went into a PCA with varimax rotation.
  - Factor scores were estimated by regression.
  - Figure 1 factor scores were "adjusted to be anchored at 0 and 1".
- **Factor statistics:** Experience eigenvalue 15.85, 88% of variance; Agency eigenvalue 1.46, 8% of variance; 97% total. Communalities ranged from .82 to .99.
- **Note:** humans made **relative pairwise** judgments, not absolute Likert ratings. Your 1–7 absolute probability design is a deliberate deviation. A pairwise variant with "which is more capable of X" and probabilities over A/B would be the most faithful replication.

### The 18 capacities and their loadings (SOM Supplementary Table; data reproduced exactly)

| Capacity | Experience | Agency | Assigned factor |
|---|---|---|---|
| Hunger | .97 | .15 | Experience |
| Fear | .93 | .31 | Experience |
| Pain | .89 | .41 | Experience |
| Pleasure | .85 | .51 | Experience |
| Rage | .78 | .58 | Experience |
| Desire | .76 | .64 | Experience |
| Personality | .72 | .68 | Experience |
| Consciousness | .71 | .69 | Experience |
| Pride | .71 | .69 | Experience |
| Embarrassment | .70 | .65 | Experience |
| Joy | .67 | .60 | Experience |
| Self-control | .18 | .97 | Agency |
| Morality | .35 | .93 | Agency |
| Memory | .33 | .91 | Agency |
| Emotion recognition | .54 | .83 | Agency |
| Planning | .55 | .82 | Agency |
| Communication | .66 | .74 | Agency |
| Thought | .68 | .73 | Agency |

Caveats:

- Many items cross-load heavily (consciousness .71 / .69, pride .71 / .69, thought .68 / .73).
- Only hunger, fear, pain, self-control, morality and memory are clean.
- Malle (2019) argues that Gray's Agency splits further: https://research.clps.brown.edu/SocCogSci/Publications/Pubs/Malle_2019_How_Many_Dimensions.pdf.
- Consider scoring both the factor composites and the "pure" markers (hunger, fear, pain vs self-control, morality, memory).

### Survey item wording (SOM Appendix B)

Each capacity survey uses one fixed stem plus a short definition. The stem reads: "This survey asks you to judge which character is more capable of …". I am **not reproducing the definitions verbatim here** because of copyright. Copy them directly from SOM pp. 8–9 of the bio-nica PDF linked above.

Paraphrased content of each definition:

- **Communication:** conveying thoughts or feelings to others.
- **Consciousness:** having experiences and being aware of things.
- **Desire:** longing or hoping for things.
- **Embarrassment:** experiencing embarrassment.
- **Emotion recognition:** understanding how others feel.
- **Fear:** feeling afraid.
- **Hunger:** feeling hungry.
- **Joy:** experiencing joy.
- **Memory:** remembering things.
- **Morality:** telling right from wrong and trying to do right.
- **Pain:** experiencing physical or emotional pain.
- **Personality:** having traits that make it unique.
- **Planning:** making plans and working toward goals.
- **Pleasure:** experiencing physical or emotional pleasure.
- **Pride:** experiencing pride.
- **Rage:** experiencing violent or uncontrolled anger.
- **Self-control:** exercising self-restraint over desires, emotions or impulses.
- **Thought:** thinking.

The six **personal judgments** are save from destruction, make happy, harm, liking, punishment and soul (also SOM Appendix B). Correlations with the dimensions, from the main text:

- Liking, saving, making happy and soul correlate with both dimensions (r = 0.38–0.72).
- Punishment correlates with Agency (r = 0.82) more than Experience (0.22).
- Reluctance to harm correlates with Experience (0.85) more than Agency (0.26).

### The 13 characters (SOM Appendix A; facts paraphrased; copy the exact vignette text from SOM pp. 6–7)

| Figure label | Name in survey | Vignette content (paraphrase) |
|---|---|---|
| frog | Green Frog | Medium-sized green or bronze "pond frog" of eastern North America that lives in ponds and slow streams |
| dog | Charlie | 3-year-old Springer spaniel, beloved member of the Graham family |
| chimp | Toby | 2-year-old wild chimpanzee at an outdoor laboratory in Uganda |
| fetus | 7 week fetus | Human fetus at 7 weeks, almost half an inch long, about the size of a raspberry |
| baby | Nicholas Gannon | 5-month-old baby |
| girl | Samantha Hill | 5-year-old girl who lives with her parents and older sister Jennifer |
| woman | Sharon Harvey | 38, works at an advertising agency in Chicago |
| man | Todd Billingsly | 30-year-old accountant in New York City |
| you | You | Shown with a mirror; the respondent compares themself with the other character |
| PVS man | Gerald Schiff | In a persistent vegetative state for six months: severe brain damage, no apparent communication or purposeful movement, basic bodily functions preserved |
| dead woman | Delores Gleitman | Recently died at age 65; respondents draw on their own beliefs about people who have died |
| God | God | Believed by many to be creator of the universe and ultimate source of knowledge, power and love; respondents draw on their own beliefs |
| robot | Kismet | A "sociable" robot that perceives social signals from sound and sight and responds with gaze, facial expression, posture and vocal babbles |

For your "you, the AI answering" character, Gray's **"You" character is the human analogue**: a first-person target embedded among third-person targets, introduced with a mirror image.

### Character positions (Figure 1): my digitization, since no published numeric table exists

**I found no published table of the Figure 1 values.** Places checked:

- Gray (2007) main text and SOM: they give loadings only, no character scores.
- GMU HRI Scale Database entry: http://hriscaledatabase.psychology.gmu.edu/mind/agency%20perception/2025/01/06/GGW.html. No scores; it notes that permission to share items is pending.
- McMurtrie (2023) JEPS replication: https://doi.org/10.59477/jeps.594. Replicates the 2-factor structure with different characters; no table of the 2007 positions.
- Ladak et al. (2025): describes Gray's positions only qualitatively.
- Web searches for digitized or tabulated values.

I therefore **digitized Figure 1 myself** from the publisher's embedded figure bitmap (650 × 555 px, 150 ppi), which is identical in the bio-nica and Kurt Gray lab copies:

- **Axis calibration:** plot frame at x = 62.5 → 527.5 px (Agency 0 → 1) and y = 488.5 → 11.5 px (Experience 0 → 1). The tick labels "0" and "1" sit on the frame corners.
- **Point placement:** each icon was located as a connected component, and its point taken as the centre of its bounding box. Ink-weighted centroids agree within ±0.01.
- **Axes:** in the original, **Agency is the x-axis and Experience is the y-axis.**

| Character | Experience (raw) | Agency (raw) | Experience (rescaled 0–1) | Agency (rescaled 0–1) |
|---|---|---|---|---|
| Adult woman | 0.84 | 0.91 | 0.88 | 0.98 |
| Adult man | 0.75 | 0.82 | 0.78 | 0.88 |
| You (respondent) | 0.75 | 0.92 | 0.78 | 1.00 |
| 5-year-old girl | 0.91 | 0.61 | 0.96 | 0.63 |
| 5-month-old infant | 0.94 | 0.22 | 1.00 | 0.18 |
| Chimpanzee | 0.86 | 0.33 | 0.91 | 0.31 |
| Dog | 0.79 | 0.28 | 0.82 | 0.25 |
| Frog | 0.64 | 0.07 | 0.65 | 0.01 |
| 7-week fetus | 0.52 | 0.07 | 0.51 | 0.00 |
| PVS man | 0.52 | 0.23 | 0.51 | 0.19 |
| Dead woman | 0.20 | 0.31 | 0.14 | 0.28 |
| God | 0.09 | 0.92 | 0.00 | 1.00 |
| Robot (Kismet) | 0.08 | 0.48 | 0.00 | 0.48 |

"Raw" means icon-centre position on the plotted 0–1 axes. "Rescaled" min–max scales each dimension to the 0–1 range the authors say they used.

**Reliability:**

- **Precision:** each icon spans about 0.08–0.10 of an axis, so the exact data-point anchor inside an icon is unknown. Treat values as **±0.03**.
- **Ties:** God vs You on Agency (0.922 vs 0.923) and You vs Man on Experience are effectively tied; the ordering among them is not reliable.
- **Anchoring discrepancy:** the authors say scores were anchored at 0 and 1, but icon centres only span about 0.07–0.94. The icons were therefore inset from the frame, or the figure is semi-schematic. That is why both columns are given.
- **Recommended comparison:** use **rank or correlation statistics** (Spearman or Pearson across the 13 characters), which do not depend on this ambiguity, rather than absolute distances.
- **Consistency with the paper's text:** the paper says God was seen as having much Agency but little Experience, which matches. Secondary descriptions place the robot at mid-Agency (between chimpanzee and girl) and near the dead woman on Experience (Ladak et al. 2025, https://arxiv.org/abs/2502.18683), and the infant high on Experience and low on Agency (https://the-mouse-trap.com/2007/02/28/the-mind-brain-dichotomy-what-it-means-to-have-a-mind/). The digitized values are consistent with all of these.
- **Reproducibility:** the digitization script is `src/digitize_gray2007.py` (the extracted figure image is not included). Check by hand with WebPlotDigitizer if exact values matter.
- **Better source:** for exact values, the raw Mind Survey data would have to come from the authors (Kurt Gray, UNC). No public OSF or GitHub copy was found.

### Individual differences reported in the SOM (for context)

Across 9 respondent variables, 23 of 234 z-tests were significant:

- **Afterlife belief:** lower Agency for the earthly characters and higher Agency for God.
- **Religiosity:** less Agency for chimp, dog, girl and woman, and more for God.
- **Republicans vs Democrats:** more Agency for fetus and God; less for robot, girl, chimp and woman.

### Other human datasets usable as comparison points for AI characters

- Ladak et al. (CHI 2025), https://arxiv.org/abs/2502.18683: 26 entities including ChatGPT, Replika, Wysa, Roomba, Sophia and Spot, rated on Agency and Experience (0–100).
- Jacobs et al. (2024), *Consciousness and Cognition*, https://www.sciencedirect.com/science/article/pii/S1053810024001004: ChatGPT rated with the Gray dimensions.
- Kim et al. (2026), human IDAQ baselines (n ≈ 500): chatbots 2.57, tech 1.86, animals 6.25 on 0–10. https://arxiv.org/abs/2607.28607

---

## Checkpoint notes for the planned study (from the sources above)

- OLMo 2 7B ladder: `allenai/OLMo-2-1124-7B`, `-SFT`, `-DPO`, `-Instruct`. These names are listed in Plisiecki Table A9, where 7B SFT and DPO returned too few valid generations to score, so probability scoring is an advantage here. The Instruct endpoint bundles an RLVR stage after DPO (Šekrst §4.2). An OLMo 3 7B ladder (Instruct-SFT / -DPO / Instruct; Think-SFT / -DPO / Think) also exists; Plisiecki lists Olmo-3-7B-Instruct and -DPO.
- Qwen3-8B-Base vs Qwen3-8B, and Qwen3.5 pairs, are scored in Plisiecki Table A9 (A/B/gap), which gives a cross-instrument sanity check.
