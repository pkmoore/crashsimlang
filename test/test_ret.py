from builtins import str
import os
import unittest
from argparse import Namespace
from cslang.cslang import main as cslang_main
from cslang.cslang_error import CSlangError

def get_test_data_path(filename):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(dir_path, filename)
    

class TestRet(unittest.TestCase):
    def test_ret(self):
        
        with self.assertRaises(CSlangError) as cm:
            cslang_main(
                Namespace(
                    mode="build", cslang_path=get_test_data_path("ret.cslang")
                )
            )

        assert "A structure does not have return value position" in str(cm.exception)
	

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
