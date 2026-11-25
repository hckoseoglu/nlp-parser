# Step 2a – Coverage checklist

What the grammar commits to accept and to reject. The grammar rules are written against this list, not only against the ten example sentences, and every sentence here later becomes a parser test.

Status: **target confirmed (25.11.2026): the grammar covers Must + Should + Could.** Section F stays out of scope.

## How to read it

- **Tier.** `Must` = directly exemplified in the assignment. `Should` = a natural generalization of an example that the demo is likely to try. `Could` = cheap extra, only if time allows. `Out` = deliberately not supported.
- `+` sentences must parse. `*` sentences must be rejected.
- Each `*` sentence is a **minimal pair** with a `+` sentence: it differs in one thing only, so a wrong result points to exactly one rule or check.
- Sentences marked (ex) are from the assignment; the rest are our own, built from the vocabulary in section G.
- Sources are the slide / book section the construction is taken from.

## A. Sentence types

| ID | Construction | Tier | Source |
|---|---|---|---|
| A1 | Declarative | Must | Slide09 p. 18; SLP2 §12.3.1 |
| A2 | Yes-no question with a modal | Must | Slide09 p. 20 |
| A3 | Yes-no question with *do / does / did* | Should | Slide09 pp. 20, 44 |
| A4 | Yes-no question with *be* as main verb | Should | – (by analogy with A2) |
| A5 | Yes-no question with progressive *be* | Should | Slide09 pp. 20, 40 |
| A6 | Wh-question with a wh-adverb (*when, where, why, how*) | Must | Slide09 p. 23 |
| A7 | Wh-subject question (*who*, *which* + noun) | Should | Slide09 p. 22 |
| A8 | Positive imperative | Must | Slide09 p. 19 |
| A9 | Negative imperative | Must | (ex) S10 |
| A10 | Wh-adverb question with *be* as main verb | Should | – (A6 and A4 combined; added 25.11.2026) |

```
A1  + My friend enjoys historical novels.
    + The school is far from our village.
A2  + Will you attend the meeting tonight?            (ex)
    + Can we watch the moonlight tonight?
    * Will you attends the meeting tonight?
A3  + Did you help my mother?
    + Does my friend enjoy historical novels?
    + Do you listen to music?
    * Does you enjoy historical novels?
    * Did you helped my mother?
    * Enjoy you historical novels?
A4  + Is the school far from our village?
    + Is watermelon a fruit?
    * Are the school far from our village?
    * Bought you a present?
    + Is your mother here?
A5  + Are you listening to music?
    * Are you listen to music?
A6  + When did you come here lastly?                  (ex)
    + Where did you buy the present?
    + Why will you attend the meeting?
    * When did you came here?
    * When you did come here?
A7  + Who bought the present?
    + Who will attend the meeting?
    + Which friend helped my mother?
    * Who enjoy historical novels?
A8  + Listen to music.
    + Help my mother with dinner.
    + Come here.
    * Listens to music.
    * Went to the school.
A9  + Do not listen to loud music.                    (ex)
    + Do not go to the school.
    * Do not listens to loud music.
    * Not listen to loud music.
A10 + Where is the school?
    + How is your mother?
    * Where are the school?
    * Where the school is?
```

## B. Noun phrase

| ID | Construction | Tier | Source |
|---|---|---|---|
| B1 | Pronouns, subject and object forms | Should | SLP2 §12.3.4 (case) |
| B2 | Determiner + noun, number agreement | Must | Slide09 pp. 26, 43 |
| B3 | Possessive determiner (*my, our, ...*) | Must | (ex) S1, S3 |
| B4 | Bare plural and bare mass noun | Must | Slide09 p. 27 |
| B5 | Adjectives before the noun, stackable | Must | Slide09 p. 28 |
| B6 | Adjective with degree / superlative adverb | Must | (ex) S5, S9 |
| B7 | PP after the noun | Must | Slide09 p. 31 |
| B8 | Coordination with *and / or* | Must (nouns), Should (full NPs) | Slide09 p. 42 |
| B9 | Proper nouns | Should | Slide09 p. 7 |
| B10 | Cardinal numbers | Should | Slide09 p. 28 |
| B11 | Time expressions as NPs | Must | Slide09 p. 65 |
| B12 | Quantifiers (*many, much, some, all*) | Could | Slide09 p. 29 |

