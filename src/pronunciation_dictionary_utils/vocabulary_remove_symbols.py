from functools import partial
from multiprocessing.pool import Pool
from typing import Literal, Optional, Tuple

from ordered_set import OrderedSet
from pronunciation_dictionary import MultiprocessingOptions, Word
from tqdm import tqdm

from pronunciation_dictionary_utils.validation import validate_mp_options, validate_vocabulary


def __validate_mode(mode: str) -> Optional[str]:
  if mode not in ["all", "start", "end", "both"]:
    return "Value needs to be 'all', 'start', 'end' or 'both'!"
  return None


def __validate_symbols(symbols: str) -> Optional[str]:
  if not isinstance(symbols, str):
    return "Value needs of type 'str'!"
  return None


def remove_symbols_from_vocabulary(vocabulary: OrderedSet[Word], symbols: str, mode: str, mp_options: MultiprocessingOptions) -> Tuple[OrderedSet[Word], OrderedSet[Word]]:
  if msg := validate_vocabulary(vocabulary):
    raise ValueError(f"Parameter 'vocabulary': {msg}")
  if msg := __validate_symbols(symbols):
    raise ValueError(f"Parameter 'symbols': {msg}")
  if msg := __validate_mode(mode):
    raise ValueError(f"Parameter 'mode': {msg}")
  if msg := validate_mp_options(mp_options):
    raise ValueError(f"Parameter 'mp_options': {msg}")

  if symbols == "":
    return OrderedSet(), 0

  process_method = partial(
    process_get_word,
    symbols=symbols,
    mode=mode,
  )

  with Pool(
    processes=mp_options.n_jobs,
    maxtasksperchild=mp_options.maxtasksperchild,
  ) as pool:
    iterator = pool.imap(process_method, vocabulary, mp_options.chunksize)
    new_words_to_words = dict(tqdm(iterator, total=len(vocabulary), unit="words"))

  changed_words = OrderedSet()
  removed_words_entirely = OrderedSet()
  final_voc = OrderedSet()
  for word in vocabulary:
    new_word = new_words_to_words[word]
    changed_word = new_word is not None
    if changed_word:
      changed_words.add(word)
      if new_word == "":
        removed_words_entirely.add(word)
        continue
      final_voc.add(new_word)
    else:
      final_voc.add(word)

  vocabulary.clear()
  vocabulary |= final_voc

  return removed_words_entirely, changed_words


def process_get_word(word: Word, symbols: str, mode: Literal["all", "start", "end", "both"]) -> Tuple[Word, Optional[Word]]:
  if mode == "all":
    new_word = "".join(
      symbol
      for symbol in word
      if symbol not in symbols
    )
  elif mode == "start":
    new_word = word.lstrip(symbols)
  elif mode == "end":
    new_word = word.rstrip(symbols)
  elif mode == "both":
    new_word = word.strip(symbols)
  else:
    assert False

  if new_word != word:
    return word, new_word
  return word, None
