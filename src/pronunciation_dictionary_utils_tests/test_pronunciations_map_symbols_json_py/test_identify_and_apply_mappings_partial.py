from collections import OrderedDict
from logging import getLogger

import pytest
from pronunciation_dictionary import MultiprocessingOptions

from pronunciation_dictionary_utils_cli.pronunciations_map_symbols_json import \
  identify_and_apply_mappings


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

    mp_options = MultiprocessingOptions(n_jobs=4, maxtasksperchild=100, chunksize=10)
    logger = getLogger()
    flogger = getLogger()

    partial_mapping_flag = True
    changed_words = identify_and_apply_mappings(
        logger, flogger, test_dictionary, mappings, partial_mapping_flag, mp_options)

    assert changed_words == {"test"}
    assert test_dictionary == expected_result


def test_with_whitespaces() -> None:
    test_dictionary = OrderedDict([("test", OrderedDict([(("EY2",), 1)]))])
    mappings = {"EY2": "ˌe ɪ"}

    mp_options = MultiprocessingOptions(n_jobs=4, maxtasksperchild=100, chunksize=10)
    logger = getLogger()
    flogger = getLogger()

    partial_mapping_flag = True
    with pytest.raises(Exception) as expected_exception:
        identify_and_apply_mappings(logger, flogger, test_dictionary, mappings, partial_mapping_flag, mp_options)
    assert str(expected_exception.value) == "Whitespaces in mappings aren't supported with partial mapping."


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
    logger = getLogger()
    flogger = getLogger()

    partial_mapping_flag = True
    changed_words = identify_and_apply_mappings(
        logger, flogger, test_dictionary, mappings, partial_mapping_flag, mp_options)

    assert changed_words == set()
    assert test_dictionary == expected_result


def test_empty() -> None:
    test_dictionary = OrderedDict()
    mappings = dict()

    expected_result = OrderedDict()

    mp_options = MultiprocessingOptions(n_jobs=4, maxtasksperchild=100, chunksize=10)
    logger = getLogger()
    flogger = getLogger()

    partial_mapping_flag = True
    changed_words = identify_and_apply_mappings(
        logger, flogger, test_dictionary, mappings, partial_mapping_flag, mp_options)

    assert changed_words == set()
    assert test_dictionary == expected_result
