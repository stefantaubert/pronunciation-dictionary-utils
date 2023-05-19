"""
The module maps symbols in pronunciations in *.dict file according to mappings from *.json file.

Example usage:
$ dict-cli map_symbols_in_pronunciations_json "my_dictionary.dict" "mappings.json" -pm

positional arguments:
  DICTIONARY                            dictionary file
  MAPPING                               mapping file

optional arguments:
  -h, --help                            show this help message and exit
  -pm, --partial-mapping                map symbols inside a symbol
"""

from argparse import ArgumentParser, Namespace
from functools import partial
import json
from json.decoder import JSONDecodeError
from logging import Logger
from typing import Optional, Dict, List, Set

from ordered_set import OrderedSet
from tqdm import tqdm

from pronunciation_dictionary import (
  DeserializationOptions, MultiprocessingOptions, SerializationOptions, get_phoneme_set)
from pronunciation_dictionary.types import PronunciationDict
from pronunciation_dictionary_utils import map_symbols
from pronunciation_dictionary_utils_cli.argparse_helper import (add_encoding_argument, add_io_group,
                                                                add_mp_group, parse_existing_file)
from pronunciation_dictionary_utils_cli.io import (try_load_dict, try_save_dict)

DEFAULT_EMPTY_WEIGHT = 1.0


def get_pronunciations_map_symbols_json_parser(parser: ArgumentParser) -> Namespace:
  """
  Configures an ArgumentParser object to parse command-line arguments.
  """
  parser.description = "Map symbols in pronunciations according to mappings in *.json file."
  parser.add_argument("dictionary", metavar='DICTIONARY',
                      type=parse_existing_file, help="dictionary file")
  parser.add_argument("mapping", metavar='MAPPING',
                      type=parse_existing_file, help="mapping file")
  parser.add_argument("-pm", "--partial-mapping", action="store_true",
                      help="map symbols inside a symbol; useful when mapping the same vowel having different tones or stress within one operation")
  add_encoding_argument(parser, "-me", "--mapping-encoding", "encoding of mapping")
  add_io_group(parser)
  add_mp_group(parser)
  return map_symbols_in_pronunciations_ns


def get_mappable_symbols(sounds_in_dictionary: Set[str], sounds_in_mappings: Set[str]) -> List[str]:
  """
  Returns a list of unique symbols that occur both in the passed dictionary and the mappings. 
  # TODO sorting
  """
  mappable_symbols = []
  mappable_symbols = [
    symbol for symbol in sounds_in_dictionary if symbol in sounds_in_mappings and symbol not in mappable_symbols]
  #sorted_mappable_symbols = sorted(mappable_symbols, key=lambda x: (-len(x), x))
  #return sorted_mappable_symbols
  return mappable_symbols


def get_unmappable_symbols(sounds_in_dictionary: Set[str], sounds_in_mappings: Set[str]) -> List[str]:
  """
  Returns a list of unique symbols that occur in the dictionary but not in the mappings.
  """
  unmappable_symbols = []
  unmappable_symbols = [
    symbol for symbol in sounds_in_dictionary if symbol not in sounds_in_mappings and symbol not in unmappable_symbols]
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
                              True, mp_options, use_tqdm=False)

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
                              False, mp_options, use_tqdm=False)

  return changed_words


def identify_and_apply_mappings(logger: Logger, flogger: Logger, dictionary: PronunciationDict, mappings: Dict[str, str],
                                partial_mapping: bool, mp_options: 'MultiprocessingOptions') -> Set[str]:
  """
  Identifies applicable mappings and triggers mapping them according to the specified method.
  It returns a set of words whose pronunciations have been changed. 
  """
  unique_sounds_in_dictionary = get_phoneme_set(dictionary)
  unique_sounds_in_mappings = set(mappings.keys())

  mappable_symbols = get_mappable_symbols(unique_sounds_in_dictionary, unique_sounds_in_mappings)
  unmappable_symbols = get_unmappable_symbols(
    unique_sounds_in_dictionary, unique_sounds_in_mappings)

  if logger and flogger:
    logger.info(f"Found {len(mappable_symbols)} applicable phoneme mappings.")
    flogger.info(f"Mapped phonemes in dictionary: {' '.join(sorted(mappable_symbols))}")
    flogger.info(f"Unmapped phonemes in dictionary: {' '.join(sorted(unmappable_symbols))}")

  sorted_mappable_symbols = sorted(mappable_symbols, key=lambda x: (-len(x), x))
  
  changed_words_total = set()
  if sorted_mappable_symbols:
    mapping_method = partial(
      apply_mapping_partial if partial_mapping else apply_mapping_full,
      dictionary=dictionary,
      mappings=mappings,
      mp_options=mp_options
    )
    for mappable_symbol in tqdm(sorted_mappable_symbols, total=len(sorted_mappable_symbols), desc="Mapping"):
      changed_words = mapping_method(mappable_symbol=mappable_symbol)
      changed_words_total |= changed_words

  return changed_words_total


def map_symbols_in_pronunciations_ns(ns: Namespace, logger: Logger, flogger: Logger) -> bool:
  """
  Loads the dictionary and the mapping file and sends them for mapping, logs and saves the results.
  """
  lp_options = DeserializationOptions(
    ns.consider_comments, ns.consider_numbers, ns.consider_pronunciation_comments, ns.consider_weights)
  mp_options = MultiprocessingOptions(ns.n_jobs, ns.maxtasksperchild, ns.chunksize)
  s_options = SerializationOptions(ns.parts_sep, ns.consider_numbers, ns.consider_weights)

  dictionary_instance = try_load_dict(ns.dictionary, ns.encoding, lp_options, mp_options, logger)
  if dictionary_instance is None:
    return False
  logger.info(f"Loaded dictionary containing {len(dictionary_instance)} entries.")

  with open(ns.mapping, "r", encoding=ns.encoding) as mapping_file:
    # warning: only last value saved for duplicate keys in file
    try:
      mappings = json.load(mapping_file)
    except (JSONDecodeError, TypeError):
      flogger.info("No or invalid content in mapping file.")
      return False
    if not isinstance(mappings, dict):
      flogger.info("No dictionary found in mapping file.")
      return False
    for key, value in mappings.items():
      if not isinstance(key, str) or not isinstance(value, str):
        flogger.info("Keys or values in mapping file are not of type string.")
        return False
  logger.info(f"Loaded mapping containing {len(mappings)} entries.")

  changed_words_total = identify_and_apply_mappings(
    logger, flogger, dictionary_instance, mappings, ns.partial_mapping, mp_options)

  if len(changed_words_total) == 0:
    logger.info("Didn't change anything.")
    return True

  success = try_save_dict(dictionary_instance, ns.dictionary, ns.encoding, s_options, logger)
  if not success:
    return False

  logger.info(f"Changed pronunciations of {len(changed_words_total)} word(s).")
  logger.info(f"Written dictionary to: \"{ns.dictionary.absolute()}\"")

  return True
