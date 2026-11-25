#!/usr/bin/env python3
"""Convert the grammar to Chomsky Normal Form (CNF).

    python3 to_cnf.py        reads grammar/grammar.txt, writes grammar/grammar_cnf.txt

Why
---
The CKY algorithm combines exactly two neighbouring pieces at a time, so it
needs a grammar in which every rule has one of two shapes (SLP2 §12.5, §13.4.1):

    A -> B C      two non-terminals
    A -> w        one word

Our grammar is written to be read by people and has other shapes too:
"VP -> V NP PP" has three children and "NP -> Nom" has one. Every context-free
grammar can be converted to CNF without changing which sentences it accepts,
and this script does that mechanically.

What the textbook's conversion does (SLP2 §13.4.1), and what it means here
--------------------------------------------------------------------------
1. Rules that mix words with non-terminals get a new symbol for the word.
   Nothing to do for us: words appear only in the lexicon. A tag such as NN
   is a non-terminal, and the lexicon holds its rules NN -> school, NN -> tree.

2. Unit productions (rules with a single non-terminal child, A -> B) are
   removed. For every rule B -> ... that is not a unit production, and every
   chain of unit productions leading from B up to some A, a rule A -> ... is
   added. Example with the chain  NP -> Nom  on top of  Nom -> ADJP Nom:

       Nom -> ADJP Nom                    stays
       NP  -> ADJP Nom                    added

   The same happens to the lexical rules. From  NN -> school  and the chain
   Nom -> N, NP -> Nom  we get  Nom -> school  and  NP -> school.  We do not
   write that out for every word: "Nom -> [NN]" stands for "Nom -> w for
   every word w that the lexicon tags NN".

3. Rules with more than two children are cut from the left with new symbols:

       VP -> VBD NP PP      becomes      <VBD+NP> -> VBD NP
                                         VP -> <VBD+NP> PP

What happens to the feature constraints
---------------------------------------
A CNF rule remembers which rule(s) of the grammar it stands for, and the
parser applies their constraints in that order:

    NP -> ADJP Nom     stands for    Nom -> ADJP Nom,  then  NP -> Nom

so the parser first applies the constraints of "Nom -> ADJP Nom" to the two
children, and then those of "NP -> Nom" (the noun must be able to stand
without a determiner) to the result. A generated symbol such as <VBD+NP> has
no constraints of its own; it only collects the features of the children seen
so far, and the constraints of the long rule are applied when its last child
arrives. The same record lets the parser turn a CNF tree back into a tree of
the original grammar (SLP2 §13.4.1, "CKY in practice").
"""

import re
import sys
from collections import defaultdict

from paths import CNF_FILE, GRAMMAR_FILE, data_lines
from rules import load_grammar


class CnfRule:
    """One rule of the converted grammar.

    kind      "complete"  parent -> left right, completes a rule of the grammar
              "collect"   parent -> left right, parent is a generated symbol
              "lexical"   parent -> [tag]: any word with this tag (tag is in .left)
    source    the grammar rule that a "complete" rule completes
    chain     the unit productions applied on top of it, innermost first
    """

    def __init__(self, kind, parent, left, right=None, source=None, chain=()):
        self.kind, self.parent, self.left, self.right = kind, parent, left, right
        self.source, self.chain = source, list(chain)

    def key(self):
        origin = [self.source.text] if self.source else []
        return (self.kind, self.parent, self.left, self.right, *origin, *(unit.text for unit in self.chain))

    def origin(self):
        """The grammar rules this CNF rule stands for, as text."""
        if self.kind == "collect":
            return "collect"
        steps = ([self.source] if self.source else []) + self.chain
        return " ; ".join(rule.text for rule in steps)

    def __str__(self):
        right = f"[{self.left}]" if self.kind == "lexical" else f"{self.left} {self.right}"
        return f"{self.parent} -> {right}"


def is_generated(symbol):
    return symbol.startswith("<")


def check_no_loop(unit_rules):
    """Stop if unit productions lead back to their start (A -> B, B -> A)."""
    def reaches(start, symbol, seen):
        for rule in unit_rules.get(symbol, ()):
            if rule.lhs == start:
                return True
            if rule.lhs not in seen:
                seen.add(rule.lhs)
                if reaches(start, rule.lhs, seen):
                    return True
        return False

    for symbol in list(unit_rules):
        if reaches(symbol, symbol, set()):
            sys.exit(f"grammar: unit productions form a loop through {symbol}")


def chains_above(symbol, unit_rules):
    """Every chain of unit productions that starts at symbol and goes up.

    For NN in our grammar:  [Nom -> N]  and  [Nom -> N, NP -> Nom].
    """
    chains = []
    for unit in unit_rules.get(symbol, ()):
        chains.append([unit])
        chains += [[unit] + rest for rest in chains_above(unit.lhs, unit_rules)]
    return chains


