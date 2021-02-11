import os
import unittest
from argparse import Namespace
from cslang.cslang import main as cslang_main
from cslang.cslang_error import CSlangError


def get_test_data_path(filename):
  dir_path = os.path.dirname(os.path.realpath(__file__))
  return os.path.join(dir_path, filename)


class TestVariants(unittest.TestCase):

  def test_single_variant(self):
    ast = cslang_main(Namespace(mode="parse",
                                check=True,
                                cslang_path=None,
                                string="""
type otherread {read filedesc: Numeric@0};
"""))

    assert ast[0][0] == "VARIANTDEF"
    assert ast[0][1] == "otherread"
    assert ast[0][2][0] == "read"
    assert ast[0][2][1][0][0] == "Numeric"
    assert ast[0][2][1][0][1] == "0"
    assert ast[0][2][1][0][2] == "filedesc"

  def test_many_variants(self):
    ast = cslang_main(Namespace(mode="parse",
                                check=True,
                                cslang_path=None,
                                string="""
type bothread {read filedesc: Numeric@0} | {otherread filedesc: Numeric@0};
"""))

    assert ast[0][0] == "VARIANTDEF"
    assert ast[0][1] == "bothread"
    assert ast[0][2][0][0] == "read"
    assert ast[0][2][0][1][0][0] == "Numeric"
    assert ast[0][2][0][1][0][1] == "0"
    assert ast[0][2][0][1][0][2] == "filedesc"
    assert ast[0][2][1][0] == "otherread"
    assert ast[0][2][1][1][0][0] == "Numeric"
    assert ast[0][2][1][1][0][1] == "0"
    assert ast[0][2][1][1][0][2] == "filedesc"
