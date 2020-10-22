import os
from cslang.runner import main as runner_main
from cslang.cslang import main as cslang_main


def get_test_data_path(filename):
  dir_path = os.path.dirname(os.path.realpath(__file__))
  return os.path.join(dir_path, filename)


class TestOpen():

  def teardown(self):
    os.system("rm test/*.dw")
    os.system("rm test/*.pickle")
    os.system("rm test/*.auto")

  def test_open(self):
    test_file = get_test_data_path("open.cslang")
    cslang_main(test_file)
    automaton, datawords_after = runner_main(test_file)
    assert automaton.is_accepting

  def test_open_fail_pred(self):
    test_file = get_test_data_path("open_fail_name.cslang")
    cslang_main(test_file)
    automaton, datawords_after = runner_main(test_file)
    assert automaton.is_accepting
