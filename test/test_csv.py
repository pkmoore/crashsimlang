import os
import unittest
from argparse import Namespace
from port.port import main as port_main
from port.port_error import PORTError


def get_test_data_path(filename):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(dir_path, filename)


class TestCSV(unittest.TestCase):
    def test_csv(self):
        test_file = get_test_data_path("csv.port")
        automaton, containerbuilder = port_main(
            Namespace(mode="build", port_path=get_test_data_path("csv.port"))
        )

        automaton, datawords, _ = port_main(
            Namespace(
                mode="run",
                format="csv",
                csv_path=get_test_data_path("write.csv"),
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
