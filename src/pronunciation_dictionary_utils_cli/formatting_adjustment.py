from argparse import ArgumentParser, Namespace
from logging import Logger

from pronunciation_dictionary import (DeserializationOptions, MultiprocessingOptions,
                                      SerializationOptions)

from pronunciation_dictionary_utils_cli.argparse_helper import (ConvertToOrderedSetAction,
                                                                add_deserialization_group,
                                                                add_mp_group,
                                                                add_serialization_group,
                                                                parse_existing_file)
from pronunciation_dictionary_utils_cli.io import try_load_dict, try_save_dict


def get_formatting_parser(parser: ArgumentParser):
  parser.description = ""

  parser.add_argument("dictionaries", metavar='DICTIONARY', type=parse_existing_file, nargs="+",
                      help="dictionary files", action=ConvertToOrderedSetAction)
  add_deserialization_group(parser)
  add_serialization_group(parser)
  add_mp_group(parser)

  return adjust_formatting


def adjust_formatting(ns: Namespace, logger: Logger, flogger: Logger):
  lp_options = DeserializationOptions(
      ns.consider_comments, ns.consider_numbers, ns.consider_pronunciation_comments, ns.consider_weights)
  s_options = SerializationOptions(ns.parts_sep, ns.include_numbers, ns.include_weights)

  mp_options = MultiprocessingOptions(ns.n_jobs, ns.maxtasksperchild, ns.chunksize)

  for dictionary in ns.dictionaries:
    dictionary_instance = try_load_dict(
      dictionary, ns.deserialization_encoding, lp_options, mp_options, logger)
    if dictionary_instance is None:
      return False

    success = try_save_dict(dictionary_instance, dictionary,
                            ns.serialization_encoding, s_options, logger)
    if not success:
      return False

    logger.info(f"Written dictionary to: \"{dictionary.absolute()}\".")
  return True