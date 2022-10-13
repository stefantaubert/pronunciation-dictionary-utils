from collections import OrderedDict

from ordered_set import OrderedSet

from pronunciation_dictionary_utils.pronunciations_map_symbols import (
  __init_pool_prepare_cache_mp, process_map_pronunciation_full)


def test_component():
  dictionary = OrderedDict()
  pronunciations = OrderedDict()
  pronunciations[tuple(("t", "e", "s", "t"))] = 2
  pronunciations[tuple(("t", "e", "e", "s", "t"))] = 3
  pronunciations[tuple(("t", "s", "t"))] = 4  # keep untouched
  pronunciations[tuple(("t", "y", "s", "t"))] = 8  # same as first
  pronunciations[tuple(("t", "X", "s", "t"))] = 5  # existing that will be extended

  dictionary["test"] = pronunciations

  __init_pool_prepare_cache_mp(dictionary)
  word, pron = process_map_pronunciation_full("test", OrderedSet(("e", "y")), "X")

  assert word == "test"
  assert pron[tuple(("t", "X", "s", "t"))] == 15
  assert pron[tuple(("t", "X", "X", "s", "t"))] == 3
  assert pron[tuple(("t", "s", "t"))] == 4
