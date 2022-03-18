from builtins import str
import os
import unittest
from argparse import Namespace
from ..port.port import main as port_main
from ..port.errors.port_error import PORTError


def get_test_data_path(filename):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(dir_path, filename)


class TestDefine(unittest.TestCase):
    def test_define(self):
        test_file = get_test_data_path("define.port")
        automaton, containerbuilder = port_main(
            Namespace(mode="build", port_path=get_test_data_path("define.port"))
        )

        automaton, datawords, _ = port_main(
            Namespace(
                mode="run",
                format="strace",
                strace_path=get_test_data_path("define.strace"),
                syscall_definitions=get_test_data_path("syscall_definitions.pickle"),
                automaton_path=get_test_data_path("define.auto"),
            )
        )
        assert "fstat" in containerbuilder.builders
        assert "statbuf" in containerbuilder.builders

        container = datawords[0].container

        assert container["type"] == "fstat"
        assert container["members"][0]["type"] == "Numeric"
        assert container["members"][0]["members"] == [3]
        assert container["members"][1]["type"] == "statbuf"
        assert container["members"][1]["members"][0]["type"] == "String"
        assert "makedev(0, 4)" in container["members"][1]["members"][0]["members"][0]
        assert container["members"][1]["members"][1]["type"] == "String"
        assert "402" in container["members"][1]["members"][1]["members"][0]

    def test_definedup(self):
        with self.assertRaises(PORTError) as cm:
            port_main(
                Namespace(mode="build", port_path=get_test_data_path("define_dup.port"))
            )

        assert "Illegal type redefinition" in str(cm.exception)

    def test_definenonexistant(self):
        with self.assertRaises(PORTError) as cm:
            port_main(
                Namespace(
                    mode="build",
                    port_path=get_test_data_path("define_nonexistant.port"),
                )
            )

        assert "definition contains undefined type" in str(cm.exception)
