
from collections import OrderedDict

from pronunciation_dictionary_utils.pronunciations_remove_symbols import \
  remove_symbols_from_pronunciations_entry


def test_component():
  pronunciations = OrderedDict((
    (("ˌaʊ", "ɚ", "s", ".", "ˈe", "l", "v", "z"), 6),
    (("ˌaʊ", "ɚ", "s", ".", "ˈe", "l", "v", "z", "!"), 7),
    ((".", "ˌaʊ", "ɚ", "s", ".", "ˈe", "l", "v", "z", ","), 8),
  ))

  result = remove_symbols_from_pronunciations_entry(pronunciations, {"!", ",", "."}, "both")

  assert result == OrderedDict((
    (("ˌaʊ", "ɚ", "s", ".", "ˈe", "l", "v", "z"), 21),
  ))
