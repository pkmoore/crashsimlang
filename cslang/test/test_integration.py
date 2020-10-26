import os
from argparse import Namespace
from cslang.cslang import main as cslang_main


def get_test_data_path(filename):
  dir_path = os.path.dirname(os.path.realpath(__file__))
  return os.path.join(dir_path, filename)


class TestIntegration():

  def test_openclose(self):
    cslang_main(Namespace(mode="strace",
                          operation="build",
                          cslang_path=get_test_data_path("openclose.cslang")))

    automaton, datawords_after = cslang_main(Namespace(mode="strace",
                          operation="run",
                          strace_path=get_test_data_path("openclose.strace"),
                          syscall_definitions=get_test_data_path("../cslang/syscall_definitions.pickle"),
                          automaton_path=get_test_data_path("openclose.auto"),
                          preamble_path=get_test_data_path("openclose.pre")))
    assert datawords_after[0].is_interesting()
    assert not datawords_after[1].is_interesting()
    assert automaton.current_state == 3
    assert automaton.is_accepting()
    assert automaton.registers["fd"] == 3
    assert automaton.registers["fn"] == "test.txt"
    assert automaton.registers["retval"] == "-1"

  def test_uninteresting_dataword(self):
    cslang_main(Namespace(mode="strace",
                          operation="build",
                          cslang_path=get_test_data_path("uninterestingdataword.cslang")))

    automaton, datawords_after = cslang_main(Namespace(mode="strace",
                          operation="run",
                          strace_path=get_test_data_path("uninterestingdataword.strace"),
                          syscall_definitions=get_test_data_path("../cslang/syscall_definitions.pickle"),
                          automaton_path=get_test_data_path("uninterestingdataword.auto"),
                          preamble_path=get_test_data_path("uninterestingdataword.pre")))
    assert automaton

  def test_empty_dataword(self):
    cslang_main(Namespace(mode="strace",
                          operation="build",
                          cslang_path=get_test_data_path("emptydataword.cslang")))

    automaton, datawords_after = cslang_main(Namespace(mode="strace",
                          operation="run",
                          strace_path=get_test_data_path("emptydataword.strace"),
                          syscall_definitions=get_test_data_path("../cslang/syscall_definitions.pickle"),
                          automaton_path=get_test_data_path("emptydataword.auto"),
                          preamble_path=get_test_data_path("emptydataword.pre")))
    assert len(automaton.states) == 2
