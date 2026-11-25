# Progress report – working notes

Raw material for the progress report (due 01.12.2026). These are facts, decisions and sources per step, **not report text**: the report itself has to be written by the group in its own words.

## Step 1 – Hand annotation of the example sentences

Artifact: `data/sentences.md`

**What was done**

- All 16 sentences of the assignment (10 well-formed, 6 ill-formed) were tagged with Penn Treebank POS tags, with a `stem + suffix` analysis for inflected words.
- A target parse tree was drawn for each well-formed sentence (bracketed notation).
- For each ill-formed sentence: the type of violation, the rule where the parse should fail, and the check that fails.
- From the trees: a first rule inventory (33 distinct patterns, 29 after merging the verb tags), a lexicon seed (about 70 word forms) and the list of features the agreement design needs.

**Provenance of the annotation (must be stated honestly in the acknowledgment)**

- The tags and trees in `data/sentences.md` were drafted by Claude from its own knowledge of English syntax and Penn Treebank conventions, shaped by the rule templates of the slides. No parser, tagger or treebank lookup was used. A script only checked the form (balanced brackets, words and tags match the sentence), not the linguistic correctness.
- They are therefore proposals: the group has to review them and be able to defend each tree. Ways to review: match every bracket against the slide rule cited for it; apply the constituency tests of Slide09 pp. 4–5 (does the group of words appear as a unit elsewhere, can it be moved as a block); compare with the Penn Treebank examples on Slide09 p. 65.
- Known judgment calls: tag of *far*; *for my friend* as adjunct vs. complement; attachment choices in S1, S4, S5, S7.

**Why this step first** (motivation worth stating in the report)

- A set of parsed sentences implicitly defines a grammar: collect the rules that appear in the trees (Slide09 p. 64). This makes the grammar data-driven instead of invented top-down.
- The same trees are the gold standard needed later for evaluation (SLP2 §14.7).
- The ill-formed sentences act as negative test cases; each one justifies one feature.

**Decisions and their reasons**

| Decision | Reason | Source |
|---|---|---|
| POS tags are the preterminals; phrase labels `S NP Nom VP PP ADJP ADVP WHADVP` | PTB tagset is mandatory; phrase labels follow the course grammar plus PTB labels where the slides have none | Slide07 pp. 27–30; Slide09 |
| No split categories, no function tags (time NP is a plain `NP`) | Avoid rule proliferation; distinctions are carried by features checked during parsing | Slide09 pp. 46–49, 55–57 |
| Complements are sisters of the verb; adjuncts are adjoined with `VP → VP X` | Complements are selected by the verb (subcategorization), adjuncts are optional and can repeat; flat rules would need one rule per combination | Slide09 pp. 38, 50–52, 67; SLP2 Ch. 13 L1 grammar |
| Wh-adverb question as `S → WHADVP Aux NP VP` | The slide rule uses `Wh-NP`, but *when* is an adverb | Slide09 p. 23 |
| Irregular forms get regular-looking analyses (`went → go + ed`) | The assignment allows assuming the analyzer's output | Assignment text |
| Punctuation left out of the trees | Not relevant for constituent structure / evaluation | – |

**Observations worth reporting**

- The PTB verb tags (`VB VBZ VBP VBD VBG VBN`) already encode the verb form, so part of the morphological information the parser needs comes for free with the tagset.
- Subject–verb agreement needs person as well as number (`I buys`: both singular).
- The tense/time restriction (`will ... yesterday`) is not in the course material; it is our own extension and needs two features, because the time adverbial can attach to a VP that has no tense yet.
- Four of the ten sentences are structurally ambiguous under the grammar (PP attachment in S1, S5, S7; coordination scope in S4). Ambiguity is expected from a CFG; the evaluation has to say how it is handled.
- Blocking `I went in the school` forces `go` to have no intransitive frame; cost: `I went yesterday` is rejected too.

**Open points (to be settled in the grammar design step)**

See the list at the end of `data/sentences.md`: binarization for CKY, ambiguity in evaluation, passive, `go` frames, tag of `far`.

**Sources to cite for this step**

- Course slides: Slide07 (POS, Penn Treebank tagset), Slide09 (Grammars and Syntax).- Jurafsky & Martin, *Speech and Language Processing*, 2nd ed.: Ch. 5 (tagset), Ch. 12 (grammar of English), Ch. 13 (L1 grammar), Ch. 15 (features).
- Penn Treebank tagset (Marcus et al., 1993).

## Step 2 – Grammar design: strategy and scope

Artifact: `data/coverage.md`

**Strategy (how the grammar is built)**

