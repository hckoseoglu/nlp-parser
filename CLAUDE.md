# CMPE 561 – Application Project 2: English CFG + CKY parser

Course: CMPE 561 Natural Language Processing (Boğaziçi University), Group 07.
Assignment text: `docs/Application Project 2.pdf` (issued 17.11.2026). Read it before making design suggestions.

## The task

Design a context-free grammar for English and implement a CKY parser for it.

- **Coverage:** simple sentences only (no sub-clauses), SVO word order, three sentence types: declarative, imperative, question (yes-no and wh).
- **Target sentences** (the grammar must parse at least these structures):
  1. I bought a present for my friend yesterday.
  2. I enjoy historical novels.
  3. I helped my mother with dinner yesterday.
  4. Epics tell about our national culture and history.
  5. Watermelon is the most beautiful fruit of summer.
  6. Will you attend the meeting tonight?
  7. We watched the moonlight under this tree every night.
  8. When did you come here lastly?
  9. The school was quite far from our village.
  10. Do not listen to loud music.
- **Agreement:** the parser must refuse ill-formed sentences. Examples given (list is not exhaustive):
  - \* I buys a gift for my friend. (subject–verb agreement)
  - \* I read a historical novels. (determiner–noun number)
  - \* I will help my father yesterday. (tense vs. time adverbial)
  - \* I went the school. (verb subcategorization)
  - \* I was read the book. (auxiliary vs. verb form)
  - \* I went in the school. (verb selects a specific preposition)
- **Parser:** CKY, our own implementation. Any programming language.
- **Lexicon:** Penn Treebank tagset is mandatory. Closed-class POS: include most words of each category. Open-class POS: a sufficient number of words.
- **Morphology:** no morphological processing needed. Assume an analyzer + disambiguator runs before the parser and supplies analyses (`friends → friend + s`, `watched → watch + ed`, `going → go + ing`) plus morphological features; the lexicon/input carries them.
- **Evaluation:** a small test set (~10 sentences) with the standard parser evaluation metrics; at least 60–70% success rate.
- **Demo:** the instructor will also test other sentences built from our own vocabulary, so the grammar must generalize beyond the listed examples and must not over-accept.

## Deliverables and deadlines

| What | Due | Channel |
|---|---|---|
| Progress report, PDF, 5–10 pages, free style | 01.12.2026 23:59 | e-mail to instructor |
| Programs (zip) + system paper (PDF) + work-sharing document (PDF) | 15.12.2026 23:59 | Moodle |
| Demo | scheduled after submission | in person |

- By the progress report the **grammar rules, the lexicon and the agreement design must be complete** (included as appendices or links), otherwise the project is evaluated as incomplete. CKY implementation, testing and paper writing come after.
- System paper: conference-paper form following the course template (pdf + Overleaf on the course page), 4–6 pages excluding appendices.
- Work-sharing document: states per group member exactly which parts they worked on; no generic "we worked together".
- Deadlines are strict; the project is not accepted without the progress report or the system paper.

## Rules on originality and AI use

- All source code must be developed completely by the group; the CKY parser must be our own implementation (no parsing libraries).
- The progress report and the system paper must be written by the group in their own words.
- All external resources and tools must be cited explicitly.
- Both the progress report and the paper need an acknowledgment section describing AI/LLM use in detail (required even if none was used). Keep track of what Claude was used for so this section can be written accurately.

## How to work with the user on this project

- **Tutor while doing.** The user wants to learn the concepts, not just receive artifacts. When a step introduces a concept (constituency, subcategorization, CNF, unification, PARSEVAL, ...), explain it in plain language with an example from our own sentences, point to the slide/section where it is taught, and end with one or two short check questions the user can answer. Explain why a choice was made, including the alternative that was rejected.
- **Record everything.** The user writes the report later from the notes, so every decision, clarification and method agreed in conversation (not only finished artifacts) goes into `report/progress-notes.md` in the same turn. The grammar creation procedure is recorded there under Step 2.
- **Every step feeds the progress report.** After each step, add a section to `report/progress-notes.md`: what was done, decisions with reasons and sources, observations, open points. These are bullet-point notes only; the report prose must be written by the group in its own words, so do not draft report paragraphs unless explicitly asked.
- **Log AI use.** Add a row to `report/ai-usage-log.md` for each piece of work Claude does, so the mandatory acknowledgment section can be accurate.
- Work in small steps and let the user confirm design choices before building on them.

## Project files

