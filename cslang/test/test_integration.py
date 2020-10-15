import os
from runner import main as runner_main
from cslang import main as cslang_main


class TestIntegration():

  def teardown(self):
    os.system("rm test/*.dw")
    os.system("rm test/*.pickle")
    os.system("rm test/*.auto")

  def test_openclose(self):
    test_file = "test/openclose.cslang"
    cslang_main(test_file)
    automaton, datawords_after = runner_main(test_file)
    assert automaton.current_state == 3
    assert automaton.is_accepting
    assert automaton.registers["fd"] == 3
    assert automaton.registers["fn"] == "test.txt"
    assert automaton.registers["retval"] == "-1"

  def test_uninteresting_dataword(self):
    test_file = "test/uninterestingdataword.cslang"
    cslang_main(test_file)
    automaton, datawords_after = runner_main(test_file)
    assert automaton

  def test_empty_dataword(self):
    test_file = "test/emptydataword.cslang"
    cslang_main(test_file)
    automaton, datawords_after = runner_main(test_file)
    assert len(automaton.states) == 2