- Two layers, as in the textbook: a plain CFG skeleton first, then constraints attached to the rules (SLP2 §15.3). Milestone: after the skeleton all 16 example sentences parse, including the ill-formed ones; after the constraints only the 10 well-formed ones.
- Rules come from three sources: (1) the example sentences fix which constructions are in scope, (2) the course material gives the general form of each construction (e.g. our single `S → MD NP VP` is an instance of `S → Aux NP VP`, Slide09 p. 20), (3) our own test sentences expose gaps.
- The grammar is written in a readable form with rules of any length (`VP → V NP PP`), identical in shape to the gold trees. CKY needs Chomsky Normal Form (SLP2 §12.5, §13.4.1), so a conversion step binarizes long rules automatically before parsing (as `X1 → Aux NP` in SLP2 Fig. 13.8) and the generated nodes are removed from the output trees afterwards (SLP2 §13.4.1, "CKY in practice"). Reasons: the grammar stays understandable and is the same object in the report, the gold trees and the parser; binarization becomes a documented component of the system rather than a manual step. Single-child rules are kept and handled by the parser itself (same section). Adjuncts use rules of the form `VP → VP PP` (Chomsky-adjunction, §12.5); this is a linguistic choice, not part of the conversion.
- An earlier idea, writing the rules binary by hand, was dropped: the worry was that constraints attached to a three-child rule get lost when the rule is split. Solution: the intermediate entry remembers the children collected so far and the constraints are checked when the rule is complete.
- Constraints are added one phenomenon at a time, each motivated by one of the ill-formed sentences. Features are flat atomic values, so a check is a comparison, not full unification (SLP2 §15.4 not needed).

**Why a checklist before the rules**

- The ten examples alone give only 29 rule patterns and miss obvious variants (no *did*-question, no positive imperative, no third-person subject). The demo tests unseen sentences from our vocabulary, so scope has to be defined by constructions, not by sentences.
- A grammar can fail in two directions: reject good sentences (under-generation) or accept bad ones (over-generation, Slide09 p. 45). The checklist has test sentences for both.
- Negative sentences are minimal pairs: one difference from a good sentence, so each tests exactly one check.

**What the checklist contains**

- 42 constructions / checks in five groups: sentence types, noun phrase, verb phrase, auxiliaries and verb forms, agreement.
- Tiers: Must (directly exemplified), Should (natural generalization), Could (if time allows), Out.
- 135 test sentences: 82 that must parse, 53 that must be rejected; 112 distinct word forms.

**Scope decisions and reasons** (target confirmed: Must + Should + Could are all in scope)

| Left out | Reason |
|---|---|
| Sub-clauses (relative, *that*-clauses, infinitive complements) | excluded by the assignment |
| Wh-questions on an object (*What did you buy?*) | missing object = long-distance dependency (SLP2 §15.3.4); not exemplified |
| Passive | not exemplified; interferes with rejecting `* I was read the book` |
| VP / sentence coordination, possessive *'s*, fronted adjuncts, comparatives | not exemplified; outside "simple SVO sentences" |

**Observations worth reporting**

- Tense/time check: present tense with a future time expression is grammatical (*I am going tomorrow*), so the check is a compatibility table, not simple equality.
- Pronoun case (*She helped me* / `* Her helped me`) is an agreement type not in the assignment's list (which is "not exhaustive"); cheap to add.
- Coordinated subjects are plural (*My mother and my father enjoy*), so coordination has to set the number feature rather than copy it from a head.

**Sources to cite for this step**

- Slide09 pp. 17–23 (sentence types), 24–37 (NP), 38–42 (VP, auxiliaries, coordination), 43–57 (agreement, subcategorization).
- SLP2 §12.3, §12.5, §13.4.1, §15.3.

### Grammar creation procedure (the method we follow)

**Inputs**

- The 10 gold trees and 6 ill-formed sentences (`data/sentences.md`).
- The coverage checklist: 42 constructions / checks, 82 sentences that must parse, 53 that must be rejected (`data/coverage.md`).
- The rule templates of the course material (Slide09; SLP2 Ch. 12, 15).

**Phase 1 – Skeleton: a plain CFG without any checks**

For each construction of the checklist, in the order sentence types → noun phrase → verb phrase → auxiliaries:

1. Bracket its must-parse sentences, using the gold trees as models.
2. Read the rules off the brackets (parent → children). If an existing rule already covers the construction, add nothing. Otherwise add the most general form given by the slides / book and note the source.
3. Write the rule in readable form (any number of children), with the checklist ID and one example phrase next to it.
4. Verify: every must-parse sentence of the construction can be derived. Every must-reject sentence that can also be derived goes on an over-generation list.

Exit condition: all 82 must-parse sentences are derivable. At this point the ill-formed sentences are derivable too; that is expected (over-generation, Slide09 p. 45) and the list from step 4 is the work plan for phase 2.

Worked example of steps 1–3, construction A3 (*Did you help my mother?*):

