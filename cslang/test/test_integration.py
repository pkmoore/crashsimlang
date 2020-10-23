import os
from cslang.runner import main as runner_main
from cslang.cslang import main as cslang_main


def get_test_data_path(filename):
  dir_path = os.path.dirname(os.path.realpath(__file__))
  return os.path.join(dir_path, filename)


class TestIntegration():

  def teardown(self):
    os.system("rm test/*.dw")
    os.system("rm test/*.pickle")
    os.system("rm test/*.auto")

  def test_openclose(self):
    test_file = get_test_data_path("openclose.cslang")
    cslang_main(test_file)
    automaton, datawords_after = runner_main(test_file)
    assert datawords_after[0].is_interesting()
    assert not datawords_after[1].is_interesting()
    assert automaton.current_state == 3
    assert automaton.is_accepting()
    assert automaton.registers["fd"] == 3
    assert automaton.registers["fn"] == "test.txt"
    assert automaton.registers["retval"] == "-1"

  def test_uninteresting_dataword(self):
    test_file = get_test_data_path("uninterestingdataword.cslang")
    cslang_main(test_file)
    automaton, datawords_after = runner_main(test_file)
    assert automaton

  def test_empty_dataword(self):
    test_file = get_test_data_path("emptydataword.cslang")
    cslang_main(test_file)
    automaton, datawords_after = runner_main(test_file)
    assert len(automaton.states) == 2