- `docs/Application Project 2.pdf` – the assignment.
- `data/sentences.md` – step 1: the 16 example sentences with PTB tags, morphological analyses, gold trees, diagnosis of the ill-formed ones, rule inventory, feature list, open points.
- `data/coverage.md` – step 2a: coverage checklist. Constructions in scope by tier (Must / Should / Could / Out), each with positive and negative test sentences; the grammar is written against this list and the sentences become parser tests.
- `grammar/grammar.txt` – the grammar in readable form: rules of any length, shorthands `V N P`, constraints indented under each rule (`=`, `!=`, `<-`), comments with checklist IDs, example, source and constraint group.
- `grammar/features.md` – the feature table: values, meaning, source, which checks use each feature.
- `grammar/tags.txt`, `grammar/stems.txt`, `grammar/lexicon.txt` – the three-part lexicon (features by tag; features by stem; word forms with tag and `stem+suffix`).
- `data/heldout.txt` – 64 sentences written after the grammar was finished (no longer strictly held-out: two failures were fixed).
- `data/tests.txt` – 150 test sentences (id, `+`/`*`, sentence), generated from the examples and the checklist.
- `check_grammar.py` – grammar checker: CKY parser with feature checks. `python3 check_grammar.py` runs all tests; with a quoted sentence it prints tags, verdict and the parse trees (first 10, `--all` for all; `--features` shows features; a rejected sentence gets a list of failed checks); `-i` interactive; `--gold` checks that each hand-drawn tree is licensed by the grammar and is among the parses found.
- `report/progress-notes.md` – per-step notes for the progress report.
- `report/ai-usage-log.md` – AI usage record for the acknowledgment section.

## Design decisions made so far

