from pronunciation_dictionary_utils.pronunciations_remove_symbols import remove_symbols_all


def test_component():
  symbols = (".", ";", "a", "d", ".", "b", "c", ".", "!")
  result = tuple(remove_symbols_all(symbols, {".", ";", "!"}))
  assert result == ("a", "d", "b", "c")
