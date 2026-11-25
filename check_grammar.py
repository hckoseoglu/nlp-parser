#!/usr/bin/env python3
"""Grammar checker: does the grammar accept a sentence, and with which trees?

A CKY parser (Jurafsky & Martin, SLP 2nd ed., §13.4.1) for the grammar in
grammar/grammar.txt. Every phrase in the table carries features (number,
verb form, ...); a rule is applied only if its constraints hold for the
features of its children (SLP2 §15.3). Every table entry remembers how it was
built, so all parse trees can be read back from the table.

Usage:
    python3 check_grammar.py                    run every sentence in data/tests.txt
    python3 check_grammar.py "Did you come?"    check one sentence and show its trees
    python3 check_grammar.py -i                 type sentences one by one
    python3 check_grammar.py --gold             check the hand-drawn trees against the grammar
Options for a single sentence:
    --all         show every tree (default: the first 10)
    --features    show the features of the words and of every phrase
"""

import argparse
import itertools
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
GRAMMAR_FILE = ROOT / "grammar" / "grammar.txt"
TAGS_FILE = ROOT / "grammar" / "tags.txt"
STEMS_FILE = ROOT / "grammar" / "stems.txt"
LEXICON_FILE = ROOT / "grammar" / "lexicon.txt"
TESTS_FILE = ROOT / "data" / "tests.txt"
GOLD_FILE = ROOT / "data" / "sentences.md"

START = "S"
MAX_TREES = 10


# ---------------------------------------------------------------- features
#
# A feature bundle maps feature names to sets of values: {"agr": {"3sg"}}.
# A set with several values means "any of these"; a missing feature means
# "not specified", which is compatible with everything. To store a bundle in
# the table it is frozen into a sorted tuple.

def read_features(tokens, word=None):
    """['agr=3sg', 'time=pres|fut'] -> {'agr': {'3sg'}, 'time': {'pres', 'fut'}}"""
    bundle = {}
    for token in tokens:
        name, values = token.split("=")
        bundle[name] = frozenset(word if v == "@" else v for v in values.split("|"))
    return bundle


def freeze(bundle):
    return tuple(sorted(bundle.items()))


def show_values(values):
    return "|".join(sorted(values)) if values is not None else "-"


def show_bundle(key):
    return ", ".join(f"{name}={show_values(values)}" for name, values in key)


def data_lines(path):
    """The lines of a data file without comments and blank lines."""
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.split("#")[0].rstrip()
        if line.strip():
            yield line


# ----------------------------------------------------------------- lexicon

def load_lexicon(lexicon_path, stems_path, tags_path):
    """Return {word form: [(tag, frozen feature bundle), ...]}.

    The features of a word form are put together from its tag (tags.txt),
    its stem (stems.txt) and its own line (lexicon.txt); later ones win.
    """
    tag_features = {}
    for line in data_lines(tags_path):
        tag, *features = line.split()
        tag_features[tag] = features

    classes = {}
    stems = defaultdict(list)
    for line in data_lines(stems_path):
        if "=" in line.split()[1]:
            name, tags = line.split("=")
            classes[name.strip()] = tags.split()
        else:
            stem, tag_class, *features = line.split()
            stems[stem].append((classes.get(tag_class, [tag_class]), read_features(features)))

    lexicon = defaultdict(list)
    for line in data_lines(lexicon_path):
        word, tag, analysis, *own = line.split()
        word = word.lower()
        stem = word if analysis == "-" else analysis.split("+")[0]
        readings = [features for tags, features in stems[stem] if tag in tags] or [{}]
        for stem_features in readings:
            bundle = read_features(tag_features.get(tag, []), word)
            bundle.update(stem_features)
            bundle.update(read_features(own, word))
            entry = (tag, freeze(bundle))
            if entry not in lexicon[word]:
                lexicon[word].append(entry)
    return dict(lexicon)


# ----------------------------------------------------------------- grammar

class Rule:
    """One grammar rule with its constraints, after the shorthands are expanded.

    checks: (kind, left, right, text) with kind "=" or "!=";
            left is (child position, feature), right is the same or a set of values
    passes: ("copy", child position)  or  ("set", feature, source)
            where source is (child position, feature) or a set of values
    """

    def __init__(self, lhs, children, checks, passes, text):
        self.lhs, self.children = lhs, children
        self.checks, self.passes, self.text = checks, passes, text


