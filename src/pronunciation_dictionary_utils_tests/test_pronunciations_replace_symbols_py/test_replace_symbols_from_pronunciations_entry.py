import re
from collections import OrderedDict

from pronunciation_dictionary_utils.pronunciations_replace_pronunciation import \
  replace_symbols_from_pronunciations_entry


def test_component():
  pronunciations = OrderedDict((
    (("ˌə", "r", "r"), 6),
    (("ˌə", "ˈɔ", "r"), 7),
    (("ˌə", "ʊ", "r"), 8),
    (("ˌə", "ʊr"), 9),
  ))

  pattern = re.compile(r"( |ˈ|ˌ)(ə|ʌ|ɔ|ɪ|ɛ|ʊ) r")
  result = replace_symbols_from_pronunciations_entry(pronunciations, pattern, r"\1\2r")

  assert result == OrderedDict((
    (('ˌər', 'r'), 6),
    (('ˌə', 'ˈɔr'), 7),
    (('ˌə', 'ʊr'), 17),
  ))


def test_empty():
  pronunciations = OrderedDict((
    (("ˌə", "r", "r"), 6),
    (("ˌə", "ʊr"), 9),
  ))

  pattern = re.compile(r".*")
  result = replace_symbols_from_pronunciations_entry(pronunciations, pattern, r"")

  assert result == OrderedDict()


def test_whitespace():
  pronunciations = OrderedDict((
    (("ˌə", "r", "r"), 6),
    (("ˌə", "ʊr"), 9),
  ))

  pattern = re.compile(r".*")
  result = replace_symbols_from_pronunciations_entry(pronunciations, pattern, r" ")

  assert result == OrderedDict()
