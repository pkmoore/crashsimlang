import os
import unittest
from argparse import Namespace
from cslang.cslang import main as cslang_main
from cslang.cslang_error import CSlangError


def get_test_data_path(filename):
  dir_path = os.path.dirname(os.path.realpath(__file__))
  return os.path.join(dir_path, filename)


class TestVariants(unittest.TestCase):

  def test_single_variant(self):
    ast = cslang_main(Namespace(mode="parse",
                                check=True,
                                cslang_path=None,
                                string="""
type otherread {read filedesc: Numeric@0};
"""))

    assert ast[0][0] == "VARIANTDEF"
    assert ast[0][1] == "otherread"
    assert ast[0][2][0] == "read"
    assert ast[0][2][1][0][0] == "Numeric"
    assert ast[0][2][1][0][1] == "0"
    assert ast[0][2][1][0][2] == "filedesc"

  def test_many_variants(self):
    ast = cslang_main(Namespace(mode="parse",
                                check=True,
                                cslang_path=None,
                                string="""
type bothread {read filedesc: Numeric@0} | {otherread filedesc: Numeric@0};
"""))

    assert ast[0][0] == "VARIANTDEF"
    assert ast[0][1] == "bothread"
    assert ast[0][2][0][0] == "read"
    assert ast[0][2][0][1][0][0] == "Numeric"
    assert ast[0][2][0][1][0][1] == "0"
    assert ast[0][2][0][1][0][2] == "filedesc"
    assert ast[0][2][1][0] == "otherread"
    assert ast[0][2][1][1][0][0] == "Numeric"
    assert ast[0][2][1][1][0][1] == "0"
    assert ast[0][2][1][1][0][2] == "filedesc"


  syscall_definitions = get_test_data_path("../cslang/syscall_definitions.pickle")


  def test_simple_variant(self):
    automaton_path = get_test_data_path("variantread.auto")
    syscall_definitions = get_test_data_path("syscall_definitions.pickle")
    cslang_main(Namespace(mode="build",
                          cslang_path=get_test_data_path("variantread.cslang")))
  
    automaton_read, datawords_after_read, s2d_read = cslang_main(Namespace(mode="run",
                                                                          format="strace",
                                                                          strace_path=get_test_data_path("variantread.strace"),
                                                                          syscall_definitions=syscall_definitions,
                                                                          automaton_path=automaton_path))
  
    automaton_recv, datawords_after_recv, s2d_recv = cslang_main(Namespace(mode="run",
                                                                           format="strace",
                                                                           strace_path=get_test_data_path("variantrecv.strace"),
                                                                           syscall_definitions=syscall_definitions,
                                                                           automaton_path=automaton_path))

    # Make sure the automata have the correct number of states
    assert len(automaton_read.states) == 3
    assert len(automaton_recv.states) == 3      

    # Make sure the automata both end in the correct state (having accepted read/recv correctly)
    assert automaton_read.current_state == 2
    assert automaton_recv.current_state == 2                                                   

  def test_not_variant(self):
    automaton_path = get_test_data_path("variantreadnot.auto")
    syscall_definitions = get_test_data_path("syscall_definitions.pickle")
    cslang_main(Namespace(mode="build",
                          cslang_path=get_test_data_path("variantreadnot.cslang")))
  
    automaton_read, datawords_after_read, s2d_read = cslang_main(Namespace(mode="run",
                                                                          format="strace",
                                                                          strace_path=get_test_data_path("variantread.strace"),
                                                                          syscall_definitions=syscall_definitions,
                                                                          automaton_path=automaton_path))
  
    automaton_recv, datawords_after_recv, s2d_recv = cslang_main(Namespace(mode="run",
                                                                           format="strace",
                                                                           strace_path=get_test_data_path("variantrecv.strace"),
                                                                           syscall_definitions=syscall_definitions,
                                                                           automaton_path=automaton_path))

    # Make sure the automata have the correct number of states
    assert len(automaton_read.states) == 3
    assert len(automaton_recv.states) == 3      

    # Make sure the automata both end in the correct state (having accepted read/recv correctly)
    assert not automaton_read.states[automaton_read.current_state].is_accepting
    assert not automaton_recv.states[automaton_recv.current_state].is_accepting   
                                                         