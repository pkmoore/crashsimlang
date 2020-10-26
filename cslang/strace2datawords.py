from __future__ import print_function
import sys
import dill as pickle
import os
from collections import OrderedDict
import adt

from posix_omni_parser import Trace
from dataword import DataWord
from dataword import UninterestingDataWord

class StraceToDatawords(object):
  def __init__(self, containerbuilder, syscall_definitions, strace_path):
    self.containerbuilder = containerbuilder
    self.syscall_definitions = syscall_definitions
    self.strace_path = strace_path


  def get_datawords(self):
    t = Trace.Trace(self.strace_path, self.syscall_definitions)
    datawords = []
    for i in t.syscalls:
      datawords.append(self.handle_event(i))
    return datawords


  def handle_event(self, event):
    if not any(self.containerbuilder.top_level.values()) \
      or not self.containerbuilder.top_level.get(event.name):
      # Right now, we define a system call we aren't interested in as
      # any system call with no captured arguments
      return UninterestingDataWord(event)
    else:
      argslist = list(event.args)
      argslist.append(event.ret[0])
      container = self.containerbuilder.instantiate_type(event.name)
      container = self._capture_args(container, argslist)
      return DataWord(event, container)

  def _capture_args(self, container, argslist):
    for i in container["members"]:
      if i["type"] in self.containerbuilder.primatives:
        i["members"].append(self._get_arg_as_type(i["arg_pos"], i["type"], argslist))
      else:
        self._capture_args(i, argslist[int(i["arg_pos"])])
    return container

  def _get_arg_as_type(self, arg_pos, out_type, argslist):
    funcs = {"String": str,
             "Numeric": int
     }
    if arg_pos == "ret":
      return funcs[out_type](argslist[-1])
    else:
      if hasattr(argslist[int(arg_pos)], 'value'):
        return funcs[out_type](argslist[int(arg_pos)].value)
      else:
        return funcs[out_type](argslist[int(arg_pos)])


  def get_mutated_strace(self, dw):
    tmp = ''
    tmp += dw.original_event.pid
    tmp += '  '
    tmp += dw.type
    tmp += '('
    coalesced_args = list(dw.original_event.args)
    modified_ret = None
    if dw.captured_arguments:
      for i in dw.captured_arguments:
        if i["arg_pos"] == "ret":
          modified_ret = i
          continue
        arg_to_be_updated = coalesced_args[int(i["arg_pos"])]
        arg_to_be_updated.value = self._recursive_update_args(arg_to_be_updated, i)
    tmp += ', '.join([str(v) for v in coalesced_args])
    tmp += ')'
    tmp += '  =  '

    if modified_ret:
      tmp += str(i["members"][0])
    else:
      tmp += " ".join([str(x) for x in dw.original_event.ret if x != None])

    return tmp


  def _recursive_update_args(self, args, values):
    # There are three cases we have to deal with here
    # Case 1. When we get a posix_omni_parser object with a single
    # value.  This is indicated by an object with a "value" attribute
    # that is not a list.  In this case, we set the object's value attribute
    if hasattr(args, 'value') and type(args.value) is not list:
        return values["members"][0]
    # Case 2 happens we are going through a list encountered in Case 3
    # and hit a non-list item.  In this case, we set the value of that item.
    elif type(args) is str or type(args.value) is not list:
        return  values["members"][0]
    # Case 3 happens when we encounter a list and must iterate through and
    # handle each of its items recursively
    # Note: This may break if there are nested parsing classes
    else:
      values = values["members"]
      for i in range(len(values)):
        args.value[int(values[i]["arg_pos"])] =  self._recursive_update_args(args.value[int(values[i]["arg_pos"])], values[i])
      return args.value
