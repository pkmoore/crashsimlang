import os
from cslang.runner import main as runner_main
from cslang.cslang import main as cslang_main


def get_test_data_path(filename):
  dir_path = os.path.dirname(os.path.realpath(__file__))
  return os.path.join(dir_path, filename)


class TestPredicates():

  def teardown(self):
    os.system("rm test/*.dw")
    os.system("rm test/*.pickle")
    os.system("rm test/*.auto")

  def test_checkfdtrue(self):
    test_file = get_test_data_path("predicates.cslang")
    cslang_main(test_file)
    automaton, datawords_after = runner_main(test_file)
    assert automaton.current_state == 3
    assert "foo, bar" in datawords_after[2].get_mutated_strace()
