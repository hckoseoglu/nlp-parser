"""The grammar rules as we write them, with their feature constraints.

grammar.txt holds rules such as

    S -> NP VP
        NP.agr = VP.agr          check:   the two values must be compatible
        VP.vform = fin           check:   against a fixed value
    VP -> VP PP
        VP_1.prep != PP.prep     check:   the two values must differ
        VP <- VP_1               pass up: the parent gets every feature of this child
    NP -> NP CC NP
        NP.agr <- 3pl            pass up: one feature, from a child or a fixed value

(Slide09 pp. 48, 56; SLP2 §15.3.) This module reads that file and applies
the constraints of a rule to the features of its children.
"""

import itertools
import re
import sys

from features import show_values
from paths import GRAMMAR_FILE, data_lines


class Rule:
    """One grammar rule, after the shorthands (V, N, P) are replaced by tags.

    lhs       the parent symbol
    children  the symbols on the right side
    checks    list of (kind, left, right, text); kind is "=" or "!=",
              left is (child position, feature),
              right is (child position, feature) or a set of fixed values
    passes    list of ("copy", child position)
              or ("set", feature, source), source being (child position, feature)
              or a set of fixed values
    text      the rule as written in the grammar file, e.g. "VP -> V NP"
    """

    def __init__(self, lhs, children, checks, passes, text):
        self.lhs, self.children = lhs, children
        self.checks, self.passes, self.text = checks, passes, text


def read_constraint(line, lhs, written):
    """Turn one constraint line of the rule  lhs -> written  into a check or a pass-up."""

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
        """A.f -> (position of A, f); anything else is a fixed value."""
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


def load_grammar(path=GRAMMAR_FILE):
    """Read the grammar file. Return (rules, shorthands).

    A rule written with a shorthand becomes one Rule per tag: "VP -> V NP"
    gives VP -> VB NP, VP -> VBD NP, ... all with the same constraints.
    """
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


def apply_constraints(rule, child_bundles, failures=None, span=None):
    """Apply a rule to the feature bundles of its children.

    Return the feature bundle of the parent, or None if a check fails.

    First all checks are made. A successful "=" check narrows both sides to
    the values they share ("the" + "novels" agree on 3pl), so that what is
    passed up afterwards is the agreed value. Then the pass-up statements
    build the parent's bundle.

    If a list is given as failures, a failed check is recorded in it (used
    to explain why a sentence is rejected).
    """
    work = [dict(bundle) for bundle in child_bundles]
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
