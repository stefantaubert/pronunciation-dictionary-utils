from collections import OrderedDict

from pronunciation_dictionary import PronunciationDict


def sort_words(dictionary: PronunciationDict, descending: bool, consider_case: bool) -> PronunciationDict:
  words = dictionary.keys()
  sorted_words = sorted(words, reverse=descending,
                        key=lambda w: w if consider_case else (w.lower(), w))
  result = OrderedDict((
    (word, dictionary.pop(word)) for word in sorted_words
  ))
  return result
