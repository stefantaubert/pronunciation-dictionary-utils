from argparse import ArgumentParser, Namespace
from logging import Logger

from pronunciation_dictionary import (DeserializationOptions, MultiprocessingOptions,
                                      SerializationOptions)

from pronunciation_dictionary_utils import select_single_pronunciation
from pronunciation_dictionary_utils_cli.argparse_helper import (add_io_group, add_mp_group,
                                                                get_optional, parse_existing_file,
                                                                parse_non_negative_integer)
from pronunciation_dictionary_utils_cli.io import try_load_dict, try_save_dict


def get_single_pronunciation_selection_parser(parser: ArgumentParser):
  parser.description = "Select a single pronunciation for each word."
  parser.add_argument("dictionary", metavar='DICTIONARY',
                      type=parse_existing_file, help="dictionary file")
  parser.add_argument("-m", "--mode", type=str, choices=["first", "last", "highest-weight", "lowest-weight", "shortest", "longest", "random", "weighted"], metavar="MODE",
                      help="mode to select the target pronunciation: first -> the first pronunciation; last -> the last pronunciation; highest-weight -> the first pronunciation with the highest weight; lowest-weight -> the first pronunciation with the lowest-weight; shortest -> the pronunciation with the least amount of phonemes; longest -> the pronunciation with the most amount of phonemes; random -> a random pronunciation & weighted -> same as random but higher weights result in higher probabilities", default="first")
  parser.add_argument("--seed", type=get_optional(parse_non_negative_integer),
                      metavar="SEED", help="custom seed if mode is random or weight", default=None)
  add_io_group(parser)
  add_mp_group(parser)
  return remove_multiple_pronunciations_ns


def remove_multiple_pronunciations_ns(ns: Namespace, logger: Logger, flogger: Logger) -> bool:
  lp_options = DeserializationOptions(
    ns.consider_comments, ns.consider_numbers, ns.consider_pronunciation_comments, ns.consider_weights)
  mp_options = MultiprocessingOptions(ns.n_jobs, ns.maxtasksperchild, ns.chunksize)

  s_options = SerializationOptions(ns.parts_sep, ns.consider_numbers, ns.consider_weights)

  dictionary_instance = try_load_dict(ns.dictionary, ns.encoding, lp_options, mp_options, logger)
  if dictionary_instance is None:
    return False

  changed_counter = select_single_pronunciation(
    dictionary_instance, ns.mode, ns.seed, mp_options)

  if changed_counter == 0:
    logger.info("Didn't changed anything.")
    return True

  logger.info(f"Changed pronunciations of {changed_counter} word(s).")

  success = try_save_dict(dictionary_instance, ns.dictionary, ns.encoding, s_options, logger)
  if not success:
    return False

  logger.info(f"Written dictionary to: \"{ns.dictionary.absolute()}\".")
  return True