def read_constraint(line, lhs, written):
    """Turn one constraint line into a check or a pass-up for the rule lhs -> written."""

    def child(name):
        """Position of the child called name (NP, or NP_2 for the second NP)."""
        numbered = re.fullmatch(r"(.+)_(\d+)", name)
        if written.count(name) == 1 and name != lhs:
            return written.index(name)
        if numbered and written.count(numbered.group(1)) >= int(numbered.group(2)):
            positions = [i for i, symbol in enumerate(written) if symbol == numbered.group(1)]
            return positions[int(numbered.group(2)) - 1]
        sys.exit(f"grammar: cannot tell which child '{name}' is in: {lhs} -> {' '.join(written)}")

    def operand(text):
        """A.f -> (position, feature); anything else is a fixed value."""
        if "." in text:
            name, feature = text.split(".")
            return child(name), feature
        return frozenset(text.split("|"))

    if "<-" in line:
        left, right = (part.strip() for part in line.split("<-"))
        if left == lhs:
            return "pass", ("copy", child(right))
        if left.split(".")[0] != lhs:
            sys.exit(f"grammar: left of '<-' must be the parent {lhs}: {line.strip()}")
        return "pass", ("set", left.split(".")[1], operand(right))
    kind = "!=" if "!=" in line else "="
    left, right = (part.strip() for part in line.split(kind))
    return "check", (kind, operand(left), operand(right), line.strip())


def load_grammar(path):
    """Return the list of rules, one per combination of shorthand tags."""
    shorthands = {}
    written = []                 # [lhs, children, constraint lines]
    for line in data_lines(path):
        if line[0].isspace():
            written[-1][2].append(line)
        elif "->" in line:
            lhs, rhs = line.split("->")
            written.append([lhs.strip(), rhs.split(), []])
        elif "=" in line:
            name, tags = line.split("=")
            shorthands[name.strip()] = tags.split()
        else:
            sys.exit(f"grammar: cannot read line: {line}")

    rules = []
    for lhs, children, lines in written:
        checks, passes = [], []
        for line in lines:
            kind, constraint = read_constraint(line, lhs, children)
            (checks if kind == "check" else passes).append(constraint)
        text = f"{lhs} -> {' '.join(children)}"
        choices = [shorthands.get(child, [child]) for child in children]
        for expanded in itertools.product(*choices):
            rules.append(Rule(lhs, expanded, checks, passes, text))
    return rules, shorthands


def apply_constraints(rule, bundles, failures=None, span=None):
    """Check the rule's constraints on the children's features.

    Return the feature bundle of the parent, or None if a check fails.
    A successful "=" check narrows both sides to the values they share, so
    what is passed up afterwards is the agreed value.
    """
    work = [dict(bundle) for bundle in bundles]
    for kind, left, right, text in rule.checks:
        a = work[left[0]].get(left[1])
        is_child = isinstance(right, tuple)
        b = work[right[0]].get(right[1]) if is_child else right
        if kind == "=":
            shared = a if b is None else b if a is None else a & b
            failed = shared is not None and not shared
            if shared:
                work[left[0]][left[1]] = shared
                if is_child:
                    work[right[0]][right[1]] = shared
        else:
            failed = a is not None and b is not None and bool(a & b)
        if failed:
            if failures is not None:
                failures.append((span, rule.text, text, show_values(a), show_values(b)))
            return None

    parent = {}
    for step in rule.passes:
        if step[0] == "copy":
            parent.update(work[step[1]])
            continue
        _, feature, source = step
        value = work[source[0]].get(source[1]) if isinstance(source, tuple) else source
        if value is None:
            parent.pop(feature, None)
        else:
            parent[feature] = value
    return parent