```
B1  + She helped me.
    + They watched us.
    * Her helped me.
    * She helped I.
B2  + This tree is beautiful.
    + These trees are beautiful.
    * This trees are beautiful.
    * These tree is beautiful.
    * I bought a presents.
    * I read a historical novels.                     (ex)
    * We watched the moonlight every nights.
B3  + My friends enjoy historical novels.
    + The school was far from our village.
B4  + I enjoy novels.
    + We listen to music.
    * I bought present.
    * Novel is beautiful.
B5  + I bought a beautiful historical novel.
    * I bought a novel beautiful.
B6  + I bought the most beautiful present.
    + I bought a very beautiful present.
    + The music was very loud.
    * I bought a very present.
B7  + I enjoy the fruit of summer.
    + The school in our village is far.
B8  + Epics tell about our national culture and history.   (ex)
    + I enjoy novels and music.
    + My mother and my father enjoy novels.
    * My mother and my father enjoys novels.
B9  + Ali bought a present.
    + I went to Ankara.
B10 + I bought two novels.
    + I bought one novel.
    * I bought two novel.
B11 + I came here yesterday.
    + We will come tomorrow.
    + I listen to music every night.
    * We watched the moonlight this tree.
B12 + I bought many novels.
    * I bought many novel.
```

## C. Verb phrase

| ID | Construction | Tier | Source |
|---|---|---|---|
| C1 | Intransitive verb | Must | Slide09 pp. 38, 51 |
| C2 | Transitive verb (NP object) | Must | Slide09 pp. 38, 51 |
| C3 | Verb + PP with a selected preposition | Must | Slide09 p. 53 |
| C4 | Verb + NP + PP | Must | Slide09 p. 52 (*help*: NP PPwith) |
| C5 | Ditransitive (NP NP) | Should | Slide09 p. 51 |
| C6 | *be* + NP / adjective phrase / PP / place adverb (*here*) | Must | (ex) S5, S9; Slide09 p. 65 |
| C7 | Adjuncts after the VP: place PP, time NP, adverb; several, any order | Must | SLP2 §12.5 |
| C8 | Adverb before the verb (*often, always, never*) | Could | – |

```
C1  + You came.
    + We came here yesterday.
    * You came the school.
C2  + I bought a present.
    + I enjoy historical novels.                      (ex)
    * I enjoy.
C3  + We went to the school.
    + I listen to music.
    + Epics tell about our history.
    * I went the school.                              (ex)
    * I went in the school.                           (ex)
    * I listen music.
C4  + I helped my mother with dinner.
    + I helped my mother.
C5  + I bought my friend a present.
    * I enjoy my friend a novel.
C6  + Watermelon is a fruit.
    + The school was far.
    + The school is in our village.
    * The school was quite.
    + The school is here.
    * The school is often.
C7  + We watched the moonlight under this tree every night.   (ex)
    + We watched the moonlight every night under this tree.
    + I bought a present for my friend in Ankara yesterday.
C8  + I often listen to music.
```

## D. Auxiliaries and verb forms

| ID | Construction | Tier | Source |
|---|---|---|---|
| D1 | Modal + bare stem | Must | Slide09 p. 40; SLP2 §12.3.6 |
| D2 | Progressive: *be* + -ing | Should | Slide09 p. 40; assignment (`going → go + ing`, ill-formed example X5) |
| D3 | Negation with *do / does / did* + *not* | Should | generalizes S10 |
| D4 | Negation after a modal or *be* | Should | generalizes S10 |
| D5 | Perfect: *have* + past participle | Could | Slide09 p. 40 |
| D6 | Auxiliary sequences (*will be watching*) | Could | Slide09 p. 41 |

