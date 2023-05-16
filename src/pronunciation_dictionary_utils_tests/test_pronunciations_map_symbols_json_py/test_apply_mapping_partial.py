from collections import OrderedDict
import pytest

from pronunciation_dictionary_utils_cli.pronunciations_map_symbols_json import (apply_mapping_partial, get_mappable_symbols)

from pronunciation_dictionary import (MultiprocessingOptions, get_phoneme_set)


def test_with_changes() -> None:
    # Data to be tested
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
                                    (("ɔ", "ˌɔ", "ɔ3", "AA1", "ˌeɪ", "."), 1), 
                                    (("A03", "NN", "HH"), 2)]))])


    # Other variables for mapping
    result = test_dictionary.copy()

    unique_sounds_in_dictionary = get_phoneme_set(result)
    unique_sounds_in_mappings = mappings.keys()
    mappable_symbols = get_mappable_symbols(unique_sounds_in_dictionary, unique_sounds_in_mappings)

    mp_options = MultiprocessingOptions(n_jobs=4, maxtasksperchild=100, chunksize=10)

    # Mapping
    changed_words_total = set()
    for mappable_symbol in mappable_symbols:
        changed_words = apply_mapping_partial(result, mappings, mappable_symbol, mp_options)
        changed_words_total |= changed_words
  
    # Comparisons
    assert len(changed_words_total) == 1 and "test" in changed_words_total, \
        f"Expected changes to words have not been made."
    assert result == expected_result, f"Resulting dictionary with changes without partial flag is not as expected."


def test_with_whitespaces() -> None:
    # Data to be tested
    test_dictionary = OrderedDict([("test", OrderedDict([(("EY2",), 1)]))])
    mappings = {"EY2": "ˌe ɪ"}

    unique_sounds_in_dictionary = get_phoneme_set(test_dictionary)
    unique_sounds_in_mappings = mappings.keys()
    mappable_symbols = get_mappable_symbols(unique_sounds_in_dictionary, unique_sounds_in_mappings)

    mp_options = MultiprocessingOptions(n_jobs=4, maxtasksperchild=100, chunksize=10)

    # Mapping
    with pytest.raises(Exception):
        changed_words = apply_mapping_partial(test_dictionary, mappings, mappable_symbols[0], mp_options)


def test_without_changes() -> None:
    # Data to be tested
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

    # Other variables for mapping
    result = test_dictionary.copy()

    unique_sounds_in_dictionary = get_phoneme_set(result)
    unique_sounds_in_mappings = mappings.keys()
    mappable_symbols = get_mappable_symbols(unique_sounds_in_dictionary, unique_sounds_in_mappings)

    mp_options = MultiprocessingOptions(n_jobs=4, maxtasksperchild=100, chunksize=10)

    # Mapping
    changed_words_total = set()
    for mappable_symbol in mappable_symbols:
        changed_words = apply_mapping_partial(result, mappings, mappable_symbol, mp_options)
        changed_words_total |= changed_words
  
    # Comparisons
    assert len(changed_words_total) == 0 and "test" not in changed_words_total, \
        f"Some words have been unexpectedly changed."
    assert result == expected_result, f"Resulting dictionary without changes without partial flag is not as expected."


def test_empty() -> None:
    # Data to be tested
    test_dictionary = OrderedDict()
    mappings = {}

    expected_result = OrderedDict()

    # Other variables for mapping
    result = test_dictionary.copy()

    unique_sounds_in_dictionary = get_phoneme_set(result)
    unique_sounds_in_mappings = mappings.keys()
    mappable_symbols = get_mappable_symbols(unique_sounds_in_dictionary, unique_sounds_in_mappings)

    mp_options = MultiprocessingOptions(n_jobs=4, maxtasksperchild=100, chunksize=10)

    # Mapping
    changed_words_total = set()
    for mappable_symbol in mappable_symbols:
        changed_words = apply_mapping_partial(result, mappings, mappable_symbol, mp_options)
        changed_words_total |= changed_words
  
    # Comparisons
    assert len(changed_words_total) == 0, f"Some words have been unexpectedly changed."
    assert result == expected_result, f"Resulting dictionary without changes without partial flag is not as expected."