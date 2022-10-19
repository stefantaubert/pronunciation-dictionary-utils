
from collections import OrderedDict

from pronunciation_dictionary_utils.pronunciations_sorting import sort_pronunciations_entry


def test_component_asc_ign_weight():
  pronunciations = OrderedDict((
    (("b", "2"), 2),
    (("b", "1"), 2),
    (("a", "2"), 3),
    (("a", "1"), 3),
    (("c", "2"), 1),
    (("c", "1"), 1),
  ))

  result = sort_pronunciations_entry(pronunciations, False, True)

  assert result == OrderedDict((
    (("a", "1"), 3),
    (("a", "2"), 3),
    (("b", "1"), 2),
    (("b", "2"), 2),
    (("c", "1"), 1),
    (("c", "2"), 1),
  ))


def test_component_asc_cns_weight():
  pronunciations = OrderedDict((
    (("b", "2"), 2),
    (("b", "1"), 2),
    (("a", "2"), 3),
    (("a", "1"), 3),
    (("c", "2"), 1),
    (("c", "1"), 1),
  ))

  result = sort_pronunciations_entry(pronunciations, False, False)

  assert result == OrderedDict((
    (("a", "1"), 3),
    (("a", "2"), 3),
    (("b", "1"), 2),
    (("b", "2"), 2),
    (("c", "1"), 1),
    (("c", "2"), 1),
  ))



def test_component_dsc_ign_weight():
  pronunciations = OrderedDict((
    (("b", "2"), 2),
    (("b", "1"), 2),
    (("a", "2"), 3),
    (("a", "1"), 3),
    (("c", "2"), 1),
    (("c", "1"), 1),
  ))

  result = sort_pronunciations_entry(pronunciations, True, True)

  assert result == OrderedDict((
    (("c", "2"), 1),
    (("c", "1"), 1),
    (("b", "2"), 2),
    (("b", "1"), 2),
    (("a", "2"), 3),
    (("a", "1"), 3),
  ))


def test_component_dsc_cns_weight():
  pronunciations = OrderedDict((
    (("b", "2"), 2),
    (("b", "1"), 2),
    (("a", "2"), 3),
    (("a", "1"), 3),
    (("c", "2"), 1),
    (("c", "1"), 1),
  ))

  result = sort_pronunciations_entry(pronunciations, True, False)

  assert result == OrderedDict((
    (("c", "2"), 1),
    (("c", "1"), 1),
    (("b", "2"), 2),
    (("b", "1"), 2),
    (("a", "2"), 3),
    (("a", "1"), 3),
  ))
