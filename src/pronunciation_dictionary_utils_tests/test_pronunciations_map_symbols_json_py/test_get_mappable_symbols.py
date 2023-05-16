from ordered_set import OrderedSet

from pronunciation_dictionary_utils_cli.pronunciations_map_symbols_json import (get_mappable_symbols, get_unmappable_symbols)


def test_symbols_found():
    sounds_in_dictionary = OrderedSet(["AO", "AO2", "AO3", "AA1", "EY2", ".", "A03", "NN", "HH"])
    sounds_in_mappings = OrderedSet(["EY1", "EY", "AO1", "EY0", "AO", "AO0", "AO2", "EY2"])

    expected_mappable_symbols = OrderedSet(['AO2', 'EY2', 'AO'])

    mappable_symbols = get_mappable_symbols(sounds_in_dictionary, sounds_in_mappings)

    assert expected_mappable_symbols == mappable_symbols, f"Resulting mappable symbols are not as expected"


def test_symbols_not_found():
    sounds_in_dictionary = OrderedSet(["AO", "AO2", "AO3", "AA1", "EY2", ".", "A03", "NN", "HH"])
    sounds_in_mappings = OrderedSet(["EY1", "EY", "AO1", "EY0", "AO0"])

    mappable_symbols = get_mappable_symbols(sounds_in_dictionary, sounds_in_mappings)

    assert len(mappable_symbols) == 0, f"Resulting mappable symbols are not as expected"


def test_empty():
    sounds_in_dictionary = OrderedSet([])
    sounds_in_mappings = OrderedSet([])

    mappable_symbols = get_mappable_symbols(sounds_in_dictionary, sounds_in_mappings)

    assert len(mappable_symbols) == 0, f"Resulting mappable symbols are not as expected"