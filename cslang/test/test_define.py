import os
import unittest
from runner import main as runner_main
from cslang import main as cslang_main
from cslang import containerbuilder


class TestOpen(unittest.TestCase):

  def test_define(self):
    # Hack: Global
    test_file = "test/define.cslang"
    preamble, datawords, automaton, containerbuilder = cslang_main(test_file)
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
