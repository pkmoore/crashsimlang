from builtins import str
import os
import unittest
from argparse import Namespace
from cslang.cslang import main as cslang_main
from cslang.cslang_error import CSlangError

def get_test_data_path(filename):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(dir_path, filename)
    

class TestDefine(unittest.TestCase):
    def test_define(self):
        test_file = get_test_data_path("ret.cslang")
        automaton, containerbuilder = cslang_main(
            Namespace(mode="build", cslang_path=get_test_data_path("ret.cslang"))
        )

        automaton, datawords, _ = cslang_main(
            Namespace(
                mode="run",
                format="strace",
                strace_path=get_test_data_path("define.strace"),
                syscall_definitions=get_test_data_path(
                    "../cslang/syscall_definitions.pickle"
                ),
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
        with self.assertRaises(CSlangError) as cm:
            cslang_main(
                Namespace(
                    mode="build", cslang_path=get_test_data_path("define_dup.cslang")
                )
            )

        assert "Illegal type redefinition" in str(cm.exception)

    def test_definenonexistant(self):
        with self.assertRaises(CSlangError) as cm:
            cslang_main(
                Namespace(
                    mode="build",
                    cslang_path=get_test_data_path("define_nonexistant.cslang"),
                )
            )

        assert "definition contains undefined type" in str(cm.exception)
