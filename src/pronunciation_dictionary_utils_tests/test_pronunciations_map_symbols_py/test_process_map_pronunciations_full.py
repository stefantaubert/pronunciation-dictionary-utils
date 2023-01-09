from collections import OrderedDict

from ordered_set import OrderedSet

from pronunciation_dictionary_utils.pronunciations_map_symbols import (
  __init_pool, process_map_pronunciations_full)


def test_component_change():
  dictionary = OrderedDict()
  pronunciations = OrderedDict()
  pronunciations[tuple(("t", "e", "s", "t"))] = 2
  pronunciations[tuple(("t", "e", "e", "s", "t"))] = 3
  pronunciations[tuple(("t", "s", "t"))] = 4  # keep untouched
  pronunciations[tuple(("t", "y", "s", "t"))] = 8  # same as first
  pronunciations[tuple(("t", "X", "s", "t"))] = 5  # existing that will be extended

  dictionary["test"] = pronunciations

  __init_pool(dictionary)
  word, new_pronunciations = process_map_pronunciations_full("test", OrderedSet(("e", "y")), ["X"])

  assert word == "test"
  assert new_pronunciations[tuple(("t", "X", "s", "t"))] == 15
  assert new_pronunciations[tuple(("t", "X", "X", "s", "t"))] == 3
  assert new_pronunciations[tuple(("t", "s", "t"))] == 4


def test_component_unchanged():
  dictionary = OrderedDict()
  pronunciations = OrderedDict()
  pronunciations[tuple(("t", "e", "s", "t"))] = 2
  dictionary["test"] = pronunciations

  __init_pool(dictionary)
  word, new_pronunciations = process_map_pronunciations_full("test", OrderedSet(("X",)), ["Y"])

  assert word == "test"
  assert new_pronunciations is None
