import os
import unittest
from argparse import Namespace
from cslang.cslang import main as cslang_main
from cslang.cslang_error import CSlangError


def get_test_data_path(filename):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(dir_path, filename)


class TestCSV(unittest.TestCase):
    def test_csv(self):
        test_file = get_test_data_path("csv.cslang")
        automaton, containerbuilder = cslang_main(
            Namespace(mode="build", cslang_path=get_test_data_path("csv.cslang"))
        )

        automaton, datawords, _ = cslang_main(
            Namespace(
                mode="run",
                format="csv",
                csv_path=get_test_data_path("csv.txt"),                                    #watch out for the file that need to be changed
                automaton_path=get_test_data_path("csv.auto"),
            )
        )
        assert "write" in containerbuilder.builders

        container = datawords[0].container

        assert container["type"] == "write"
        assert container["members"][0]["type"] == "String"
        assert container["members"][0]["members"][0] == "fd=999"
        assert container["members"][1]["type"] == "String"
        assert container["members"][1]["members"][0] == "data=what's up world"

        assert automaton.is_accepting
        assert automaton.current_state == 1

