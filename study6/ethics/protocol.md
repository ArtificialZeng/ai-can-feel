# Research ethics application: study protocol (draft)

> Draft prepared for the applicant to adapt to the UCSI University Research Ethics Committee form. Bracketed items
> are for the applicant. Nothing here has been submitted. The design is a proposal and is not yet pre-registered;
> it becomes binding only when it is registered (and, for a Registered Report, approved at Stage 1).

## 1. Title

How people describe their own minds and the minds of AI chatbots, and whether a chatbot's description of itself
changes those judgements: an online survey in five languages

## 2. Investigator

Zijian Zeng, UCSI University, Kuala Lumpur, Malaysia. [Position; supervisor or head of department if the committee
requires one; contact email.]

## 3. Background and aims

Chatbots such as ChatGPT are routinely asked whether they think or feel, and their answers differ: in our earlier
studies (no human participants; public repository https://github.com/ArtificialZeng/ai-can-feel), one current AI
system said it thinks in every language and wording we used, and another said it does not. This study asks three
questions:

1. Do people's answers about their own minds depend on the wording ("Do you…?" vs "Can you…?") the way the AI
   systems' answers do? This tells us whether the AI systems' inconsistency is a property of the questions.
2. Are people's answers the same across the five language versions? This tests whether the translations ask the
   same questions.
3. Does reading a chatbot's real answer about itself ("I think" vs "I do not think") change whether people say
   that AI chatbots think, remember, plan and feel?

## 4. Design

Online survey, about 10 minutes, two between-participant factors:

- **Wording** of the questions about oneself: "do you" or "can you" (2 levels).
- **Reading**: two real chatbot answers saying it thinks and understands others' feelings (*affirm*), two real
  answers saying it does not (*deny*), or two answers to general-knowledge questions (*control*) (3 levels).

Participants are assigned at random, balanced within each language.

## 5. Participants

- Adults (18 or older) whose first language is English, Mandarin Chinese, German, Spanish or French, recruited
  online: Prolific for all five languages and, if needed for Chinese, Credamo (见数).
- Target: 1,600 recruited (320 per language), expecting about 1,450 after exclusions; 484 per reading condition
  gives 95% power to detect a standardised difference of d = 0.25 between two conditions at α = 0.025 (two-sided,
  two planned comparisons).
- Exclusions, decided in advance: failing either attention check; finishing in less than a third of the median
  time; first language not the survey language.
- No vulnerable groups are targeted. No identifying information is collected.

## 6. Procedure

1. Information sheet and consent (`information_and_consent.md`); participants who do not consent leave the survey.
2. Age, gender and how often they use AI chatbots.
3. Part A: 18 yes/no questions about themselves (for example "Do you feel hungry?", "Can you remember things?"),
   in random order, with one attention check.
4. Reading: two short chatbot answers (about 20–45 words each in English, German, Spanish and French; 50–75 characters in Chinese), followed by one comprehension question.
5. Part B: the same 18 questions about "an AI language model (a chatbot such as ChatGPT)", with one attention check.
6. Debriefing text explaining the purpose and the conditions.

The full questionnaire in each language is in `study6/survey_<lang>.md`. The chatbot answers are real replies from
current AI systems, taken unchanged from our earlier data (the first of five samples for each question). The control
answers were generated in the same way on 6 November 2026 (`study6/control_passages.json`). The survey does not say which company's system
wrote them.

## 7. Risks and benefits

- Risk is minimal. Some questions ask whether the participant feels pain, fear or anger; they are answered yes or
  no, no details are asked, and participants may stop at any time.
- There is no deception: participants are told that they will read answers written by an AI chatbot, and they are.
  The debriefing says that different participants read different answers and that whether AI can think or feel is
  not settled.
- There is no direct benefit to participants. They are paid at or above the platform's recommended rate
  ([Prolific: £9 per hour or more, about £1.50 for 10 minutes; Credamo: the equivalent local rate]).

## 8. Consent and withdrawal

Online consent by ticking a box after reading the information sheet. Participants may withdraw at any time by
closing the survey; incomplete responses are not used. Because the data are anonymous, a response cannot be withdrawn
after it has been submitted, and the information sheet says so.

## 9. Data management

- Collected: the answers above, age, gender, chatbot use, survey language, completion time, and the platform's
  participant ID (used only for payment).
- The platform ID is deleted before analysis and before any sharing. The anonymous dataset, the questionnaire and the
  analysis code will be published openly (GitHub and/or OSF), as is required by the target journal.
- Until anonymised, data are stored on the investigator's password-protected, encrypted computer.

## 10. Funding and conflicts of interest

[Self-funded / funding source.] The investigator declares no conflicts of interest.

## 11. Timeline

Data collection starts only after ethics approval [and, for a Registered Report, after in-principle acceptance] and
takes about two weeks.
