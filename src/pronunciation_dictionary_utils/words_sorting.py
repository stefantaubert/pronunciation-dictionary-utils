from collections import OrderedDict

from pronunciation_dictionary import PronunciationDict

from pronunciation_dictionary_utils.validation import validate_dictionary, validate_type


def sort_words(dictionary: PronunciationDict, descending: bool, consider_case: bool) -> PronunciationDict:
  if msg := validate_dictionary(dictionary):
    raise ValueError(f"Parameter 'dictionary': {msg}")
  if msg := validate_type(descending, bool):
    raise ValueError(f"Parameter 'descending': {msg}")
  if msg := validate_type(consider_case, bool):
    raise ValueError(f"Parameter 'consider_case': {msg}")

  words = dictionary.keys()
  sorted_words = sorted(words, reverse=descending,
                        key=lambda w: w if consider_case else (w.lower(), w))
  result = OrderedDict((
    (word, dictionary[word]) for word in sorted_words
  ))
  return result
