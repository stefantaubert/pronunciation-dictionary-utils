from collections import OrderedDict

from pronunciation_dictionary import MultiprocessingOptions

from pronunciation_dictionary_utils.pronunciations_map_symbols_dict import map_symbols_dict


def test_with_changes() -> None:
  test_dictionary = OrderedDict([("test", OrderedDict([
                                  (("AO", "AO2", "AO3", "AA1", "EY2", "."), 1),
                                  (("A03", "NN", "HH"), 2)
                                  ]))])
  mappings = {
      "EY1": "ˈeɪ",
      "EY": "eɪ",
      "AO1": "ˈɔ",
      "EY0": "eɪ",
      "AO": "ɔ",
      "AO0": "ɔ",
      "AO2": "ˌɔ",
      "EY2": "ˌeɪ"
  }

  expected_result = OrderedDict([("test", OrderedDict([
                                  (("ɔ", "ˌɔ", "AO3", "AA1", "ˌeɪ", "."), 1),
                                  (("A03", "NN", "HH"), 2)]))])

  mp_options = MultiprocessingOptions(n_jobs=4, maxtasksperchild=100, chunksize=10)

  partial_mapping_flag = False
  changed_words = map_symbols_dict(test_dictionary, mappings,
                                   partial_mapping_flag, mp_options, silent=True)

  assert changed_words == {"test"}
  assert test_dictionary == expected_result


def test_with_whitespaces() -> None:
  test_dictionary = OrderedDict([("test", OrderedDict([
                                  (("AO", "AO2", "AO3", "AA1", "EY2", "."), 1),
                                  (("A03", "NN", "HH"), 2)
                                  ]))])
  mappings = {
      "EY1": "ˈeɪ",
      "EY": "eɪ",
      "AO1": "ˈɔ",
      "EY0": "eɪ",
      "AO": "ɔ",
      "AO0": "ɔ",
      "AO2": "ˌɔ",
      "EY2": "ˌe ɪ"
  }

  expected_result = OrderedDict([("test", OrderedDict([
                                  (("ɔ", "ˌɔ", "AO3", "AA1", "ˌe", "ɪ", "."), 1),
                                  (("A03", "NN", "HH"), 2)]))])

  mp_options = MultiprocessingOptions(n_jobs=4, maxtasksperchild=100, chunksize=10)

  partial_mapping_flag = False
  changed_words = map_symbols_dict(test_dictionary, mappings,
                                   partial_mapping_flag, mp_options, silent=True)

  assert changed_words == {"test"}
  assert test_dictionary == expected_result


def test_without_changes() -> None:
  test_dictionary = OrderedDict([("test", OrderedDict([
                                  (("AO", "AO2", "AO3", "AA1", "EY2", "."), 1),
                                  (("A03", "NN", "HH"), 2)
                                  ]))])
  mappings = {
      "V": "v",
      "F": "f",
      "D": "d",
      "MM": "m"
  }

  expected_result = OrderedDict([("test", OrderedDict([
                                  (("AO", "AO2", "AO3", "AA1", "EY2", "."), 1),
                                  (("A03", "NN", "HH"), 2)
                                  ]))])

  mp_options = MultiprocessingOptions(n_jobs=4, maxtasksperchild=100, chunksize=10)

  partial_mapping_flag = False
  changed_words = map_symbols_dict(test_dictionary, mappings,
                                   partial_mapping_flag, mp_options, silent=True)

  assert changed_words == set()
  assert test_dictionary == expected_result


def test_empty() -> None:
  test_dictionary = OrderedDict()
  mappings = dict()

  expected_result = OrderedDict()

  mp_options = MultiprocessingOptions(n_jobs=4, maxtasksperchild=100, chunksize=10)

  partial_mapping_flag = False
  changed_words = map_symbols_dict(test_dictionary, mappings,
                                   partial_mapping_flag, mp_options, silent=True)

  assert len(changed_words) == 0
  assert test_dictionary == expected_result
