from collections import OrderedDict

from pronunciation_dictionary import PronunciationDict, Pronunciations

from pronunciation_dictionary_utils.validation import validate_pronunciations


def merge_pronunciations(pronunciations1: Pronunciations, pronunciations2: Pronunciations) -> bool:
  if msg := validate_pronunciations(pronunciations1):
    raise ValueError(f"Parameter 'pronunciations1': {msg}")
  if msg := validate_pronunciations(pronunciations2):
    raise ValueError(f"Parameter 'pronunciations2': {msg}")

  if pronunciations1 == pronunciations2:
    return False

  changed_anything = False

  for pronunciation2, weight2 in pronunciations2.items():
    if pronunciation2 in pronunciations1:
      weight1 = pronunciations1[pronunciation2]
      new_weight = weight1 + weight2
      if weight1 != new_weight:
        pronunciations1[pronunciation2] = new_weight
        changed_anything = True
    else:
      pronunciations1[pronunciation2] = weight2
      changed_anything = True
  return changed_anything


# def merge_rel_weights(pronunciations1: Pronunciations, pronunciations2: Pronunciations, weights_ratio: float) -> bool:
#   if msg := validate_pronunciations(pronunciations1):
#     raise ValueError(f"Parameter 'pronunciations1': {msg}")
#   if msg := validate_pronunciations(pronunciations2):
#     raise ValueError(f"Parameter 'pronunciations2': {msg}")
#   if msg := validate_ratio(weights_ratio):
#     raise ValueError(f"Parameter 'weights_ratio': {msg}")

#   if pronunciations1 == pronunciations2:
#     return False

#   changed_anything = False
#   changed_anything |= convert_weights_to_probabilities(pronunciations1)
#   changed_anything |= convert_weights_to_probabilities(pronunciations2)

#   if weights_ratio != 1:
#     for pronunciation1, weight1 in pronunciations1.items():
#       if pronunciation1 not in pronunciations2:
#         new_weight = weight1 * weights_ratio
#         pronunciations1[pronunciation1] = new_weight
#         changed_anything = True

#   for pronunciation2, weight2 in pronunciations2.items():
#     new_weight2 = weight2 * (1 - weights_ratio)
#     if pronunciation2 in pronunciations1:
#       weight1 = pronunciations1[pronunciation2]
#       new_weight1 = weight1 * weights_ratio
#       new_weight = new_weight1 + new_weight2
#       if weight1 != new_weight:
#         pronunciations1[pronunciation2] = new_weight
#         changed_anything = True
#     else:
#       new_weight = new_weight2
#       pronunciations1[pronunciation2] = new_weight
#       changed_anything = True
#   return changed_anything


def convert_weights_to_probabilities_dict(dictionary: PronunciationDict) -> None:
  for pronunciations in dictionary.values():
    convert_weights_to_probabilities(pronunciations)


def convert_weights_to_probabilities(pronunciations: Pronunciations) -> bool:
  assert isinstance(pronunciations, OrderedDict)
  changed_anything = False
  sum_probs = sum(pronunciations.values())
  for pronunciation, prob in pronunciations.items():
    normed_prob = prob / sum_probs
    if prob != normed_prob:
      pronunciations[pronunciation] = normed_prob
      changed_anything = True
  return changed_anything


# def merge_equal_weight_sum(pronunciations1: Pronunciations, pronunciations2: Pronunciations, ratio: float) -> None:
#   assert sum(pronunciations1.values()) * ratio == sum(pronunciations2.values()) * (1 - ratio)
#   for pronunciation2, weight2 in pronunciations2.items():
#     if pronunciation2 in pronunciations1:
#       pronunciations1[pronunciation2] += weight2
#     else:
#       pronunciations1[pronunciations2] = weight2
