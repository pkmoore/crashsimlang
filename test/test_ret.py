from builtins import str
import os
import unittest
from argparse import Namespace
from ..port.port import main as port_main
from ..port.errors.port_error import PORTError


def get_test_data_path(filename):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(dir_path, filename)


class TestRet(unittest.TestCase):
    def test_ret(self):

        with self.assertRaises(PORTError) as cm:
            port_main(Namespace(mode="build", port_path=get_test_data_path("ret.port")))

        assert "A structure does not have return value position" in str(cm.exception)

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
