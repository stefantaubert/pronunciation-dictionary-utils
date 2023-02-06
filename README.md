# pronunciation-dictionary-utils

[![PyPI](https://img.shields.io/pypi/v/pronunciation-dictionary-utils.svg)](https://pypi.python.org/pypi/pronunciation-dictionary-utils)
[![PyPI](https://img.shields.io/pypi/pyversions/pronunciation-dictionary-utils.svg)](https://pypi.python.org/pypi/pronunciation-dictionary-utils)
[![MIT](https://img.shields.io/github/license/stefantaubert/pronunciation-dictionary-utils.svg)](LICENSE)
[![PyPI](https://img.shields.io/github/commits-since/stefantaubert/pronunciation-dictionary-utils/latest/master.svg)](https://pypi.python.org/pypi/pronunciation-dictionary-utils)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.7529307.svg)](https://doi.org/10.5281/zenodo.7529307)

Library and CLI to modify pronunciation dictionaries (any language).

## Features

- `export-vocabulary`: export vocabulary from dictionaries
- `export-phonemes`: export phoneme set from dictionaries
- `merge`: merge dictionaries together
- `extract`: extract subset of dictionary vocabulary
- `map-symbols-in-pronunciations`: map phonemes/symbols in pronunciations to another phoneme/symbol, e.g., mapping ARPAbet to IPA
- `remove-symbols-from-vocabulary`: remove phonemes/symbols from vocabulary
- `remove-symbols-from-pronunciations`: remove phonemes/symbols from pronunciations
- `remove-symbols-from-words`: remove characters/symbols from words
- `change-formatting`: change formatting of dictionaries
- `select-single-pronunciation`: select single pronunciation
- `change-word-casing`: transform all words to upper- or lower-case
- `sort-words`: sort dictionary after words
- `sort-pronunciations`: sort dictionary pronunciations
- `normalize-weights`: normalize pronunciation weights for each word

## Roadmap

- Adding tests
- Implementation of printing of statistics
- Add change of pronunciation for a word via CLI

## Installation

```sh
pip install pronunciation-dictionary-utils --user
```

## Usage

```txt
usage: dict-cli [-h] [-v]
                {export-vocabulary,export-phonemes,merge,extract,map-symbols-in-pronunciations,map-symbols-in-pronunciations-json,remove-symbols-from-vocabulary,remove-symbols-from-pronunciations,remove-symbols-from-words,change-formatting,select-single-pronunciation,change-word-casing,sort-words,sort-pronunciations,normalize-weights}
                ...

This program provides methods to modify pronunciation dictionaries.

positional arguments:
  {export-vocabulary,export-phonemes,merge,extract,map-symbols-in-pronunciations,map-symbols-in-pronunciations-json,remove-symbols-from-vocabulary,remove-symbols-from-pronunciations,remove-symbols-from-words,change-formatting,select-single-pronunciation,change-word-casing,sort-words,sort-pronunciations,normalize-weights}
                                        description
    export-vocabulary                   export vocabulary from dictionaries
    export-phonemes                     export phoneme set from dictionaries
    merge                               merge dictionaries together
    extract                             extract subset of dictionary vocabulary
    map-symbols-in-pronunciations       map phonemes/symbols in pronunciations to another phoneme/symbol, e.g., mapping ARPAbet to IPA
    map-symbols-in-pronunciations-json  map phonemes/symbols in pronunciations to phoneme/symbol specified in file
    remove-symbols-from-vocabulary      remove phonemes/symbols from vocabulary
    remove-symbols-from-pronunciations  remove phonemes/symbols from pronunciations
    remove-symbols-from-words           remove characters/symbols from words
    change-formatting                   change formatting of dictionaries
    select-single-pronunciation         select single pronunciation
    change-word-casing                  transform all words to upper- or lower-case
    sort-words                          sort dictionary after words
    sort-pronunciations                 sort dictionary pronunciations
    normalize-weights                   normalize pronunciation weights for each word

optional arguments:
  -h, --help                            show this help message and exit
  -v, --version                         show program's version number and exit
```

### Example

```sh
# Download CMU dictionary
wget https://raw.githubusercontent.com/cmusphinx/cmudict/master/cmudict.dict \
  -O "/tmp/example.dict"

# Change formatting to remove numbers from words, comments and save as UTF-8
dict-cli change-formatting \
  "/tmp/example.dict" \
  --deserialization-encoding "ISO-8859-1" \
  --consider-numbers \
  --consider-pronunciation-comments \
  --serialization-encoding "UTF-8"

# Export phoneme set
dict-cli export-phonemes \
  "/tmp/example.dict" \
  "/tmp/example-phoneme-set.txt"
  
# Export vocabulary
dict-cli export-vocabulary \
  "/tmp/example.dict" \
  "/tmp/example-vocabulary.txt"

# Keep first pronunciation for each word and discard the rest
dict-cli select-single-pronunciation \
  "/tmp/example.dict" \
  --mode "first"

# Replace all "ER0" phonemes with "ER"
dict-cli map-symbols-in-pronunciations \
  "/tmp/example.dict" \
  "ER0" "ER"
```

## Contributing

### Development setup

```sh
# update
sudo apt update
# install Python 3.8, 3.9, 3.10 & 3.11 for ensuring that tests can be run
sudo apt install python3-pip \
  python3.8 python3.8-dev python3.8-distutils python3.8-venv \
  python3.9 python3.9-dev python3.9-distutils python3.9-venv \
  python3.10 python3.10-dev python3.10-distutils python3.10-venv \
  python3.11 python3.11-dev python3.11-distutils python3.11-venv
# install pipenv for creation of virtual environments
python3.8 -m pip install pipenv --user

# check out repo
git clone https://github.com/stefantaubert/pronunciation-dictionary-utils.git
cd pronunciation-dictionary-utils
# create virtual environment
python3.8 -m pipenv install --dev
```

## Running the tests

```sh
# first install the tool like in "Development setup"
# then, navigate into the directory of the repo (if not already done)
cd pronunciation-dictionary-utils
# activate environment
python3.8 -m pipenv shell
# run tests
tox
```

Final lines of test result output:

```log
py38: commands succeeded
py39: commands succeeded
py310: commands succeeded
py311: commands succeeded
congratulations :)
```

## Acknowledgments

Funded by the Deutsche Forschungsgemeinschaft (DFG, German Research Foundation) – Project-ID 416228727 – CRC 1410

## Citation

If you want to cite this repo, you can use this BibTeX-entry generated by GitHub (see *About => Cite this repository*).

## Changelog

- v0.0.4 (unreleased)
  - Bugfixes:
    - Support for Python 3.11 was not correctly defined
- v0.0.3 (2023-01-12)
  - Added:
    - Added `sort-words` to support sorting of words
    - Added `sort-pronunciations` to support sorting of pronunciations
    - Added `normalize-weights` to support normalization of pronunciation weights
    - Added `map-symbols-in-pronunciations-json` to map phonemes/symbols in pronunciations to phonemes/symbols specified in json file
    - Added `--mode` to symbol removal in pronunciations
    - Added returning of an exit code
    - Included tests in package distribution
  - Changed:
    - Symbols are now positional in `remove-symbols-from-words`, `remove-symbols-from-pronunciations` and `remove-symbols-from-vocabulary`
    - Notify if something changed after merging dictionary
    - Update CLI
    - Update pronunciation-dictionary version to 0.0.5
  - Removed:
    - Removed parameter 'ratio' for merging pronunciation weights
  - Bugfixes
- v0.0.2 (2022-12-02)
  - Support sorting of words
  - Support sorting of pronunciations
  - Support normalization of pronunciation weights
  - Added `mode` to symbol removal in pronunciations
  - Symbols are now positional in symbol removal
  - Removed parameter `ratio` for merging pronunciation weights
  - Notify if something changed after merging dictionary
  - Update CLI
  - Update `pronunciation-dictionary` version to `0.0.5`
  - Bugfixes
- v0.0.1 (2022-09-30)
  - Initial release