def convert(rules):
    """Return the CNF rules for a list of grammar rules."""
    unit_rules = defaultdict(list)          # child symbol -> the unit productions above it
    longer_rules = []                       # rules with two or more children
    for rule in rules:
        if len(rule.children) == 1:
            unit_rules[rule.children[0]].append(rule)
        else:
            longer_rules.append(rule)
    check_no_loop(unit_rules)

    phrases = {rule.lhs for rule in rules}
    tags = {child for rule in rules for child in rule.children} - phrases

    cnf = []

    # Step 2a: unit productions above a tag become lexical rules.
    #          NN -> school, Nom -> N, NP -> Nom   gives   Nom -> [NN], NP -> [NN]
    for tag in sorted(tags):
        for chain in chains_above(tag, unit_rules):
            cnf.append(CnfRule("lexical", chain[-1].lhs, tag, chain=chain))

    # Step 2b: unit productions above a longer rule give a copy of that rule
    #          under the higher symbol.
    #          Nom -> ADJP Nom, NP -> Nom   gives   NP -> ADJP Nom
    with_chains = []
    for rule in longer_rules:
        with_chains.append((rule, []))
        for chain in chains_above(rule.lhs, unit_rules):
            with_chains.append((rule, chain))

    # Step 3: rules with more than two children are cut from the left.
    #         VP -> VBD NP PP   gives   <VBD+NP> -> VBD NP   and   VP -> <VBD+NP> PP
    generated_symbols = set()
    for rule, chain in with_chains:
        left = rule.children[0]
        for child in rule.children[1:-1]:
            generated = f"<{left.strip('<>')}+{child}>"
            if generated not in generated_symbols:
                generated_symbols.add(generated)
                cnf.append(CnfRule("collect", generated, left, child))
            left = generated
        parent = chain[-1].lhs if chain else rule.lhs
        cnf.append(CnfRule("complete", parent, left, rule.children[-1], rule, chain))
    return cnf


# ------------------------------------------------------- the CNF grammar file

def write_cnf(cnf_rules, path=CNF_FILE):
    """Write the CNF rules to a file, one per line:  rule | the grammar rules it stands for."""
    sections = [
        ("complete", "Binary rules. Right of the bar: the rule of grammar.txt whose constraints\n"
                     "# are applied, then any unit productions applied on top of it."),
        ("collect", "Generated symbols: the first children of a rule with more than two children.\n"
                    "# They have no constraints; they collect the features of the children."),
        ("lexical", "Lexical rules. [NN] stands for any word that the lexicon tags NN.\n"
                    "# Right of the bar: the unit productions applied to the word's features.\n"
                    "# The lexicon's own rules (NN -> school, ...) carry over unchanged."),
    ]
    counts = {kind: sum(rule.kind == kind for rule in cnf_rules) for kind, _ in sections}
    lines = [
        "# The grammar in Chomsky Normal Form.",
        "# GENERATED by to_cnf.py from grammar.txt - do not edit, edit grammar.txt instead.",
        f"# {counts['complete']} binary rules, {counts['collect']} generated symbols, "
        f"{counts['lexical']} lexical rules.",
    ]
    for kind, title in sections:
        lines += ["", f"# {title}"]
        for rule in cnf_rules:
            if rule.kind == kind:
                lines.append(f"{str(rule):<34} | {rule.origin()}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return counts


def read_cnf(rules, path=CNF_FILE):
    """Read the CNF file back. The grammar rules are needed for their constraints."""
    by_text = {rule.text: rule for rule in rules}
    cnf = []
    for line in data_lines(path):
        written, origin = (part.strip() for part in line.split(" | "))
        parent, right_side = (part.strip() for part in written.split("->"))
        lexical = re.fullmatch(r"\[(\S+)\]", right_side)
        steps = [] if origin == "collect" else [by_text[text.strip()] for text in origin.split(";")]
        if lexical:
            cnf.append(CnfRule("lexical", parent, lexical.group(1), chain=steps))
        elif origin == "collect":
            cnf.append(CnfRule("collect", parent, *right_side.split()))
        else:
            cnf.append(CnfRule("complete", parent, *right_side.split(), source=steps[0], chain=steps[1:]))
    return cnf


def main():
    rules, _ = load_grammar(GRAMMAR_FILE)
    counts = write_cnf(convert(rules), CNF_FILE)
    written = len({rule.text for rule in rules})
    print(f"read    {GRAMMAR_FILE.name}: {written} rules as written, {len(rules)} with the shorthands replaced by tags")
    print(f"wrote   {CNF_FILE.name}: {counts['complete']} binary rules, "
          f"{counts['collect']} generated symbols, {counts['lexical']} lexical rules")


if __name__ == "__main__":
    main()
