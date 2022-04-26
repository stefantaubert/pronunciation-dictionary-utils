from ordered_set import OrderedSet

from pronunciation_dictionary_utils.types import PronunciationDict, Word
from pronunciation_dictionary_utils.validation import validate_dictionary


def get_vocabulary(dictionary: PronunciationDict) -> OrderedSet[Word]:
  if msg := validate_dictionary(dictionary):
    raise ValueError(f"Parameter 'dictionary': {msg}")
  result = OrderedSet(dictionary.keys())
  return result
