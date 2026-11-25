"""The CKY parsing algorithm, with feature checks.

The algorithm (Cocke-Kasami-Younger; SLP2 §13.4.1, Fig. 13.10)
------------------------------------------------------------
CKY needs a grammar in Chomsky Normal Form: every rule is either
A -> B C (two non-terminals) or A -> w (one word). to_cnf.py produces it.

Number the gaps between the words of the sentence:

      0  She  1  enjoys  2  historical  3  novels  4

A stretch of words is named by the gaps at its ends: [1,4] is "enjoys
historical novels". The parser fills a table with one cell for every stretch.
Cell [i,j] holds every phrase the grammar can build over the words from gap i
to gap j.

The idea is to work from short stretches to long ones (dynamic programming):

  * A stretch of one word, [j-1,j]: look the word up in the lexicon.
  * A longer stretch [i,j]: in CNF every phrase has exactly two children, so
    the stretch must split somewhere into a left part [i,k] and a right part
    [k,j]. Try every split point k. Both parts are shorter, so their cells are
    already filled. For every B in cell [i,k] and C in cell [k,j], every rule
    A -> B C puts an A into cell [i,j].

The sentence is accepted if the start symbol S ends up in cell [0,n], the
cell for the whole sentence.

Order of filling. The table is filled one column at a time, left to right
(j = 1 .. n), and inside a column from the bottom up (i = j-2 down to 0).
This guarantees that the two cells a split needs are filled before the cell
itself: [i,k] lies in an earlier column, [k,j] lower in the same column.

Cost. There are about n*n/2 cells, each tries up to n split points, so the
work grows with n*n*n (times the number of rules), not exponentially, even
though a sentence can have exponentially many trees. Each sub-phrase is built
once and reused by every larger phrase that contains it.

What we add to the textbook algorithm
-------------------------------------
1. Features. A table entry is a symbol together with its feature bundle, for
   example (NP, agr=3sg). A rule A -> B C produces an entry only if the
   constraints of the grammar rule(s) it stands for hold for the features of
   B and C; the result is A with the features passed up. This is how the
   agreement checks are made during parsing (SLP2 §15.3, §15.5).

2. Backpointers. A recognizer only needs to know that A is in a cell. To get
   trees, every entry also keeps a list of the ways it was built: which rule,
   which split point, which two entries. Following these backpointers from S
   in cell [0,n] gives the trees; an entry built in several ways gives
   several trees (ambiguity).

3. Back to the original grammar. The trees read from the table are CNF trees.
   Because each CNF rule knows which grammar rules it stands for, a CNF tree
   is turned back into a tree of the grammar as we wrote it: generated
   symbols are removed and removed unit productions are put back.
"""

from collections import defaultdict, namedtuple

from features import freeze
from rules import apply_constraints
from to_cnf import is_generated

START = "S"

# A table entry: a symbol with its features. For a generated symbol the
# "features" are the bundles of the children collected so far.
Entry = namedtuple("Entry", "symbol features")

# The two kinds of backpointer: how an entry was built.
FromWord = namedtuple("FromWord", "word tag_entry rule")       # rule is None for the tag itself
FromPair = namedtuple("FromPair", "rule split left right")


class CnfGrammar:
    """The CNF rules, indexed the way the parser looks them up."""

    def __init__(self, cnf_rules):
        self.binary = defaultdict(list)      # (left symbol, right symbol) -> rules
        self.lexical = defaultdict(list)     # tag -> rules  parent -> [tag]
        for rule in cnf_rules:
            if rule.kind == "lexical":
                self.lexical[rule.left].append(rule)
            else:
                self.binary[(rule.left, rule.right)].append(rule)


def split_words(sentence):
    """Drop the final punctuation mark and split on spaces."""
    return sentence.strip().rstrip(".?!").split()


def collected(entry):
    """The feature bundles an entry contributes to its parent rule: its own
    bundle, or for a generated symbol the bundles it has collected."""
    return entry.features if is_generated(entry.symbol) else (entry.features,)


def build(rule, child_bundles, failures=None, span=None):
    """Apply a CNF rule to the feature bundles of its children.

    A CNF rule stands for a grammar rule followed by zero or more unit
    productions. Their constraints are applied in that order, each to the
    result of the one before. Return the list of resulting bundles, one per
    step (the last one belongs to the CNF rule's parent), or None as soon as
    a check fails.
    """
    steps = []
    bundles = child_bundles
    for grammar_rule in ([rule.source] if rule.source else []) + rule.chain:
        bundle = apply_constraints(grammar_rule, bundles, failures, span)
        if bundle is None:
            return None
        steps.append(freeze(bundle))
        bundles = [steps[-1]]
    return steps


