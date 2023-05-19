from collections import OrderedDict
import pytest

from pronunciation_dictionary_utils_cli.pronunciations_map_symbols_json import (
    apply_mapping_partial, get_mappable_symbols)

from pronunciation_dictionary import (MultiprocessingOptions, get_phoneme_set)


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
                                    (("ɔ", "ˌɔ", "ɔ3", "AA1", "ˌeɪ", "."), 1),
                                    (("A03", "NN", "HH"), 2)]))])

    result = test_dictionary.copy()

    unique_sounds_in_dictionary = get_phoneme_set(result)
    unique_sounds_in_mappings = set(mappings.keys())
    mappable_symbols = get_mappable_symbols(unique_sounds_in_dictionary, unique_sounds_in_mappings)
    sorted_mappable_symbols = sorted(mappable_symbols, key=lambda x: (-len(x), x))

    mp_options = MultiprocessingOptions(n_jobs=4, maxtasksperchild=100, chunksize=10)

    changed_words_total = set()
    for mappable_symbol in sorted_mappable_symbols:
        changed_words = apply_mapping_partial(result, mappings, mappable_symbol, mp_options)
        changed_words_total |= changed_words

    assert changed_words_total == {"test"}
    assert result == expected_result


def test_with_whitespaces() -> None:
    test_dictionary = OrderedDict([("test", OrderedDict([(("EY2",), 1)]))])
    mappings = {"EY2": "ˌe ɪ"}

    unique_sounds_in_dictionary = get_phoneme_set(test_dictionary)
    unique_sounds_in_mappings = set(mappings.keys())
    mappable_symbols = get_mappable_symbols(unique_sounds_in_dictionary, unique_sounds_in_mappings)

    mp_options = MultiprocessingOptions(n_jobs=4, maxtasksperchild=100, chunksize=10)

    with pytest.raises(Exception) as expected_exception:
        changed_words = apply_mapping_partial(
            test_dictionary, mappings, mappable_symbols[0], mp_options)
        assert str(expected_exception) == "Whitespaces in mappings aren't supported with partial mapping."


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

    result = test_dictionary.copy()

    unique_sounds_in_dictionary = get_phoneme_set(result)
    unique_sounds_in_mappings = set(mappings.keys())
    mappable_symbols = get_mappable_symbols(unique_sounds_in_dictionary, unique_sounds_in_mappings)

    mp_options = MultiprocessingOptions(n_jobs=4, maxtasksperchild=100, chunksize=10)

    changed_words_total = set()
    for mappable_symbol in mappable_symbols:
        changed_words = apply_mapping_partial(result, mappings, mappable_symbol, mp_options)
        changed_words_total |= changed_words

    assert changed_words_total == set()
    assert result == expected_result


def test_empty() -> None:
    test_dictionary = OrderedDict()
    mappings = dict()

    expected_result = OrderedDict()

    result = test_dictionary.copy()

    unique_sounds_in_dictionary = get_phoneme_set(result)
    unique_sounds_in_mappings = set(mappings.keys())
    mappable_symbols = get_mappable_symbols(unique_sounds_in_dictionary, unique_sounds_in_mappings)

    mp_options = MultiprocessingOptions(n_jobs=4, maxtasksperchild=100, chunksize=10)

    changed_words_total = set()
    for mappable_symbol in mappable_symbols:
        changed_words = apply_mapping_partial(result, mappings, mappable_symbol, mp_options)
        changed_words_total |= changed_words

    assert changed_words_total == set()
    assert result == expected_result
