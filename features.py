"""Feature bundles: the properties a word or phrase carries (number, verb form, ...).

A bundle maps feature names to sets of values, for example

    {"agr": {"3sg"}, "time": {"pres", "fut"}}

- A set with several values means "any of these" (present tense fits a
  present or a future time).
- A missing feature means "not specified", which is compatible with
  everything ("the" has no number, so it fits "school" and "schools").

To store a bundle in the parse table it is frozen into a sorted tuple, which
Python can use as a dictionary key.
"""


def read_features(tokens, word=None):
    """['agr=3sg', 'time=pres|fut'] -> {'agr': {'3sg'}, 'time': {'pres', 'fut'}}

    The value "@" stands for the word itself (a preposition is its own "prep").
    """
    bundle = {}
    for token in tokens:
        name, values = token.split("=")
        bundle[name] = frozenset(word if value == "@" else value for value in values.split("|"))
    return bundle


def freeze(bundle):
    return tuple(sorted(bundle.items()))


def show_values(values):
    return "|".join(sorted(values)) if values is not None else "-"


def show_bundle(frozen):
    return ", ".join(f"{name}={show_values(values)}" for name, values in frozen)
