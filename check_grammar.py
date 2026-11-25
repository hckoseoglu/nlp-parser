#!/usr/bin/env python3
"""Check sentences against the grammar: accepted or not, and with which trees.

    python3 check_grammar.py                    run every sentence in data/tests.txt
    python3 check_grammar.py "Did you come?"    parse one sentence and show its trees
    python3 check_grammar.py -i                 type sentences one by one
    python3 check_grammar.py --gold             check the hand-drawn trees against the grammar

Options for a single sentence:
    --all         show every tree (default: the first 10)
    --features    show the features of the words and of every phrase
    --table       show the CKY table cell by cell, in the order it is filled
    --cnf         show the trees as the CNF grammar builds them, before they
                  are converted back to the grammar as we wrote it

The work is done by the other modules:
    rules.py      reads grammar/grammar.txt (rules with feature constraints)
    lexicon.py    reads the lexicon (tags.txt, stems.txt, lexicon.txt)
    to_cnf.py     converts the grammar to Chomsky Normal Form
    cky.py        the CKY parsing algorithm
Every run first converts the grammar again, so grammar/grammar_cnf.txt always
matches grammar/grammar.txt.
"""

import argparse
import re
import sys
from collections import Counter

from cky import CnfGrammar, cky_parse, cnf_trees, original_trees, sentence_entries, split_words
from features import show_bundle
from lexicon import load_lexicon
from paths import CNF_FILE, GOLD_FILE, GRAMMAR_FILE, TESTS_FILE
from rules import load_grammar
from to_cnf import convert, is_generated, read_cnf, write_cnf

MAX_TREES = 10


class Checker:
    """Grammar + lexicon + parser, ready to parse sentences."""

    def __init__(self, grammar_file=GRAMMAR_FILE, cnf_file=None):
        """With a cnf_file the converted grammar is written there and read
        back, so the parser works from the CNF file itself."""
        self.lexicon = load_lexicon()
        rules, shorthands = load_grammar(grammar_file)
        self.rules = {(rule.lhs, rule.children) for rule in rules}
        self.check_symbols(shorthands)
        cnf_rules = convert(rules)
        if cnf_file:
            write_cnf(cnf_rules, cnf_file)
            cnf_rules = read_cnf(rules, cnf_file)
        self.grammar = CnfGrammar(cnf_rules)

    def check_symbols(self, shorthands):
        """Stop on a symbol with no rule and no word, or a verb without a frame."""
        phrases = {lhs for lhs, _ in self.rules}
        tags = {tag for entries in self.lexicon.values() for tag, _ in entries}
        unknown = {child for _, children in self.rules for child in children} - phrases - tags
        if unknown:
            sys.exit(f"grammar: symbols with no rule and no word: {sorted(unknown)}")
        frameless = sorted(word for word, entries in self.lexicon.items()
                           for tag, features in entries
                           if tag in shorthands.get("V", ()) and "frame" not in dict(features))
        if frameless:
            sys.exit(f"lexicon: verbs whose stem has no frame in stems.txt: {frameless}")

    def unknown_words(self, sentence):
        return [w for w in split_words(sentence) if w.lower() not in self.lexicon]

    def table(self, sentence, failures=None):
        return cky_parse(split_words(sentence), self.lexicon, self.grammar, failures)

    def parses(self, sentence, cnf=False):
        """Every tree for the whole sentence (empty list: not accepted)."""
        words = split_words(sentence)
        if not words or self.unknown_words(sentence):
            return []
        table = self.table(sentence)
        read = cnf_trees if cnf else original_trees
        trees = []
        for entry in sentence_entries(table):
            trees += read(table, entry, 0, len(words))
        return trees

    def accepts(self, sentence):
        return bool(self.parses(sentence))


# ------------------------------------------------------------------ printing

def one_line(tree, features=False):
    label, children = tree[0], tree[1]
    if features and len(tree) > 2 and tree[2]:
        label += "{" + show_bundle(tree[2]) + "}"
    if isinstance(children[0], str):
        return f"[{label} {children[0]}]"
    return f"[{label} {' '.join(one_line(child, features) for child in children)}]"


