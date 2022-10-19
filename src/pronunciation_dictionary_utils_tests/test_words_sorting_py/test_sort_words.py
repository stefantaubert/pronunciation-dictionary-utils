from collections import OrderedDict

from pronunciation_dictionary_utils.words_sorting import sort_words


def test_component_ascending_cased():
  pronunciation_dict = OrderedDict()

  pronunciation_dict["B"] = OrderedDict((
    (("b",), 1),
  ))

  pronunciation_dict["b"] = OrderedDict((
    (("b",), 1),
  ))

  pronunciation_dict["A"] = OrderedDict((
    (("a",), 1),
  ))

  pronunciation_dict["a"] = OrderedDict((
    (("a",), 1),
  ))

  pronunciation_dict["C"] = OrderedDict((
    (("c",), 1),
  ))

  pronunciation_dict["c"] = OrderedDict((
    (("c",), 1),
  ))

  result = sort_words(pronunciation_dict, False, True)

  assert list(result.keys()) == ["A", "B", "C", "a", "b", "c"]
  assert result["A"] == OrderedDict((
    (("a",), 1),
  ))


def test_component_ascending_uncased():
  pronunciation_dict = OrderedDict()

  pronunciation_dict["B"] = OrderedDict((
    (("b",), 1),
  ))

  pronunciation_dict["b"] = OrderedDict((
    (("b",), 1),
  ))

  pronunciation_dict["A"] = OrderedDict((
    (("a",), 1),
  ))

  pronunciation_dict["a"] = OrderedDict((
    (("a",), 1),
  ))

  pronunciation_dict["C"] = OrderedDict((
    (("c",), 1),
  ))

  pronunciation_dict["c"] = OrderedDict((
    (("c",), 1),
  ))

  result = sort_words(pronunciation_dict, False, False)

  assert list(result.keys()) == ["A", "a", "B", "b", "C", "c"]
  assert result["A"] == OrderedDict((
    (("a",), 1),
  ))


def test_component_descending_cased():
  pronunciation_dict = OrderedDict()

  pronunciation_dict["B"] = OrderedDict((
    (("b",), 1),
  ))

  pronunciation_dict["b"] = OrderedDict((
    (("b",), 1),
  ))

  pronunciation_dict["A"] = OrderedDict((
    (("a",), 1),
  ))

  pronunciation_dict["a"] = OrderedDict((
    (("a",), 1),
  ))

  pronunciation_dict["C"] = OrderedDict((
    (("c",), 1),
  ))

  pronunciation_dict["c"] = OrderedDict((
    (("c",), 1),
  ))

  result = sort_words(pronunciation_dict, True, True)

  assert list(result.keys()) == ["c", "b", "a", "C", "B", "A"]
  assert result["A"] == OrderedDict((
    (("a",), 1),
  ))


def test_component_descending_uncased():
  pronunciation_dict = OrderedDict()

  pronunciation_dict["B"] = OrderedDict((
    (("b",), 1),
  ))

  pronunciation_dict["b"] = OrderedDict((
    (("b",), 1),
  ))

  pronunciation_dict["A"] = OrderedDict((
    (("a",), 1),
  ))

  pronunciation_dict["a"] = OrderedDict((
    (("a",), 1),
  ))

  pronunciation_dict["C"] = OrderedDict((
    (("c",), 1),
  ))

  pronunciation_dict["c"] = OrderedDict((
    (("c",), 1),
  ))

  result = sort_words(pronunciation_dict, True, False)

  assert list(result.keys()) == ["c", "C", "b", "B", "a", "A"]
  assert result["A"] == OrderedDict((
    (("a",), 1),
  ))
