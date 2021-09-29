from builtins import str
import os
import unittest
from argparse import Namespace
from cslang.cslang import main as cslang_main
from cslang.cslang_error import CSlangError


def get_test_data_path(filename):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(dir_path, filename)


class TestRepetition(unittest.TestCase):
    def test_single(self):
        test_file = get_test_data_path("repetition.cslang")
        automaton, containerbuilder = cslang_main(
            Namespace(mode="build", cslang_path=get_test_data_path("repetition.cslang"))
        )
        assert len(automaton.states) == 3
        assert len(automaton.subautomata) == 2
        automaton, datawords, _ = cslang_main(
            Namespace(
                mode="run",
                format="strace",
                strace_path=get_test_data_path("repetition.strace"),
                syscall_definitions=get_test_data_path(
                    "../cslang/syscall_definitions.pickle"
                ),
                automaton_path=get_test_data_path("repetition.auto"),
            )
        )

        assert automaton.current_state == 2
        assert automaton.is_accepting()