- Step 1, bracket: `[S [VBD Did] [NP [PRP you]] [VP [VB help] [NP [PRP$ my] [Nom [NN mother]]]]]`. Models: the question shape comes from example S6 (*Will you attend ...*), the phrase *my mother* from S3.
- Step 2, read off: each bracket is one rule. `NP → PRP`, `VP → VB NP`, `NP → PRP$ Nom`, `Nom → NN` already exist from the example trees. Only `S → VBD NP VP` is new, and it differs from the existing `S → MD NP VP` only in the first slot. The general form in the course material is `S → Aux NP VP` (Slide09 p. 20), so both are replaced by one rule, `S → V NP VP`.
- Step 3, write: `S → V NP VP   # A2, A3, A5  "Did | you | help my mother"  (Slide09 p. 20)`.
- Result: a whole new construction cost one rule, and that rule also covers questions with *does*, *can*, *is*, ... that we never bracketed.

**Phase 2 – Constraints: one phenomenon at a time**

Order: number and person agreement → verb form after an auxiliary → verb complements and preposition choice → bare nouns, time nouns, tense vs. time → pronoun case. For each phenomenon:

1. Decide the feature, its possible values, and which words carry it in the lexicon.
2. Attach a check (`=`) to the rule where the two parts that must agree meet (e.g. subject and verb phrase meet in `S → NP VP`).
3. Add pass-up statements (`←`) to the rules in between, so the feature travels from the word up to that rule. The feature is normally taken from the head child (SLP2 §15.3.2).
4. Verify again: the must-reject sentences of this phenomenon now fail, and no must-parse sentence was broken.

Exit condition: all 53 must-reject sentences fail and all 82 must-parse sentences still succeed.

**Phase 3 – Lexicon**

- Closed classes as complete as possible (SLP2 §5.1 lists them); open classes: enough words, each verb with all its forms (bare, -s, past, -ing, participle).
- Every entry: word form, Penn Treebank tag, `stem + suffix` analysis, feature values; verbs also get their complement frames.

**Phase 4 – Conversion for the parser (done by the program, not by hand)**

- Rules with more than two children are binarized automatically before CKY; generated nodes are removed from the output trees.

**How verification is done**

- A plain CKY recognizer (SLP2 Fig. 13.10, no features) is written early so that the skeleton can be tested mechanically on the 135 sentences instead of by hand.

### Decisions taken in discussion (25.11.2026)

- **Scope target:** all three tiers (Must + Should + Could).
- **No separate `Aux` symbol.** The slides write the question rule as `S → Aux NP VP` (Slide09 p. 20), but the Penn Treebank tagset has no auxiliary tag: only modals have their own tag (`MD`); *do*, *be*, *have* get ordinary verb tags (`were/VBD reported/VBN`, Slide07 p. 29). (Universal Dependencies does have an `AUX` tag; it is a different tagset.) Our solution: a lexical feature `aux = yes`, checked by the question and negation rules. What must follow an auxiliary (bare stem / -ing / participle) is treated like the complement requirement of an ordinary verb, as suggested in SLP2 §12.3.6. Consistent with the general decision "checks instead of extra symbols".
- **`V` is a shorthand** in the grammar file for any verb tag (`MD VB VBP VBZ VBD VBG VBN`), so a rule is not written seven times; it is not a node in the trees.
- **Lexical ambiguity is allowed:** e.g. *did* has an auxiliary entry and a main-verb entry; CKY keeps both.
- **Tagset facts:** Penn Treebank has 45 tags (36 word tags + 9 punctuation / symbol tags; Slide07 p. 27). The grammar uses about 22 of the word tags: `NN NNS NNP PRP PRP$ MD VB VBD VBG VBN VBP VBZ DT CD JJ RB RBS IN TO CC WDT WP WRB`. Unused ones belong to constructions left out of scope (`POS`, `JJR`, `RBR`, `RP`, `EX`, ...).

## Step 3 – Phase 1 done: skeleton grammar and grammar checker

Artifacts: `grammar/grammar.txt`, `grammar/lexicon.txt`, `data/tests.txt`, `check_grammar.py`

**What was done**

- The skeleton grammar was derived by walking the checklist (procedure of Step 2, phase 1): 46 rules as written, 142 after the `V` shorthand is expanded to the seven verb tags.
- Phrase symbols: `S NP Nom VP PP ADJP ADVP WHNP WHADVP`. Word-level symbols: 23 Penn Treebank tags.
- Every rule carries a comment with the checklist items it serves, an example and its source.
- A first lexicon: 149 word forms, 173 entries (a form with several tags has several entries, e.g. *read* is `VB`, `VBP`, `VBD`, `VBN`), each with tag and `stem+suffix` analysis. Every verb has all its forms.
- The test set as a file: 139 sentences = the 16 examples of the assignment + 123 checklist sentences; 86 must parse, 53 must be rejected.
- A grammar checker in Python (`check_grammar.py`): reads grammar and lexicon, expands the shorthand, binarizes long rules automatically, and runs a plain CKY recognizer (SLP2 Fig. 13.10) that answers accept / reject. Modes: run the whole test set, check one sentence, interactive, and a check that the hand-drawn trees use only rules of the grammar.

