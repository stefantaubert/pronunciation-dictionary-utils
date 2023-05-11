from ordered_set import OrderedSet

from pronunciation_dictionary_utils_cli.pronunciations_map_symbols_json import get_mappable_and_unmappable_symbols

def test_get_mappable_and_unmappable_symbols():
    sounds_in_dictionary = OrderedSet(["AO", "AO2", "AO3", "AA1", "EY2", ".", "A03", "NN", "HH"])
    sounds_in_mappings = OrderedSet(["EY1", "EY", "AO1", "EY0", "AO", "AO0", "AO2", "EY2"])

    expected_mappable_symbols = OrderedSet(['AO2', 'EY2', 'AO'])
    expected_unmappable_symbols = OrderedSet(['AO3', 'AA1', '.', 'A03', 'NN', 'HH'])

    mappable_symbols, unmappable_symbols = get_mappable_and_unmappable_symbols(sounds_in_dictionary, sounds_in_mappings)

    assert expected_mappable_symbols == mappable_symbols, f"Resulting mappable symbols are not as expected"
    assert expected_unmappable_symbols == unmappable_symbols, f"Resulting unmappable symbols are not as expected"