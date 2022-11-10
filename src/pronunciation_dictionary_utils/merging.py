from typing import Optional

from ordered_set import OrderedSet
from pronunciation_dictionary import PronunciationDict

from pronunciation_dictionary_utils.common import merge_pronunciations
from pronunciation_dictionary_utils.validation import validate_dictionary


def __validate_mode(mode: str) -> Optional[str]:
  if mode not in ["add", "replace", "extend"]:
    return "Invalid value!"
  return None


def merge_dictionaries(dictionary: PronunciationDict, other_dictionary: PronunciationDict, mode: str) -> bool:
  if msg := validate_dictionary(dictionary):
    raise ValueError(f"Parameter 'dictionary': {msg}")
  if msg := validate_dictionary(other_dictionary):
    raise ValueError(f"Parameter 'other_dictionary': {msg}")
  if msg := __validate_mode(mode):
    raise ValueError(f"Parameter 'mode': {msg}")

  changed_anything = False
  if mode == "add":
    changed_anything = dictionary_add_new(dictionary, other_dictionary)
  elif mode == "replace":
    changed_anything = dictionary_replace(dictionary, other_dictionary)
  elif mode == "extend":
    changed_anything = dictionary_extend(dictionary, other_dictionary)
  else:
    assert False
  return changed_anything


def dictionary_replace(dictionary1: PronunciationDict, dictionary2: PronunciationDict) -> bool:
  changed_anything = False
  for key, value in dictionary2.items():
    if key not in dictionary1:
      changed_anything = True
      dictionary1[key] = value
    else:
      if dictionary1[key] != value:
        dictionary1[key] = value
        changed_anything = True
  return changed_anything


def dictionary_add_new(dictionary1: PronunciationDict, dictionary2: PronunciationDict) -> bool:
  new_keys = OrderedSet(dictionary2.keys()).difference(dictionary1.keys())
  for key in new_keys:
    assert key not in dictionary1
    dictionary1[key] = dictionary2[key]
  changed_anything = len(new_keys) > 0
  return changed_anything


def dictionary_extend(dictionary1: PronunciationDict, dictionary2: PronunciationDict) -> bool:
  keys = OrderedSet(dictionary2.keys())
  same_keys = keys.intersection(dictionary1.keys())
  new_keys = keys.difference(dictionary1.keys())

  changed_anything = False
  for key in same_keys:
    assert key in dictionary1
    changed_anything |= merge_pronunciations(dictionary1[key], dictionary2[key])

  for key in new_keys:
    assert key not in dictionary1
    dictionary1[key] = dictionary2[key]
  changed_anything |= len(new_keys) > 0
  return changed_anything
