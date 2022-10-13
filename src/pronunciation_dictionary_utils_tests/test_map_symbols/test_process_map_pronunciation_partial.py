from collections import OrderedDict

from ordered_set import OrderedSet

from pronunciation_dictionary_utils.pronunciations_map_symbols import (
  __init_pool_prepare_cache_mp, process_map_pronunciation_partial)


def test_component():
  dictionary = OrderedDict()
  pronunciations = OrderedDict()
  pronunciations[tuple(("t", "Ae", "s", "t"))] = 2
  pronunciations[tuple(("t", "Ae", "e", "s", "t"))] = 3
  pronunciations[tuple(("t", "s", "t"))] = 4  # keep untouched
  pronunciations[tuple(("t", "Ay", "s", "t"))] = 8  # same as first
  pronunciations[tuple(("t", "AX", "s", "t"))] = 5  # existing that will be extended

  dictionary["test"] = pronunciations

  __init_pool_prepare_cache_mp(dictionary)
  word, pron = process_map_pronunciation_partial("test", OrderedSet(("e", "y")), "X")

  assert word == "test"
  assert pron[tuple(("t", "AX", "s", "t"))] == 15
  assert pron[tuple(("t", "AX", "X", "s", "t"))] == 3
  assert pron[tuple(("t", "s", "t"))] == 4
