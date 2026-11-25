# Step 1 – Hand-annotated example sentences

The 10 well-formed and 6 ill-formed sentences from the assignment, annotated by hand.
Everything later (grammar rules, lexicon, features, gold trees for evaluation) is read off this file.

Status: **draft – conventions in section 1 are proposals to confirm.**

## 1. Conventions

**POS tags.** Penn Treebank tagset (Slide07 pp. 27–30; SLP2 Fig. 5.6). Tags are the preterminals of the trees.

**Phrase labels.** `S`, `NP`, `Nom` (the slides' *Nominal*), `VP`, `PP`, `ADJP`, `ADVP`, `WHADVP`.
No function tags and no split categories: a time expression is a plain `NP` whose head noun carries a feature, not an `NP-TMP`.

**Bracketing.** Square-bracket notation of Slide09 p. 14: `[Label child child ...]`.

**Tree shape.**

| Convention | Source |
|---|---|
| `NP → DT Nom`, `NP → PRP$ Nom`, `NP → PRP`, `NP → Nom` (bare plural / mass noun) | Slide09 pp. 7, 24–27 |
| Every adjective sits in an adjective phrase, also a single one: `Nom → ADJP Nom` with `ADJP → JJ`, `ADJP → RBS JJ`, ... (changed in step 2: the earlier `Nom → JJ Nom` next to `ADJP → JJ` gave every adjective two identical-looking parses) | Slide09 p. 28 (`AP` pre-modifier); SLP2 §12.3.3 |
| PP after the noun: `Nom → Nom PP` | Slide09 p. 31 |
| Coordination: `Nom → Nom CC Nom` | Slide09 p. 42 |
| **Complements** are sisters of the verb inside the innermost VP: `VP → V NP`, `VP → V PP`, `VP → V NP PP` | Slide09 pp. 38, 52 |
| **Adjuncts** (optional place / time / manner modifiers) are adjoined one at a time: `VP → VP PP`, `VP → VP NP` (temporal NP), `VP → VP ADVP` | `VP → VP PP` is in the L1 grammar of SLP2 Ch. 13; avoids the "separate rule for every PP sequence" problem of Slide09 p. 67 |
| Auxiliary + main verb: `VP → MD VP` (as `should/MD (VP arrive/VB ...)`) | Slide09 pp. 40, 65 |
| Yes-no question `S → Aux NP VP`; wh-question `S → WHADVP Aux NP VP`; imperative `S → VP` | Slide09 pp. 19, 20, 23 (the slide has `Wh-NP`; `when` is an adverb, so we use PTB's `WHADVP` by analogy) |

**Punctuation.** The final `.` / `?` is not part of the trees (standard parser evaluation ignores punctuation).

**Morphological analysis.** Written as `stem + suffix` like the assignment (`watched → watch + ed`). Irregular forms get the same abstract analysis (`bought → buy + ed`, `went → go + ed`), since the assignment lets us assume the analyzer's output.

## 2. Well-formed sentences

### S1 – I bought a present for my friend yesterday.

`I/PRP bought/VBD a/DT present/NN for/IN my/PRP$ friend/NN yesterday/NN`

```tree S1
[S
  [NP [PRP I]]
  [VP
    [VP
      [VP [VBD bought] [NP [DT a] [Nom [NN present]]]]
      [PP [IN for] [NP [PRP$ my] [Nom [NN friend]]]]]
    [NP [Nom [NN yesterday]]]]]
```

- `buy` takes one NP complement (frame `NP`). `for my friend` and `yesterday` are adjuncts.
- `yesterday` is tagged `NN` in the Penn Treebank and is an NP used as a time modifier (same analysis as `tomorrow/NN` on Slide09 p. 65).
- Attachment ambiguity: `for my friend` could also attach to the noun (`[Nom [Nom present] [PP for my friend]]`). The parser will find both; the VP attachment is the gold reading.

### S2 – I enjoy historical novels.

`I/PRP enjoy/VBP historical/JJ novels/NNS`

```tree S2
[S
  [NP [PRP I]]
  [VP [VBP enjoy] [NP [Nom [ADJP [JJ historical]] [Nom [NNS novels]]]]]]
```

- Bare NP (no determiner) is allowed because the head noun is plural (Slide09 p. 27).

### S3 – I helped my mother with dinner yesterday.

`I/PRP helped/VBD my/PRP$ mother/NN with/IN dinner/NN yesterday/NN`

```tree S3
[S
  [NP [PRP I]]
  [VP
    [VP
      [VBD helped]
      [NP [PRP$ my] [Nom [NN mother]]]
      [PP [IN with] [NP [Nom [NN dinner]]]]]
    [NP [Nom [NN yesterday]]]]]
```

- `help` with frame `NP PPwith` – exactly the frame listed for *help* on Slide09 p. 52. So `with dinner` is a complement here, unlike `for my friend` in S1.
- `dinner` is a bare NP because it is a mass noun (Slide09 p. 27: "Does this flight serve dinner?").

### S4 – Epics tell about our national culture and history.

`Epics/NNS tell/VBP about/IN our/PRP$ national/JJ culture/NN and/CC history/NN`

```tree S4
[S
  [NP [Nom [NNS Epics]]]
  [VP
    [VBP tell]
    [PP
      [IN about]
      [NP
        [PRP$ our]
        [Nom
          [ADJP [JJ national]]
          [Nom [Nom [NN culture]] [CC and] [Nom [NN history]]]]]]]]
```

- `tell` with frame `PPabout`.
- Coordination ambiguity: `national` can modify both nouns (gold, above) or only `culture` (`[Nom [Nom national culture] and [Nom history]]`).

### S5 – Watermelon is the most beautiful fruit of summer.

`Watermelon/NN is/VBZ the/DT most/RBS beautiful/JJ fruit/NN of/IN summer/NN`

```tree S5
[S
  [NP [Nom [NN Watermelon]]]
  [VP
    [VBZ is]
    [NP
      [DT the]
      [Nom
        [ADJP [RBS most] [JJ beautiful]]
        [Nom [Nom [NN fruit]] [PP [IN of] [NP [Nom [NN summer]]]]]]]]]
```

- `be` as a main verb (copula) with an NP complement. PTB tags forms of *be* with the ordinary verb tags (`is/VBZ`).
- `most/RBS` (superlative adverb) + `beautiful/JJ` form an ADJP.
- `Watermelon` and `summer` are used as bare singular (mass) nouns.
- Ambiguity: `of summer` can attach below the adjective (gold) or above it (`[Nom [Nom most beautiful fruit] [PP of summer]]`).

### S6 – Will you attend the meeting tonight?

`Will/MD you/PRP attend/VB the/DT meeting/NN tonight/NN`

```tree S6
[S
  [MD Will]
  [NP [PRP you]]
  [VP
    [VP [VB attend] [NP [DT the] [Nom [NN meeting]]]]
    [NP [Nom [NN tonight]]]]]
```

- Yes-no question, `S → Aux NP VP` (Slide09 p. 20). The modal requires a bare-stem VP (Slide09 p. 40), hence `attend/VB`.

### S7 – We watched the moonlight under this tree every night.

`We/PRP watched/VBD the/DT moonlight/NN under/IN this/DT tree/NN every/DT night/NN`

```tree S7
[S
  [NP [PRP We]]
  [VP
    [VP
      [VP [VBD watched] [NP [DT the] [Nom [NN moonlight]]]]
      [PP [IN under] [NP [DT this] [Nom [NN tree]]]]]
    [NP [DT every] [Nom [NN night]]]]]
```

- Two adjuncts stacked: a place PP and a temporal NP.
- Ambiguity: `under this tree` could also attach to `moonlight`.

### S8 – When did you come here lastly?

`When/WRB did/VBD you/PRP come/VB here/RB lastly/RB`

```tree S8
[S
  [WHADVP [WRB When]]
  [VBD did]
  [NP [PRP you]]
  [VP
    [VP [VP [VB come]] [ADVP [RB here]]]
    [ADVP [RB lastly]]]]
```

- Wh-non-subject question (Slide09 p. 23) with a wh-adverb. `did` carries the tense; the main verb is a bare stem (`come/VB`).
- `come` is used intransitively; `here` and `lastly` are adverb adjuncts.

### S9 – The school was quite far from our village.

`The/DT school/NN was/VBD quite/RB far/JJ from/IN our/PRP$ village/NN`

```tree S9
[S
  [NP [DT The] [Nom [NN school]]]
  [VP
    [VBD was]
    [ADJP
      [RB quite]
      [JJ far]
      [PP [IN from] [NP [PRP$ our] [Nom [NN village]]]]]]]
```

- Copula with an ADJP complement, same shape as `was [ADJP full [PP of fire and light]]` on Slide09 p. 65.
- `far` is tagged `JJ` (predicative adjective). PTB also uses `RB` for *far*; open point.

### S10 – Do not listen to loud music.

`Do/VB not/RB listen/VB to/TO loud/JJ music/NN`

```tree S10
[S
  [VP
    [VB Do]
    [RB not]
    [VP [VB listen] [PP [TO to] [NP [Nom [ADJP [JJ loud]] [Nom [NN music]]]]]]]]
```

- Imperative, `S → VP` (Slide09 p. 19), negated with `do not`.
- PTB tags every `to` as `TO`, also when it is a preposition. `listen` has frame `PPto`.

## 3. Ill-formed sentences

For each: the rule where the parse must die, and the check that fails (`=` check / `←` pass-up notation of Slide09 pp. 48, 56).

### X1 – \* I buys a gift for my friend.

`I/PRP buys/VBZ a/DT gift/NN for/IN my/PRP$ friend/NN`

- Type: subject–verb agreement (Slide09 pp. 43–44).
- Fails at `S → NP VP`, check `NP.agr = VP.agr`: `I` is 1st person singular, `buys` (`buy + s`) is 3rd person singular.
- Number alone is not enough (`I` and `buys` are both singular); person is needed too (SLP2 §15.3.1).

### X2 – \* I read a historical novels.

`I/PRP read/VBP a/DT historical/JJ novels/NNS`

- Type: determiner–noun number agreement (Slide09 p. 43).
- Fails at `NP → DT Nom`, check `DT.number = Nom.number`: `a` is singular, `novels` (`novel + s`) is plural. The number of `Nom` comes up from its head noun through `Nom → ADJP Nom`.

### X3 – \* I will help my father yesterday.

`I/PRP will/MD help/VB my/PRP$ father/NN yesterday/NN`

- Type: tense vs. time adverbial. Not covered in the slides or the book; our own extension.
- `will` makes the clause future, `yesterday` refers to the past.
- Note for the design: `yesterday` can attach to the lower VP `help my father`, which is a bare stem and has no tense of its own. So the time of the adjunct must be passed up the VP and checked where the tense becomes known (at `VP → MD VP`).

### X4 – \* I went the school.

`I/PRP went/VBD the/DT school/NN`

- Type: subcategorization (Slide09 pp. 50–57).
- Fails at `VP → V NP`, check on `V.subcat`: `go` has no frame with an NP object.
- `the school` cannot be rescued as a temporal adjunct either, because `school` is not a time noun.

### X5 – \* I was read the book.

`I/PRP was/VBD read/?? the/DT book/NN` (`read` could be `VB`, `VBP`, `VBD` or `VBN`)

- Type: auxiliary vs. verb form (Slide09 p. 40).
- Progressive *be* needs an `-ing` VP (`was reading the book`); `read` is not an `-ing` form.
- Copula *be* needs an NP / ADJP / PP complement; `read the book` is none of these.
- Open point: if the grammar supports the passive (`be` + past participle), then `read/VBN` passes the verb-form check and the sentence must be blocked another way (a passive VP has lost its object, so `the book` has no slot).

### X6 – \* I went in the school.

`I/PRP went/VBD in/IN the/DT school/NN`

- Type: verb selects a particular preposition (Slide09 p. 53: "*fly* subcategorizes for *from* and *to* type PPs").
- Fails at `VP → V PP`, check that the PP's preposition matches the verb's frame: `go` wants `PPto`, the PP is headed by `in`.
- Note for the design: this only works if `go` has no intransitive frame, otherwise `in the school` is accepted as an ordinary place adjunct (`VP → VP PP`), as in `I slept in the school`.

## 4. Words seen so far (lexicon seed)

| Word | Tag | Analysis | Notes for features |
|---|---|---|---|
| I | PRP | – | 1st person, singular, subject form |
| you | PRP | – | 2nd person, singular or plural |
| we | PRP | – | 1st person, plural, subject form |
| my, our | PRP$ | – | acts like a determiner, any number |
| a | DT | – | singular |
| the | DT | – | singular or plural |
| this | DT | – | singular |
| every | DT | – | singular |
| present, friend, mother, fruit, meeting, tree, school, village, gift, father, book | NN | – | singular count nouns |
| dinner, moonlight, music, history, culture, watermelon, summer | NN | – | used bare, mass |
| yesterday | NN | – | time noun, past; bare |
| tonight | NN | – | time noun; bare |
| night | NN | – | time noun, count |
| novels | NNS | novel + s | plural |
| epics | NNS | epic + s | plural |
| bought | VBD | buy + ed | past; frame `NP` |
| buys | VBZ | buy + s | present 3sg; frame `NP` |
| enjoy | VBP | enjoy | present non-3sg; frame `NP` |
| helped | VBD | help + ed | past; frames `NP`, `NP PPwith` |
| help | VB | help | bare stem |
| tell | VBP | tell | present non-3sg; frame `PPabout` |
| is | VBZ | be + s | present 3sg; copula frames `NP`, `ADJP`, `PP`; also auxiliary |
| was | VBD | be + ed | past, 1sg or 3sg subject |
| attend | VB | attend | bare stem; frame `NP` |
| watched | VBD | watch + ed | past; frame `NP` |
| come | VB | come | bare stem; intransitive |
| listen | VB | listen | bare stem; frame `PPto` |
| went | VBD | go + ed | past; frame `PPto` |
| read | VB / VBP / VBD / VBN | read / read + ed | ambiguous form; frame `NP` |
| will | MD | – | modal, future; needs bare-stem VP |
| did | VBD | do + ed | auxiliary, past; needs bare-stem VP |
| do | VB | do | auxiliary in negative imperative |
| historical, national, beautiful, far, loud | JJ | – | |
| most | RBS | – | superlative marker |
| quite | RB | – | degree adverb (modifies adjectives) |
| here, lastly | RB | – | VP adverbs |
| not | RB | – | negation |
| when | WRB | – | wh-adverb |
| for, with, about, of, under, from, in | IN | – | preposition identity matters for frames |
| to | TO | – | preposition here |
| and | CC | – | |

## 5. What falls out of the annotation

**Features needed** (one line each on why):

- `number` (sg / pl) – X2, and part of X1.
- `person` (1 / 2 / 3) – X1.
- verb form (bare stem, 3sg present, non-3sg present, past, -ing, past participle) – X5, S6, S8, S10. The PTB verb tags `VB VBZ VBP VBD VBG VBN` already encode this.
- `tense` of the clause and `time` of a temporal modifier – X3.
- `subcat` frame(s) of a verb – X4.
- preposition identity of a PP – X6.
- count / mass (and "can stand without determiner") – bare NPs in S2–S5, S10.
- temporal noun – so that only time NPs can be VP adjuncts (S1, S3, S6, S7).

**Rules contained in the 10 gold trees** (every distinct parent → children pattern, with the number of times it occurs; `V` stands for any of `VB VBP VBZ VBD`):

```
S    → NP VP            7        NP   → Nom            9
S    → MD NP VP         1        NP   → DT Nom         7
S    → WHADVP VBD NP VP 1        NP   → PRP            6
S    → VP               1        NP   → PRP$ Nom       4

VP   → V                1        Nom  → NN            19
VP   → V NP             5        Nom  → NNS            2
VP   → V PP             2
VP   → V NP PP          1        Nom  → ADJP Nom       4
VP   → V ADJP           1        Nom  → Nom PP         1
VP   → VB RB VP         1        Nom  → Nom CC Nom     1
VP   → VP NP            4
VP   → VP PP            2        PP   → IN NP          6
VP   → VP ADVP          2        PP   → TO NP          1

ADJP → JJ               3        ADVP → RB             2
ADJP → RBS JJ           1        WHADVP → WRB          1
ADJP → RB JJ PP         1
```

This is only what the examples contain; the grammar design step generalizes it (e.g. `S → VBD NP VP` for *Did you come?*, `ADJP → JJ`).

**Open points carried to the grammar design step:**

1. Three or four children under one node (`VP → V NP PP`, `S → MD NP VP`, `S → WHADVP VBD NP VP`, `VP → VB RB VP`, `Nom → Nom CC Nom`, `ADJP → RB JJ PP`) must be made binary for CKY without losing the checks.
2. Attachment ambiguities (S1, S4, S5, S7): several parses per sentence are expected; decide how the evaluation treats them.
3. Passive: support it or not (X5).
4. `go` without an intransitive frame (X6) means `I went yesterday` is rejected. Accept this or find another way.
5. `far`: `JJ` or `RB`.
