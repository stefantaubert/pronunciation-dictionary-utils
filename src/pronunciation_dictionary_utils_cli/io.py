from logging import Logger
from pathlib import Path
from typing import Optional

from pronunciation_dictionary import (DeserializationOptions, MultiprocessingOptions,
                                      PronunciationDict, SerializationOptions, load_dict, save_dict)


def try_save_dict(pronunciation_dict: PronunciationDict, path: Path, encoding: str, options: SerializationOptions, logger: Logger) -> bool:
  try:
    save_dict(pronunciation_dict, path, encoding, options)
  except Exception as ex:
    logger.debug(ex)
    logger.error(f"Dictionary \"{path.absolute()}\" couldn't be written.")
    return False
  return True


def try_load_dict(path: Path, encoding: str, options: DeserializationOptions, mp_options: MultiprocessingOptions, logger: Logger) -> Optional[PronunciationDict]:
  try:
    result = load_dict(path, encoding, options, mp_options)
  except Exception as ex:
    logger.debug(ex)
    logger.error(f"Dictionary \"{path.absolute()}\" couldn't be read.")
    return None
  return result
