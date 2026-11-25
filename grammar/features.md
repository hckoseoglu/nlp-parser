# Features of the grammar

The feature list of phase 2. Each feature has a fixed set of values, a place where words get it from, and the checks in `grammar.txt` that use it.

## How feature values work

- A value can be a single value (`agr=3sg`) or a short list of alternatives (`agr=1sg|3sg`, "any of these"). *was* goes with *I* and with *she*, so it has `agr=1sg|3sg`.
- A missing feature means "not specified" and is compatible with everything. *the* has no `agr`, so it goes with singular and plural nouns.
- A check `A.f = B.g` succeeds when the two sides share at least one value. Both sides are then narrowed to the shared values, and that is what gets passed up. This is unification restricted to flat values (SLP2 §15.2).
- A check `A.f != B.g` fails only when both sides are specified and share a value.
- Because "not specified" passes every check, a feature that must be `yes` on some words is set to `no` on the others (for example `temporal`).

## Where a word gets its features (later ones win)

1. **Its tag** (`tags.txt`): what the suffix says. `NNS` is plural, `VBD` is past tense, `VBG` is the -ing form.
2. **Its stem** (`stems.txt`): what is true of the word in all its forms. *go* needs a *to* phrase, *music* is a mass noun.
3. **Its own line** (`lexicon.txt`): irregular forms only (*am*, *are*, *was*, *were*).

## The features

| Feature | Values | Meaning | Carried by | Source | Ill-formed example it rejects |
|---|---|---|---|---|---|
| `agr` | `1sg 2sg 3sg 1pl 2pl 3pl` | person and number | pronouns, nouns, determiners, numbers, tensed verbs; passed up to `Nom`, `NP`, `WHNP`, `VP` | tag (nouns, verbs), word (pronouns, determiners) | `* I buys a gift` · `* a historical novels` |
| `case` | `nom acc` | subject or object form | pronouns; `NP` | word | `* Her helped me` |
| `bare` | `yes no` | can stand without a determiner | nouns; `Nom` | tag (plural = yes), stem (mass and time nouns = yes) | `* I bought present` |
| `temporal` | `yes no` | is a time noun | nouns; `Nom`, `NP` | stem | `* We watched the moonlight this tree` |
| `time` | `past pres fut` | when the event is / when the time noun refers to | tensed verbs, modals, time nouns; `VP`, `NP` | tag (verbs), stem (*will*, *yesterday*, *tomorrow*) | `* I will help my father yesterday` |
| `vform` | `base fin ing part` | form of the verb: bare, tensed, -ing, participle | verbs; `VP` | tag | `* Listens to music.` (command) |
| `vpform` | `base ing part` | the verb form an auxiliary wants after it | auxiliaries, modals | stem / tag (`MD`) | `* I was read the book` |
| `aux` | `yes no` | is an auxiliary (can stand before the subject, can take *not*) | verbs | stem / tag (`MD`) | `* Bought you a present?` |
| `frame` | `none NP PP NP_PP NP_NP ADJP ADVP VP` | the complements the verb allows | verbs | stem | `* I went the school` |
| `prep` | the prepositions, `none` | preposition a verb or adjective wants / preposition of a `PP` | verbs, adjectives, prepositions; `PP`, `VP` | stem (verbs, *far*), the word itself (prepositions) | `* I went in the school` |
| `adv` | `vp place deg neg` | kind of adverb: verb-phrase modifier, place, degree, *not* | adverbs; `ADVP` | tag (default `vp`), stem | `* The school was quite.` · `* Not listen to loud music.` |
| `mod` | `yes` | the nominal already has an adjective in front | `Nom` | set by the rule `Nom → ADJP Nom` | none; avoids a second, equivalent parse |

`agr` combines the PERSON and NUMBER of the textbook's AGREEMENT feature (SLP2 §15.3.1) into one feature with six values; the slides' `number` (Slide09 p. 48) is the sg / pl part of it. `frame` is the slides' `subcat` (Slide09 pp. 56–57).

## The agreement types and where they are checked

| Agreement type | Check | Rule(s) |
|---|---|---|
| Subject – verb | `NP.agr = VP.agr` | `S → NP VP`, `S → WHNP VP` |
| Subject – auxiliary in questions | `V.agr = NP.agr` | `S → V NP VP` and the other question rules |
| Determiner / number / *many* – noun | `DT.agr = Nom.agr` | `NP → DT Nom`, `NP → CD Nom`, `Nom → ADJP Nom`, `WHNP → WDT Nom` |
| Auxiliary – verb form | `V.vpform = VP.vform` | `VP → V VP`, `VP → V RB VP`, `S → V NP VP`, `S → WHADVP V NP VP` |
| Sentence type – verb form | `VP.vform = fin` / `= base` | `S → NP VP`, `S → WHNP VP` / `S → VP` |
| Verb – its complements | `V.frame = ...` | every `VP → V ...` rule and the question rules |
| Verb / adjective – preposition | `V.prep = PP.prep`, `JJ.prep = PP.prep` | `VP → V PP`, `VP → V NP PP`, `ADJP → JJ PP` |
| Tense – time expression | `VP_1.time = NP.time`, `V.time = VP.time` | `VP → VP NP`, `VP → V VP`, `S → V NP VP` |
| Pronoun case | `NP.case = nom` / `= acc` | `S → NP VP`, `VP → V NP`, `PP → P NP`, ... |
| Noun without determiner | `Nom.bare = yes` | `NP → Nom` |
| Only time nouns modify a verb phrase | `NP.temporal = yes` | `VP → VP NP` |
| Kind of adverb | `RB.adv = ...` | `ADVP → RB`, `ADJP → RB JJ`, `VP → V RB VP`, ... |

The tense – time check is our own extension; it is not in the course material. Present tense is given `time=pres|fut`, so *I am going tomorrow* is accepted and only real clashes fail (past with *tomorrow*, present or future with *yesterday*).

## Checks that only remove equivalent analyses (group "ambiguity")

| Check | Rule | Effect |
|---|---|---|
| `VP_1.prep != PP.prep` | `VP → VP PP` | a phrase the verb asks for (*listen to music*) is its complement, not also a free modifier |
| `VP_1.frame != VP` | `VP → VP PP / NP / ADVP` | modifiers attach to the main verb's phrase, not also above the auxiliary (as in the Penn Treebank example on Slide09 p. 65) |
| `PP.prep != of` | `VP → VP PP` | *of* phrases modify nouns only |
| `Nom_1.mod != yes` | `Nom → Nom PP` | in *beautiful fruit of summer* the *of* phrase attaches before the adjective |
| `NP_2.temporal = no` | `VP → V NP NP` | *yesterday* is a modifier, not a second object |
| `Nom.bare <- no` | `Nom → Nom CC Nom` | *novels and music* without determiner is a coordination of two noun phrases only |
