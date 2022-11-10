from collections import OrderedDict

import pytest

from pronunciation_dictionary_utils.common import merge_pronunciations


def test_component():
  p1 = OrderedDict()
  p1[("a",)] = 2
  p1[("b",)] = 3
  p1[("d",)] = 5

  p2 = OrderedDict()
  p2[("a",)] = 2
  p2[("c",)] = 4
  p2[("e", "f")] = 6

  changed_anything = merge_pronunciations(p1, p2)

  assert changed_anything
  assert p1 == OrderedDict((
    (("a",), 4),
    (("b",), 3),
    (("d",), 5),
    (("c",), 4),
    (("e", "f"), 6),
  ))


def test_same_instance__changes_nothing():
  p1 = OrderedDict()
  p1[("a",)] = 2

  changed_anything = merge_pronunciations(p1, p1)

  assert not changed_anything
  assert p1 == OrderedDict((
    (("a",), 2),
  ))


def test_same_key__weights_are_added():
  p1 = OrderedDict()
  p1[("a",)] = 2

  p2 = OrderedDict()
  p2[("a",)] = 3

  changed_anything = merge_pronunciations(p1, p2)

  assert changed_anything
  assert p1 == OrderedDict((
    (("a",), 5),
  ))


def test_same_key_zero_weight__changes_nothing():
  p1 = OrderedDict()
  p1[("a",)] = 2

  p2 = OrderedDict()
  p2[("a",)] = 0

  changed_anything = merge_pronunciations(p1, p2)

  assert not changed_anything
  assert p1 == OrderedDict((
    (("a",), 2),
  ))


def test_different_key__key_is_added():
  p1 = OrderedDict()
  p1[("a",)] = 2

  p2 = OrderedDict()
  p2[("b",)] = 3

  changed_anything = merge_pronunciations(p1, p2)

  assert changed_anything
  assert p1 == OrderedDict((
    (("a",), 2),
    (("b",), 3),
  ))


def test_p1_empty_raises_error():
  p1 = OrderedDict()

  p2 = OrderedDict()
  p2[("a",)] = 2

  with pytest.raises(ValueError) as error:
    merge_pronunciations(p1, p2)


def test_p2_empty_raises_error():
  p1 = OrderedDict()
  p1[("a",)] = 2

  p2 = OrderedDict()

  with pytest.raises(ValueError) as error:
    merge_pronunciations(p1, p2)
