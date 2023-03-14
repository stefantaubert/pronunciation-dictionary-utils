import json
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
  add_encoding_argument(parser, "-me", "--mapping-encoding", "encoding of mapping")
  add_io_group(parser)
  add_mp_group(parser)
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

  # loads the file with the mappings, saves the mappings to a dictionary
  with open(ns.mapping, "r", encoding=ns.encoding) as mapping_file:
    if mapping_file is None:  # no file
      return False
    mappings = json.load(mapping_file)
    if mappings is None:  # empty file
      return False

  logger.info(f"Loaded mapping containing {len(mappings)} entries.")

  dictionary_phonemes = get_phoneme_set(dictionary_instance)  # unique sounds from the dictionary
  common_keys = dictionary_phonemes.intersection(mappings)  # sounds that are both in the dictionary and the mapping file
  dict_unmapped = dictionary_phonemes - mappings.keys()  # sounds that are in the dictionary but not in the mapping file

  common_keys = sorted(common_keys, reverse=True, key=len)  # sorting common_keys in a descending order by length

  logger.info(f"Found {len(common_keys)} applicable phoneme mappings.")
  flogger.info(f"Mapped phonemes in dictionary: {' '.join(sorted(common_keys))}")
  flogger.info(f"Unmapped phonemes in dictionary: {' '.join(sorted(dict_unmapped))}")

  # iterates through common_keys:
  # - loads a key as from_symbol and a value as to_phonemes,
  # - maps each instance of the key (from_symbol) in the file to the value (to_phonemes)
  changed_words_total = set()
  for key in tqdm(common_keys, total=len(common_keys), desc="Mapping"):
    # gets a value (mapping) to map the key to
    mapping = mappings[key]
    to_phonemes = mapping
    # gets a key
    from_symbol = key
    from_symbol = OrderedSet((from_symbol,))
    # changes symbols in dictionary_instance. If whitespaces: 
    # - without partial method, values are split at whitespaces and appear in the final version
    # - with partial method, an error is thrown because it is not be meant to be supported
    if ns.partial_mapping is False:
      to_phonemes = mapping.split(" ")
      to_phonemes = [p for p in to_phonemes if len(p) > 0]
    changed_words = map_symbols(
      dictionary_instance, from_symbol, to_phonemes, ns.partial_mapping, mp_options, use_tqdm=False)
    changed_words_total |= changed_words

  if len(changed_words_total) == 0:
    logger.info("Didn't change anything.")
    return True

  success = try_save_dict(dictionary_instance, ns.dictionary, ns.encoding, s_options, logger)
  if not success:
    return False

  logger.info(f"Changed pronunciations of {len(changed_words_total)} word(s).")
  logger.info(f"Written dictionary to: \"{ns.dictionary.absolute()}\"")
  
  return True