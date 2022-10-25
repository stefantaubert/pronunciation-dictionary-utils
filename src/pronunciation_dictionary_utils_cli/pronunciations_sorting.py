from argparse import ArgumentParser, Namespace
from logging import Logger

from pronunciation_dictionary import (DeserializationOptions, MultiprocessingOptions,
                                      SerializationOptions)

from pronunciation_dictionary_utils import sort_pronunciations
from pronunciation_dictionary_utils_cli.argparse_helper import (add_io_group, add_mp_group,
                                                                parse_existing_file)
from pronunciation_dictionary_utils_cli.io import try_load_dict, try_save_dict


def get_pronunciations_sorting_parser(parser: ArgumentParser):
  parser.description = "Sort pronunciations in dictionary first after weight descending and then ascending after pronunciation."
  parser.add_argument("dictionary", metavar='DICTIONARY',
                      type=parse_existing_file, help="dictionary file")
  parser.add_argument("-d", "--descending", action="store_true",
                      help="reverse sorting, i.e., ascending after weight and then descending after pronunciation")
  parser.add_argument("-iw", "--ignore-weight", action="store_true",
                      help="ignore weights in sorting")
  add_io_group(parser)
  add_mp_group(parser)
  return sort_pronunciations_ns


def sort_pronunciations_ns(ns: Namespace, logger: Logger, flogger: Logger) -> bool:
  lp_options = DeserializationOptions(
      ns.consider_comments, ns.consider_numbers, ns.consider_pronunciation_comments, ns.consider_weights)

  mp_options = MultiprocessingOptions(ns.n_jobs, ns.maxtasksperchild, ns.chunksize)
  s_options = SerializationOptions(ns.parts_sep, ns.consider_numbers, ns.consider_weights)

  dictionary_instance = try_load_dict(ns.dictionary, ns.encoding, lp_options, mp_options, logger)
  if dictionary_instance is None:
    return False

  changed_counter = sort_pronunciations(
    dictionary_instance, ns.descending, ns.ignore_weight, mp_options)

  changed_anything = changed_counter > 0

  if not changed_anything:
    logger.info("Didn't changed anything.")
    return True

  success = try_save_dict(dictionary_instance, ns.dictionary, ns.encoding, s_options, logger)
  if not success:
    return False

  logger.info(f"Written dictionary to: \"{ns.dictionary.absolute()}\".")

  return True
