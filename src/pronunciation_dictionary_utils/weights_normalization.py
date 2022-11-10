from collections import OrderedDict
from functools import partial
from multiprocessing.pool import Pool
from typing import Optional, Tuple

from ordered_set import OrderedSet
from pronunciation_dictionary import MultiprocessingOptions, PronunciationDict, Pronunciations, Word
from tqdm import tqdm

from pronunciation_dictionary_utils.validation import validate_dictionary, validate_mp_options


def normalize_weights(dictionary: PronunciationDict, mp_options: MultiprocessingOptions) -> int:
  if msg := validate_dictionary(dictionary):
    raise ValueError(f"Parameter 'dictionary': {msg}")
  if msg := validate_mp_options(mp_options):
    raise ValueError(f"Parameter 'mp_options': {msg}")

  process_method = partial(
    process_normalize_weights,
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


def process_normalize_weights(word: Word) -> Tuple[Word, Optional[Pronunciations]]:
  global process_lookup_dict
  assert word in process_lookup_dict
  pronunciations = process_lookup_dict[word]
  new_pronunciations = normalize_pronunciations_weights_entry(pronunciations)
  changed_anything = pronunciations != new_pronunciations
  if changed_anything:
    return word, new_pronunciations
  return word, None


def normalize_pronunciations_weights_entry(pronunciations: Pronunciations) -> Pronunciations:
  weights_sum = sum(pronunciations.values())
  if weights_sum == 0:
    return pronunciations
  new_pronunciations = OrderedDict((
    (pronunciation, weight / weights_sum)
    for pronunciation, weight in pronunciations.items()
  ))
  return new_pronunciations
