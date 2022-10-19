from pronunciation_dictionary_utils.pronunciations_remove_symbols import remove_symbols_start


def test_component():
  symbols = (".", ";", "a", "d", ".", "b", "c", ".", "!")
  result = tuple(remove_symbols_start(symbols, {".", ";", "!"}))
  assert result == ("a", "d", ".", "b", "c", ".", "!")