**Results (25.11.2026)**

| Check | Result |
|---|---|
| Sentences that must parse | 86 of 86 accepted |
| Hand-drawn trees S1–S10 licensed by the grammar (every local tree is a rule, every word/tag is in the lexicon) | 10 of 10 |
| Sentences that must be rejected | 3 of 53 rejected, 50 accepted |

- The phase 1 exit condition is met (all good sentences parse). The 50 accepted bad sentences are the expected over-generation and form the work plan for phase 2.
- The 3 bad sentences already rejected need no feature, they have no rule at all: `When you did come here?`, `I bought a novel beautiful.`, `I bought a very present.`

**Over-generation list, grouped by the check that is missing** (IDs from `data/tests.txt`)

| Missing check | Count | Sentences |
|---|---|---|
| Subject–verb / subject–auxiliary agreement (person, number) | 13 | X1, A3.4, A4.3, A7.4, B8.3, D2.4, D3.3, D5.3, E1.3–E1.6, E2.2 |
| Verb form required by an auxiliary | 11 | X5, A2.2, A3.5, A5.2, A6.3, A9.2, D1.3, D1.4, D3.4, D5.4, D6.2 |
| Determiner / number word vs. noun number | 7 | X2, B2.3–B2.6, B10.3, B12.2 |
| Verb complements and preposition choice | 7 | X4, X6, C1.3, C2.2, C3.4, C5.2, C6.4 |
| Tense vs. time expression | 4 | X3, E4.4, E4.5, E4.6 |
| Singular count noun without determiner | 2 | B4.3, B4.4 |
| Imperative needs the bare verb form | 2 | A8.4, A8.5 |
| Pronoun case | 2 | B1.3, B1.4 |
| Only time nouns as noun-phrase modifiers | 1 | B11.4 |
| *not* is not an ordinary adverb | 1 | A9.3 |

**How the checker itself was verified**

- A second, independent recognizer (naive fixpoint computation over the original, unbinarized rules; throwaway script, not in the repo) was compared with the CKY recognizer on 4278 strings: the 139 test sentences, shuffled versions of them and 4000 random word sequences. No disagreement. This confirms that automatic binarization and the handling of one-child rules do not change the language of the grammar.

**Design points that came up**

- **Spurious ambiguity.** With both `Nom → JJ Nom` and `ADJP → JJ` / `Nom → ADJP Nom`, every single adjective had two parses that mean the same. Fix: every adjective sits in an `ADJP` (as the `AP` of Slide09 p. 28 / SLP2 §12.3.3). The gold trees S2, S4, S10 were updated accordingly.
- **Questions with *be* as main verb** (*Is the school far?*) do not fit `S → Aux NP VP`, because what follows the subject is not a verb phrase. Three rules were added: `S → V NP NP | V NP ADJP | V NP PP`.
- **Negation** follows the flat Penn Treebank shape `VP → V RB VP` (gold tree S10) and needs three more rules for *be* (`was not far`, `is not a fruit`, `is not in our village`).
- **Binarization in the checker**: `A → B C D` becomes `<B+C> → B C` and `A → <B+C> D`; rules that start with the same children share the generated symbol. One-child rules are not removed; the recognizer follows them while filling the table.
- **IDs:** the ill-formed examples were renamed from B1–B6 to X1–X6, because B is also the noun-phrase group of the checklist.

**Known gaps / open points**

- `Where is the school?` (wh-adverb + *be*) is rejected; it is not in the checklist. Decide whether to add it.
- `helped my mother with dinner` has two analyses (PP as complement of *help*, or as a free modifier). Still true after phase 2 unless handled; matters for evaluation.
- Programming language: Python was used for the checker because no decision had been made; confirm.

**Sources to cite for this step**

- SLP2 §13.4.1 and Fig. 13.10 (CKY recognition, conversion to CNF, unit productions), §12.5 (binary branching, Chomsky-adjunction), §12.3.3 (adjective phrases).
- Slide09 pp. 17–42 for the individual rules (page per rule in `grammar/grammar.txt`).

### Addendum to Step 3 (25.11.2026): checklist item A10 added

- Trying the checker by hand showed that `Where is the school?` was rejected: a wh-adverb question whose verb is *be* has no verb phrase after the subject, so `S → WHADVP V NP VP` (A6) does not fit. It was not in the checklist, but it is a natural sentence for the demo.
- Added checklist item **A10** (wh-adverb question with *be* as main verb, tier Should), one rule `S → WHADVP V NP`, and four test sentences (`Where is the school?`, `How is your mother?`, `* Where are the school?`, `* Where the school is?`).
- This is the procedure working as intended: a sentence we expected to parse did not, which pointed to a missing rule (source 3 of the strategy: our own test sentences expose gaps).
- Numbers after the change: 47 rules as written; checklist 43 items with 139 sentences (84 must parse, 55 must be rejected); test file 143 sentences (88 + 55). Checker result: 88 of 88 good sentences accepted; 4 of 55 bad ones rejected, 51 accepted (the new one, `Where are the school?`, joins the subject–verb agreement group, now 14). All 10 gold trees still licensed.
- Still not covered: a wh-adverb question with *be* plus a predicate (`Why is the school far?`).

