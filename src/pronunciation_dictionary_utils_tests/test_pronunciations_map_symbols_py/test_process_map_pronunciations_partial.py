from collections import OrderedDict

from ordered_set import OrderedSet

from pronunciation_dictionary_utils.pronunciations_map_symbols import (
  __init_pool, process_map_pronunciations_partial)


def test_component_change():
  dictionary = OrderedDict()
  pronunciations = OrderedDict()
  pronunciations[tuple(("t", "Ae", "s", "t"))] = 2
  pronunciations[tuple(("t", "Ae", "e", "s", "t"))] = 3
  pronunciations[tuple(("t", "s", "t"))] = 4  # keep untouched
  pronunciations[tuple(("t", "Ay", "s", "t"))] = 8  # same as first
  pronunciations[tuple(("t", "AX", "s", "t"))] = 5  # existing that will be extended

  dictionary["test"] = pronunciations

  __init_pool(dictionary)
  word, new_pronunciations = process_map_pronunciations_partial("test", OrderedSet(("e", "y")), "X")

  assert word == "test"
  assert new_pronunciations[tuple(("t", "AX", "s", "t"))] == 15
  assert new_pronunciations[tuple(("t", "AX", "X", "s", "t"))] == 3
  assert new_pronunciations[tuple(("t", "s", "t"))] == 4


def test_component_unchanged():
  dictionary = OrderedDict()
  pronunciations = OrderedDict()
  pronunciations[tuple(("t", "e", "s", "t"))] = 2
  dictionary["test"] = pronunciations

  __init_pool(dictionary)
  word, new_pronunciations = process_map_pronunciations_partial("test", OrderedSet(("X",)), "Y")

  assert word == "test"
  assert new_pronunciations is None
