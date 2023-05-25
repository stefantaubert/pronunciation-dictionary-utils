from collections import OrderedDict

from pronunciation_dictionary_utils_cli.pronunciations_map_symbols_json import apply_mapping_full

from pronunciation_dictionary import MultiprocessingOptions


def test_with_changes() -> None:
    test_dictionary = OrderedDict([("test", OrderedDict([(("AO2",), 1)]))])
    mappings = {"AO2": "ˌɔ"}
    mappable_symbol = "AO2"
    expected_result = OrderedDict([("test", OrderedDict([(("ˌɔ",), 1)]))])
    mp_options = MultiprocessingOptions(n_jobs=4, maxtasksperchild=100, chunksize=10)

    changed_words = apply_mapping_full(test_dictionary, mappings, mappable_symbol, mp_options)

    assert changed_words == {"test"}
    assert test_dictionary == expected_result


def test_with_whitespaces() -> None:
    test_dictionary = OrderedDict([("test", OrderedDict([(("EY2",), 1)]))])
    mappings = {"EY2": "ˌe ɪ"}
    mappable_symbol = ("EY2")
    expected_result = OrderedDict([("test", OrderedDict([(("ˌe", "ɪ"), 1)]))])
    mp_options = MultiprocessingOptions(n_jobs=4, maxtasksperchild=100, chunksize=10)

    changed_words = apply_mapping_full(test_dictionary, mappings, mappable_symbol, mp_options)

    assert changed_words == {"test"}
    assert test_dictionary == expected_result
