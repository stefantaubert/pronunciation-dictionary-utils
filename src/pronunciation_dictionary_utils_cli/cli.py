import argparse
import logging
import platform
import sys
from argparse import ArgumentParser
from importlib.metadata import version
from logging import getLogger
from pathlib import Path
from pkgutil import iter_modules
from tempfile import gettempdir
from time import perf_counter
from typing import Callable, Generator, List, Tuple

from pronunciation_dictionary_utils_cli.argparse_helper import get_optional, parse_path
from pronunciation_dictionary_utils_cli.formatting_adjustment import get_formatting_parser
from pronunciation_dictionary_utils_cli.logging_configuration import (configure_root_logger,
                                                                      get_file_logger,
                                                                      init_and_return_loggers,
                                                                      try_init_file_logger)
from pronunciation_dictionary_utils_cli.merging import get_merging_parser
from pronunciation_dictionary_utils_cli.phoneme_set_extraction import \
  get_phoneme_set_extraction_parser
from pronunciation_dictionary_utils_cli.pronunciations_map_symbols import \
  get_pronunciations_map_symbols_parser
# nat: new functionality
from pronunciation_dictionary_utils_cli.pronunciations_map_symbols_json import \
  get_pronunciations_map_symbols_json_parser
from pronunciation_dictionary_utils_cli.pronunciations_remove_symbols import \
  get_pronunciations_remove_symbols_parser
from pronunciation_dictionary_utils_cli.pronunciations_sorting import \
  get_pronunciations_sorting_parser
from pronunciation_dictionary_utils_cli.single_pronunciation_selection import \
  get_single_pronunciation_selection_parser
from pronunciation_dictionary_utils_cli.subset_extraction import get_subset_extraction_parser
from pronunciation_dictionary_utils_cli.vocabulary_extraction import \
  get_vocabulary_extraction_parser
from pronunciation_dictionary_utils_cli.vocabulary_remove_symbols import \
  get_vocabulary_remove_symbols_parser
from pronunciation_dictionary_utils_cli.weights_normalization import \
  get_weights_normalization_parser
from pronunciation_dictionary_utils_cli.words_casing_adjustment import \
  get_words_casing_adjustment_parser
from pronunciation_dictionary_utils_cli.words_remove_symbols import get_words_remove_symbols_parser
from pronunciation_dictionary_utils_cli.words_sorting import get_words_sorting_parser

prog_name = "pronunciation-dictionary-utils"
__version__ = version(prog_name)

INVOKE_HANDLER_VAR = "invoke_handler"

CONSOLE_PRINT_GREEN = "\x1b[1;49;32m"
CONSOLE_PRINT_RED = "\x1b[1;49;31m"
CONSOLE_PRINT_RESET = "\x1b[0m"


def custom_formatter(prog):
  return argparse.ArgumentDefaultsHelpFormatter(prog, max_help_position=40)


def print_features():
  parsers = get_parsers()
  for command, description, method in parsers:
    print(f"- `{command}`: {description}")


def get_parsers() -> Generator[Tuple[str, str, Callable], None, None]:
  yield from (
    ("export-vocabulary", "export vocabulary from dictionaries",
     get_vocabulary_extraction_parser),
    ("export-phonemes", "export phoneme set from dictionaries",
     get_phoneme_set_extraction_parser),
    ("merge", "merge dictionaries together",
     get_merging_parser),
    ("extract", "extract subset of dictionary vocabulary",
     get_subset_extraction_parser),
    ("map-symbols-in-pronunciations", "map phonemes/symbols in pronunciations to another phoneme/symbol, e.g., mapping ARPAbet to IPA",
     get_pronunciations_map_symbols_parser),
    # nat: new functionality
    ("map-symbols-in-pronunciations-json", "map phonemes/symbols in pronunciations to phoneme/symbol specified in file",
     get_pronunciations_map_symbols_json_parser),
    ("remove-symbols-from-vocabulary", "remove phonemes/symbols from vocabulary",
     get_vocabulary_remove_symbols_parser),
    ("remove-symbols-from-pronunciations", "remove phonemes/symbols from pronunciations",
     get_pronunciations_remove_symbols_parser),
    ("remove-symbols-from-words", "remove characters/symbols from words",
     get_words_remove_symbols_parser),
    ("change-formatting", "change formatting of dictionaries",
     get_formatting_parser),
    ("select-single-pronunciation", "select single pronunciation",
     get_single_pronunciation_selection_parser),
    ("change-word-casing", "transform all words to upper- or lower-case",
     get_words_casing_adjustment_parser),
    ("sort-words", "sort dictionary after words", get_words_sorting_parser),
    ("sort-pronunciations", "sort dictionary pronunciations", get_pronunciations_sorting_parser),
    ("normalize-weights", "normalize pronunciation weights for each word", get_weights_normalization_parser),
  )


