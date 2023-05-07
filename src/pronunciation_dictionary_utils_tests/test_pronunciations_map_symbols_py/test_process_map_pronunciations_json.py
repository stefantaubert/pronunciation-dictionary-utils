from collections import OrderedDict

from pronunciation_dictionary_utils_cli.pronunciations_map_symbols_json import (
    get_mappable_and_unmappable_symbols, process_mappable_symbol)

# Creates testing data

test_dictionary = OrderedDict([('test', OrderedDict([
                                   (('AO', 'AO2', 'AO3', 'AA1', 'EY2', '.'), 1), 
                                   (('A03', 'NN', 'HH'), 2)
                                   ]))])

mappings = {
    "AO": "ɔ",
    "AO0": "ɔ",
    "AO1": "ˈɔ",
    "AO2": "ˌɔ",
    "EY": "eɪ",
    "EY0": "eɪ",
    "EY1": "ˈeɪ",
    "EY2": "ˌeɪ"
}

testing_flag = True

# Mapping

mappable_symbols, unmappable_symbols = get_mappable_and_unmappable_symbols(test_dictionary, mappings)
changed_words = set()

partial_mapping_flag = False

resulting_dictionary_with_changes_without_partial_flag = test_dictionary.copy()
for mappable_symbol in mappable_symbols:
    changed_words = process_mappable_symbol(resulting_dictionary_with_changes_without_partial_flag, mappings, 
                                            mappable_symbol, partial_mapping_flag, None, testing_flag)

resulting_dictionary_without_changes_without_partial_flag = test_dictionary.copy()
for mappable_symbol in mappable_symbols:
    changed_words = process_mappable_symbol(resulting_dictionary_without_changes_without_partial_flag, mappings, 
                                            mappable_symbol, partial_mapping_flag, None, testing_flag)

partial_mapping_flag = True

resulting_dictionary_with_changes_with_partial_flag = test_dictionary.copy()
for mappable_symbol in mappable_symbols:
    changed_words = process_mappable_symbol(resulting_dictionary_with_changes_with_partial_flag, mappings, 
                                            mappable_symbol, partial_mapping_flag, None, testing_flag)

resulting_dictionary_without_changes_with_partial_flag = test_dictionary.copy()
for mappable_symbol in mappable_symbols:
    changed_words = process_mappable_symbol(resulting_dictionary_without_changes_with_partial_flag, mappings, 
                                            mappable_symbol, partial_mapping_flag, None, testing_flag)

# Expected data

expected_dictionary_with_changes_without_partial_flag = OrderedDict([('test', OrderedDict([
                                   (('ɔ', 'ˌɔ', 'AO3', 'AA1', 'ˌeɪ', '.'), 1), 
                                   (('A03', 'NN', 'HH'), 2)]))])

expected_dictionary_with_changes_with_partial_flag = OrderedDict([('test', OrderedDict([
                                   (('ɔ', 'ˌɔ', 'ɔ3', 'AA1', 'ˌeɪ', '.'), 1), 
                                   (('A03', 'NN', 'HH'), 2)]))])

expected_dictionary_without_changes_without_partial_flag = OrderedDict([('test', OrderedDict([
                                   (('A03', 'NN', 'HH'), 1)]))])

expected_dictionary_without_changes_with_partial_flag = OrderedDict([('test', OrderedDict([
                                   (('A03', 'NN', 'HH'), 1)]))])

# Comparisons

assert resulting_dictionary_with_changes_without_partial_flag == \
    expected_dictionary_with_changes_without_partial_flag, \
    f"Resulting dictionary with changes without partial flag is not as expected"
assert resulting_dictionary_with_changes_with_partial_flag == \
    expected_dictionary_with_changes_with_partial_flag, \
    f"Resulting dictionary with changes with partial flag is not as expected"
assert resulting_dictionary_without_changes_without_partial_flag == \
    expected_dictionary_without_changes_without_partial_flag, \
    f"Resulting dictionary without changes without partial flag is not as expected"
assert resulting_dictionary_without_changes_with_partial_flag == \
    expected_dictionary_without_changes_with_partial_flag, \
    f"Resulting dictionary without changes with partial flag is not as expected"