def show_tree(tree, indent=0, width=78, features=False):
    """Bracketed tree; a phrase that does not fit on the line is broken up."""
    flat = one_line(tree, features)
    if indent + len(flat) <= width or isinstance(tree[1][0], str):
        return " " * indent + flat
    label = one_line((tree[0], ["."], tree[2]), features)[1:-3]
    lines = [" " * indent + "[" + label]
    lines += [show_tree(child, indent + 2, width, features) for child in tree[1]]
    return "\n".join(lines) + "]"


def print_table(table, words):
    """The CKY table, one line per cell, in the order the cells are filled."""
    n = len(words)
    print("  CKY table (cells in the order they are filled):")
    for j in range(1, n + 1):
        for i in range(j - 1, -1, -1):
            symbols = sorted({entry.symbol for entry in table[i][j]}, key=lambda s: (is_generated(s), s))
            stretch = " ".join(words[i:j])
            print(f"    [{i},{j}] {stretch:<32} {' '.join(symbols) or '-'}")


def print_failures(failures, words, limit=5):
    """Show the failed checks that covered the most words: the likely reasons."""
    seen, lines = set(), []
    for (i, j), rule, check, a, b in sorted(failures, key=lambda f: f[0][0] - f[0][1]):
        line = f"    \"{' '.join(words[i:j])}\":  {rule}  fails  {check}  ({a} / {b})"
        if line not in seen:
            seen.add(line)
            lines.append(line)
    if lines:
        print("  failed checks, longest stretch of words first (the cause is usually among them):")
        print("\n".join(lines[:limit]))


# ------------------------------------------------------------------ commands

def check_one(checker, sentence, args):
    """Print the verdict for one sentence, the tags of its words and its trees."""
    words = split_words(sentence)
    if not words:
        return
    unknown = checker.unknown_words(sentence)
    if unknown:
        print(f"  not in the lexicon: {', '.join(unknown)}")
        return
    for word in words:
        entries = checker.lexicon[word.lower()]
        if args.features:
            for tag, features in entries:
                print(f"  {word:<12} {tag:<5} {show_bundle(features)}")
        else:
            print(f"  {word:<12} {' '.join(sorted({tag for tag, _ in entries}))}")

    failures = []
    table = checker.table(sentence, failures)
    if args.table:
        print_table(table, words)
    trees = checker.parses(sentence, cnf=args.cnf)
    if not trees:
        phrases = sorted({entry.symbol for entry in table[0][len(words)] if not is_generated(entry.symbol)})
        print("  REJECTED: no S covers the whole sentence")
        print(f"  covering the whole sentence: {', '.join(phrases) or 'nothing'}")
        print_failures(failures, words)
        return
    kind = "CNF parse" if args.cnf else "parse"
    print(f"  ACCEPTED, {len(trees)} {kind}{'s' if len(trees) != 1 else ''}")
    shown = trees if args.all else trees[:MAX_TREES]
    for number, tree in enumerate(shown, 1):
        print(f"\n  {kind} {number}:")
        print(show_tree(tree, indent=4, features=args.features))
    if len(shown) < len(trees):
        print(f"\n  ... and {len(trees) - len(shown)} more (use --all to see them)")


def run_tests(checker):
    """Run data/tests.txt. Return True when every sentence gets the expected verdict."""
    good_rejected, bad_accepted, unknown = [], [], []
    n_good = n_bad = 0
    parse_counts = Counter()
    for line in TESTS_FILE.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        test_id, expected, sentence = line.split("\t")
        if checker.unknown_words(sentence):
            unknown.append((test_id, sentence, checker.unknown_words(sentence)))
            continue
        n_parses = len(checker.parses(sentence))
        if expected == "+":
            n_good += 1
            parse_counts[n_parses] += 1
            if not n_parses:
                good_rejected.append((test_id, sentence))
        else:
            n_bad += 1
            if n_parses:
                bad_accepted.append((test_id, sentence))

    print(f"must parse:      {n_good - len(good_rejected):3d} of {n_good} accepted")
    print(f"must be rejected:{n_bad - len(bad_accepted):3d} of {n_bad} rejected")
    spread = ", ".join(f"{count} with {n}" for n, count in sorted(parse_counts.items()) if n)
    print(f"parses per accepted good sentence: {spread}")
    if unknown:
        print("\nSentences with words missing from the lexicon:")
        for test_id, sentence, words in unknown:
            print(f"  {test_id:<6} {sentence}   [{', '.join(words)}]")
    if good_rejected:
        print("\nGood sentences the grammar rejects:")
        for test_id, sentence in good_rejected:
            print(f"  {test_id:<6} {sentence}")
    if bad_accepted:
        print("\nBad sentences the grammar accepts:")
        for test_id, sentence in bad_accepted:
            print(f"  {test_id:<6} {sentence}")
    return not good_rejected and not bad_accepted and not unknown


