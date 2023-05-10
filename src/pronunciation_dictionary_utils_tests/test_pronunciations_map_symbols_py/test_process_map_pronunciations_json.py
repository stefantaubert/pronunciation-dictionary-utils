from collections import OrderedDict

from pronunciation_dictionary_utils_cli.pronunciations_map_symbols_json import (
    get_mappable_and_unmappable_symbols, process_mappable_symbol)

from pronunciation_dictionary import (get_phoneme_set, MultiprocessingOptions)


def test_process_map_pronunciations_json_with_changes_with_partial_method() -> None:
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

    # Expected results
    expected_result = OrderedDict([("test", OrderedDict([
                                    (("ɔ", "ˌɔ", "ɔ3", "AA1", "ˌeɪ", "."), 1), 
                                    (("A03", "NN", "HH"), 2)]))])
    
    # Mock object necessary for mapping
    mp_options = MultiprocessingOptions(n_jobs=4, maxtasksperchild=100, chunksize=10)

    # Mapping
    mappable_symbols, _ = get_mappable_and_unmappable_symbols(get_phoneme_set(test_dictionary), mappings.keys())
    
    changed_words = set()

    partial_mapping_flag = True
    result = test_dictionary.copy()
    for mappable_symbol in mappable_symbols:
        changed_words = process_mappable_symbol(result, mappings, mappable_symbol, partial_mapping_flag, mp_options)

    # Comparisons
    assert len(changed_words) == 1 and "test" in changed_words, \
        f"Expected changes to words have not been made."
    assert result == expected_result, f"Resulting dictionary with changes with partial flag is not as expected."

def test_process_map_pronunciations_json_with_changes_without_partial_method() -> None:
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

    # Expected results
    expected_result = OrderedDict([("test", OrderedDict([
                                    (("ɔ", "ˌɔ", "AO3", "AA1", "ˌeɪ", "."), 1), 
                                    (("A03", "NN", "HH"), 2)]))])
    
    # Mock object necessary for mapping
    mp_options = MultiprocessingOptions(n_jobs=4, maxtasksperchild=100, chunksize=10)

    # Mapping
    mappable_symbols, _ = get_mappable_and_unmappable_symbols(get_phoneme_set(test_dictionary), mappings.keys())
    
    changed_words = set()

    partial_mapping_flag = False
    result = test_dictionary.copy()
    for mappable_symbol in mappable_symbols:
        changed_words = process_mappable_symbol(result, mappings, mappable_symbol, partial_mapping_flag, mp_options)

    # Comparisons
    assert len(changed_words) == 1 and "test" in changed_words, \
        f"Expected changes to words have not been made."
    assert result == expected_result, f"Resulting dictionary with changes without partial flag is not as expected."

def test_process_map_pronunciations_json_without_changes_with_partial_method() -> None:
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

    # Expected results
    expected_result = OrderedDict([("test", OrderedDict([
                                    (("AO", "AO2", "AO3", "AA1", "EY2", "."), 1), 
                                    (("A03", "NN", "HH"), 2)
                                    ]))])
    
    # Mock object necessary for mapping
    mp_options = MultiprocessingOptions(n_jobs=4, maxtasksperchild=100, chunksize=10)

    # Mapping
    mappable_symbols, _ = get_mappable_and_unmappable_symbols(get_phoneme_set(test_dictionary), mappings.keys())
    
    changed_words = set()

    partial_mapping_flag = True
    result = test_dictionary.copy()
    for mappable_symbol in mappable_symbols:
        changed_words = process_mappable_symbol(result, mappings, mappable_symbol, partial_mapping_flag, mp_options)

    # Comparisons
    assert len(changed_words) == 0 and "test" not in changed_words, \
        f"Some words have been unexpectedly changed."
    assert result == expected_result, f"Resulting dictionary without changes with partial flag is not as expected."
    
def test_process_map_pronunciations_json_without_changes_without_partial_method() -> None:
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

    # Expected results
    expected_result = OrderedDict([("test", OrderedDict([
                                    (("AO", "AO2", "AO3", "AA1", "EY2", "."), 1), 
                                    (("A03", "NN", "HH"), 2)
                                    ]))])
    
    # Mock object necessary for mapping
    mp_options = MultiprocessingOptions(n_jobs=4, maxtasksperchild=100, chunksize=10)

    # Mapping
    mappable_symbols, _ = get_mappable_and_unmappable_symbols(get_phoneme_set(test_dictionary), mappings.keys())
    
    changed_words = set()

    partial_mapping_flag = False
    result = test_dictionary.copy()
    for mappable_symbol in mappable_symbols:
        changed_words = process_mappable_symbol(result, mappings, mappable_symbol, partial_mapping_flag, mp_options)

    # Comparisons
    assert len(changed_words) == 0 and "test" not in changed_words, \
        f"Some words have been unexpectedly changed."
    assert result == expected_result, f"Resulting dictionary without changes without partial flag is not as expected."