### Addendum to Step 3 (25.11.2026): the checker now outputs parse trees

**Concept: recognizer vs. parser**

- A CKY *recognizer* stores in each table cell only which symbols span that stretch of words; it can say accept / reject but not how. A CKY *parser* additionally stores, for every symbol in a cell, how it was built: which rule, which split point, which two smaller entries (backpointers). SLP2 §13.4.1 ("CKY Parsing") describes exactly this change, and adds that the same symbol must be allowed several times in a cell, once per way of building it. So the trees do not come for free from the recognizer; the table has to remember more.
- Reading the trees: start at `S` in the cell that covers the whole sentence and follow the backpointers down. Several ways to build an entry = several trees (ambiguity).

**What was implemented in `check_grammar.py`**

- Each cell maps a symbol to the list of ways it was built. Three kinds of way: a tag over a word; a one-child rule from another symbol over the same span; a two-child rule with its split point.
- Trees are read back recursively from the backpointers. Symbols generated by the automatic binarization are not shown: their children are moved up to the parent, which restores the rule as written in the grammar file (SLP2 §13.4.1, "CKY in practice").
- One-child rules are followed step by step (so the chain `NP → Nom → NN` appears in the tree); the grammar loader stops with an error if one-child rules form a loop.
- Output for a single sentence: tags per word, verdict, number of parses, the trees in bracketed form (first 10; `--all` for every tree).
- `--gold` is now stronger: each hand-drawn tree must be one of the trees the parser finds for its sentence.

**Results**

- All 10 hand-drawn trees are found by the parser (each is 1 of N parses, see below).
- Checks on the tree output over the 143 test sentences: every tree has exactly the words of the sentence, uses only rules of the grammar, contains no generated symbol, and no sentence gets the same tree twice. The independent recognizer still agrees on 4282 strings.

**Observation: the skeleton is highly ambiguous** (number of parses per example sentence)

| S1 | S2 | S3 | S4 | S5 | S6 | S7 | S8 | S9 | S10 |
|---|---|---|---|---|---|---|---|---|---|
| 12 | 6 | 12 | 12 | 7 | 6 | 12 | 3 | 4 | 28 |

Only 8 of the 88 good test sentences have a single parse; the maximum is 30. Three different causes, worth separating in the report:

1. **Word-form ambiguity**: *bought* is `VBD` or `VBN`, *come* is `VB`, `VBP` or `VBN`. `Did you come?` has 3 parses that differ only in the tag of *come*. Disappears with the verb-form checks.
2. **Missing complement checks**: without them a verb can take anything, e.g. *bought* as a verb with no object and `a present` attached as if it were a time modifier, or `a present ... yesterday` as two objects. Disappears with the subcategorization checks.
3. **Real structural ambiguity**: `for my friend` attached to the verb or to `present`. Stays after phase 2; this is the attachment ambiguity of SLP2 §13.2.

Expectation to verify after phase 2: the number of parses per sentence should drop to the real ambiguity only (S1: 2 or 3). The parse count is therefore a second measure of how well the constraints work, next to accept / reject.

## Step 4 – Phase 2 method: how the features and checks are derived

(Method only; results are added per group of checks as they are done.)

### Where the feature values of a word come from

The assignment says no morphological processing has to be implemented: a morphological analyzer and disambiguator is assumed to run before the parser and to deliver the analysis (`friends → friend + s`) "and some morphological features". In our system the **lexicon plays the role of that analyzer's output**: it is a lookup table from a word form to its analysis and features. Nothing is computed from the spelling of a word.

A word's features have three sources:

| Source | What it gives | Examples |
|---|---|---|
| The suffix / the Penn Treebank tag (form-level: what a morphological analyzer outputs) | number of a noun, form of a verb, tense | `novel+s`, `NNS` → plural; `buy+s`, `VBZ` → present, 3rd person singular; `watch+ed`, `VBD` → past; `go+ing`, `VBG` → -ing form; `VBN` → past participle |
| The stem (word-level: true for every form of the word, not visible in any suffix) | which complements a verb takes, which preposition it selects, auxiliary or not, count / mass noun, time noun | `go, goes, went, going, gone` all require a *to*-phrase; `music` is a mass noun; `yesterday` is a time noun referring to the past |
| Listed for the individual word (closed-class words, irregular) | person, number and case of pronouns; number of determiners | `I`: 1st person, singular, subject form; `this`: singular |

Consequence for the lexicon design (proposal): two tables instead of one.

- **Stems**: one entry per stem with its word-level features (`go`: verb, complement = *to*-phrase).
- **Word forms**: one entry per form with tag and analysis (`went  VBD  go+ed`).

