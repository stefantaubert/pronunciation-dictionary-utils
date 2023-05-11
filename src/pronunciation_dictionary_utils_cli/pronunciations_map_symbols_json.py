import json
from argparse import ArgumentParser, Namespace
from logging import Logger
from typing import Dict, Set, Tuple

from ordered_set import OrderedSet
from tqdm import tqdm

from pronunciation_dictionary import (DeserializationOptions, MultiprocessingOptions,
                                      SerializationOptions, get_phoneme_set)
from pronunciation_dictionary_utils import map_symbols
from pronunciation_dictionary_utils_cli.argparse_helper import (add_encoding_argument, add_io_group, 
  add_mp_group, parse_existing_file)
from pronunciation_dictionary_utils_cli.io import (try_load_dict, try_save_dict)

DEFAULT_EMPTY_WEIGHT = 1.0


def get_pronunciations_map_symbols_json_parser(parser: ArgumentParser):
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

def get_mappable_and_unmappable_symbols(sounds_in_dictionary: Set[str], sounds_in_mappings: Set[str]) -> Tuple[OrderedSet, OrderedSet]:
  # sounds that are both in the dictionary and the mapping file
  mappable_symbols = sounds_in_dictionary & sounds_in_mappings
  mappable_symbols = OrderedSet(sorted(mappable_symbols, reverse=True, key=len))
  
  # sounds that are in the dictionary but not in the mapping file
  unmappable_symbols = OrderedSet(sounds_in_dictionary - sounds_in_mappings)

  return mappable_symbols, unmappable_symbols

"""
# version with two methods out of "process_mappable_symbol", one with partial mapping and one without

def process_mappable_symbol_with_partial_method(dictionary: Dict[str, str], mappings: Dict[str, str], mappable_symbol: str, 
                            mp_options: MultiprocessingOptions = None) -> Set[str]:
  from_symbol = OrderedSet((mappable_symbol,))
  to_phonemes = mappings[mappable_symbol]

  if " " in to_phonemes:
      raise Exception("Whitespaces in mapping values aren't supported with partial mapping.")

  changed_words = map_symbols(dictionary, from_symbol, to_phonemes, partial_mapping=True, mp_options, use_tqdm=False)

  return changed_words


def process_mappable_symbol_without_partial_method(dictionary: Dict[str, str], mappings: Dict[str, str], mappable_symbol: str, 
                            mp_options: MultiprocessingOptions = None) -> Set[str]:
  from_symbol = OrderedSet((mappable_symbol,))
  to_phonemes = mappings[mappable_symbol]
  to_phonemes = to_phonemes.split(" ")  # allows whitespaces
  to_phonemes = [p for p in to_phonemes if len(p) > 0]

  changed_words = map_symbols(dictionary, from_symbol, to_phonemes, partial_mapping=False, mp_options, use_tqdm=False)

  return changed_words
"""
def process_mappable_symbol(dictionary: Dict[str, str], mappings: Dict[str, str], mappable_symbol: str, 
                            partial_mapping: bool = False, mp_options: MultiprocessingOptions = None) -> Set[str]:
  from_symbol = OrderedSet((mappable_symbol,))
  to_phonemes = mappings[mappable_symbol]
  if partial_mapping is False:
    to_phonemes = to_phonemes.split(" ")  # allows whitespaces
    to_phonemes = [p for p in to_phonemes if len(p) > 0]
  if partial_mapping is True and " " in to_phonemes:
      raise Exception("Whitespaces in mapping values aren't supported with partial mapping.")

  changed_words = map_symbols(
    dictionary, from_symbol, to_phonemes, partial_mapping, mp_options, use_tqdm=False)

  return changed_words

def process_mappable_symbols(logger: Logger, flogger: Logger, dictionary: Dict[str, str], mappings: Dict[str, str], 
                             partial_mapping: bool, mp_options: 'MultiprocessingOptions') -> Set[str]:
  unique_sounds_in_dictionary = get_phoneme_set(dictionary)
  unique_sounds_in_mappings = mappings.keys()
  mappable_symbols, unmappable_symbols = get_mappable_and_unmappable_symbols(unique_sounds_in_dictionary, unique_sounds_in_mappings)

  logger.info(f"Found {len(mappable_symbols)} applicable phoneme mappings.")
  flogger.info(f"Mapped phonemes in dictionary: {' '.join(sorted(mappable_symbols))}")
  flogger.info(f"Unmapped phonemes in dictionary: {' '.join(sorted(unmappable_symbols))}")

  changed_words_total = set()
  if mappable_symbols:
    for mappable_symbol in tqdm(mappable_symbols, total=len(mappable_symbols), desc="Mapping"):
      changed_words = process_mappable_symbol(dictionary, mappings, mappable_symbol, partial_mapping, mp_options)
      """
      # version with two methods out of "process_mappable_symbol", one with partial mapping and one without

      if partial_mapping:
        changed_words = process_mappable_symbol_with_partial_method(dictionary, mappings, mappable_symbol, mp_options)
      else:
        changed_words = process_mappable_symbol_without_partial_method(dictionary, mappings, mappable_symbol, mp_options)
      """
      changed_words_total |= changed_words
  
  return changed_words_total


def map_symbols_in_pronunciations_ns(ns: Namespace, logger: Logger, flogger: Logger) -> bool:
  lp_options = DeserializationOptions(
    ns.consider_comments, ns.consider_numbers, ns.consider_pronunciation_comments, ns.consider_weights)
  mp_options = MultiprocessingOptions(ns.n_jobs, ns.maxtasksperchild, ns.chunksize)
  s_options = SerializationOptions(ns.parts_sep, ns.consider_numbers, ns.consider_weights)

  dictionary_instance = try_load_dict(ns.dictionary, ns.encoding, lp_options, mp_options, logger)
  if dictionary_instance is None:
    return False
  logger.info(f"Loaded dictionary containing {len(dictionary_instance)} entries.")
  
  with open(ns.mapping, "r", encoding=ns.encoding) as mapping_file: # only last value saved for duplicate keys from file
    # following checks are never reached by failures
    if mapping_file is None:  # no file
      return False
    mappings = json.load(mapping_file)
    if mappings is None:  # empty file
      return False
    if not isinstance(mappings, dict):
      return False
    mapping_file.close()
  logger.info(f"Loaded mapping containing {len(mappings)} entries.")

  changed_words_total = process_mappable_symbols(logger, flogger, dictionary_instance, mappings, 
                                                 ns.partial_mapping, mp_options)

  if len(changed_words_total) == 0:
    logger.info("Didn't change anything.")
    return True

  success = try_save_dict(dictionary_instance, ns.dictionary, ns.encoding, s_options, logger)
  if not success:
    return False

  logger.info(f"Changed pronunciations of {len(changed_words_total)} word(s).")
  logger.info(f"Written dictionary to: \"{ns.dictionary.absolute()}\"")
  
  return True