def read_tree(text):
    """Read one bracketed tree, e.g. [NP [DT the] [Nom [NN school]]]."""
    tokens = re.findall(r"\[|\]|[^\s\[\]]+", text)
    position = 0

    def node():
        nonlocal position
        position += 1                      # skip "["
        label = tokens[position]
        position += 1
        children = []
        while tokens[position] != "]":
            if tokens[position] == "[":
                children.append(node())
            else:
                children.append(tokens[position])
                position += 1
        position += 1                      # skip "]"
        return label, children

    return node()


def leaves(tree):
    children = tree[1]
    if isinstance(children[0], str):
        return [children[0]]
    return [word for child in children for word in leaves(child)]


def check_gold(checker):
    """Check every hand-drawn tree: it must use only rules and words of the
    grammar, and it must be one of the trees the parser finds for its sentence."""
    text = GOLD_FILE.read_text(encoding="utf-8")
    all_fine = True

    def problems(tree, found):
        label, children = tree
        if isinstance(children[0], str):
            if label not in {tag for tag, _ in checker.lexicon.get(children[0].lower(), ())}:
                found.append(f"{children[0]}/{label} is not in the lexicon")
            return
        if (label, tuple(child[0] for child in children)) not in checker.rules:
            found.append(f"no rule {label} -> {' '.join(child[0] for child in children)}")
        for child in children:
            problems(child, found)

    for tree_id, tree_text in re.findall(r"```tree (\S+)\n(.*?)```", text, re.S):
        gold = read_tree(tree_text)
        found = []
        problems(gold, found)
        trees = checker.parses(" ".join(leaves(gold)))
        if not found and one_line(gold) not in {one_line(tree) for tree in trees}:
            found.append(f"the parser does not find this tree (it finds {len(trees)})")
        verdict = f"ok, 1 of {len(trees)} parses" if not found else "; ".join(found)
        print(f"  {tree_id:<4} {verdict}")
        all_fine = all_fine and not found
    return all_fine


def main():
    parser = argparse.ArgumentParser(description="Check sentences against the grammar.")
    parser.add_argument("sentence", nargs="?", help="a sentence to parse")
    parser.add_argument("-i", "--interactive", action="store_true", help="type sentences one by one")
    parser.add_argument("--gold", action="store_true", help="check the hand-drawn trees")
    parser.add_argument("--all", action="store_true", help=f"show every tree, not only the first {MAX_TREES}")
    parser.add_argument("--features", action="store_true", help="show the features of words and phrases")
    parser.add_argument("--table", action="store_true", help="show the CKY table")
    parser.add_argument("--cnf", action="store_true", help="show the trees of the CNF grammar")
    args = parser.parse_args()

    checker = Checker(GRAMMAR_FILE, CNF_FILE)
    if args.gold:
        sys.exit(0 if check_gold(checker) else 1)
    if args.interactive:
        print("Type a sentence (empty line to stop).")
        while True:
            try:
                sentence = input("> ")
            except EOFError:
                break
            if not sentence.strip():
                break
            check_one(checker, sentence, args)
        return
    if args.sentence:
        check_one(checker, args.sentence, args)
        return
    sys.exit(0 if run_tests(checker) else 1)


if __name__ == "__main__":
    main()
