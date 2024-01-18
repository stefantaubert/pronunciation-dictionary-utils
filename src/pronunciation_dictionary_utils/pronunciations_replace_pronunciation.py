import re
from collections import OrderedDict
from functools import partial
from multiprocessing.pool import Pool
from typing import Optional, Tuple

from ordered_set import OrderedSet
from pronunciation_dictionary import (MultiprocessingOptions, PronunciationDict, Pronunciations,
                                      Symbol, Word)
from tqdm import tqdm

from pronunciation_dictionary_utils.validation import (validate_dictionary, validate_mp_options,
                                                       validate_type)

DEFAULT_EMPTY_WEIGHT = 1


DEFAULT_EMPTY_WEIGHT = 1


def replace_symbols_in_pronunciations(dictionary: PronunciationDict, text: str, replace_with: str, keep_empty: bool, empty_symbol: Optional[Symbol], mp_options: MultiprocessingOptions, silent: bool = False) -> Tuple[OrderedSet[Word], int]:
  if msg := validate_dictionary(dictionary):
    raise ValueError(f"Parameter 'dictionary': {msg}")
  if msg := validate_type(text, str):
    raise ValueError(f"Parameter 'text': {msg}")
  if msg := validate_type(replace_with, str):
    raise ValueError(f"Parameter 'replace_with': {msg}")
  if msg := validate_type(keep_empty, bool):
    raise ValueError(f"Parameter 'keep_empty': {msg}")
  if empty_symbol is not None and (msg := validate_type(empty_symbol, str)):
    raise ValueError(f"Parameter 'empty_symbol': {msg}")
  if msg := validate_mp_options(mp_options):
    raise ValueError(f"Parameter 'mp_options': {msg}")

  if len(text) == 0:
    return OrderedSet(), 0

  pattern = re.compile(text)

  process_method = partial(
    process_get_pronunciation,
    text=pattern,
    replace_with=replace_with,
  )

  with Pool(
    processes=mp_options.n_jobs,
    initializer=__init_pool_prepare_cache_mp,
    initargs=(dictionary,),
    maxtasksperchild=mp_options.maxtasksperchild,
  ) as pool:
    entries = OrderedSet(dictionary.keys())
    iterator = pool.imap(process_method, entries, mp_options.chunksize)
    pronunciations_to_i = list(tqdm(iterator, total=len(entries), unit="words", disable=silent))

  changed_counter = 0
  removed_words = OrderedSet()
  for word, new_pronunciations in pronunciations_to_i:
    pronunciations_unchanged = new_pronunciations is None
    if pronunciations_unchanged:
      continue

    if len(new_pronunciations) == 0:
      if keep_empty:
        assert empty_symbol is not None
        dictionary[word] = OrderedDict((
          ((empty_symbol,), DEFAULT_EMPTY_WEIGHT),
        ))
      else:
        removed_words.add(word)
        dictionary.pop(word)
    else:
      dictionary[word] = new_pronunciations
    changed_counter += 1

  return removed_words, changed_counter


process_lookup_dict: PronunciationDict = None


def __init_pool_prepare_cache_mp(lookup_dict: PronunciationDict) -> None:
  global process_lookup_dict
  process_lookup_dict = lookup_dict


def process_get_pronunciation(word: Word, text: re.Pattern, replace_with: str) -> Tuple[Word, Optional[Pronunciations]]:
  global process_lookup_dict
  assert word in process_lookup_dict
  pronunciations = process_lookup_dict[word]
  new_pronunciations = replace_symbols_from_pronunciations_entry(pronunciations, text, replace_with)
  if new_pronunciations == pronunciations:
    return word, None
  return word, new_pronunciations


def replace_symbols_from_pronunciations_entry(pronunciations: Pronunciations, pattern: re.Pattern, replace_with: str) -> Pronunciations:
  new_pronunciations = OrderedDict()
  changed_anything = False
  for pronunciation, weight in pronunciations.items():
    phonemes_str = " ".join(pronunciation)
    phonemes_new = re.sub(pattern, replace_with, phonemes_str)
    new_pronunciation = phonemes_new.split(" ")
    new_pronunciation = tuple(x for x in new_pronunciation if x != '')

    if new_pronunciation != new_pronunciations:
      changed_anything = True

    if len(new_pronunciation) > 0:
      if new_pronunciation in new_pronunciations:
        new_pronunciations[new_pronunciation] += weight
      else:
        new_pronunciations[new_pronunciation] = weight
  if changed_anything:
    return new_pronunciations
  return pronunciations
