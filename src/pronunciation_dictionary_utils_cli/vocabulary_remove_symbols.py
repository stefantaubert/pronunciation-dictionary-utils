from argparse import ArgumentParser, Namespace
from logging import Logger
from pathlib import Path
from tempfile import gettempdir
from typing import cast

from ordered_set import OrderedSet
from pronunciation_dictionary import MultiprocessingOptions

from pronunciation_dictionary_utils.vocabulary_remove_symbols import remove_symbols_from_vocabulary
from pronunciation_dictionary_utils_cli.argparse_helper import (ConvertToOrderedSetAction,
                                                                add_encoding_argument, add_mp_group,
                                                                get_optional, parse_existing_file,
                                                                parse_path)


def get_vocabulary_remove_symbols_parser(parser: ArgumentParser):
  default_removed_out = Path(gettempdir()) / "removed-words.txt"
  parser.description = "Remove symbols from words. If all symbols of a word will be removed, the word will be taken out of the vocabulary."
  parser.add_argument("vocabulary", metavar='VOCABULARY',
                      type=parse_existing_file, help="vocabulary file")
  parser.add_argument("symbols", type=str, metavar='SYMBOL', nargs='+',
                      help="remove these symbols from the words", action=ConvertToOrderedSetAction)
  parser.add_argument("-m", "--mode", type=str, choices=["all", "start", "end", "both"], metavar="MODE",
                      help="mode to remove the symbols: all = on all locations; start = only from start; end = only from end; both = start + end", default="both")
  # parser.add_argument("--remove-empty", action="store_true",
  #                     help="if a pronunciation will be empty after removal, remove the corresponding word from the dictionary")
  parser.add_argument("-ro", "--removed-out", metavar="PATH", type=get_optional(parse_path),
                      help="write removed words to this file", default=default_removed_out)
  add_encoding_argument(parser, "-e", "--encoding",
                        "encoding used for serialization/deserialization")
  add_mp_group(parser)
  return remove_symbols_from_words_ns


def remove_symbols_from_words_ns(ns: Namespace, logger: Logger, flogger: Logger) -> bool:
  symbols_str = ''.join(ns.symbols)
  try:
    vocabulary_content = cast(Path, ns.vocabulary).read_text(ns.encoding)
  except Exception as ex:
    logger.debug(ex)
    logger.error("Vocabulary couldn't be read.")
    return False

  vocabulary = OrderedSet(vocabulary_content.splitlines())
  logger.info(f"Parsed vocabulary containing {len(vocabulary)} words.")

  mp_options = MultiprocessingOptions(ns.n_jobs, ns.maxtasksperchild, ns.chunksize)

  removed_words_entirely, changed_words = remove_symbols_from_vocabulary(
    vocabulary, symbols_str, ns.mode, mp_options)

  if len(changed_words) == 0:
    logger.info("Didn't changed anything.")
    return True

  logger.info(f"Changed {len(changed_words)} word(s).")

  new_vocabulary_content = "\n".join(vocabulary)
  try:
    ns.vocabulary.write_text(new_vocabulary_content, ns.encoding)
  except Exception as ex:
    logger.debug(ex)
    logger.error("Vocabulary output couldn't be created!")
    return False
  logger.info(f"Written vocabulary to: \"{ns.vocabulary.absolute()}\".")

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
