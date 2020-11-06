import os
import unittest
from argparse import Namespace
from cslang.cslang import main as cslang_main
from cslang.cslang import containerbuilder
from cslang.cslang_error import CSlangError


def get_test_data_path(filename):
  dir_path = os.path.dirname(os.path.realpath(__file__))
  return os.path.join(dir_path, filename)


class TestJSON(unittest.TestCase):

  def test_json(self):
    test_file = get_test_data_path("update.cslang")
    automaton, containerbuilder = cslang_main(Namespace(mode="jsonrpc",
                                                        operation="build",
                                                        cslang_path=get_test_data_path("update.cslang")))

    automaton, datawords, _ = cslang_main(Namespace(mode="jsonrpc",
                                       operation="run",
                                       json_path=get_test_data_path("update.json"),
                                       automaton_path=get_test_data_path("update.auto"),
                                       containerbuilder_path=get_test_data_path("update.cb")))
    assert "update" in containerbuilder.builders
    assert "test" in containerbuilder.builders

    container = datawords[0].container

    assert container["type"] == "update"
    assert container["members"][0]["type"] == "Numeric"
    assert container["members"][0]["members"] == [1]
    assert container["members"][1]["type"] == "Numeric"
    assert container["members"][1]["members"][0] == 2

    container2 = datawords[2].container

    assert container2["type"] == "update"
    assert container2["members"][0]["members"][0] == 999
    assert container2["members"][1]["members"][0] == 888

    assert automaton.is_accepting
    assert automaton.current_state == 3
