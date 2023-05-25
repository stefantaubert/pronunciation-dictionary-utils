from collections import OrderedDict
from ordered_set import OrderedSet

from pronunciation_dictionary_utils_cli.pronunciations_map_symbols_json import (
    apply_mapping_full, get_mappable_symbols)

from pronunciation_dictionary import (MultiprocessingOptions, get_phoneme_set)


def test_with_changes_partial_unavailable() -> None:
    test_dictionary = OrderedDict([("test", OrderedDict([((("AO2"),), 1)]))])
    mappings = {"AO2": "ˌɔ"}

    expected_result = OrderedDict([("test", OrderedDict([((("ˌɔ"),), 1)]))])

    unique_sounds_in_dictionary = get_phoneme_set(test_dictionary)
    unique_sounds_in_mappings = set(mappings.keys())
    mappable_symbols = get_mappable_symbols(unique_sounds_in_dictionary, unique_sounds_in_mappings)
    sorted_mappable_symbols = OrderedSet(sorted(mappable_symbols, key=len, reverse=True))

    mp_options = MultiprocessingOptions(n_jobs=4, maxtasksperchild=100, chunksize=10)

    changed_words_total = set()
    for mappable_symbol in sorted_mappable_symbols:
        changed_words = apply_mapping_full(test_dictionary, mappings, mappable_symbol, mp_options)
        changed_words_total |= changed_words

    assert changed_words_total == {"test"}
    assert test_dictionary == expected_result


def test_without_changes_partial_available() -> None:
    test_dictionary = OrderedDict([("test", OrderedDict([((("AO2"),), 1)]))])
    mappings = {"AO": "ɔ", "AO2": "ˌɔ"}

    expected_result = OrderedDict([("test", OrderedDict([((("ˌɔ"),), 1)]))])

    unique_sounds_in_dictionary = get_phoneme_set(test_dictionary)
    unique_sounds_in_mappings = set(mappings.keys())
    mappable_symbols = get_mappable_symbols(unique_sounds_in_dictionary, unique_sounds_in_mappings)
    sorted_mappable_symbols = OrderedSet(sorted(mappable_symbols, key=len, reverse=True))

    mp_options = MultiprocessingOptions(n_jobs=4, maxtasksperchild=100, chunksize=10)

    changed_words_total = set()
    for mappable_symbol in sorted_mappable_symbols:
        changed_words = apply_mapping_full(test_dictionary, mappings, mappable_symbol, mp_options)
        changed_words_total |= changed_words

    assert changed_words_total == {"test"}
    assert test_dictionary == expected_result


def test_with_whitespaces() -> None:
    test_dictionary = OrderedDict([("test", OrderedDict([((("EY2"),), 1)]))])
    mappings = {"EY2": "ˌe ɪ"}

    expected_result = OrderedDict([("test", OrderedDict([(("ˌe", "ɪ"), 1)]))])

    unique_sounds_in_dictionary = get_phoneme_set(test_dictionary)
    unique_sounds_in_mappings = set(mappings.keys())
    mappable_symbols = get_mappable_symbols(unique_sounds_in_dictionary, unique_sounds_in_mappings)
    sorted_mappable_symbols = OrderedSet(sorted(mappable_symbols, key=len, reverse=True))

    mp_options = MultiprocessingOptions(n_jobs=4, maxtasksperchild=100, chunksize=10)

    changed_words_total = set()
    for mappable_symbol in sorted_mappable_symbols:
        changed_words = apply_mapping_full(test_dictionary, mappings, mappable_symbol, mp_options)
        changed_words_total |= changed_words

    assert changed_words_total == {"test"}
    assert test_dictionary == expected_result


def test_without_changes() -> None:
    test_dictionary = OrderedDict([("test", OrderedDict([((("EY2"),), 1)]))])
    mappings = {"V": "v"}

    expected_result = OrderedDict([("test", OrderedDict([((("EY2"),), 1)]))])

    unique_sounds_in_dictionary = get_phoneme_set(test_dictionary)
    unique_sounds_in_mappings = set(mappings.keys())
    mappable_symbols = get_mappable_symbols(unique_sounds_in_dictionary, unique_sounds_in_mappings)
    sorted_mappable_symbols = OrderedSet(sorted(mappable_symbols, key=len, reverse=True))
    
    mp_options = MultiprocessingOptions(n_jobs=4, maxtasksperchild=100, chunksize=10)

    changed_words_total = set()
    for mappable_symbol in sorted_mappable_symbols:
        changed_words = apply_mapping_full(test_dictionary, mappings, mappable_symbol, mp_options)
        changed_words_total |= changed_words

    assert changed_words_total == set()
    assert test_dictionary == expected_result


def test_empty() -> None:
    test_dictionary = OrderedDict()
    mappings = dict()

    expected_result = OrderedDict()

    unique_sounds_in_dictionary = get_phoneme_set(test_dictionary)
    unique_sounds_in_mappings = set(mappings.keys())
    mappable_symbols = get_mappable_symbols(unique_sounds_in_dictionary, unique_sounds_in_mappings)
    sorted_mappable_symbols = OrderedSet(sorted(mappable_symbols, key=len, reverse=True))

    mp_options = MultiprocessingOptions(n_jobs=4, maxtasksperchild=100, chunksize=10)

    changed_words_total = set()
    for mappable_symbol in sorted_mappable_symbols:
        changed_words = apply_mapping_full(test_dictionary, mappings, mappable_symbol, mp_options)
        changed_words_total |= changed_words

    assert changed_words_total == set()
    assert test_dictionary == expected_result
