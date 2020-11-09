import os
import unittest
from argparse import Namespace
from cslang.cslang import main as cslang_main
from cslang.cslang_error import CSlangError
from cslang.adt import ContainerBuilder


def get_test_data_path(filename):
  dir_path = os.path.dirname(os.path.realpath(__file__))
  return os.path.join(dir_path, filename)


class TestOpen(unittest.TestCase):

  def test_late_preamble_statement(self):
    with self.assertRaises(CSlangError) as cm:
      cslang_main(Namespace(mode="build",
                            cslang_path=get_test_data_path("bad_preamble.cslang")))

    assert "Found preamble statement after" in str(cm.exception)
