import os
import unittest

from runner import main as runner_main
from cslang import main as cslang_main
from cslang_error import CSlangError

from adt import ContainerBuilder


class TestOpen(unittest.TestCase):

  def teardown(self):
    os.system("rm test/*.dw")
    os.system("rm test/*.pickle")
    os.system("rm test/*.auto")

  def test_late_preamble_statement(self):
    test_file = "test/bad_preamble.cslang"
    cslang_main(test_file, parse_only=True)
    self.assertRaises(CSlangError)

