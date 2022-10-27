from argparse import ArgumentParser, Namespace
from logging import Logger
from pathlib import Path

from pronunciation_dictionary import (DeserializationOptions, MultiprocessingOptions,
                                      SerializationOptions)

from pronunciation_dictionary_utils import merge_dictionaries
from pronunciation_dictionary_utils_cli.argparse_helper import (ConvertToOrderedSetAction,
                                                                add_io_group, add_mp_group,
                                                                get_optional, parse_existing_file,
                                                                parse_float_0_to_1, parse_path)
from pronunciation_dictionary_utils_cli.io import try_load_dict, try_save_dict


def get_merging_parser(parser: ArgumentParser):
  parser.description = "Merge multiple dictionaries into one."
  parser.add_argument("dictionary", metavar='DICTIONARY',
                      type=parse_existing_file, help="dictionary file")
  parser.add_argument("dictionaries", metavar='MERGE-DICTIONARY', type=parse_existing_file, nargs="+",
                      help="dictionary files that should be merged to DICTIONARY", action=ConvertToOrderedSetAction)
  parser.add_argument("--duplicate-handling", type=str, metavar="MODE",
                      choices=["add", "extend", "replace"], help="sets how existing pronunciations should be handled: add = add missing pronunciations; extend = add missing pronunciations and extend existing ones; replace: add missing pronunciations and replace existing ones.", default="extend")
  parser.add_argument("--ratio", type=get_optional(parse_float_0_to_1), metavar="RATIO",
                      help="merge pronunciations weights with these ratio, i.e., existing weights * ratio + weights to merge * (1-ratio); only relevant on 'extend'", default=0.5)
  add_io_group(parser)
  add_mp_group(parser)
  return merge_dictionary_files_ns


def merge_dictionary_files_ns(ns: Namespace, logger: Logger, flogger: Logger) -> bool:
  assert len(ns.dictionaries) > 0

  if ns.duplicate_handling == "extend" and ns.ratio is None:
    logger.error("Parameter 'ratio' is required on extending!")
    return False

  lp_options = DeserializationOptions(
      ns.consider_comments, ns.consider_numbers, ns.consider_pronunciation_comments, ns.consider_weights)
  mp_options = MultiprocessingOptions(ns.n_jobs, ns.maxtasksperchild, ns.chunksize)

  s_options = SerializationOptions(ns.parts_sep, ns.consider_numbers, ns.consider_weights)

  resulting_dictionary = try_load_dict(ns.dictionary, ns.encoding, lp_options, mp_options, logger)
  if resulting_dictionary is None:
    return False

  changed_anything = False
  for dictionary in ns.dictionaries:
    dictionary_instance = try_load_dict(dictionary, ns.encoding, lp_options, mp_options, logger)
    if dictionary_instance is None:
      return False
    changed_anything |= merge_dictionaries(
      resulting_dictionary, dictionary_instance, ns.duplicate_handling, ns.ratio)

  if not changed_anything:
    logger.info("Didn't changed anything.")
    return True

  output_path: Path = ns.dictionaries[0]
  success = try_save_dict(resulting_dictionary, output_path,
                          ns.encoding, s_options, logger)
  if not success:
    return False

  logger.info(f"Written dictionary to: \"{output_path.absolute()}\".")
  return True
