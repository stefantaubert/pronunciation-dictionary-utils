from argparse import ArgumentParser, Namespace
from logging import Logger

from pronunciation_dictionary import (DeserializationOptions, MultiprocessingOptions,
                                      SerializationOptions)

from pronunciation_dictionary_utils import sort_words
from pronunciation_dictionary_utils_cli.argparse_helper import (add_io_group, add_mp_group,
                                                                parse_existing_file)
from pronunciation_dictionary_utils_cli.io import try_load_dict, try_save_dict


def get_words_sorting_parser(parser: ArgumentParser):
  parser.description = "Sort dictionary after words."
  parser.add_argument("dictionary", metavar='DICTIONARY',
                      type=parse_existing_file, help="dictionary file")
  parser.add_argument("-d", "--descending", action="store_true", help="sort descending")
  parser.add_argument("-co", "--consider-case", action="store_true", help="consider casing")
  add_io_group(parser)
  add_mp_group(parser)
  return sort_words_ns


def sort_words_ns(ns: Namespace, logger: Logger, flogger: Logger) -> bool:
  lp_options = DeserializationOptions(
      ns.consider_comments, ns.consider_numbers, ns.consider_pronunciation_comments, ns.consider_weights)

  mp_options = MultiprocessingOptions(ns.n_jobs, ns.maxtasksperchild, ns.chunksize)
  s_options = SerializationOptions(ns.parts_sep, ns.consider_numbers, ns.consider_weights)

  dictionary_instance = try_load_dict(ns.dictionary, ns.encoding, lp_options, mp_options, logger)
  if dictionary_instance is None:
    return False

  new_dictionary = sort_words(dictionary_instance, ns.descending, ns.consider_case)

  changed_anything = new_dictionary != dictionary_instance

  if not changed_anything:
    logger.info("Didn't changed anything.")
    return True

  success = try_save_dict(new_dictionary, ns.dictionary, ns.encoding, s_options, logger)
  if not success:
    return False

  logger.info(f"Written dictionary to: \"{ns.dictionary.absolute()}\".")

  return True
