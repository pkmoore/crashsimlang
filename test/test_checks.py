import os
import unittest
from argparse import Namespace
from ..port.port import main as port_main
from ..port.errors.port_error import PORTError


def get_test_data_path(filename):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(dir_path, filename)


class TestChecks(unittest.TestCase):
    def test_no_output_on_not_datawords(self):
        with self.assertRaises(PORTError) as cm:
            ast = port_main(
                Namespace(
                    mode="parse",
                    check=True,
                    string="""
event read {filedesc: Numeric@0};
bad <- 4;
NOT read({}) -> read({filedesc: ->bad});
""",
                )
            )
