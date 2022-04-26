# pronunciation-dictionary-utils

[![PyPI](https://img.shields.io/pypi/v/pronunciation-dictionary-utils.svg)](https://pypi.python.org/pypi/pronunciation-dictionary-utils)
[![PyPI](https://img.shields.io/pypi/pyversions/pronunciation-dictionary-utils.svg)](https://pypi.python.org/pypi/pronunciation-dictionary-utils)
[![MIT](https://img.shields.io/github/license/stefantaubert/pronunciation-dictionary-utils.svg)](LICENSE)

Library and CLI to modify pronunciation dictionaries (any language).

## Features

- Merge multiple pronunciation dictionaries
- Extract subset of pronunciation dictionary
- Remove characters from vocabulary
- Remove phonemes from pronunciations
- Select single pronunciation per word
- Change word casing
- Change file formatting
- Export vocabulary
- Export phoneme set

## Roadmap

- Adding tests
- Implementation of printing of statistics
- Implementation of phoneme mapping, e.g., mapping ARPAbet to IPA

## Installation

```sh
pip install pronunciation-dictionary-utils --user
```

## Usage

```sh
dict-cli
```

## Citation

If you want to cite this repo, you can use this BibTeX-entry:

```bibtex
@misc{tspdu22,
  author = {Taubert, Stefan},
  title = {pronunciation-dictionary-utils},
  year = {2022},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/stefantaubert/pronunciation-dictionary-utils}}
}
```
