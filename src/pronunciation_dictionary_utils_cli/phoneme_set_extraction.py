from argparse import ArgumentParser, Namespace
from logging import Logger
from pathlib import Path
from tempfile import gettempdir
from typing import cast

from ordered_set import OrderedSet
from pronunciation_dictionary import DeserializationOptions, MultiprocessingOptions, get_phoneme_set

from pronunciation_dictionary_utils_cli.argparse_helper import (ConvertToOrderedSetAction,
                                                                add_deserialization_group,
                                                                add_encoding_argument, add_mp_group,
                                                                parse_existing_file, parse_path)
from pronunciation_dictionary_utils_cli.io import try_load_dict


def get_phoneme_set_extraction_parser(parser: ArgumentParser):
  default_removed_out = Path(gettempdir()) / "removed-words.txt"
  parser.description = "Remove symbols from pronunciations."
  parser.add_argument("dictionaries", metavar='DICTIONARY', type=parse_existing_file, nargs="+",
                      help="dictionary files", action=ConvertToOrderedSetAction)
  parser.add_argument("output", metavar="OUTPUT", type=parse_path,
                      help="output phoneme set to this file", default=default_removed_out)
  add_encoding_argument(parser, "-e", "--output-encoding", "encoding of the vocabulary file")
  parser.add_argument("-u", "--unsorted", action="store_true",
                      help="do not sort phonemes in output")
  add_deserialization_group(parser)
  add_mp_group(parser)
  return get_phoneme_set_from_ns


def get_phoneme_set_from_ns(ns: Namespace, logger: Logger, flogger: Logger) -> bool:
  assert len(ns.dictionaries) > 0

  lp_options = DeserializationOptions(
      ns.consider_comments, ns.consider_numbers, ns.consider_pronunciation_comments, ns.consider_weights)
  mp_options = MultiprocessingOptions(ns.n_jobs, ns.maxtasksperchild, ns.chunksize)

  total_vocabulary = OrderedSet()
  for dictionary_path in ns.dictionaries:
    dictionary_instance = try_load_dict(
      dictionary_path, ns.deserialization_encoding, lp_options, mp_options, logger)
    if dictionary_instance is None:
      return False

    vocabulary = get_phoneme_set(dictionary_instance)
    total_vocabulary.update(vocabulary)

  sort = not ns.unsorted
  result = total_vocabulary
  if sort:
    result = sorted(result)
  content = "\n".join(result)

  try:
    ns.output.parent.mkdir(parents=True, exist_ok=True)
    cast(Path, ns.output).write_text(content, ns.output_encoding)
  except Exception as ex:
    logger.debug(ex)
    logger.error("Phoneme set couldn't be saved!")
    return False

  logger.info(
    f"Written phoneme set containing {len(result)} phonemes to: \"{ns.output.absolute()}\".")
  return True
