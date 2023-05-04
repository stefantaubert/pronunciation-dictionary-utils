from collections import OrderedDict

# Creates testing data

dictionary = OrderedDict([('test', OrderedDict([
                                   (('AO', 'AO2', 'AO3', 'AA1', 'EY2', '.'), 1), 
                                   (('A03', 'NN', 'HH'), 2)
                                   ]))])

'''
OrderedDict([('test', OrderedDict([(('t', 'e', 's', 't'), 2), 
                                   (('t', 'e', 'e', 's', 't'), 3), 
                                   (('t', 's', 't'), 4), 
                                   (('t', 'y', 's', 't'), 8), 
                                   (('t', 'X', 's', 't'), 5)
                                   ])
            )])

# same as

dictionary = OrderedDict()
pronunciations = OrderedDict()
pronunciations[tuple(("t", "e", "s", "t"))] = 2
pronunciations[tuple(("t", "e", "e", "s", "t"))] = 3
pronunciations[tuple(("t", "s", "t"))] = 4  # keep untouched
pronunciations[tuple(("t", "y", "s", "t"))] = 8  # same as first
pronunciations[tuple(("t", "X", "s", "t"))] = 5  # existing that will be extended
dictionary["test"] = pronunciations
print(dictionary)
'''

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

partial_mapping_flag = False

# Mapping

resulting_dictionary_with_changes_without_partial_flag = OrderedDict()
resulting_dictionary_with_changes_with_partial_flag = OrderedDict()
resulting_dictionary_without_changes_without_partial_flag = OrderedDict()
resulting_dictionary_without_changes_with_partial_flag = OrderedDict()

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

assert resulting_dictionary_with_changes_without_partial_flag == expected_dictionary_with_changes_without_partial_flag, f"Resulting dictionary with changes without partial flag is not as expected"
assert resulting_dictionary_with_changes_with_partial_flag == expected_dictionary_with_changes_with_partial_flag, f"Resulting dictionary with changes with partial flag is not as expected"
assert resulting_dictionary_without_changes_without_partial_flag == expected_dictionary_without_changes_without_partial_flag, f"Resulting dictionary without changes without partial flag is not as expected"
assert resulting_dictionary_without_changes_with_partial_flag == expected_dictionary_without_changes_with_partial_flag, f"Resulting dictionary without changes with partial flag is not as expected"