When the lexicon is loaded, a word form gets the features of its tag/suffix plus the features of its stem. This is where the `stem + suffix` analysis is actually used: `went → go + ed` tells the program to take the complement requirement from `go` and the tense from `ed`. Advantage: the complement frame of a verb is written once, not once per form (five to six forms per verb).

Notes:

- Passive is out of scope, so no "passive" feature exists. The past participle is simply the verb form `VBN`, needed after *have*.
- Disambiguation: the assignment allows assuming that the disambiguator has already chosen one analysis per word. We do not need that assumption: the lexicon lists every analysis of a form (*read*: `VB`, `VBP`, `VBD`, `VBN`) and the checks of the grammar keep only the analyses that fit the sentence.

### Procedure for deriving one group of checks

Input: the over-generation list of Step 3 (bad sentences the skeleton accepts, grouped by missing check) and the minimal pairs of the checklist.

For each group, in the order subject–verb agreement → verb form after an auxiliary → determiner vs. noun → verb complements and prepositions → tense vs. time → the small ones:

1. **Take a minimal pair.** One accepted and one rejected sentence that differ in one word (`She enjoys novels` / `* She enjoy novels`).
2. **Find the two words in conflict** (here `she` and `enjoy`) and name the property that clashes as a feature with a fixed set of values (`person`: 1, 2, 3; `number`: sg, pl).
3. **Decide the source of the feature** for each kind of word: tag/suffix, stem, or listed (table above).
4. **Find the meeting point.** Parse the good sentence and take the lowest node of the tree that contains both words. The rule at that node is where the check (`=`) is attached. For subject and verb this is `S → NP VP`.
5. **Build the path up.** For every rule between each of the two words and the meeting point, add a pass-up statement (`←`) that copies the feature from the head child to the parent (head features, SLP2 §15.3.2; heads, Slide09 pp. 69–71). Example: verb → `VP` through `VP → V NP`.
6. **Decide what "unspecified" means.** Some words do not fix a value (`the` goes with singular and plural; a past-tense verb goes with any subject). An unspecified value is compatible with everything; a check fails only when both sides have a value and the values differ. For checks that are not equality (tense vs. time) write an explicit compatibility table.
7. **Fill in the lexicon** for all words carrying the feature.
8. **Verify**, in this order: (a) every bad sentence of the group is now rejected; (b) every good sentence of the whole test set is still accepted; (c) the number of parses of the good sentences went down but not to zero.
9. **Record**: the check under its rule in `grammar/grammar.txt`, the feature in the feature table, numbers before / after in these notes.

Exit condition of phase 2: all 55 bad sentences rejected, all 88 good sentences accepted, and the parses that remain for a good sentence differ only by real structural ambiguity.

Sources: Slide09 pp. 43–49 (agreement with feature constraints), 50–57 (subcategorization with features), 69–71 (heads); SLP2 §15.3 (feature structures in the grammar), §15.3.1–15.3.3; the assignment text for the assumed morphological analyzer.

### Clarification (25.11.2026): the lexicon has two jobs

- **Job 1 – stand in for the morphological analyzer.** Word form → stem + suffix + morphological features (number, person, tense, verb form). This is the part the assignment lets us assume. In the two-table layout this is the word-forms table.
- **Job 2 – be the dictionary of the grammar.** A CFG consists of constituent rules and lexical rules (Slide09 p. 6); the lexicon holds, per word, its part of speech and its syntactic properties. "*go* needs a *to*-phrase" is not morphology: no analyzer could read it off the form *went*. It is subcategorization, a property of the verb, and the course material stores it in the lexicon: `find: Verb, subcat: verb-NP, verb-NP-NP` / `disappear: Verb, subcat: verb-empty` (Slide09 p. 57); SLP2 §15.3.3 ("associating ... SUBCAT ... with each of the verbs in the lexicon"). In the two-table layout this is the stems table.
- Why it cannot live in the rules: `I went the school` and `I attended the school` have the same tags and the same structure; they differ only in which verb is used. The only alternatives are per-verb information in the lexicon or one verb category per complement pattern (`Verb-with-NP-complement`, Slide09 p. 55), which is the rule proliferation we decided to avoid.
- The stem delivered by the morphological analysis is the link between the two jobs: `went → go + ed` says which dictionary entry (`go`) applies.

### Worked example (25.11.2026): how the complement requirement of a verb is used during parsing

Same mechanism as agreement: the lexicon supplies feature values, rules pass them up (`←`), and a rule checks them (`=`) at the moment CKY tries to apply it. If the check fails, the phrase is not put into the table, so nothing above it can be built. (Feature names below are provisional until the feature table is fixed.)

```
PP → TO NP | IN NP
    PP.prep ← the preposition            # "to the school" gets prep = to

VP → V PP
    V.frame = PP                         # the verb accepts a preposition phrase
    V.prep  = PP.prep                    # ... headed by the preposition it asks for

VP → V
    V.frame = none                       # the verb can stand without a complement
```

