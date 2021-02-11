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
type other_read read;
"""))
    assert False

