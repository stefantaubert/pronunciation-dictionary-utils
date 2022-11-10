from argparse import ArgumentParser, Namespace
from logging import Logger

from pronunciation_dictionary import (DeserializationOptions, MultiprocessingOptions,
                                      SerializationOptions)

from pronunciation_dictionary_utils import change_word_casing
from pronunciation_dictionary_utils_cli.argparse_helper import (add_io_group, add_mp_group,
                                                                parse_existing_file)
from pronunciation_dictionary_utils_cli.io import try_load_dict, try_save_dict


def get_words_casing_adjustment_parser(parser: ArgumentParser):
  parser.description = "Adjust casing of words in dictionary."
  parser.add_argument("dictionary", metavar='DICTIONARY',
                      type=parse_existing_file, help="dictionary file")
  parser.add_argument("mode", metavar="MODE", type=str, choices=["lower", "upper"],
                      help="mode to change the casing")
  add_io_group(parser)
  add_mp_group(parser)
  return change_casing_ns


def change_casing_ns(ns: Namespace, logger: Logger, flogger: Logger) -> bool:
  lp_options = DeserializationOptions(
      ns.consider_comments, ns.consider_numbers, ns.consider_pronunciation_comments, ns.consider_weights)
  mp_options = MultiprocessingOptions(ns.n_jobs, ns.maxtasksperchild, ns.chunksize)

  s_options = SerializationOptions(ns.parts_sep, ns.consider_numbers, ns.consider_weights)

  dictionary_instance = try_load_dict(ns.dictionary, ns.encoding, lp_options, mp_options, logger)
  if dictionary_instance is None:
    return False

  removed_words, created_words = change_word_casing(dictionary_instance, ns.mode, mp_options)

  if len(removed_words) == 0:
    logger.info("Didn't changed anything.")
    return True

  logger.info(f"Replaced {len(removed_words)} with {len(created_words)} word spelling(s).")

  success = try_save_dict(dictionary_instance, ns.dictionary, ns.encoding, s_options, logger)
  if not success:
    return False

  logger.info(f"Written dictionary to: \"{ns.dictionary.absolute()}\".")
  return True
