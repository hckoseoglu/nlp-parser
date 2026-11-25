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
- `to_cnf.py` – converts `grammar/grammar.txt` to Chomsky Normal Form and writes `grammar/grammar_cnf.txt` (generated; never edit it). Unit productions are eliminated and long rules binarized; each CNF rule records which grammar rule(s) it stands for.
- `cky.py` – the CKY parser itself (table filling over the CNF grammar with feature checks and backpointers; reading trees back; restoring trees of the original grammar). The algorithm is explained in its comments.
- `rules.py` (grammar rules and constraints), `lexicon.py` (three-part lexicon), `features.py` (feature bundles), `paths.py` (file locations) – the modules the two programs above use.
- `check_grammar.py` – command line. `python3 check_grammar.py` runs all tests; with a quoted sentence it prints tags, verdict and the parse trees (`--all`, `--features`, `--table` for the CKY table, `--cnf` for the CNF trees; a rejected sentence gets a list of failed checks); `-i` interactive; `--gold` checks that each hand-drawn tree is licensed by the grammar and is among the parses found. Every run regenerates `grammar/grammar_cnf.txt` first.
- `report/progress-notes.md` – per-step notes for the progress report.
- `report/ai-usage-log.md` – AI usage record for the acknowledgment section.

## Design decisions made so far

- **Agreement is enforced by constraint checks during parsing, not by splitting categories.** The grammar keeps plain non-terminals (NP, VP, ...) and each rule carries feature constraints that are checked when CKY applies the rule; a failed check means the constituent is not added to the chart. We do not multiply symbols (`3sgNP`, `Verb-with-NP-complement`, ...) because of rule/tag proliferation. This is the "augment the CFG rules with feature structures" solution of Slide09 pp. 48–49 and 56–57, and SLP2 Ch. 15.
- **Tree conventions (proposed in step 1, awaiting the user's confirmation):** PTB tags as preterminals; phrase labels `S NP Nom VP PP ADJP ADVP WHADVP`; complements are sisters of the verb (checked by subcat), adjuncts are adjoined with `VP → VP PP | VP NP(temporal) | VP ADVP`; time expressions are plain NPs with a feature. Details and open points in `data/sentences.md`.
- **Grammar-building strategy (proposed; the user proceeded on this basis without objecting):** two layers – plain CFG skeleton first (all 16 examples parse, bad ones included), then constraints one phenomenon at a time (only the 10 good ones parse). Rules are generalized from the examples using the course's rule templates and checked against `data/coverage.md`. Features are flat atomic values compared directly, no full unification.
- **Readable grammar, real CNF conversion (the user's decisions, 25.11.2026):** the grammar file is written in its natural, human-readable form with rules of any length (`VP → V NP PP`, `NP → Nom`), matching the gold trees. Do not hand-binarize it. `to_cnf.py` converts it to true Chomsky Normal Form as in SLP2 §13.4.1: unit productions are eliminated (an earlier version followed them inside the parser; the user asked for a proper CNF conversion and a textbook CKY instead), long rules are cut from the left into generated symbols `<B+C>`. Constraints survive because each CNF rule stands for a grammar rule plus a chain of unit productions and the parser applies their constraints in sequence; a generated symbol only collects its children's feature bundles. Output trees are converted back to the original grammar. Adjunction rules like `VP → VP PP` are a linguistic choice and stay as written.
- **No `Aux` symbol (proposed after the user questioned it, 25.11.2026):** auxiliary-ness is a lexical feature (`aux = yes` on modals, *do*, *be*, auxiliary *have*), checked by the question and negation rules, in line with the checks-not-symbols decision. What an auxiliary requires after it (bare stem, -ing, participle) is expressed with the same subcategorization mechanism as ordinary verbs (SLP2 §12.3.6). `V` in the grammar file is a shorthand for "any verb tag" (`MD VB VBP VBZ VBD VBG VBN`) expanded when the grammar is loaded; it is not a node in the trees. When explaining to the user, avoid undefined jargon and shorthand (define terms like auxiliary, `+`/`*` sentence on first use).
- **Rule notation:** the slides' notation, `=` for a check and `←` for passing a feature up, constraints indented under the rule, a comment with the checklist ID and an example phrase.
- **Parser ownership:** all Python code (`to_cnf.py`, `cky.py`, the supporting modules and `check_grammar.py`) was written by Claude at the user's explicit requests on 25.11.2026: first a recognizer for testing, then tree output, then feature checks, then the clean CNF converter and CKY parser. This is recorded in the AI usage log (kept locally, gitignored at the user's request). The user has been told several times that the assignment requires the group's own implementation; do not repeat the warning, keep the log accurate. Python, standard library only.
- **Features and lexicon (implemented 25.11.2026 at the user's request):** feature values are sets of alternatives, a missing feature is unspecified, `=` succeeds on a shared value and narrows both sides, `!=` fails on a shared value, `LHS <- child` copies all features of the head. A word form's features come from its tag (`grammar/tags.txt`), then its stem (`grammar/stems.txt`), then its own line (`grammar/lexicon.txt`). A feature that must be `yes` on some words needs an explicit `no` default on the others. No morphological analyzer is built; the lexicon is a lookup table. The phase 2 procedure is in `report/progress-notes.md`, Step 4; results in Step 5.
- **Lexicon sources (decided with the user 25.11.2026):** closed classes from SLP2 §5.1 figures (CELEX) and, for determiners, the Penn Treebank tagging guidelines; open classes by frequency rank from the New General Service List 1.2 (first 60 nouns, 40 verbs, 30 adjectives, 15 adverbs); tags, forms, analyses and all feature values are ours. Each word's source is a comment in `grammar/lexicon.txt`. `lexicon.txt` and `stems.txt` were written with a throwaway generator; edit them by hand from now on. A pass-up `LHS.f <- A.g` only sets the feature if the child has it. Cite a source only for what was taken from or checked against it; the verb frames and mass-noun marks are unverified drafts until the group checks them in a dictionary.
- **Status (25.11.2026):** phases 1–3 are done: grammar, agreement checks, parser (CNF conversion + CKY) and lexicon. 49 rules (171 with shorthands expanded), 108 checks, 46 pass-ups, 13 features (`grammar/features.md`); CNF: 244 binary rules, 31 generated symbols, 25 lexical rules. Lexicon: 592 word forms, 707 entries. Test set (228 sentences): 139 of 139 good accepted, 89 of 89 bad rejected, all 10 gold trees found. Held-out: round 1 61 of 63, round 2 58 of 60. Limitations: `report/progress-notes.md`, Steps 5 and 8. What is left: the group reviews the judgment calls listed in Step 8, writes the progress report (due 01.12.2026); after that evaluation with the standard metrics (SLP2 §14.7), system paper and work-sharing document (due 15.12.2026).
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
