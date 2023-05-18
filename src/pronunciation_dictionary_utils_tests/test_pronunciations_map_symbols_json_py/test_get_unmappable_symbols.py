from ordered_set import OrderedSet

from pronunciation_dictionary_utils_cli.pronunciations_map_symbols_json import get_unmappable_symbols


def test_symbols_found():
    sounds_in_dictionary = OrderedSet(["AO", "AO2", "AO3", "AA1", "EY2", ".", "A03", "NN", "HH"])
    sounds_in_mappings = OrderedSet(["EY1", "EY", "AO1", "EY0", "AO", "AO0", "AO2", "EY2"])

    expected_unmappable_symbols = OrderedSet(["AO3", "AA1", ".", "A03", "NN", "HH"])

    unmappable_symbols = get_unmappable_symbols(sounds_in_dictionary, sounds_in_mappings)

    assert expected_unmappable_symbols == unmappable_symbols


def test_symbols_not_found():
    sounds_in_dictionary = OrderedSet(["AO", "AO2", "EY2"])
    sounds_in_mappings = OrderedSet(["EY1", "EY", "AO1", "EY0", "AO", "AO0", "AO2", "EY2"])

    unmappable_symbols = get_unmappable_symbols(sounds_in_dictionary, sounds_in_mappings)

    assert len(unmappable_symbols) == 0


def test_empty():
    sounds_in_dictionary = OrderedSet([])
    sounds_in_mappings = OrderedSet([])

    unmappable_symbols = get_unmappable_symbols(sounds_in_dictionary, sounds_in_mappings)

    assert len(unmappable_symbols) == 0