def to_cky_form(rules):
    """Split the rules into the two tables the parser needs.

    binary[(B, C)] = what can be built from B followed by C: rules A -> B C,
                     and generated symbols
    one_child[B]   = the rules A -> B

    A rule with more than two children is cut from the left with generated
    symbols (SLP2 §13.4.1):  A -> B C D  becomes  <B+C> -> B C  and  A -> <B+C> D.
    A generated entry only collects the children seen so far; the constraints
    of the rule are checked when its last child arrives. One-child rules are
    kept and followed while the table is filled (SLP2 §13.4.1, "CKY in practice").
    """
    binary = defaultdict(list)
    one_child = defaultdict(list)
    for rule in rules:
        if len(rule.children) == 1:
            one_child[rule.children[0]].append(rule)
            continue
        left = rule.children[0]
        for child in rule.children[1:-1]:
            generated = f"<{left.strip('<>')}+{child}>"
            if generated not in binary[(left, child)]:
                binary[(left, child)].append(generated)
            left = generated
        binary[(left, rule.children[-1])].append(rule)
    check_no_loop(one_child)
    return binary, one_child


def check_no_loop(one_child):
    """Stop if one-child rules lead back to their start (A -> B, B -> A)."""
    def reaches(start, symbol, seen):
        for rule in one_child.get(symbol, ()):
            if rule.lhs == start:
                return True
            if rule.lhs not in seen:
                seen.add(rule.lhs)
                if reaches(start, rule.lhs, seen):
                    return True
        return False

    for symbol in list(one_child):
        if reaches(symbol, symbol, set()):
            sys.exit(f"grammar: one-child rules form a loop through {symbol}")


# ------------------------------------------------------------------ parser

def split_words(sentence):
    """Drop the final punctuation mark and split on spaces."""
    return sentence.strip().rstrip(".?!").split()


def is_generated(symbol):
    return symbol.startswith("<")


def cky(words, lexicon, binary, one_child, failures=None):
    """Fill the CKY table (SLP2 Fig. 13.10).

    An entry is (symbol, frozen feature bundle). table[i][j] maps every entry
    that spans words i..j-1 to the list of ways it can be built there (the
    backpointers). A way is one of
        ("word", word)                  a tag over a single word
        ("unit", entry)                 from an entry over the same span, by A -> B
        ("pair", k, left, right)        from entries over i..k and k..j, by A -> B C
    For a generated symbol the "bundle" is the tuple of the bundles of the
    children collected so far.
    """
    def add(i, j, entry, way):
        cell = table[i][j]
        is_new = entry not in cell
        cell.setdefault(entry, []).append(way)
        if is_new:
            symbol, key = entry
            for rule in one_child.get(symbol, ()):
                parent = apply_constraints(rule, [key], failures, (i, j))
                if parent is not None:
                    add(i, j, (rule.lhs, freeze(parent)), ("unit", entry))

    n = len(words)
    table = [[{} for _ in range(n + 1)] for _ in range(n + 1)]
    for j in range(1, n + 1):
        for entry in lexicon.get(words[j - 1].lower(), ()):
            add(j - 1, j, entry, ("word", words[j - 1]))
        for i in range(j - 2, -1, -1):
            for k in range(i + 1, j):
                for left in list(table[i][k]):
                    for right in list(table[k][j]):
                        collected = left[1] if is_generated(left[0]) else (left[1],)
                        collected += (right[1],)
                        for target in binary.get((left[0], right[0]), ()):
                            way = ("pair", k, left, right)
                            if isinstance(target, str):
                                add(i, j, (target, collected), way)
                                continue
                            parent = apply_constraints(target, collected, failures, (i, j))
                            if parent is not None:
                                add(i, j, (target.lhs, freeze(parent)), way)
    return table


def read_trees(table, entry, i, j, memo=None):
    """Return every tree for an entry over words i..j-1, following the backpointers.

    A tree is (label, [children], feature bundle); the child of a tag is the
    word itself. Generated symbols are not shown: their children move up to
    the parent, which gives back the rule as it is written in the grammar file.
    """
    if memo is None:
        memo = {}
    if (entry, i, j) in memo:
        return memo[(entry, i, j)]
    symbol, key = entry
    trees = []
    for way in table[i][j][entry]:
        if way[0] == "word":
            trees.append((symbol, [way[1]], key))
        elif way[0] == "unit":
            for child in read_trees(table, way[1], i, j, memo):
                trees.append((symbol, [child], key))
        else:
            _, k, left, right = way
            for left_tree in read_trees(table, left, i, k, memo):
                for right_tree in read_trees(table, right, k, j, memo):
                    first = left_tree[1] if is_generated(left[0]) else [left_tree]
                    trees.append((symbol, first + [right_tree], key))
    memo[(entry, i, j)] = trees
    return trees


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


