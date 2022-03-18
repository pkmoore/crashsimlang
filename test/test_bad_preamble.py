from builtins import str
import os
import unittest
from argparse import Namespace
from ..port.port import main as port_main
from ..port.errors.port_error import PORTError
from ..port.compiler.adt import ContainerBuilder


def get_test_data_path(filename):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(dir_path, filename)


class TestOpen(unittest.TestCase):
    def test_late_preamble_statement(self):
        with self.assertRaises(PORTError) as cm:
            port_main(
                Namespace(
                    mode="build", port_path=get_test_data_path("bad_preamble.port")
                )
            )

        assert "Found preamble statement after" in str(cm.exception)
