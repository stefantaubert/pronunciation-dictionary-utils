import json
from typing import Dict, List, Tuple
from argparse import ArgumentParser, Namespace

from logging import Logger

from ordered_set import OrderedSet
from pronunciation_dictionary import (DeserializationOptions, MultiprocessingOptions,
                                      SerializationOptions, get_phoneme_set)
from tqdm import tqdm

from pronunciation_dictionary_utils import map_symbols
from pronunciation_dictionary_utils_cli.argparse_helper import (add_encoding_argument, add_io_group, 
  add_mp_group, parse_existing_file, parse_non_empty_or_whitespace)
from pronunciation_dictionary_utils_cli.io import try_load_dict, try_save_dict

from pronunciation_dictionary_utils.pronunciations_map_symbols import (
  __init_pool, process_map_pronunciations_full, process_map_pronunciations_partial)

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

def get_mappable_and_unmappable_symbols(dictionary: Dict[str, str], mappings: Dict[str, str]) -> Tuple[list, list]:
  dictionary_unique_sounds = get_phoneme_set(dictionary)
  
  # sounds that are both in the dictionary and the mapping file
  mappable_symbols = dictionary_unique_sounds.intersection(mappings)
  mappable_symbols = sorted(mappable_symbols, reverse=True, key=len)
  
  # sounds that are in the dictionary but not in the mapping file
  unmappable_symbols = dictionary_unique_sounds - mappings.keys()

  return mappable_symbols, unmappable_symbols

def process_mappable_symbol(dictionary, mappings, mappable_symbol, partial_mapping=False, mp_options=None, testing=False) -> set():
  # prepares the mappable symbol
  from_symbol = mappable_symbol
  from_symbol = OrderedSet((from_symbol,))

  # prepares the mapping process by getting a mapping (value in dictionary mappings for key mappable_symbol) 
  # to map the mappable symbol to
  mapping = mappings[mappable_symbol]
  to_phonemes = mapping
  if partial_mapping is False:
    to_phonemes = mapping.split(" ")  # allows whitespaces
    to_phonemes = [p for p in to_phonemes if len(p) > 0]
  if partial_mapping is True and " " in to_phonemes:
      raise Exception("Whitespaces in mapping values aren't supported with partial mapping.")
  
  changed_words = set()

  # maps the mappable symbol to the mapping
  if not testing:
    changed_words = map_symbols(
      dictionary, from_symbol, to_phonemes, partial_mapping, mp_options, use_tqdm=False)
  else:
    __init_pool(dictionary)
    if partial_mapping is True:
       word, new_pronunciations = process_map_pronunciations_partial("test", from_symbol, to_phonemes)
    else:
       word, new_pronunciations = process_map_pronunciations_full("test", from_symbol, to_phonemes)
    if new_pronunciations:
      dictionary[word] = new_pronunciations
      changed_words.add(word)

  return changed_words


def map_symbols_in_pronunciations_ns(ns: Namespace, logger: Logger, flogger: Logger) -> bool:
  lp_options = DeserializationOptions(
    ns.consider_comments, ns.consider_numbers, ns.consider_pronunciation_comments, ns.consider_weights)
  mp_options = MultiprocessingOptions(ns.n_jobs, ns.maxtasksperchild, ns.chunksize)
  s_options = SerializationOptions(ns.parts_sep, ns.consider_numbers, ns.consider_weights)

  # loads the file to be changed
  dictionary_instance = try_load_dict(ns.dictionary, ns.encoding, lp_options, mp_options, logger)
  if dictionary_instance is None:
    return False
  
  # loads the file with the mappings
  with open(ns.mapping, "r", encoding=ns.encoding) as mapping_file:
    if mapping_file is None:  # no file
      return False
    mappings = json.load(mapping_file)
    if mappings is None:  # empty file
      return False

  logger.info(f"Loaded mapping containing {len(mappings)} entries.")

  mappable_symbols, unmappable_symbols = get_mappable_and_unmappable_symbols(dictionary_instance, mappings)

  logger.info(f"Found {len(mappable_symbols)} applicable phoneme mappings.")
  flogger.info(f"Mapped phonemes in dictionary: {' '.join(sorted(mappable_symbols))}")
  flogger.info(f"Unmapped phonemes in dictionary: {' '.join(sorted(unmappable_symbols))}")

  # mapping all mappable symbols in the dictionary
  changed_words_total = set()
  if mappable_symbols:
    for mappable_symbol in tqdm(mappable_symbols, total=len(mappable_symbols), desc="Mapping"):
      changed_words = process_mappable_symbol(dictionary_instance, mappings, mappable_symbol, ns.partial_mapping, mp_options)
      changed_words_total |= changed_words
  else:
    tqdm(total=1, desc="Mapping").update(1)

  if len(changed_words_total) == 0:
    logger.info("Didn't change anything.")
    return True

  success = try_save_dict(dictionary_instance, ns.dictionary, ns.encoding, s_options, logger)
  if not success:
    return False

  logger.info(f"Changed pronunciations of {len(changed_words_total)} word(s).")
  logger.info(f"Written dictionary to: \"{ns.dictionary.absolute()}\"")
  
  return True