import os
from runner import main as runner_main
from cslang import main as cslang_main


class TestRegisterExpressions():

  def test_concat(self):
    global automaton
    test_file = "test/registerconcat.cslang"
    cslang_main(test_file)
    automaton = runner_main(test_file)
    assert automaton.registers["numnum"] == "hello"
    assert automaton.registers["regnum"] == "hello"
    assert automaton.registers["numreg"] == "lohel"
    assert automaton.registers["regreg"] == "helhel"

  def test_add(self):
    global automaton
    test_file = "test/registeradd.cslang"
    cslang_main(test_file)
    automaton = runner_main(test_file)
    assert automaton.registers["numnum"] == 7
    assert automaton.registers["regnum"] == 6
    assert automaton.registers["numreg"] == 6
    assert automaton.registers["regreg"] == 4


  def test_subtract(self):
    global automaton
    test_file = "test/registersub.cslang"
    cslang_main(test_file)
    automaton = runner_main(test_file)
    assert automaton.registers["numnum"] == 1
    assert automaton.registers["regnum"] == 1
    assert automaton.registers["numreg"] == 1
    assert automaton.registers["regreg"] == 0


  def test_multiply(self):
    global automaton
    test_file = "test/registermul.cslang"
    cslang_main(test_file)
    automaton = runner_main(test_file)
    assert automaton.registers["numnum"] == 12
    assert automaton.registers["regnum"] == 8
    assert automaton.registers["numreg"] == 8
    assert automaton.registers["regreg"] == 4

  def test_divide(self):
    global automaton
    test_file = "test/registerdiv.cslang"
    cslang_main(test_file)
    automaton = runner_main(test_file)
    assert automaton.registers["numnum"] == 3
    assert automaton.registers["regnum"] == 1
    assert automaton.registers["numreg"] == 1
    assert automaton.registers["regreg"] == 1
    assert automaton.registers["floordiv1"] == 1
    assert automaton.registers["floordiv2"] == 0
