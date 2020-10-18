import os
from runner import main as runner_main
from cslang import main as cslang_main


class TestPredicates():

  def teardown(self):
    os.system("rm test/*.dw")
    os.system("rm test/*.pickle")
    os.system("rm test/*.auto")

  def test_checkfdtrue(self):
    test_file = "test/predicates.cslang"
    cslang_main(test_file)
    automaton, datawords_after = runner_main(test_file)
    assert automaton.current_state == 1
    assert datawords_after[0].predicate_results[0][1] == True
    assert datawords_after[0].predicate_results[1][1] == False
    assert datawords_after[0].predicate_results[2][1] == True
    assert datawords_after[0].predicate_results[3][1] == False