Lexicon: stem `go`: frame = PP, prep = to. Form `went`: `go+ed`, so it inherits both.

- `I went to the school`: `to the school` becomes a PP with prep = to. At `VP → V PP`: frame PP = PP, prep to = to. The VP is built, then `S → NP VP`. Accepted.
- `* I went in the school`: the PP has prep = in. At `VP → V PP`: to ≠ in, no VP. The other route, `went` alone as a VP (`VP → V`) with `in the school` added as a modifier (`VP → VP PP`), fails at `VP → V` because `go` has no "none" frame. No VP at all, so no S. Rejected.
- `* I went the school`: `VP → V NP` requires frame = NP; `go` does not have it. Rejected.
- Difference to agreement: agreement compares the same feature on two sister phrases (number of subject and of verb phrase); here the verb states what it wants beside it and the rule compares that wish with what is actually there (Slide09 pp. 56–57).

## Step 5 – Phase 2 done: features and agreement checks, implemented and tested

Artifacts: `grammar/grammar.txt` (rules + constraints), `grammar/features.md` (feature table), `grammar/tags.txt`, `grammar/stems.txt`, `grammar/lexicon.txt` (three-part lexicon), `check_grammar.py` (parser with feature checks), `data/tests.txt`, `data/heldout.txt`

**What was done**

- 12 features defined (table in `grammar/features.md`): `agr`, `case`, `bare`, `temporal`, `time`, `vform`, `vpform`, `aux`, `frame`, `prep`, `adv`, `mod`.
- The 48 rules now carry 105 checks (`=` / `!=`) and 44 pass-up statements (`<-`), written under each rule in the slides' notation, each with a comment naming its group.
- The lexicon was split in three parts: features from the tag (`tags.txt`, the morphological part), features of the stem (`stems.txt`, the dictionary part), word forms with tag and `stem+suffix` analysis (`lexicon.txt`). 150 word forms, 186 lexical entries.
- The parser applies the checks while it fills the CKY table: a rule produces an entry only if all its checks hold for the features of its children.
- Constructions added during this step: *be* + place adverb (`The school is here`, `They were not here`, `Is your mother here?`; three rules), found missing by the held-out test.

**Design decisions and reasons**

| Decision | Reason |
|---|---|
| A feature value is a set of alternatives; a missing feature is "not specified"; a check succeeds if the two sides share a value and narrows both to the shared values | *was* goes with 1sg and 3sg, *you* is 2sg or 2pl, *the* fits any number. With single values these words would need several lexicon entries, and every extra entry gives an extra identical-looking parse. This is unification (SLP2 §15.2) restricted to flat values |
| One feature `agr` with six values (1sg ... 3pl) instead of separate person and number | The same feature then serves subject–verb agreement (needs person) and determiner–noun agreement (needs number); corresponds to the AGREEMENT bundle of SLP2 §15.3.1 |
| Tense and time expressions share one feature, `time` | The check becomes an ordinary compatibility check, no special table: past verb = `past`, present verb = `pres|fut`, *will* = `fut`, *yesterday* = `past`, *tomorrow* = `fut`, *tonight* unspecified. A time noun attached to a bare verb phrase passes its `time` up, so `will [help my father yesterday]` clashes at the auxiliary |
| Auxiliaries are verbs with frame `VP` and a `vpform` (the form they demand) | One mechanism for auxiliaries and for ordinary complements (SLP2 §12.3.6); no `Aux` symbol |
| A second constraint operator `!=` | Needed to say "a phrase the verb asks for is not also a free modifier"; removes equivalent double analyses |
| `LHS <- child` copies all features of the head child | Head features (SLP2 §15.3.2): one line instead of one line per feature |
| Because "not specified" passes every check, a feature that must be `yes` somewhere is `no` by default (set through the tag) | Otherwise `NP.temporal = yes` would accept every noun |
| Binarization with constraints: the generated intermediate entry only collects the feature bundles of the children seen so far; the checks run when the last child of the written rule arrives | The grammar stays in its readable form; checks that involve the first and the last child of a long rule are not lost |

**Results on the test set** (150 sentences: 91 must parse, 59 must be rejected)

| Checks switched on (cumulative) | Good accepted | Bad rejected | Parses of the 91 good sentences | Good sentences with exactly one parse |
|---|---|---|---|---|
| none (skeleton) | 91 | 4 | 690 | 8 |
| + subject–verb | 91 | 13 | 689 | 8 |
| + verb form, auxiliary | 91 | 28 | 323 | 10 |
| + determiner–noun | 91 | 34 | 323 | 10 |
| + complements, prepositions | 91 | 43 | 151 | 56 |
| + tense vs. time | 91 | 47 | 151 | 56 |
| + case, bare noun, time noun, adverb kind | 91 | 59 | 128 | 67 |
| + ambiguity checks | 91 | 59 | 103 | 83 |