def cky_parse(words, lexicon, grammar, failures=None):
    """Fill the CKY table for a list of words and return it.

    table[i][j] is a dictionary: entry -> list of backpointers.
    """
    n = len(words)
    table = [[{} for _ in range(n + 1)] for _ in range(n + 1)]

    def add(i, j, entry, backpointer):
        table[i][j].setdefault(entry, []).append(backpointer)

    for j in range(1, n + 1):                           # one column per word, left to right

        # --- The cell for the single word j: [j-1, j] -------------------------
        # Every reading of the word in the lexicon gives its tag (NN -> school).
        # Lexical rules of the CNF grammar give the phrases a single word can
        # be (Nom -> [NN], NP -> [NN]), if their constraints allow it.
        word = words[j - 1]
        for tag, features in lexicon.get(word.lower(), ()):
            tag_entry = Entry(tag, features)
            add(j - 1, j, tag_entry, FromWord(word, tag_entry, None))
            for rule in grammar.lexical.get(tag, ()):
                steps = build(rule, [features], failures, (j - 1, j))
                if steps is not None:
                    add(j - 1, j, Entry(rule.parent, steps[-1]), FromWord(word, tag_entry, rule))

        # --- The longer stretches that end at word j: [i, j] ------------------
        # From the shortest (i = j-2) to the longest (i = 0).
        for i in range(j - 2, -1, -1):
            for k in range(i + 1, j):                   # every split into [i,k] and [k,j]
                for left in list(table[i][k]):
                    for right in list(table[k][j]):
                        for rule in grammar.binary.get((left.symbol, right.symbol), ()):
                            backpointer = FromPair(rule, k, left, right)
                            child_bundles = collected(left) + (right.features,)
                            if rule.kind == "collect":
                                # first part of a long rule: no checks yet, keep the features
                                add(i, j, Entry(rule.parent, child_bundles), backpointer)
                                continue
                            steps = build(rule, child_bundles, failures, (i, j))
                            if steps is not None:       # all constraints hold
                                add(i, j, Entry(rule.parent, steps[-1]), backpointer)
    return table


def sentence_entries(table):
    """The entries for the start symbol over the whole sentence."""
    return [entry for entry in table[0][len(table) - 1] if entry.symbol == START]


# ---------------------------------------------------------- reading the trees
#
# A tree is (label, children, features); the only child of a tag is the word.

def cnf_trees(table, entry, i, j, memo=None):
    """Every tree for an entry, exactly as the CNF grammar built it."""
    memo = {} if memo is None else memo
    if (entry, i, j) not in memo:
        trees = []
        for back in table[i][j][entry]:
            if isinstance(back, FromWord):
                trees.append((entry.symbol, [back.word], entry.features))
                continue
            for left_tree in cnf_trees(table, back.left, i, back.split, memo):
                for right_tree in cnf_trees(table, back.right, back.split, j, memo):
                    features = () if is_generated(entry.symbol) else entry.features
                    trees.append((entry.symbol, [left_tree, right_tree], features))
        memo[(entry, i, j)] = trees
    return memo[(entry, i, j)]


def original_trees(table, entry, i, j, memo=None):
    """Every tree for an entry, converted back to the grammar as we wrote it.

    Two things are undone (SLP2 §13.4.1, "CKY in practice"):
      * a generated symbol is not shown; its children move up to the parent,
        which gives back the rule with more than two children;
      * the unit productions that the CNF rule stands for are put back as
        separate levels:  NP -> [NN]  becomes  [NP [Nom [NN school]]].
    """
    memo = {} if memo is None else memo
    if (entry, i, j) in memo:
        return memo[(entry, i, j)]

    def put_back(node, rule, child_bundles):
        """Wrap node in the levels the CNF rule's unit productions stand for."""
        steps = build(rule, child_bundles)
        if rule.source:                                 # the grammar rule itself
            node = (rule.source.lhs, node, steps[0])
            steps = steps[1:]
        for unit, features in zip(rule.chain, steps):   # the unit productions above it
            node = (unit.lhs, [node], features)
        return node

    trees = []
    for back in table[i][j][entry]:
        if isinstance(back, FromWord):
            leaf = (back.tag_entry.symbol, [back.word], back.tag_entry.features)
            if back.rule is None:
                trees.append(leaf)
            else:
                trees.append(put_back(leaf, back.rule, [back.tag_entry.features]))
            continue
        for left_tree in original_trees(table, back.left, i, back.split, memo):
            for right_tree in original_trees(table, back.right, back.split, j, memo):
                # the children of a generated symbol move up
                first = left_tree[1] if is_generated(back.left.symbol) else [left_tree]
                children = first + [right_tree]
                if back.rule.kind == "collect":
                    trees.append((entry.symbol, children, ()))
                else:
                    child_bundles = collected(back.left) + (back.right.features,)
                    trees.append(put_back(children, back.rule, child_bundles))
    memo[(entry, i, j)] = trees
    return trees
