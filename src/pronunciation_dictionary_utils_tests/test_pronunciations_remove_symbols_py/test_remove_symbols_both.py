from pronunciation_dictionary_utils.pronunciations_remove_symbols import remove_symbols_both


def test_component():
  symbols = (".", ";", "a", "d", ".", "b", "c", ".", "!")
  result = tuple(remove_symbols_both(symbols, {".", ";", "!"}))
  assert result == ("a", "d", ".", "b", "c")
