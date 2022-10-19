from collections import OrderedDict
from functools import partial
from multiprocessing.pool import Pool
from typing import Generator, Iterable, Literal, Optional, Set, Tuple

from ordered_set import OrderedSet
from pronunciation_dictionary import (MultiprocessingOptions, PronunciationDict, Pronunciations,
                                      Symbol, Word)
from tqdm import tqdm

from pronunciation_dictionary_utils.validation import (validate_dictionary, validate_mp_options,
                                                       validate_type)

DEFAULT_EMPTY_WEIGHT = 1


def __validate_mode(mode: str) -> Optional[str]:
  if mode not in ["all", "start", "end", "both"]:
    return "Value needs to be 'all', 'start', 'end' or 'both'!"
  return None


def remove_symbols_from_pronunciations(dictionary: PronunciationDict, symbols: OrderedSet[Symbol], mode: str, keep_empty: bool, empty_symbol: Optional[Symbol], mp_options: MultiprocessingOptions) -> Tuple[OrderedSet[Word], int]:
  if msg := validate_dictionary(dictionary):
    raise ValueError(f"Parameter 'dictionary': {msg}")
  if msg := validate_type(symbols, OrderedSet):
    raise ValueError(f"Parameter 'symbols': {msg}")
  if msg := __validate_mode(mode):
    raise ValueError(f"Parameter 'mode': {msg}")
  if msg := validate_type(keep_empty, bool):
    raise ValueError(f"Parameter 'keep_empty': {msg}")
  if empty_symbol is not None and (msg := validate_type(empty_symbol, str)):
    raise ValueError(f"Parameter 'empty_symbol': {msg}")
  if msg := validate_mp_options(mp_options):
    raise ValueError(f"Parameter 'mp_options': {msg}")

  if len(symbols) == 0:
    return OrderedSet(), 0

  process_method = partial(
    process_get_pronunciation,
    symbols=symbols,
    mode=mode,
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


def process_get_pronunciation(word: Word, symbols: Set[Symbol], mode: str) -> Tuple[Word, Optional[Pronunciations]]:
  global process_lookup_dict
  assert word in process_lookup_dict
  pronunciations = process_lookup_dict[word]
  new_pronunciations = remove_symbols_from_pronunciations_entry(pronunciations, symbols, mode)
  if new_pronunciations == pronunciations:
    return word, None
  return word, new_pronunciations


def remove_symbols_start(symbols: Iterable[Symbol], remove: Set[Symbol]) -> Generator[Symbol, None, None]:
  start = True
  for s in symbols:
    if start and s in remove:
      continue
    start = False
    yield s


def remove_symbols_end(symbols: Iterable[Symbol], remove: Set[Symbol]) -> Generator[Symbol, None, None]:
  symbols_rev = reversed(tuple(symbols))
  symbols_rev_rem = tuple(remove_symbols_start(symbols_rev, remove))
  result = reversed(symbols_rev_rem)
  yield from result


def remove_symbols_both(symbols: Iterable[Symbol], remove: Set[Symbol]) -> Generator[Symbol, None, None]:
  step1 = remove_symbols_start(symbols, remove)
  yield from remove_symbols_end(step1, remove)


def remove_symbols_all(symbols: Iterable[Symbol], remove: Set[Symbol]) -> Generator[Symbol, None, None]:
  res = (
    symbol
    for symbol in symbols
    if symbol not in remove
  )
  yield from res


def remove_symbols_mode(symbols: Iterable[Symbol], remove: Set[Symbol], mode: Literal["all", "start", "end", "both"]) -> Generator[Symbol, None, None]:
  if mode == "all":
    yield from remove_symbols_all(symbols, remove)
  elif mode == "start":
    yield from remove_symbols_start(symbols, remove)
  elif mode == "end":
    yield from remove_symbols_end(symbols, remove)
  elif mode == "both":
    yield from remove_symbols_both(symbols, remove)
  else:
    assert False


def remove_symbols_from_pronunciations_entry(pronunciations: Pronunciations, symbols: Set[Symbol], mode: str) -> Pronunciations:
  new_pronunciations = OrderedDict()
  changed_anything = False
  for pronunciation, weight in pronunciations.items():
    new_pronunciation = tuple(remove_symbols_mode(pronunciation, symbols, mode))

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
