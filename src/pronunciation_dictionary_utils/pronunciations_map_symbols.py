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


def __validate_symbol(symbol: str) -> Optional[str]:
  if not isinstance(symbol, str):
    return "Value needs of type 'str'!"
  assert len(symbol) > 0
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

  map_method = process_map_pronunciations_partial if partial_mapping else process_map_pronunciations_full
  process_method = partial(
    map_method,
    symbols=symbols,
    map_symbol=map_symbol,
  )

  with Pool(
    processes=mp_options.n_jobs,
    initializer=__init_pool,
    initargs=(dictionary,),
    maxtasksperchild=mp_options.maxtasksperchild,
  ) as pool:
    all_words = OrderedSet(dictionary.keys())
    iterator = pool.imap(process_method, all_words, mp_options.chunksize)
    new_pronunciations_to_words = dict(tqdm(iterator, total=len(all_words), unit="words"))

  changes_counter = 0

  for word, new_pronunciations in new_pronunciations_to_words.items():
    changed_pronunciations = new_pronunciations is not None
    if changed_pronunciations:
      dictionary[word] = new_pronunciations
      changes_counter += 1

  return changes_counter


PROCESS_LOOKUP_DICT: PronunciationDict = None


def __init_pool(lookup_dict: PronunciationDict) -> None:
  global PROCESS_LOOKUP_DICT
  PROCESS_LOOKUP_DICT = lookup_dict


def replace_str(s: str, replace: OrderedSet[str], replace_with: str) -> str:
  for r_str in replace:
    if r_str in s:
      s = s.replace(r_str, replace_with)
  return s


def process_map_pronunciations_partial(word: Word, symbols: OrderedSet[Symbol], map_symbol: Symbol) -> Tuple[Word, Optional[Pronunciations]]:
  global PROCESS_LOOKUP_DICT
  assert word in PROCESS_LOOKUP_DICT
  pronunciations = PROCESS_LOOKUP_DICT[word]
  new_pronunciations = map_pronunciations_partial(pronunciations, symbols, map_symbol)
  if new_pronunciations == pronunciations:
    del pronunciations
    del new_pronunciations
    return word, None
  del pronunciations
  return word, new_pronunciations


def process_map_pronunciations_full(word: Word, symbols: OrderedSet[Symbol], map_symbol: Symbol) -> Tuple[Word, Optional[Pronunciations]]:
  global PROCESS_LOOKUP_DICT
  assert word in PROCESS_LOOKUP_DICT
  pronunciations = PROCESS_LOOKUP_DICT[word]
  new_pronunciations = map_pronunciations_full(pronunciations, symbols, map_symbol)
  if new_pronunciations == pronunciations:
    del pronunciations
    del new_pronunciations
    return word, None
  del pronunciations
  return word, new_pronunciations


def map_pronunciations_partial(pronunciations: Pronunciations, replace_symbols: OrderedSet[Symbol], map_symbol: Symbol) -> Pronunciations:
  assert len(pronunciations) > 0
  assert map_symbol != ""
  new_pronunciations = OrderedDict()
  for pronunciation, weight in pronunciations.items():
    assert len(pronunciation) > 0
    new_pronunciation = tuple(
      replace_str(symbol, replace_symbols, map_symbol)
      for symbol in pronunciation
    )
    if new_pronunciation in new_pronunciations:
      new_pronunciations[new_pronunciation] += weight
    else:
      new_pronunciations[new_pronunciation] = weight
  return new_pronunciations


def map_pronunciations_full(pronunciations: Pronunciations, replace_symbols: OrderedSet[Symbol], map_symbol: Symbol) -> Pronunciations:
  assert len(pronunciations) > 0
  assert map_symbol != ""
  new_pronunciations = OrderedDict()
  for pronunciation, weight in pronunciations.items():
    assert len(pronunciation) > 0
    new_pronunciation = tuple(
      map_symbol if symbol in replace_symbols else symbol
      for symbol in pronunciation
    )
    if new_pronunciation in new_pronunciations:
      new_pronunciations[new_pronunciation] += weight
    else:
      new_pronunciations[new_pronunciation] = weight
  return new_pronunciations
