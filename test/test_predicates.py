from builtins import object
import os
from argparse import Namespace
from cslang.cslang import main as cslang_main


def get_test_data_path(filename):
  dir_path = os.path.dirname(os.path.realpath(__file__))
  return os.path.join(dir_path, filename)


class TestPredicates(object):

  def test_checkfdtrue(self):
    syscall_definitions = get_test_data_path("../cslang/syscall_definitions.pickle")
    automaton_path = get_test_data_path("predicates.auto")
    cslang_main(Namespace(mode="build",
                          cslang_path=get_test_data_path("predicates.cslang")))

    automaton, datawords_after, s2d = cslang_main(Namespace(mode="run",
                          format="strace",
                          strace_path=get_test_data_path("predicates.strace"),
                          syscall_definitions=syscall_definitions,
                          automaton_path=automaton_path))
    assert automaton.current_state == 4
    assert not automaton.is_accepting()
    assert "foo, bar" in s2d.get_mutated_strace(datawords_after[2])
