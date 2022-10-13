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


def __validate_symbol(symbols: str) -> Optional[str]:
  if not isinstance(symbols, str):
    return "Value needs of type 'str'!"
  return None


def map_symbols(dictionary: PronunciationDict, symbols: OrderedSet[Symbol], map_symbol: Symbol, partial_mapping: bool, mp_options: MultiprocessingOptions) -> int:
  if msg := validate_dictionary(dictionary):
    raise ValueError(f"Parameter 'dictionary': {msg}")
  if msg := validate_type(symbols, OrderedSet):
    raise ValueError(f"Parameter 'symbols': {msg}")
  for symbol in symbols:
    if msg := __validate_symbol(symbol):
      raise ValueError(f"Parameter 'symbols': {msg}")
  if len(symbols) == 0:
    raise ValueError("Parameter 'symbols': At least one symbol needs to be passed!")
  if msg := __validate_symbol(map_symbol):
    raise ValueError(f"Parameter 'map_symbol': {msg}")
  if msg := validate_type(partial_mapping, bool):
    raise ValueError(f"Parameter 'partial_mapping': {msg}")
  if msg := validate_mp_options(mp_options):
    raise ValueError(f"Parameter 'mp_options': {msg}")

  map_method = process_map_pronunciation_partial if partial_mapping else process_map_pronunciation_full
  process_method = partial(
    map_method,
    symbols=symbols,
    map_symbol=map_symbol,
  )

  with Pool(
    processes=mp_options.n_jobs,
    initializer=__init_pool_prepare_cache_mp,
    initargs=(dictionary,),
    maxtasksperchild=mp_options.maxtasksperchild,
  ) as pool:
    entries = OrderedSet(dictionary.keys())
    iterator = pool.imap(process_method, entries, mp_options.chunksize)
    new_pronunciations_to_words = dict(tqdm(iterator, total=len(entries), unit="words"))

  changed_counter = 0

  for word, new_pronunciations in new_pronunciations_to_words.items():
    changed_pronunciation = new_pronunciations is not None
    if changed_pronunciation:
      dictionary[word] = new_pronunciations
      changed_counter += 1

  return changed_counter


process_lookup_dict: PronunciationDict = None


def __init_pool_prepare_cache_mp(lookup_dict: PronunciationDict) -> None:
  global process_lookup_dict
  process_lookup_dict = lookup_dict


def replace_str(s: str, replace: OrderedSet[str], replace_with: str) -> str:
  for r in replace:
    if r in s:
      s = s.replace(r, replace_with)
  return s


def process_map_pronunciation_partial(word: Word, symbols: OrderedSet[Symbol], map_symbol: Symbol) -> Tuple[Word, Optional[Pronunciations]]:
  global process_lookup_dict
  assert word in process_lookup_dict
  pronunciations = process_lookup_dict[word]
  assert len(pronunciations) > 0
  changed_anything = False
  new_pronunciations = OrderedDict()
  for pronunciation, weight in pronunciations.items():
    new_pronunciation = tuple(
      replace_str(symbol, symbols, map_symbol)
      for symbol in pronunciation
    )

    if new_pronunciation != pronunciation:
      changed_anything = True

    assert len(new_pronunciation) > 0
    if new_pronunciation in new_pronunciations:
      new_pronunciations[new_pronunciation] += weight
    else:
      new_pronunciations[new_pronunciation] = weight

  if changed_anything:
    return word, new_pronunciations
  return word, None


def process_map_pronunciation_full(word: Word, symbols: OrderedSet[Symbol], map_symbol: Symbol) -> Tuple[Word, Optional[Pronunciations]]:
  global process_lookup_dict
  assert word in process_lookup_dict
  pronunciations = process_lookup_dict[word]
  assert len(pronunciations) > 0
  changed_anything = False
  new_pronunciations = OrderedDict()
  for pronunciation, weight in pronunciations.items():
    new_pronunciation = tuple(
      map_symbol if symbol in symbols else symbol
      for symbol in pronunciation
    )

    if new_pronunciation != pronunciation:
      changed_anything = True

    assert len(new_pronunciation) > 0
    if new_pronunciation in new_pronunciations:
      new_pronunciations[new_pronunciation] += weight
    else:
      new_pronunciations[new_pronunciation] = weight
  if changed_anything:
    return word, new_pronunciations
  return word, None
