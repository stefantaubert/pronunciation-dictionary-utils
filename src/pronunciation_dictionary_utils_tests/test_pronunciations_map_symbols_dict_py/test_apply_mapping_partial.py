from collections import OrderedDict

import pytest
from pronunciation_dictionary import MultiprocessingOptions

from pronunciation_dictionary_utils.pronunciations_map_symbols_dict import apply_mapping_partial


def test_with_changes() -> None:
    test_dictionary = OrderedDict([("test", OrderedDict([(("AO2",), 1)]))])
    mappings = {"AO": "ɔ"}
    expected_result = OrderedDict([("test", OrderedDict([(("ɔ2",), 1)]))])
    mappable_symbol = "AO"
    mp_options = MultiprocessingOptions(n_jobs=4, maxtasksperchild=100, chunksize=10)

    changed_words = apply_mapping_partial(test_dictionary, mappings, mappable_symbol, mp_options)

    assert changed_words == {"test"}
    assert test_dictionary == expected_result


def test_with_whitespaces() -> None:
    test_dictionary = OrderedDict([("test", OrderedDict([(("EY2",), 1)]))])
    mappings = {"EY2": "ˌe ɪ"}
    mappable_symbol = "EY2"
    mp_options = MultiprocessingOptions(n_jobs=4, maxtasksperchild=100, chunksize=10)

    with pytest.raises(Exception) as expected_exception:
        apply_mapping_partial(test_dictionary, mappings, mappable_symbol, mp_options)
    assert str(expected_exception.value) == "Whitespaces in mappings aren't supported with partial mapping."
