from builtins import str
import os
import unittest
from argparse import Namespace
from ..port.port import main as port_main
from ..port.errors.port_error import PORTError


def get_test_data_path(filename):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(dir_path, filename)


class TestRepetition(unittest.TestCase):
    def test_single(self):
        test_file = get_test_data_path("repetition.port")
        automaton, containerbuilder = port_main(
            Namespace(mode="build", port_path=get_test_data_path("repetition.port"))
        )
        assert len(automaton.states) == 3
        assert len(automaton.subautomata) == 2
        automaton, datawords, _ = port_main(
            Namespace(
                mode="run",
                format="strace",
                strace_path=get_test_data_path("repetition.strace"),
                syscall_definitions=get_test_data_path("syscall_definitions.pickle"),
                automaton_path=get_test_data_path("repetition.auto"),
            )
        )

        assert automaton.current_state == 2
        assert automaton.is_accepting()
