from functools import partial
from logging import getLogger
from typing import Dict, Set

from ordered_set import OrderedSet
from pronunciation_dictionary import MultiprocessingOptions, get_phoneme_set
from pronunciation_dictionary.types import PronunciationDict
from tqdm import tqdm

from pronunciation_dictionary_utils import map_symbols


def get_mappable_symbols(sounds_in_dictionary: Set[str], sounds_in_mappings: Set[str]) -> Set[str]:
  """
  Returns a list of unique symbols that occur both in the passed dictionary and the mappings. 
  """
  mappable_symbols = sounds_in_dictionary & sounds_in_mappings
  return mappable_symbols


def get_unmappable_symbols(sounds_in_dictionary: Set[str], sounds_in_mappings: Set[str]) -> Set[str]:
  """
  Returns a list of unique symbols that occur in the dictionary but not in the mappings.
  """
  unmappable_symbols = sounds_in_dictionary - sounds_in_mappings
  return unmappable_symbols


def apply_mapping_partial(dictionary: PronunciationDict, mappings: Dict[str, str], mappable_symbol: str,
                          mp_options: 'MultiprocessingOptions') -> Set[str]:
  """
  Applies partial mapping for a single mappable symbol. It returns a set of words whose pronunciations 
  have been changed. It enables mapping the symbol occuring within a longer symbol, e.g., passing the 
  symbol "AO1" and a mapping "AO": "ɔ" would result in "ɔ1".
  """
  from_symbol = OrderedSet((mappable_symbol,))
  to_phonemes = mappings[mappable_symbol]

  if " " in to_phonemes:
    raise Exception("Whitespaces in mappings aren't supported with partial mapping.")

  changed_words = map_symbols(dictionary, from_symbol, to_phonemes,
                              True, mp_options, silent=True)

  return changed_words


def apply_mapping_full(dictionary: PronunciationDict, mappings: Dict[str, str], mappable_symbol: str,
                       mp_options: 'MultiprocessingOptions') -> Set[str]:
  """
  Applies mapping for a single mappable symbol. It returns a set of words whose pronunciations have 
  been changed. It does not map the symbol occuring within a longer symbol e.g., passing the 
  symbol "AO1" and a mapping "AO": "ɔ" would result in "AO1".
  """
  from_symbol = OrderedSet((mappable_symbol,))
  to_phonemes = mappings[mappable_symbol]

  # method without partial flag allows whitespaces within mappings
  to_phonemes = to_phonemes.split(" ")
  to_phonemes = [p for p in to_phonemes if len(p) > 0]

  changed_words = map_symbols(dictionary, from_symbol, to_phonemes,
                              False, mp_options, silent=True)

  return changed_words


def map_symbols_dict(dictionary: PronunciationDict, mappings: Dict[str, str],
                     partial_mapping: bool, mp_options: MultiprocessingOptions, silent: bool = False) -> Set[str]:
  """
  Identifies applicable mappings and triggers mapping them according to the specified method.
  It returns a set of words whose pronunciations have been changed. 
  """
  logger = getLogger(__name__)
  unique_sounds_in_dictionary = get_phoneme_set(dictionary)
  unique_sounds_in_mappings = set(mappings.keys())

  mappable_symbols = get_mappable_symbols(unique_sounds_in_dictionary, unique_sounds_in_mappings)
  unmappable_symbols = get_unmappable_symbols(
    unique_sounds_in_dictionary, unique_sounds_in_mappings)

  logger.info(f"Found {len(mappable_symbols)} applicable phoneme mappings.")
  logger.info(f"Mapped phonemes in dictionary: {' '.join(sorted(mappable_symbols))}")
  logger.info(f"Unmapped phonemes in dictionary: {' '.join(sorted(unmappable_symbols))}")

  changed_words_total = set()
  if mappable_symbols:
    mapping_method = partial(
      apply_mapping_partial if partial_mapping else apply_mapping_full,
      dictionary=dictionary,
      mappings=mappings,
      mp_options=mp_options
    )

    sorted_mappable_symbols = OrderedSet(sorted(mappable_symbols, key=len, reverse=True))

    for mappable_symbol in tqdm(sorted_mappable_symbols, total=len(sorted_mappable_symbols), desc="Mapping", disable=silent):
      changed_words = mapping_method(mappable_symbol=mappable_symbol)
      changed_words_total |= changed_words

  return changed_words_total
