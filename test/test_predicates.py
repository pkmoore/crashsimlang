from builtins import object
import os
from argparse import Namespace
from ..port.port import main as port_main


def get_test_data_path(filename):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(dir_path, filename)


class TestPredicates(object):
    def test_checkfdtrue(self):
        syscall_definitions = get_test_data_path("syscall_definitions.pickle")
        automaton_path = get_test_data_path("predicates.auto")
        port_main(
            Namespace(mode="build", port_path=get_test_data_path("predicates.port"))
        )

        automaton, datawords_after, s2d = port_main(
            Namespace(
                mode="run",
                format="strace",
                strace_path=get_test_data_path("predicates.strace"),
                syscall_definitions=syscall_definitions,
                automaton_path=automaton_path,
            )
        )
        assert automaton.current_state == 4
        assert not automaton.is_accepting()
        assert "foo, bar" in s2d.get_mutated_event(datawords_after[2])