```
D1  + I will help my father.
    + You can come here.
    * I will helped my father.
    * She can comes here.
D2  + I am reading the book.
    + We were watching the moonlight.
    + She is going to the school.
    * I was read the book.                            (ex)
    * We was watching the moonlight.
D3  + I did not buy a present.
    + She does not enjoy novels.
    * She do not enjoy novels.
    * I did not bought a present.
    * I bought not a present.
D4  + I will not attend the meeting.
    + The school was not far.
    + I am not reading the book.
    + They were not here.
D5  + I have watched the moonlight.
    + She has bought a present.
    * She have bought a present.
    * I have watch the moonlight.
D6  + I will be watching the moonlight.
    * She has will come.
```

## E. Agreement checks (cut across A–D)

| ID | Check | Tier | Source |
|---|---|---|---|
| E1 | Subject–verb person and number | Must | Slide09 pp. 43–49; SLP2 §15.3.1 |
| E2 | Subject–auxiliary in questions | Should | Slide09 p. 44 |
| E3 | Determiner–noun number | Must | see B2 |
| E4 | Tense of the clause vs. time expression | Must | own extension |
| E5 | Pronoun case | Should | see B1 |
| E6 | Verb form required by an auxiliary | Must | see D1–D5 |
| E7 | Complements required by the verb, incl. preposition | Must | see C1–C5 |

```
E1  + She enjoys novels.
    + They enjoy novels.
    * She enjoy novels.
    * They enjoys novels.
    * I buys a gift for my friend.                    (ex)
    * I is far from the school.
    * You was far from the school.
E2  + Does she enjoy novels?
    * Do she enjoy novels?
E4  + I will help my father tomorrow.
    + I helped my father yesterday.
    + Did you come yesterday?
    * I will help my father yesterday.                (ex)
    * I helped my father tomorrow.
    * Will you come yesterday?
    * I enjoy novels yesterday.
```

Note on E4: present tense with a future time is fine in English (*I am going to the school tomorrow*), so only past-with-future, future-with-past and present-with-past count as clashes.

## F. Out of scope

| Construction | Example | Reason |
|---|---|---|
| Sub-clauses: relative clauses, *that*-clauses, infinitive complements | *the novel that I read*, *I want to go* | excluded by the assignment ("without any sub-clauses") |
| Wh-question on an object or complement | *What did you buy?* | the object is missing from its position; needs long-distance dependency handling (SLP2 §15.3.4), no example requires it |
| Passive | *The book was read.* | no example requires it; makes `* I was read the book` harder to block |
| Coordination of VPs or sentences | *I came and you went.* | joins clauses; beyond "simple sentences" |
| Possessive *'s* | *my friend's present* | needs clitic tokenization; no example |
| Fronted adjuncts | *Yesterday I bought a present.* | assignment asks for SVO order only |
| Comparatives | *more beautiful than ...* | no example |
| Contractions, sentence-internal punctuation | *don't*, commas | handled, if at all, before the parser |

## G. Vocabulary the checklist needs beyond the 16 examples

Closed-class words (will be in the lexicon anyway once the closed classes are filled):
*he, she, it, they, me, him, her, us, them; an, these, those, that; can; am, are, were, be, does, have, has; who, which, where, why, how; or; very; one, two; many.*

Open-class additions:
- Noun forms: *friends, presents, trees, novel, nights*; time nouns *today, tomorrow*; proper nouns *Ali, Ankara*.
- Verb forms: *enjoys, buy, bought* (also as participle), *go, going, came, watch, watching, reading, listening, helped* etc. – every verb needs its full set of forms (bare, -s, past, -ing, participle).
- Adverb: *often* (only if C8 is kept).

## Summary

| Tier | Constructions |
|---|---|
| Must | A1 A2 A6 A8 A9 · B2–B7 B8(nouns) B11 · C1–C4 C6 C7 · D1 · E1 E3 E4 E6 E7 |
| Should | A3 A4 A5 A7 A10 · B1 B8(NPs) B9 B10 · C5 · D2 D3 D4 · E2 E5 |
| Could | B12 · C8 · D5 D6 |
| Out | section F |

Test sentences so far: 87 that must parse, 59 that must be rejected (146 in total).
