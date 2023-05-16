import pytest
from collections import OrderedDict

from pronunciation_dictionary_utils_cli.pronunciations_map_symbols_json import identify_and_apply_mappings

from pronunciation_dictionary import MultiprocessingOptions


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
    
    # Mock object necessary for mapping
    mp_options = MultiprocessingOptions(n_jobs=4, maxtasksperchild=100, chunksize=10)

    # Mapping
    partial_mapping_flag = True
    result = test_dictionary.copy()
    changed_words = identify_and_apply_mappings(None, None, result, mappings, partial_mapping_flag, mp_options)

    # Comparisons
    assert len(changed_words) == 1 and "test" in changed_words, \
        f"Expected changes to words have not been made."
    assert result == expected_result, f"Resulting dictionary with changes with partial flag is not as expected."


def test_with_whitespaces() -> None:
    # Data to be tested
    test_dictionary = OrderedDict([("test", OrderedDict([(("EY2",), 1)]))])
    mappings = {"EY2": "ˌe ɪ"}

    # Mock object necessary for mapping
    mp_options = MultiprocessingOptions(n_jobs=4, maxtasksperchild=100, chunksize=10)

    # Mapping
    partial_mapping_flag = True
    with pytest.raises(Exception):
        changed_words = identify_and_apply_mappings(None, None, test_dictionary, mappings, partial_mapping_flag, mp_options)


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
    
    # Mock object necessary for mapping
    mp_options = MultiprocessingOptions(n_jobs=4, maxtasksperchild=100, chunksize=10)

    # Mapping
    partial_mapping_flag = True
    result = test_dictionary.copy()
    changed_words = identify_and_apply_mappings(None, None, result, mappings, partial_mapping_flag, mp_options)

    # Comparisons
    assert len(changed_words) == 0 and "test" not in changed_words, \
        f"Some words have been unexpectedly changed."
    assert result == expected_result, f"Resulting dictionary without changes with partial flag is not as expected."


def test_empty() -> None:
    # Data to be tested
    test_dictionary = OrderedDict()
    mappings = {}

    expected_result = OrderedDict()
    
    # Mock object necessary for mapping
    mp_options = MultiprocessingOptions(n_jobs=4, maxtasksperchild=100, chunksize=10)

    # Mapping
    partial_mapping_flag = True
    result = test_dictionary.copy()
    changed_words = identify_and_apply_mappings(None, None, result, mappings, partial_mapping_flag, mp_options)

    # Comparisons
    assert len(changed_words) == 0 and "test" not in changed_words, \
        f"Some words have been unexpectedly changed."
    assert result == expected_result, f"Resulting dictionary without changes with partial flag is not as expected."