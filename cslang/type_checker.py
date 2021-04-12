from __future__ import print_function
from __future__ import absolute_import
from .cslang_error import CSlangError

def check_ast(ast):
  check_no_output_on_not_dataword(ast)


def check_no_output_on_not_dataword(ast):
  for node in ast:
    node_type = node[0]
    if node_type == "DATAWORD":
      not_flag = node[1]
      if not_flag and  node[5] != None:
        print(node)
        raise CSlangError("Output expressions are not allowed on NOT datawords")
