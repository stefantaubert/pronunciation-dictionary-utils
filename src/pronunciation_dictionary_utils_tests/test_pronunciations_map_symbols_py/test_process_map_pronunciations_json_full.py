from typing import Tuple, Dict, Set

from collections import OrderedDict
from ordered_set import OrderedSet

from pronunciation_dictionary import (PronunciationDict, get_phoneme_set)

#from pronunciation_dictionary_utils import map_symbols
from pronunciation_dictionary_utils.pronunciations_map_symbols import (
  __init_pool, process_map_pronunciations_full, map_pronunciations_partial)

def create_test_data(partial_mapping: bool) -> Tuple[PronunciationDict, Dict[str, str], bool]:
  dictionary = OrderedDict()
  pronunciations = OrderedDict()
  pronunciations[tuple(("AO", "AO2", "AO3", "AA1", "EY2", "."))] = 1
  dictionary["test"] = pronunciations
  '''
  dictionary = {
    "test": {
      "pronunciations": {
        ("AO", "AO2", "AO3", "AA1", "EY2", "."): 1
      }
    }
  }
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
  return dictionary, mappings, partial_mapping

def map_test_data(dictionary: PronunciationDict, mappings: Dict[str, str], partial_mapping: bool) -> Set[str]:

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
    
    __init_pool(dictionary)
    print("from_symbol: ", from_symbol)
    print("to_phonemes: ", to_phonemes)
    if partial_mapping is True:
       word, new_pronunciations = map_pronunciations_partial("test", from_symbol, to_phonemes)
    else:
       word, new_pronunciations = process_map_pronunciations_full("test", from_symbol, to_phonemes)
    if new_pronunciations:
      dictionary[word] = new_pronunciations
      words_with_changed_pronunciations.add(word)

  return words_with_changed_pronunciations

# jumpstarts the test, compares the results
def test_pronunciations_map_symbols_py():
    dictionary, mappings, partial_mapping = create_test_data(False)

    words_with_changed_pronunciation = map_test_data(dictionary, mappings, partial_mapping)

    # validates the processed objects

    # Does the dictionary with changed pronunciations exist?
    assert dictionary, f"Processed dictionary is empty"

    # Is there at least one pronunciation present?
    #assert len(dictionary["test"]["pronunciations"].keys()) > 0

    # Have any pronunciations in the dictionary changed?
    assert words_with_changed_pronunciation, f"No words have been changed"
    assert "test" in words_with_changed_pronunciation, f"Expected word is not among the words that have been changed"

    # Are only expected symbols present in pronunciations?
    expected_pronunciation = tuple(['ɔ', 'ˌɔ', 'AO3', 'AA1', 'ˌeɪ', '.'])
    for word in dictionary:
        for pronunciation in dictionary[word]:
            offending_symbols = [s for s in pronunciation if s not in expected_pronunciation]
            assert not offending_symbols, f"Unexpected symbol(s) found in {word}: {', '.join(offending_symbols)}"
            # Are pronunciations in the dictionary as expected?
            assert pronunciation == expected_pronunciation, f"Expected {expected_pronunciation} as pronunciation, not {pronunciation}"