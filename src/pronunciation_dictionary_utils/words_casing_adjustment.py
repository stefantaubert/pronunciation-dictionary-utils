from collections import OrderedDict
from functools import partial
from multiprocessing.pool import Pool
from typing import Literal, Optional, Tuple

from ordered_set import OrderedSet
from pronunciation_dictionary import MultiprocessingOptions, PronunciationDict, Word
from tqdm import tqdm

from pronunciation_dictionary_utils.common import merge_pronunciations
from pronunciation_dictionary_utils.validation import validate_dictionary


def __validate_mode(mode: str) -> Optional[str]:
  if mode not in ["lower", "upper"]:
    return "Invalid value!"
  return None


def change_word_casing(dictionary: PronunciationDict, mode: str, mp_options: MultiprocessingOptions) -> int:
  if msg := validate_dictionary(dictionary):
    raise ValueError(f"Parameter 'dictionary': {msg}")
  if msg := __validate_mode(mode):
    raise ValueError(f"Parameter 'mode': {msg}")

  process_method = partial(
    __process_change_casing,
    mode=mode,
  )

  with Pool(
    processes=mp_options.n_jobs,
    maxtasksperchild=mp_options.maxtasksperchild,
  ) as pool:
    iterator = pool.imap(process_method, dictionary.keys(), mp_options.chunksize)
    new_words_to_words = dict(tqdm(iterator, total=len(dictionary), unit="words"))

  new_words = OrderedDict((
    (k, new_word)
    for k in dictionary.keys()
    if (new_word := new_words_to_words[k])
  ))

  del new_words_to_words

  created_words = OrderedSet()

  for word, new_word in new_words.items():
    popped_pronunciations = dictionary.pop(word)
    if new_word in dictionary:
      existing_pronunciations = dictionary[new_word]
      merge_pronunciations(existing_pronunciations, popped_pronunciations)
    else:
      created_words.add(new_word)
      dictionary[new_word] = popped_pronunciations

  removed_words = OrderedSet(new_words.keys())
  return removed_words, created_words


def __process_change_casing(word: Word, mode: Literal["upper", "lower"]) -> Tuple[Word, Optional[Word]]:
  if mode == "upper":
    new_word = word.upper()
  elif mode == "lower":
    new_word = word.lower()
  else:
    assert False

  if new_word != word:
    return word, new_word
  return word, None