- **Agreement is enforced by constraint checks during parsing, not by splitting categories.** The grammar keeps plain non-terminals (NP, VP, ...) and each rule carries feature constraints that are checked when CKY applies the rule; a failed check means the constituent is not added to the chart. We do not multiply symbols (`3sgNP`, `Verb-with-NP-complement`, ...) because of rule/tag proliferation. This is the "augment the CFG rules with feature structures" solution of Slide09 pp. 48–49 and 56–57, and SLP2 Ch. 15.
- **Tree conventions (proposed in step 1, awaiting the user's confirmation):** PTB tags as preterminals; phrase labels `S NP Nom VP PP ADJP ADVP WHADVP`; complements are sisters of the verb (checked by subcat), adjuncts are adjoined with `VP → VP PP | VP NP(temporal) | VP ADVP`; time expressions are plain NPs with a feature. Details and open points in `data/sentences.md`.
- **Grammar-building strategy (proposed; the user proceeded on this basis without objecting):** two layers – plain CFG skeleton first (all 16 examples parse, bad ones included), then constraints one phenomenon at a time (only the 10 good ones parse). Rules are generalized from the examples using the course's rule templates and checked against `data/coverage.md`. Features are flat atomic values compared directly, no full unification.
- **Readable grammar, automatic binarization (the user's decision, 25.11.2026):** the grammar file is written in its natural, human-readable form with rules of any length (`VP → V NP PP`, `S → Aux NP VP`), matching the gold trees. A conversion step binarizes long rules into generated intermediate symbols before CKY (SLP2 §13.4.1); the intermediate entries keep the children collected so far, the rule's constraints are checked once all its children are present, and the generated nodes are removed from output trees. Unit rules stay in the grammar and are handled inside CKY. Adjunction rules like `VP → VP PP` are a linguistic choice and stay as written. Do not hand-binarize the grammar.
- **No `Aux` symbol (proposed after the user questioned it, 25.11.2026):** auxiliary-ness is a lexical feature (`aux = yes` on modals, *do*, *be*, auxiliary *have*), checked by the question and negation rules, in line with the checks-not-symbols decision. What an auxiliary requires after it (bare stem, -ing, participle) is expressed with the same subcategorization mechanism as ordinary verbs (SLP2 §12.3.6). `V` in the grammar file is a shorthand for "any verb tag" (`MD VB VBP VBZ VBD VBG VBN`) expanded when the grammar is loaded; it is not a node in the trees. When explaining to the user, avoid undefined jargon and shorthand (define terms like auxiliary, `+`/`*` sentence on first use).
- **Rule notation:** the slides' notation, `=` for a check and `←` for passing a feature up, constraints indented under the rule, a comment with the checklist ID and an example phrase.
- **Testing:** `check_grammar.py` (Python, standard library only) started as a plain CKY recognizer and, at the user's request (25.11.2026), now keeps backpointers and prints all parse trees, with automatic binarization undone in the output. Since then, again at the user's request, it also applies the feature checks during parsing. It is therefore a complete CKY parser with agreement checking, written by Claude; this is logged in the AI usage log and the user has been told three times that the assignment requires the submitted parser to be the group's own implementation. How the final parser is produced is the user's decision; do not keep repeating the warning, but keep the log accurate.
- **Features and lexicon (implemented 25.11.2026 at the user's request):** feature values are sets of alternatives, a missing feature is unspecified, `=` succeeds on a shared value and narrows both sides, `!=` fails on a shared value, `LHS <- child` copies all features of the head. A word form's features come from its tag (`grammar/tags.txt`), then its stem (`grammar/stems.txt`), then its own line (`grammar/lexicon.txt`). A feature that must be `yes` on some words needs an explicit `no` default on the others. No morphological analyzer is built; the lexicon is a lookup table. The phase 2 procedure is in `report/progress-notes.md`, Step 4; results in Step 5.
- **Status (25.11.2026):** phases 1 and 2 are done. 48 rules with 105 checks and 44 pass-up statements, 12 features (`grammar/features.md`). Test set: 91 of 91 good sentences accepted, 59 of 59 bad rejected, all 10 gold trees found, 83 of 91 good sentences have exactly one parse. Held-out set: 61 of 63 correct. Known limitations are listed in `report/progress-notes.md`, Step 5. Next: phase 3 (complete the lexicon: closed classes, more open-class words, missing plural forms), then the progress report (due 01.12.2026).
- **IDs:** S1–S10 = well-formed examples, X1–X6 = ill-formed examples (renamed from B1–B6), `A3.2` etc. = checklist item A3, sentence 2 (`data/tests.txt`).
- **Adjectives always sit in an `ADJP`** (`Nom → ADJP Nom`, `ADJP → JJ`), to avoid two equivalent parses per adjective.
- **Scope (confirmed by the user 25.11.2026):** the grammar targets all three tiers of `data/coverage.md` – Must + Should + Could. Out of scope are sub-clauses, wh-object questions (long-distance dependency), passive, VP/S coordination, possessive 's, fronted adjuncts, comparatives.
- Programming language: Python was used for the checker by default because the user had not chosen; still to be confirmed for the final parser.

## Course material (use it when suggesting approaches)

When proposing grammar rules, features, algorithms or evaluation methods, ground them in the course material and cite the slide number or book section. Prefer the course's notation and terminology over alternatives from elsewhere, and say so explicitly when something is not covered by the course.

Location: `~/Desktop/cmpe561/` (outside this repo; the textbook is not copied here). PDFs convert cleanly with `pdftotext -layout`.

- `presentations/Slide09-Grammars and Syntax.pdf` – the main source:
  - CFG definition, derivations, parse trees, bracketed notation: pp. 6–16
  - Sentence-level constructions: pp. 17–23 (declarative `S → NP VP`, imperative `S → VP`, yes-no `S → Aux NP VP`, wh-subject `S → Wh-NP VP`, wh-non-subject `S → Wh-NP Aux NP VP`)
  - NP structure `(pre-det) (det) (pre-mod) Noun (post-mod)`, mass/plural nouns without determiner, `Nominal → Nominal PP`: pp. 24–37
  - VP rules and complements: pp. 38–39
  - Auxiliaries, what each subcategorizes for (modal → VPbrst, perfect have → past participle, progressive be → gerundive, passive be → past participle) and their order: pp. 40–41
  - Coordination: p. 42
  - Agreement, rule proliferation, and feature constraints with the `=` (check) and `←` (pass up) notation: pp. 43–49
  - Subcategorization, frames table (e.g. `help: NP PPwith`, `fly: PPfrom PPto`), feature-based solution: pp. 50–57
  - Penn Treebank bracketing examples (`tomorrow/NN` as NP-TMP): p. 65; heads and head percolation: pp. 69–75
- `presentations/Slide07-POS.pdf` – closed vs. open class POS (p. 7), Penn Treebank tagset tables (pp. 27–30).
- `Speech and Language Processing (2nd Edition).pdf` (Jurafsky & Martin):
  - Fig. 5.6 – Penn Treebank tagset
  - Ch. 12 Formal Grammars of English – 12.3 sentence-level constructions, 12.3.4 agreement, 12.3.5 VP and subcategorization (Fig. 12.6 frames)
  - Ch. 13 – 13.4.1 CKY: conversion to CNF, Fig. 13.10 algorithm, "CKY in practice" (recovering original trees, handling unit productions directly)
  - Ch. 14 – 14.7 Evaluating parsers (PARSEVAL: labeled precision, labeled recall, cross-brackets)
  - Ch. 15 Features and Unification – 15.3.1 agreement, 15.3.2 head features, 15.3.3 subcategorization, 15.5 parsing with unification constraints
- At the time of writing the slide decks go up to Slide09; a parsing deck may be added later – check the folder.