- Final: 91 of 91 good sentences accepted, 59 of 59 bad sentences rejected. All six ill-formed examples of the assignment are rejected by the intended check:

| Example | Rule where it fails | Failed check |
|---|---|---|
| `* I buys a gift for my friend.` | `S → NP VP` | `NP.agr = VP.agr` (1sg / 3sg) |
| `* I read a historical novels.` | `NP → DT Nom` | `DT.agr = Nom.agr` (3sg / 3pl) |
| `* I will help my father yesterday.` | `VP → V VP` | `V.time = VP_1.time` (fut / past) |
| `* I went the school.` | `VP → V NP` | `V.frame = NP` (PP / NP) |
| `* I was read the book.` | `VP → V VP` | `V.vpform = VP_1.vform` (ing / base) |
| `* I went in the school.` | `VP → V PP` | `V.prep = PP.prep` (to / in) |

- All 10 hand-drawn trees are still found by the parser. Parses per example: S1 2, S2 1, S3 2, S4 3, S5 1, S6 1, S7 2, S8 1, S9 1, S10 1 (before the checks: 12, 6, 12, 12, 7, 6, 12, 3, 4, 28).
- The 8 good sentences that keep more than one parse are real ambiguities: a preposition phrase attaching to the verb or to the noun before it (S1, S3, S7, ...), and the scope of *national* / *our* in S4.

**Held-out test** (`data/heldout.txt`: 64 new sentences written after the grammar was finished, 30 good and 34 bad)

- First run: 63 could be judged (one contains a word form missing from the lexicon, *fruits*). 59 of 63 correct. All 33 bad sentences were rejected. 4 good sentences were rejected: `The school is here.`, `They were not here.`, `Where did they go yesterday?`, `Who are your friends?`
- The first two led to the *be* + place adverb rules; after adding them 61 of 63 are correct. The other two are listed as limitations below. Since the set was used for this fix it is no longer strictly held-out.

**How the implementation was verified**

- With all constraints removed, the new parser agrees with the independent naive recognizer on 3300 strings (tests, shuffled tests, random word sequences): the table filling, binarization and one-child rules are right.
- On the same strings, nothing is accepted with constraints that is rejected without them (constraints can only remove parses).
- Every tree output for the test set has the words of the sentence, uses only rules of the grammar, shows no generated symbol, and no sentence gets the same tree twice.
- For every bad test sentence the failed checks were listed and read by hand (the table above for the six examples).

**Tools added to the checker**

- `--features` prints the features of every word reading and of every phrase in the tree.
- For a rejected sentence the checker lists the failed checks that covered the longest stretch of words. This is a heuristic: checks failed by an irrelevant reading of a word (e.g. *helped* as a participle) are listed too.

**Known limitations** (each verified by running the sentence)

| Behaviour | Why |
|---|---|
| `I went yesterday.` and `Where did they go?` are rejected | *go* always requires its *to* phrase; this is the price of rejecting `* I went in the school` (otherwise *in the school* would be accepted as a place modifier) |
| `Who are your friends?` is rejected | *who* is 3rd person singular so that `* Who enjoy novels?` fails; in questions with *be* the verb agrees with the noun phrase after it |
| `My mother or my father enjoys novels.` is rejected (with *enjoy* it is accepted) | every coordination is plural; correct for *and* only |
| `Why is the school far?`, `Do you not listen to music?` are rejected | constructions not in the checklist |
| `Is Ali your friends?` is accepted | no number check between subject and the noun phrase after *be* |
| `I enjoy novels tomorrow.` is accepted | present tense is compatible with future time (needed for `I am going tomorrow`) |
| `The school was far to our village.` and `I came here summer.` are accepted | any preposition phrase can be a modifier; *summer* is both a bare noun and a time noun |
| Wh-questions on an object, passive, sub-clauses | out of scope (Step 2) |
| Small vocabulary; some plural forms missing (*fruits*) | phase 3 |

**Concepts for the report**

- Unification as intersection of value sets; under-specification.
- Head features: a phrase takes its features from its head child.
- Agreement (two phrases share a feature) vs. subcategorization (the verb states what it wants next to it) are the same mechanism.
- Constraints remove over-generation and, as a side effect, most of the ambiguity: 690 → 103 parses for the 91 good sentences. What is left is structural ambiguity (SLP2 §13.2).

**Sources to cite for this step**

- Slide09 pp. 43–49 (agreement with feature constraints), pp. 50–57 (subcategorization), p. 40 (auxiliaries), p. 65 (attachment of modifiers in the Penn Treebank), pp. 69–71 (heads).
- SLP2 §15.2 (unification), §15.3.1–15.3.3 (agreement, head features, subcategorization), §12.3.6 (auxiliaries), §13.2 (ambiguity), §13.4.1 (CKY).
