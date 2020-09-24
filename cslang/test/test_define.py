import os
from runner import main as runner_main
from cslang import main as cslang_main
from cslang import containerbuilder


class TestOpen():

  def test_define(self):
    # Hack: Global
    test_file = "test/define.cslang"
    preamble, datawords, automaton, containerbuilder = cslang_main(test_file)
    assert "fstat" in containerbuilder.builders

