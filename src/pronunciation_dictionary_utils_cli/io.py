from logging import Logger, getLogger
from pathlib import Path
from typing import Optional

from pronunciation_dictionary import (DeserializationOptions, MultiprocessingOptions,
                                      PronunciationDict, SerializationOptions, load_dict, save_dict)

from pronunciation_dictionary_utils_cli.logging_configuration import get_file_logger


def try_save_dict(pronunciation_dict: PronunciationDict, path: Path, encoding: str, options: SerializationOptions, logger: Logger) -> bool:
  try:
    save_dict(pronunciation_dict, path, encoding, options)
  except Exception as ex:
    logger.debug(ex)
    logger.error(f"Dictionary \"{path.absolute()}\" couldn't be written.")
    return False
  return True


def try_load_dict(path: Path, encoding: str, options: DeserializationOptions, mp_options: MultiprocessingOptions, logger: Logger) -> Optional[PronunciationDict]:
  # Output logs to file
  pdict_logger = getLogger("pronunciation_dictionary.deserialization")
  pdict_logger.parent = get_file_logger()

  try:
    result = load_dict(path, encoding, options, mp_options)
  except Exception as ex:
    logger.debug(ex)
    logger.error(f"Dictionary \"{path.absolute()}\" couldn't be read.")
    return None
  return result
