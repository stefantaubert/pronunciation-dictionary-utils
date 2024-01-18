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

import json
from argparse import ArgumentParser, Namespace
from json.decoder import JSONDecodeError
from logging import Logger
from typing import Dict, Optional

from pronunciation_dictionary import (DeserializationOptions, MultiprocessingOptions,
                                      SerializationOptions)

from pronunciation_dictionary_utils.pronunciations_map_symbols_dict import map_symbols_dict
from pronunciation_dictionary_utils_cli.argparse_helper import (add_encoding_argument, add_io_group,
                                                                add_mp_group, parse_existing_file)
from pronunciation_dictionary_utils_cli.io import try_load_dict, try_save_dict

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


def try_load_mappings(flogger: Logger, mapping: str, encoding: str) -> Optional[Dict[str, str]]:
  with open(mapping, "r", encoding=encoding) as mapping_file:
    # warning: only last value saved for duplicate keys in file
    try:
      mappings = json.load(mapping_file)
    except (JSONDecodeError, TypeError):
      flogger.info("No or invalid content in mapping file.")
      return None
  if not isinstance(mappings, dict):
    flogger.info("No dictionary found in mapping file.")
    return None
  for key, value in mappings.items():
    if not isinstance(key, str) or not isinstance(value, str):
      flogger.info("Keys or values in mapping file are not of type string.")
      return None
  return mappings


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

  mappings = try_load_mappings(flogger, ns.mapping, ns.encoding)
  if mappings is None:
    return False
  logger.info(f"Loaded mapping containing {len(mappings)} entries.")

  changed_words_total = map_symbols_dict(
    dictionary_instance, mappings, ns.partial_mapping, mp_options, silent=False)

  if len(changed_words_total) == 0:
    logger.info("Didn't change anything.")
    return True

  success = try_save_dict(dictionary_instance, ns.dictionary, ns.encoding, s_options, logger)
  if not success:
    return False

  logger.info(f"Changed pronunciations of {len(changed_words_total)} word(s).")
  logger.info(f"Written dictionary to: \"{ns.dictionary.absolute()}\"")

  return True
