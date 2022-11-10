from argparse import ArgumentParser, Namespace
from logging import Logger

from pronunciation_dictionary import (DeserializationOptions, MultiprocessingOptions,
                                      SerializationOptions)

from pronunciation_dictionary_utils import merge_dictionaries
from pronunciation_dictionary_utils_cli.argparse_helper import (ConvertToOrderedSetAction,
                                                                add_io_group, add_mp_group,
                                                                parse_existing_file)
from pronunciation_dictionary_utils_cli.io import try_load_dict, try_save_dict


def get_merging_parser(parser: ArgumentParser):
  parser.description = "Merge multiple dictionaries into one."
  parser.add_argument("dictionary", metavar='DICTIONARY',
                      type=parse_existing_file, help="dictionary file")
  parser.add_argument("dictionaries", metavar='MERGE-DICTIONARY', type=parse_existing_file, nargs="+",
                      help="dictionary files that should be merged to DICTIONARY", action=ConvertToOrderedSetAction)
  parser.add_argument("--duplicate-handling", type=str, metavar="MODE",
                      choices=["add", "extend", "replace"], help="sets how existing pronunciations should be handled: add = add missing pronunciations; extend = add missing pronunciations and extend existing ones; replace: add missing pronunciations and replace existing ones.", default="extend")
  add_io_group(parser)
  add_mp_group(parser)
  return merge_dictionary_files_ns


def merge_dictionary_files_ns(ns: Namespace, logger: Logger, flogger: Logger) -> bool:
  assert len(ns.dictionaries) > 0

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
      resulting_dictionary, dictionary_instance, ns.duplicate_handling)

  if not changed_anything:
    logger.info("Didn't changed anything.")
    return True

  success = try_save_dict(resulting_dictionary, ns.dictionary,
                          ns.encoding, s_options, logger)
  if not success:
    return False

  logger.info(f"Written dictionary to: \"{ns.dictionary.absolute()}\".")
  return True
