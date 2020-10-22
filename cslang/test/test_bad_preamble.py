import os
import unittest

from cslang.runner import main as runner_main
from cslang.cslang import main as cslang_main
from cslang.cslang_error import CSlangError
from cslang.adt import ContainerBuilder


def get_test_data_path(filename):
  dir_path = os.path.dirname(os.path.realpath(__file__))
  return os.path.join(dir_path, filename)


class TestOpen(unittest.TestCase):

  def teardown(self):
    os.system("rm test/*.dw")
    os.system("rm test/*.pickle")
    os.system("rm test/*.auto")

  def test_late_preamble_statement(self):
    test_file = get_test_data_path("./bad_preamble.cslang")
    with self.assertRaises(CSlangError):
      cslang_main(test_file, parse_only=True)

