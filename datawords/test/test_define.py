import os
from runner import main as runner_main
from cslang import main as cslang_main
from cslang import containerbuilder


class TestOpen():

  def test_define(self):
    # Hack: Global
    global containerbuilder
    test_file = "test/define.cslang"
    cslang_main(test_file, parse_only=True)
    assert "fstat" in containerbuilder.builders

