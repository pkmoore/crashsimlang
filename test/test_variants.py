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
type read {filedesc: Numeric@0};
type otherread read;
"""))
    assert ast[0][0] == "TYPEDEF"
    assert ast[0][1] == "read"
    assert ast[1][0] == "VARIANTDEF"
    assert ast[1][1] == "otherread"
    assert ast[1][2] == ("read",)

  def test_many_variants(self):
    ast = cslang_main(Namespace(mode="parse",
                                check=True,
                                cslang_path=None,
                                string="""
type read {filedesc: Numeric@0};
type otherread {fildesc: Numeric@0};
type bothread read | otherread;
"""))

    assert ast[0][0] == "TYPEDEF"
    assert ast[0][1] == "read"
    assert ast[1][0] == "TYPEDEF"
    assert ast[1][1] == "otherread"
    assert ast[2][0] == "VARIANTDEF"
    assert ast[2][1] == "bothread"
    assert ast[2][2] == ("read", "otherread")
