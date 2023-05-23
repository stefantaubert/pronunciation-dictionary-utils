from pronunciation_dictionary_utils_cli.pronunciations_map_symbols_json import get_unmappable_symbols


def test_symbols_found():
  sounds_in_dictionary = {"AO", "AO2", "AO3", "AA1", "EY2", ".", "A03", "NN", "HH"}
  sounds_in_mappings = {"EY1", "EY", "AO1", "EY0", "AO", "AO0", "AO2", "EY2"}

  expected_unmappable_symbols = {"A03", "AA1", "AO3", "HH", "NN", "."}
  unmappable_symbols = get_unmappable_symbols(sounds_in_dictionary, sounds_in_mappings)

  assert unmappable_symbols == expected_unmappable_symbols


def test_symbols_not_found():
  sounds_in_dictionary = {"AO", "AO2", "EY2"}
  sounds_in_mappings = {"EY1", "EY", "AO1", "EY0", "AO", "AO0", "AO2", "EY2"}

  unmappable_symbols = get_unmappable_symbols(sounds_in_dictionary, sounds_in_mappings)

  assert unmappable_symbols == set()


def test_empty():
  sounds_in_dictionary = set()
  sounds_in_mappings = set()

  unmappable_symbols = get_unmappable_symbols(sounds_in_dictionary, sounds_in_mappings)

  assert unmappable_symbols == set()
