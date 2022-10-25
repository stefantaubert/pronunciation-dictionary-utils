from collections import OrderedDict
from functools import partial
from multiprocessing.pool import Pool
from typing import Optional, Tuple

from ordered_set import OrderedSet
from pronunciation_dictionary import MultiprocessingOptions, PronunciationDict, Pronunciations, Word
from tqdm import tqdm

from pronunciation_dictionary_utils.validation import (validate_dictionary, validate_mp_options,
                                                       validate_type)


def sort_pronunciations(dictionary: PronunciationDict, descending: bool, ignore_weight: bool, mp_options: MultiprocessingOptions) -> int:
  if msg := validate_dictionary(dictionary):
    raise ValueError(f"Parameter 'dictionary': {msg}")
  if msg := validate_type(descending, bool):
    raise ValueError(f"Parameter 'descending': {msg}")
  if msg := validate_type(ignore_weight, bool):
    raise ValueError(f"Parameter 'ignore_weight': {msg}")
  if msg := validate_mp_options(mp_options):
    raise ValueError(f"Parameter 'mp_options': {msg}")

  process_method = partial(
    process_sort_pronunciations,
    descending=descending,
    ignore_weight=ignore_weight,
  )

  with Pool(
    processes=mp_options.n_jobs,
    initializer=__init_pool_prepare_cache_mp,
    initargs=(dictionary,),
    maxtasksperchild=mp_options.maxtasksperchild,
  ) as pool:
    entries = OrderedSet(dictionary.keys())
    iterator = pool.imap(process_method, entries, mp_options.chunksize)
    pronunciations_to_i = list(tqdm(iterator, total=len(entries), unit="words"))

  changed_counter = 0
  for word, new_pronunciations in pronunciations_to_i:
    pronunciations_unchanged = new_pronunciations is None
    if pronunciations_unchanged:
      continue

    dictionary[word] = new_pronunciations
    changed_counter += 1

  return changed_counter


process_lookup_dict: PronunciationDict = None


def __init_pool_prepare_cache_mp(lookup_dict: PronunciationDict) -> None:
  global process_lookup_dict
  process_lookup_dict = lookup_dict


def process_sort_pronunciations(word: Word, descending: bool, ignore_weight: bool) -> Tuple[Word, Optional[Pronunciations]]:
  global process_lookup_dict
  assert word in process_lookup_dict
  pronunciations = process_lookup_dict[word]
  new_pronunciations = sort_pronunciations_entry(pronunciations, descending, ignore_weight)
  changed_anything = pronunciations != new_pronunciations
  if changed_anything:
    return word, new_pronunciations
  return word, None


def sort_pronunciations_entry(pronunciations: Pronunciations, descending: bool, ignore_weight: bool) -> Pronunciations:
  pronunciations_sorted = sorted(pronunciations.items(
  ), key=lambda kv: kv[0] if ignore_weight else (-kv[1], kv[0]), reverse=descending)
  new_pronunciations = OrderedDict(pronunciations_sorted)
  return new_pronunciations
