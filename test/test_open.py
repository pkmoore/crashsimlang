import os
from argparse import Namespace
from cslang.cslang import main as cslang_main


def get_test_data_path(filename):
  dir_path = os.path.dirname(os.path.realpath(__file__))
  return os.path.join(dir_path, filename)


class TestOpen():

  def test_open(self):
    cslang_main(Namespace(mode="strace",
                          operation="build",
                          cslang_path=get_test_data_path("open.cslang")))

    automaton, datawords_after, _ = cslang_main(Namespace(mode="strace",
                          operation="run",
                          strace_path=get_test_data_path("open.strace"),
                          syscall_definitions=get_test_data_path("../cslang/syscall_definitions.pickle"),
                          automaton_path=get_test_data_path("open.auto"),
                          containerbuilder_path=get_test_data_path("open.cb")))

    assert automaton.is_accepting

  def test_open_fail_pred(self):
    cslang_main(Namespace(mode="strace",
                          operation="build",
                          cslang_path=get_test_data_path("open_fail_name.cslang")))

    automaton, datawords_after, _ = cslang_main(Namespace(mode="strace",
                          operation="run",
                          strace_path=get_test_data_path("open_fail_name.strace"),
                          syscall_definitions=get_test_data_path("../cslang/syscall_definitions.pickle"),
                          automaton_path=get_test_data_path("open_fail_name.auto"),
                          containerbuilder_path=get_test_data_path("open_fail_name.cb")))

    assert automaton.is_accepting
