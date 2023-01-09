import json  # handling json file
from argparse import ArgumentParser, Namespace
from collections import OrderedDict  # OrderedDict() for sorting mappings
from logging import Logger

from ordered_set import OrderedSet  # instead of ConvertToOrderedSetAction
from pronunciation_dictionary import (DeserializationOptions, MultiprocessingOptions,
                                      SerializationOptions)

from pronunciation_dictionary_utils import map_symbols
from pronunciation_dictionary_utils_cli.argparse_helper import (  # ConvertToOrderedSetAction,
  add_io_group, add_mp_group, parse_existing_file, parse_non_empty_or_whitespace)
from pronunciation_dictionary_utils_cli.io import try_load_dict, try_save_dict

DEFAULT_EMPTY_WEIGHT = 1.0

# arguments for the main function


def get_pronunciations_map_symbols_json_parser(parser: ArgumentParser):
  parser.description = "Map symbols in pronunciations according to mappings in *.json file."
  # file to be changed
  parser.add_argument("dictionary", metavar='DICTIONARY',
                      type=parse_existing_file, help="dictionary file")
  # source file for mappings
  parser.add_argument("mapping", metavar='MAPPING',
                      type=parse_existing_file, help="mapping file")
  # additional option, partial mapping
  parser.add_argument("-pm", "--partial-mapping", action="store_true",
                      help="map symbols inside a symbol; useful when mapping the same vowel having different tones or stress within one operation")
  add_io_group(parser)  # argparse_helper.py, for modification of dictionary content
  add_mp_group(parser)  # argparse_helper.py, multiprocessing arguments
  return map_symbols_in_pronunciations_ns


def map_symbols_in_pronunciations_ns(ns: Namespace, logger: Logger, flogger: Logger) -> bool:
  lp_options = DeserializationOptions(
    ns.consider_comments, ns.consider_numbers, ns.consider_pronunciation_comments, ns.consider_weights)
  mp_options = MultiprocessingOptions(ns.n_jobs, ns.maxtasksperchild, ns.chunksize)

  s_options = SerializationOptions(ns.parts_sep, ns.consider_numbers, ns.consider_weights)

  # loads the file to be changed
  dictionary_instance = try_load_dict(ns.dictionary, ns.encoding, lp_options, mp_options, logger)
  if dictionary_instance is None:
    return False

  # loads the file with the mappings, saves it to an ordered dictionary
  with open(ns.mapping, "r") as mapping_file:
    if mapping_file is None:  # no file
      return False
    mappings = json.load(mapping_file, object_pairs_hook=OrderedDict)
    if mappings is None:  # empty file
      return False

  # iterates through the dictionary keys, from last key to first (== longest mappings are dealt with first):
  # - loads a key as from_symbol and a value as to_symbol,
  # - maps each instance of the key (from_symbol) in the file to the value (to_symbol)
  for key, mapping in mappings.items():
    from_symbol = parse_non_empty_or_whitespace(key)  # gets keys
    from_symbol = OrderedSet((from_symbol,))
    # changes symbols in dictionary_instance
    changed_counter = map_symbols(
      dictionary_instance, from_symbol, mapping, ns.partial_mapping, mp_options)

  if changed_counter == 0:
    logger.info("Didn't change anything.")
    return True

  logger.info(f"Changed pronunciations of {changed_counter} word(s).")

  success = try_save_dict(dictionary_instance, ns.dictionary, ns.encoding, s_options, logger)
  if not success:
    return False

  logger.info(f"Written dictionary to: \"{ns.dictionary.absolute()}\"")

  return True