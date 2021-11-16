from builtins import object
import os
from argparse import Namespace
from port.port import main as port_main


def get_test_data_path(filename):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(dir_path, filename)


class TestOpen(object):
    def test_open(self):
        port_main(Namespace(mode="build", port_path=get_test_data_path("open.port")))

        automaton, datawords_after, _ = port_main(
            Namespace(
                mode="run",
                format="strace",
                strace_path=get_test_data_path("open.strace"),
                syscall_definitions=get_test_data_path("syscall_definitions.pickle"),
                automaton_path=get_test_data_path("open.auto"),
            )
        )

        assert automaton.is_accepting

    def test_open_fail_pred(self):
        port_main(
            Namespace(
                mode="build",
                format="strace",
                port_path=get_test_data_path("open_fail_name.port"),
            )
        )

        automaton, datawords_after, _ = port_main(
            Namespace(
                mode="run",
                format="strace",
                strace_path=get_test_data_path("open_fail_name.strace"),
                syscall_definitions=get_test_data_path("syscall_definitions.pickle"),
                automaton_path=get_test_data_path("open_fail_name.auto"),
            )
        )

        assert automaton.is_accepting
