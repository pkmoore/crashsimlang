from builtins import str
import os
import unittest
from argparse import Namespace
from port.port import main as port_main
from port.port_error import PORTError


def get_test_data_path(filename):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(dir_path, filename)


class TestRegisterExpressions(unittest.TestCase):
    def test_assign(self):
        port_main(
            Namespace(mode="build", port_path=get_test_data_path("registerassign.port"))
        )

        automaton, datawords_after, _ = port_main(
            Namespace(
                mode="run",
                format="strace",
                strace_path=get_test_data_path("registerassign.strace"),
                syscall_definitions=get_test_data_path("syscall_definitions.pickle"),
                automaton_path=get_test_data_path("registerassign.auto"),
            )
        )
        assert automaton.registers["assignstr"] == "hel"
        assert automaton.registers["assignnum"] == 5
        assert automaton.registers["assignidn"] == 4
        assert automaton.registers["assignids"] == "worked"

    def test_concat(self):
        test_file = get_test_data_path("registerconcat.port")
        port_main(
            Namespace(mode="build", port_path=get_test_data_path("registerconcat.port"))
        )

        automaton, datawords_after, _ = port_main(
            Namespace(
                mode="run",
                format="strace",
                strace_path=get_test_data_path("registerconcat.strace"),
                syscall_definitions=get_test_data_path("syscall_definitions.pickle"),
                automaton_path=get_test_data_path("registerconcat.auto"),
            )
        )
        assert automaton.registers["numnum"] == "hello"
        assert automaton.registers["regnum"] == "hello"
        assert automaton.registers["numreg"] == "lohel"
        assert automaton.registers["regreg"] == "helhel"

    def test_badadd(self):
        with self.assertRaises(PORTError) as cm:
            port_main(
                Namespace(
                    mode="build",
                    port_path=get_test_data_path("register_badadd.port"),
                )
            )

        assert "Type mismatch between registers" in str(cm.exception)

    def test_add(self):
        port_main(
            Namespace(mode="build", port_path=get_test_data_path("registeradd.port"))
        )

        automaton, datawords_after, _ = port_main(
            Namespace(
                mode="run",
                format="strace",
                strace_path=get_test_data_path("registeradd.strace"),
                syscall_definitions=get_test_data_path("syscall_definitions.pickle"),
                automaton_path=get_test_data_path("registeradd.auto"),
            )
        )
        assert automaton.registers["numnum"] == 7
        assert automaton.registers["regnum"] == 6
        assert automaton.registers["numreg"] == 6
        assert automaton.registers["regreg"] == 4

        assert automaton.registers["fnumnum"] == 7
        assert automaton.registers["fregnum"] == 5
        assert automaton.registers["fnumreg"] == 5
        assert automaton.registers["fregreg"] == 4.6

        assert automaton.registers["nnumnum"] == 0
        assert automaton.registers["nregnum"] == 0
        assert automaton.registers["nnumreg"] == 0
        assert automaton.registers["nregreg"] == -3

    def test_subtract(self):
        port_main(
            Namespace(mode="build", port_path=get_test_data_path("registersub.port"))
        )

        automaton, datawords_after, _ = port_main(
            Namespace(
                mode="run",
                format="strace",
                strace_path=get_test_data_path("registersub.strace"),
                syscall_definitions=get_test_data_path("syscall_definitions.pickle"),
                automaton_path=get_test_data_path("registersub.auto"),
            )
        )
        assert automaton.registers["numnum"] == 1
        assert automaton.registers["regnum"] == 1
        assert automaton.registers["numreg"] == 1
        assert automaton.registers["regreg"] == 0

        assert automaton.registers["fnumnum"] == 0
        assert automaton.registers["fregnum"] == 0
        assert automaton.registers["fnumreg"] == 0
        assert automaton.registers["fregreg"] == 0

        assert automaton.registers["nnumnum"] == 0
        assert automaton.registers["nregnum"] == 0
        assert automaton.registers["nnumreg"] == 0
        assert automaton.registers["nregreg"] == 0

    def test_multiply(self):
        port_main(
            Namespace(mode="build", port_path=get_test_data_path("registermul.port"))
        )

        automaton, datawords_after, _ = port_main(
            Namespace(
                mode="run",
                format="strace",
                strace_path=get_test_data_path("registermul.strace"),
                syscall_definitions=get_test_data_path("syscall_definitions.pickle"),
                automaton_path=get_test_data_path("registermul.auto"),
            )
        )
        assert automaton.registers["numnum"] == 12
        assert automaton.registers["regnum"] == 8
        assert automaton.registers["numreg"] == 8
        assert automaton.registers["regreg"] == 4

        assert automaton.registers["fnumnum"] == 7
        assert automaton.registers["fregnum"] == 5
        assert automaton.registers["fnumreg"] == 5
        assert automaton.registers["fregreg"] == 6.25

        assert automaton.registers["nnumnum"] == 1
        assert automaton.registers["nregnum"] == 1
        assert automaton.registers["nnumreg"] == 1
        assert automaton.registers["nregreg"] == 1

    def test_divide(self):
        test_file = get_test_data_path("registerdiv.port")
        port_main(
            Namespace(mode="build", port_path=get_test_data_path("registerdiv.port"))
        )

        automaton, datawords_after, _ = port_main(
            Namespace(
                mode="run",
                format="strace",
                strace_path=get_test_data_path("registerdiv.strace"),
                syscall_definitions=get_test_data_path("syscall_definitions.pickle"),
                automaton_path=get_test_data_path("registerdiv.auto"),
            )
        )
        assert automaton.registers["numnum"] == 3
        assert automaton.registers["regnum"] == 1
        assert automaton.registers["numreg"] == 1
        assert automaton.registers["regreg"] == 1

        assert automaton.registers["fnumnum"] == 3.5
        assert automaton.registers["fregnum"] == 1.75
        assert automaton.registers["fnumreg"] == 3.125
        assert automaton.registers["fregreg"] == 1

        assert automaton.registers["nnumnum"] == -5
        assert automaton.registers["nregnum"] == -0.2
        assert automaton.registers["nnumreg"] == -5
        assert automaton.registers["nregreg"] == 5
