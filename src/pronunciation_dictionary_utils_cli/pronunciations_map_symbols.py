from argparse import ArgumentParser, Namespace
from logging import Logger
from pathlib import Path
from tempfile import gettempdir

from pronunciation_dictionary import (DeserializationOptions, MultiprocessingOptions,
                                      SerializationOptions)

from pronunciation_dictionary_utils import map_symbols
from pronunciation_dictionary_utils_cli.argparse_helper import (ConvertToOrderedSetAction,
                                                                add_io_group, add_mp_group,
                                                                get_optional, parse_existing_file,
                                                                parse_non_empty_or_whitespace,
                                                                parse_path)
from pronunciation_dictionary_utils_cli.globals import DEFAULT_PUNCTUATION
from pronunciation_dictionary_utils_cli.io import try_load_dict, try_save_dict

DEFAULT_EMPTY_WEIGHT = 1


def get_pronunciations_map_symbols_parser(parser: ArgumentParser):
  default_removed_out = Path(gettempdir()) / "removed-words.txt"
  parser.description = "Map symbols in pronunciations."
  parser.add_argument("dictionary", metavar='dictionary',
                      type=parse_existing_file, help="dictionary file")
  parser.add_argument("from_symbols", type=str, metavar='FROM-SYMBOL', nargs='+',
                      help="map these symbols from the pronunciations to MAP_SYMBOL", action=ConvertToOrderedSetAction, default=DEFAULT_PUNCTUATION)
  parser.add_argument("to_symbol", type=parse_non_empty_or_whitespace,
                      metavar="TO-SYMBOL", help="this symbol will be taken")
  parser.add_argument("-pm", "--partial-mapping", action="store_true",
                      help="map symbols inside a symbol; useful when mapping the same vowel having different tones or stress within one operation")
  add_io_group(parser)
  add_mp_group(parser)
  return map_symbols_in_pronunciations_ns


def map_symbols_in_pronunciations_ns(ns: Namespace, logger: Logger, flogger: Logger) -> bool:
  lp_options = DeserializationOptions(
      ns.consider_comments, ns.consider_numbers, ns.consider_pronunciation_comments, ns.consider_weights)
  mp_options = MultiprocessingOptions(ns.n_jobs, ns.maxtasksperchild, ns.chunksize)

  s_options = SerializationOptions(ns.parts_sep, ns.consider_numbers, ns.consider_weights)

  dictionary_instance = try_load_dict(ns.dictionary, ns.encoding, lp_options, mp_options, logger)
  if dictionary_instance is None:
    return False

  changed_counter = map_symbols(
    dictionary_instance, ns.from_symbols, ns.to_symbol, ns.partial_mapping, mp_options)

  if changed_counter == 0:
    logger.info("Didn't changed anything.")
    return True

  logger.info(f"Changed pronunciations of {changed_counter} word(s).")

  success = try_save_dict(dictionary_instance, ns.dictionary, ns.encoding, s_options, logger)
  if not success:
    return False

  logger.info(f"Written dictionary to: \"{ns.dictionary.absolute()}\"")

  return True