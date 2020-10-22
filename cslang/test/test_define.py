import os
import unittest
from cslang.runner import main as runner_main
from cslang.cslang import main as cslang_main
from cslang.cslang import containerbuilder


def get_test_data_path(filename):
  dir_path = os.path.dirname(os.path.realpath(__file__))
  return os.path.join(dir_path, filename)


class TestOpen(unittest.TestCase):

  def test_define(self):
    test_file = get_test_data_path("define.cslang")
    preamble, datawords, automaton, containerbuilder = cslang_main(test_file)
    runner_main(test_file)
    assert "fstat" in containerbuilder.builders
    assert "statbuf" in containerbuilder.builders

    container = datawords[0].container

    assert container["type"] == "fstat"
    assert container["members"][0]["type"] == "Numeric"
    assert container["members"][0]["members"] == [3]
    assert container["members"][1]["type"] == "statbuf"
    assert container["members"][1]["members"][0]["type"] == "String"
    assert "makedev(0, 4)" in container["members"][1]["members"][0]["members"][0]
    assert container["members"][1]["members"][1]["type"] == "String"
    assert "402" in container["members"][1]["members"][1]["members"][0]
