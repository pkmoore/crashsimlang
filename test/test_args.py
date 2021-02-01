import os
import unittest
from argparse import Namespace
from cslang.cslang import main as cslang_main
from cslang.cslang_error import CSlangError


def get_test_data_path(filename):
  dir_path = os.path.dirname(os.path.realpath(__file__))
  return os.path.join(dir_path, filename)


class TestArgs(unittest.TestCase):

  def test_exception_on_both_c_and_s(self):
    with self.assertRaises(CSlangError) as cm:
      ast = cslang_main(Namespace(mode="parse",
                                  cslang_file="test/bad.cslang",
                                  check=True,
                                  string="""
type read {filedesc: Numeric@0};
bad <- 4;
NOT read({}) -> read({filedesc: ->bad});
"""))