def _init_parser():
  main_parser = ArgumentParser(
    formatter_class=custom_formatter,
    description="This program provides methods to modify pronunciation dictionaries.",
  )
  main_parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)
  subparsers = main_parser.add_subparsers(help="description")
  default_log_path = Path(gettempdir()) / f"{prog_name}.log"

  for command, description, method in get_parsers():
    method_parser = subparsers.add_parser(
      command, help=description, formatter_class=custom_formatter)
    # init parser
    invoke_method = method(method_parser)
    method_parser.set_defaults(**{
      INVOKE_HANDLER_VAR: invoke_method,
    })
    logging_group = method_parser.add_argument_group("logging arguments")
    logging_group.add_argument("--log", type=get_optional(parse_path), metavar="FILE",
                               nargs="?", const=None, help="path to write the log", default=default_log_path)
    logging_group.add_argument("--debug", action="store_true",
                               help="include debugging information in log")

  return main_parser


def parse_args(args: List[str]) -> None:
  configure_root_logger()
  root_logger = getLogger()

  local_debugging = debug_file_exists()
  if local_debugging:
    root_logger.debug(f"Received arguments: {str(args)}")

  parser = _init_parser()

  try:
    ns = parser.parse_args(args)
  except SystemExit as error:
    error_code = error.args[0]
    # -v -> 0; invalid arg -> 2
    sys.exit(error_code)

  if local_debugging:
    root_logger.debug(f"Parsed arguments: {str(ns)}")

  if not hasattr(ns, INVOKE_HANDLER_VAR):
    parser.print_help()
    sys.exit(0)

  invoke_handler: Callable[..., bool] = getattr(ns, INVOKE_HANDLER_VAR)
  delattr(ns, INVOKE_HANDLER_VAR)
  log_to_file = ns.log is not None
  if log_to_file:
    log_level = logging.DEBUG if (local_debugging or ns.debug) else logging.INFO
    log_to_file_successful = try_init_file_logger(ns.log, log_level)
    if not log_to_file_successful:
      root_logger.warning("Logging to file is not possible!")

  flogger = get_file_logger()
  if not local_debugging:
    sys_version = sys.version.replace('\n', '')
    flogger.debug(f"CLI version: {__version__}")
    flogger.debug(f"Python version: {sys_version}")
    flogger.debug("Modules: %s", ', '.join(sorted(p.name for p in iter_modules())))

    my_system = platform.uname()
    flogger.debug(f"System: {my_system.system}")
    flogger.debug(f"Node Name: {my_system.node}")
    flogger.debug(f"Release: {my_system.release}")
    flogger.debug(f"Version: {my_system.version}")
    flogger.debug(f"Machine: {my_system.machine}")
    flogger.debug(f"Processor: {my_system.processor}")

  flogger.debug(f"Received arguments: {str(args)}")
  flogger.debug(f"Parsed arguments: {str(ns)}")

  start_time = perf_counter()
  cmd_flogger, cmd_logger = init_and_return_loggers(__name__)
  #success, changed_anything = invoke_handler(ns, cmd_logger, cmd_flogger)
  success = invoke_handler(ns, cmd_logger, cmd_flogger)
  if success:
    root_logger.info(f"{CONSOLE_PRINT_GREEN}Everything was successful!{CONSOLE_PRINT_RESET}")
    flogger.info("Everything was successful!")
  else:
    if log_to_file:
      root_logger.error("Not everything was successful! See log for details.")
    else:
      root_logger.error("Not everything was successful!")
    flogger.error("Not everything was successful!")

  duration_s = perf_counter() - start_time
  flogger.debug(f"Total duration (s): {duration_s}")

  if log_to_file:
    # path not encapsulated in "" because it is only console out
    root_logger.info(f"Written log to: {ns.log.absolute()}")

  if not success:
    sys.exit(1)
  sys.exit(0)

def run():
  arguments = sys.argv[1:]
  parse_args(arguments)


def debug_file_exists():
  return (Path(gettempdir()) / f"{prog_name}-debug").is_file()


def create_debug_file():
  if not debug_file_exists():
    (Path(gettempdir()) / f"{prog_name}-debug").write_text("", "UTF-8")


if __name__ == "__main__":
  # create_debug_file()
  # print_features()
  run()
