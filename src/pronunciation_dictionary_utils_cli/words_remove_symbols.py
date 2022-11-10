from argparse import ArgumentParser, Namespace
from logging import Logger
from pathlib import Path
from tempfile import gettempdir

from pronunciation_dictionary import (DeserializationOptions, MultiprocessingOptions,
                                      SerializationOptions)

from pronunciation_dictionary_utils import remove_symbols_from_words
from pronunciation_dictionary_utils_cli.argparse_helper import (ConvertToOrderedSetAction,
                                                                add_io_group, add_mp_group,
                                                                get_optional, parse_existing_file,
                                                                parse_path)
from pronunciation_dictionary_utils_cli.io import try_load_dict, try_save_dict


def get_words_remove_symbols_parser(parser: ArgumentParser):
  # TODO make it possible to include weights in output if they were not in input
  default_removed_out = Path(gettempdir()) / "removed-words.txt"
  parser.description = "Remove symbols from words. If all symbols of a word will be removed, the word will be taken out of the dictionary."
  parser.add_argument("dictionary", metavar='DICTIONARY',
                      type=parse_existing_file, help="dictionary file")
  parser.add_argument("symbols", type=str, metavar='SYMBOL', nargs='+',
                      help="remove these symbols from the words", action=ConvertToOrderedSetAction)
  parser.add_argument("-m", "--mode", type=str, choices=["all", "start", "end", "both"], metavar="MODE",
                      help="mode to remove the symbols: all = on all locations; start = only from start; end = only from end; both = start + end", default="both")
  # parser.add_argument("--remove-empty", action="store_true",
  #                     help="if a pronunciation will be empty after removal, remove the corresponding word from the dictionary")
  parser.add_argument("-ro", "--removed-out", metavar="PATH", type=get_optional(parse_path),
                      help="write removed words to this file", default=default_removed_out)
  add_io_group(parser)
  add_mp_group(parser)
  return remove_symbols_from_words_ns


def remove_symbols_from_words_ns(ns: Namespace, logger: Logger, flogger: Logger) -> bool:
  symbols_str = ''.join(ns.symbols)

  lp_options = DeserializationOptions(
      ns.consider_comments, ns.consider_numbers, ns.consider_pronunciation_comments, ns.consider_weights)
  mp_options = MultiprocessingOptions(ns.n_jobs, ns.maxtasksperchild, ns.chunksize)

  s_options = SerializationOptions(ns.parts_sep, ns.consider_numbers, ns.consider_weights)

  dictionary_instance = try_load_dict(ns.dictionary, ns.encoding, lp_options, mp_options, logger)
  if dictionary_instance is None:
    return False

  removed_words_entirely, removed_words = remove_symbols_from_words(
    dictionary_instance, symbols_str, ns.mode, mp_options)

  if len(removed_words) == 0:
    logger.info("Didn't changed anything.")
    return True

  logger.info(f"Renamed {len(removed_words)} word(s).")

  success = try_save_dict(dictionary_instance, ns.dictionary, ns.encoding, s_options, logger)
  if not success:
    return False

  logger.info(f"Written dictionary to: \"{ns.dictionary.absolute()}\".")

  if len(removed_words_entirely) > 0:
    logger.warning(f"{len(removed_words_entirely)} words were removed entirely.")
    if ns.removed_out is not None:
      content = "\n".join(removed_words_entirely)
      ns.removed_out.parent.mkdir(parents=True, exist_ok=True)
      try:
        ns.removed_out.write_text(content, "UTF-8")
      except Exception as ex:
        logger.debug(ex)
        logger.error("Removed words output couldn't be created!")
        return False
      logger.info(f"Written removed words to: \"{ns.removed_out.absolute()}\".")
  else:
    logger.info("No words were removed.")
  return True
