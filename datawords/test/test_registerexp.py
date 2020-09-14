import os
from runner import main as runner_main
from cslang import main as cslang_main


class TestRegisterExpressions():

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

