import os
from runner import main as runner_main
from cslang import main as cslang_main


class TestOpen():

  def teardown(self):
    os.system("rm test/*.dw")
    os.system("rm test/*.pickle")
    os.system("rm test/*.auto")

  def test_open(self):
    test_file = "test/open.cslang"
    cslang_main(test_file)
    automaton = runner_main(test_file)
    assert automaton.is_accepting

  def test_open_fail_pred(self):
    test_file = "test/open_fail_name.cslang"
    cslang_main(test_file)
    automaton = runner_main(test_file)
    assert automaton.is_accepting
