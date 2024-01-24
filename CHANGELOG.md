# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.0.5] - 2024-01-24

### Added

- `replace_symbols_in_pronunciations`
- `map_symbols_dict`
- Support for Python 3.12

### Changed

- Logging method

## [0.0.4] - 2023-06-02

### Added

- Support for partial mapping in `map-symbols-in-pronunciations-json`
- Added testing units for `map-symbols-in-pronunciations-json`

### Bugfixes

- Support for Python 3.11 was not correctly defined
- Adjusted return value for `map_symbols` in `pronunciations_map_symbols`
- Corrected log messages

## [0.0.3] - 2023-01-12

### Added

- Added `sort-words` to support sorting of words
- Added `sort-pronunciations` to support sorting of pronunciations
- Added `normalize-weights` to support normalization of pronunciation weights
- Added `map-symbols-in-pronunciations-json` to map phonemes/symbols in pronunciations to phonemes/symbols specified in json file
- Added `--mode` to symbol removal in pronunciations
- Added returning of an exit code
- Included tests in package distribution

### Changed

- Symbols are now positional in `remove-symbols-from-words`, `remove-symbols-from-pronunciations` and `remove-symbols-from-vocabulary`
- Notify if something changed after merging dictionary
- Update CLI
- Update pronunciation-dictionary version to 0.0.5

### Removed

- Removed parameter 'ratio' for merging pronunciation weights

## [0.0.2] - 2022-12-02

### Added

- Support sorting of words
- Support sorting of pronunciations
- Support normalization of pronunciation weights
- Added `mode` to symbol removal in pronunciations

### Changed

- Symbols are now positional in symbol removal
- Notify if something changed after merging dictionary
- Update CLI
- Update `pronunciation-dictionary` version to `0.0.5`

### Removed

- Removed parameter `ratio` for merging pronunciation weights

### Fixed

- Several bugfixes

## [0.0.1] - 2022-09-30

- Initial release

[unreleased]: https://github.com/stefantaubert/pronunciation-dictionary-utils/compare/v0.0.5...HEAD
[0.0.5]: https://github.com/stefantaubert/pronunciation-dictionary-utils/compare/v0.0.4...v0.0.5
[0.0.4]: https://github.com/stefantaubert/pronunciation-dictionary-utils/compare/v0.0.3...v0.0.4
[0.0.3]: https://github.com/stefantaubert/pronunciation-dictionary-utils/compare/v0.0.2...v0.0.3
[0.0.2]: https://github.com/stefantaubert/pronunciation-dictionary-utils/compare/v0.0.1...v0.0.2
[0.0.1]: https://github.com/stefantaubert/pronunciation-dictionary-utils/releases/tag/v0.0.1
