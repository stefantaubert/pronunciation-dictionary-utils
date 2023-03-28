try:
    from unittest.mock import patch # python 3.4+
except ImportError:
    from mock import patch

import pronunciation_dictionary_utils_cli.pronunciations_map_symbols_json as json_module
import sys

from logging import Logger
from argparse import ArgumentParser, Namespace

dict_path = 'src/pronunciation_dictionary_utils_tests/test_pronunciations_map_symbols_py/test_dict1.dict'
map_path = 'src/pronunciation_dictionary_utils_tests/test_pronunciations_map_symbols_py/test_map1.json'

# creates a dictionary file and a mapping file (assures correct content in dict_file when running the test multiple times)
def create_test_files():
    # dictionary file
    dict_file = open(dict_path, 'w')
    dict_file.write("test  AO AO2 AO3 AA1 EY2 .")
    dict_file.close()
    # mapping file
    map_file = open(map_path, 'w')
    map_file.write('''{
    "AO": "ɔ",
    "AO0": "ɔ",
    "AO1": "ˈɔ",
    "AO2": "ˌɔ",
    "EY": "eɪ",
    "EY0": "eɪ",
    "EY1": "ˈeɪ",
    "EY2": "ˌeɪ"
    }''')
    map_file.close()

# provides arguments for the command from the programme file, runs the command
def run_commands():
    test_args = ['dict-cli', 'map-symbols-in-pronunciations-json', dict_path, map_path]
    with patch('sys.argv', test_args):
        json_module.map_symbols_in_pronunciations_ns(Namespace, Logger, Logger)

# compares the expected and the actual output for equality
def compare_outputs():
    with open(dict_path, 'w') as outfile:
        outfile.seek(0)
        output_expected = "test  ɔ ˌɔ AO3 AA1 ˌeɪ .\n"
        output_is = outfile.read()
        # Are the expected and actual outputs not empty?
        assert output_expected is not None, f"Expected output is empty"
        assert output_is is not None, f"Read output is empty"
        # Are the expected and actual outputs strings?
        assert isinstance(output_expected, str), f"Expected output is not of type string"
        assert isinstance(output_is, str), f"Read output is not of type string"
        # Are the expected and actual outputs equal?
        assert(output_is == output_expected), f"Expected and read outputs aren't equal"

def test_pronunciations_map_symbols_py():
    create_test_files()
    run_commands()
    compare_outputs()

test_pronunciations_map_symbols_py()