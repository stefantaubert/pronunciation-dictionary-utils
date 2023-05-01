from collections import OrderedDict
from ordered_set import OrderedSet

from pronunciation_dictionary import (PronunciationDict, get_phoneme_set)

#from pronunciation_dictionary_utils import map_symbols
from pronunciation_dictionary_utils.pronunciations_map_symbols import (
  __init_pool, process_map_pronunciations_full)

def create_test_data(partial_mapping: bool) -> tuple[PronunciationDict, dict[str,str], bool]:
  dictionary = OrderedDict()
  pronunciations = OrderedDict()
  # pronunciations["test"] = "A0 AO2 AO3 AA1 EY2 ."
  pronunciations[tuple(("AO", "AO2", "AO3", "AA1", "EY2", "."))] = 1
  dictionary["test"] = pronunciations
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
  return dictionary, mappings, partial_mapping

def map_test_data(dictionary: PronunciationDict, mappings: dict[str, str], partial_mapping: bool) -> set[str]:

  dictionary_phonemes = get_phoneme_set(dictionary)  # unique sounds from the dictionary
  common_keys = dictionary_phonemes.intersection(mappings)  # sounds that are both in the dictionary and the mapping file
  dict_unmapped = dictionary_phonemes - mappings.keys()  # sounds that are in the dictionary but not in the mapping file

  common_keys = sorted(common_keys, reverse=True, key=len)  # sorting common_keys in a descending order by length

  words_with_changed_pronunciations = set()

  # iterates through common_keys:
  # - loads a key as from_symbol and a value as to_phonemes,
  # - maps each instance of the key (from_symbol) in the dictionary to the value (to_phonemes)
  for key in common_keys:
    # gets a value (mapping) to map the key to
    mapping = mappings[key]
    to_phonemes = mapping
    # gets a key
    from_symbol = key
    from_symbol = OrderedSet((from_symbol,))
    # changes symbols in dictionary. If whitespaces: 
    # - without partial method, values are split at whitespaces and appear in the final version
    # - with partial method, an error is thrown because it is not be meant to be supported
    if partial_mapping is False:
      to_phonemes = mapping.split(" ")
      to_phonemes = [p for p in to_phonemes if len(p) > 0]
    if partial_mapping is True and " " in to_phonemes:
        raise Exception("Whitespaces in mapping values aren't supported with partial mapping.")
    
    #__init_pool(dictionary)
    print("from_symbol: ", from_symbol)
    print("to_phonemes: ", to_phonemes)
    word, new_pronunciations = process_map_pronunciations_full("test", from_symbol, to_phonemes)
    words_with_changed_pronunciations.add(word)

  return words_with_changed_pronunciations

# jumpstarts the test, compares the results
def test_pronunciations_map_symbols_py():
    dictionary, mappings, partial_mapping = create_test_data(False)

    changed_words = map_test_data(dictionary, mappings, partial_mapping)

    # to validate the processed objects
    # expected_result["test"] = "ɔ ˌɔ AO3 AA1 ˌeɪ ."
    expected_result = {
       "test":  "ɔ ˌɔ AO3 AA1 ˌeɪ .\n"
    } # from "A0", "AO2", "AO3", "AA1", "EY2", "."

    # Are the expected and actual dictionaries not empty?
    assert expected_result, f"Expected dictionary is empty"
    assert dictionary, f"Processed dictionary is empty"
    # Are the expected and actual dictionaries of type dict?
    assert isinstance(expected_result, dict), f"Expected dictionary is not of type dict"
    assert isinstance(dictionary, dict), f"Processed dictionary is not of type dict"
    print("Expected: ", expected_result)
    print("Is: ", dictionary)
    # Have any values been changed?
    assert changed_words, f"No words have been changed"
    assert "test" in changed_words, f"Expected word is not among the words that have been changed"
    # Are only expected symbols present in dictionary with changed words?
    expected_symbols = set(['.', '1', '3', 'A', 'O', 'e', 'ɔ', 'ɪ', 'ˌ'])
    for word, pronunciation in dictionary.items():
        for symbol in pronunciation.keys():
            assert all(s in expected_symbols for s in symbol), f"{pronunciation} contains unexpected symbols {symbol} in {word}"
    # Are the expected and actual dictionaries equal?
    assert(dictionary == expected_result), f"Expected and processed dictionaries aren't equal"