class Checker:
    def __init__(self, grammar_file=GRAMMAR_FILE):
        self.lexicon = load_lexicon(LEXICON_FILE, STEMS_FILE, TAGS_FILE)
        rules, shorthands = load_grammar(grammar_file)
        self.rules = {(rule.lhs, rule.children) for rule in rules}
        self.check_symbols(shorthands)
        self.binary, self.one_child = to_cky_form(rules)

    def check_symbols(self, shorthands):
        """Stop on a symbol with no rule and no word, or a verb without a frame."""
        phrases = {lhs for lhs, _ in self.rules}
        tags = {tag for entries in self.lexicon.values() for tag, _ in entries}
        unknown = {child for _, children in self.rules for child in children} - phrases - tags
        if unknown:
            sys.exit(f"grammar: symbols with no rule and no word: {sorted(unknown)}")
        frameless = sorted(word for word, entries in self.lexicon.items()
                           for tag, key in entries
                           if tag in shorthands.get("V", ()) and "frame" not in dict(key))
        if frameless:
            sys.exit(f"lexicon: verbs whose stem has no frame in stems.txt: {frameless}")

    def unknown_words(self, sentence):
        return [w for w in split_words(sentence) if w.lower() not in self.lexicon]

    def table(self, sentence, failures=None):
        return cky(split_words(sentence), self.lexicon, self.binary, self.one_child, failures)

    def parses(self, sentence):
        """Every tree with the start symbol over the whole sentence."""
        words = split_words(sentence)
        if not words or self.unknown_words(sentence):
            return []
        table = self.table(sentence)
        trees = []
        for entry in table[0][len(words)]:
            if entry[0] == START:
                trees += read_trees(table, entry, 0, len(words))
        return trees

    def accepts(self, sentence):
        return bool(self.parses(sentence))


# ----------------------------------------------------------------- commands

def check_one(checker, sentence, show_all=False, features=False):
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
        if features:
            for tag, key in entries:
                print(f"  {word:<12} {tag:<5} {show_bundle(key)}")
        else:
            print(f"  {word:<12} {' '.join(sorted({tag for tag, _ in entries}))}")

    trees = checker.parses(sentence)
    if not trees:
        failures = []
        whole = checker.table(sentence, failures)[0][len(words)]
        phrases = sorted({symbol for symbol, _ in whole if not is_generated(symbol)})
        print("  REJECTED: no S covers the whole sentence")
        print(f"  covering the whole sentence: {', '.join(phrases) or 'nothing'}")
        print_failures(failures, words)
        return
    print(f"  ACCEPTED, {len(trees)} parse{'s' if len(trees) != 1 else ''}")
    shown = trees if show_all else trees[:MAX_TREES]
    for number, tree in enumerate(shown, 1):
        print(f"\n  parse {number}:")
        print(show_tree(tree, indent=4, features=features))
    if len(shown) < len(trees):
        print(f"\n  ... and {len(trees) - len(shown)} more (use --all to see them)")


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
    parser.add_argument("sentence", nargs="?", help="a sentence to check")
    parser.add_argument("-i", "--interactive", action="store_true", help="type sentences one by one")
    parser.add_argument("--gold", action="store_true", help="check the hand-drawn trees")
    parser.add_argument("--all", action="store_true", help=f"show every tree, not only the first {MAX_TREES}")
    parser.add_argument("--features", action="store_true", help="show the features of words and phrases")
    args = parser.parse_args()

    checker = Checker()
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
            check_one(checker, sentence, args.all, args.features)
        return
    if args.sentence:
        check_one(checker, args.sentence, args.all, args.features)
        return
    sys.exit(0 if run_tests(checker) else 1)


if __name__ == "__main__":
    main()
