"""The lexicon: for every word form, its Penn Treebank tags and features.

The lexicon stands in for the morphological analyzer that the assignment lets
us assume: it is a lookup table, nothing is computed from the spelling.
The features of a word form are put together from three files, later ones win:

    tags.txt      what the tag (the suffix) says      NNS is plural, VBD is past
    stems.txt     what holds for all forms of a word  "go" needs a "to" phrase
    lexicon.txt   the word forms: tag, stem+suffix, and features of irregular forms

The stem+suffix analysis links the last two: "went" is go+ed, so it gets the
features of the stem "go".
"""

from collections import defaultdict

from features import freeze, read_features
from paths import LEXICON_FILE, STEMS_FILE, TAGS_FILE, data_lines


def load_lexicon(lexicon_path=LEXICON_FILE, stems_path=STEMS_FILE, tags_path=TAGS_FILE):
    """Return {word form: [(tag, frozen feature bundle), ...]}.

    A word form has one entry per reading: "read" has four (VB, VBP, VBD, VBN),
    "did" has two with the same tag (auxiliary and main verb).
    """
    tag_features = {}
    for line in data_lines(tags_path):
        tag, *features = line.split()
        tag_features[tag] = features

    # stems.txt holds class definitions (V = VB VBP ...) and stem entries
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
        word, tag, analysis, *own_features = line.split()
        word = word.lower()
        stem = word if analysis == "-" else analysis.split("+")[0]
        stem_readings = [features for tags, features in stems[stem] if tag in tags] or [{}]
        for stem_features in stem_readings:
            bundle = read_features(tag_features.get(tag, []), word)
            bundle.update(stem_features)
            bundle.update(read_features(own_features, word))
            entry = (tag, freeze(bundle))
            if entry not in lexicon[word]:
                lexicon[word].append(entry)
    return dict(lexicon)
