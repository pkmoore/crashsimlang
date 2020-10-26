from __future__ import print_function
import sys
import dill as pickle
import os
from collections import OrderedDict
import adt

from posix_omni_parser import Trace





class DataWord(object):
  def __init__(self, system_call, container):
    self.original_system_call = system_call
    self.container = container
    self.predicate_results = []
    if container:
      self.type = container["type"]
      self.captured_arguments = container["members"]
    else:
      self.type = system_call.name
      self.captured_arguments = None


  def is_interesting(self):
    return True


  def get_name(self):
    return self.original_system_call.name


  def get_dataword(self):
    tmp = ''
    tmp += self.original_system_call.name
    tmp += '('
    # Only print dataword parameters if we have them
    if self.container:
      tmp += ', '.join([str(x["members"][0]) for x in self.captured_arguments])
    tmp += ')'
    return tmp


  def get_mutated_strace(self):
    tmp = ''
    tmp += self.original_system_call.pid
    tmp += '  '
    tmp += self.type
    tmp += '('
    coalesced_args = list(self.original_system_call.args)
    modified_ret = None
    if self.captured_arguments:
      for i in self.captured_arguments:
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
      tmp += " ".join([str(x) for x in self.original_system_call.ret if x != None])

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



class UninterestingDataWord(DataWord):
  def __init__(self, system_call):
    super(UninterestingDataWord, self).__init__(system_call, {})

  def is_interesting(self):
    return False




class Preamble:
  def __init__(self):
    self.captures = []
    self.containerbuilder = None
    self._current_captured_args = None
    self._current_syscall = None


  def inject_containerbuilder(self, containerbuilder):
    self.containerbuilder = containerbuilder

    container = []
    # Instantiate an instance of each top level type
    # and add it to a list that the preamble will use
    for k in containerbuilder.builders.keys():
      if containerbuilder.top_level[k]:
        container.append(containerbuilder.instantiate_type(k))

    #  These are our top level types
    for i in container:
      cur_type = i["type"]
      if cur_type not in self.captures:
        self.captures.append(cur_type)


  def handle_syscall(self, call):
    self._current_syscall = call
    if len(self.captures) == 0 or self._current_syscall.name not in self.captures:
      # Right now, we define a system call we aren't interested in as
      # any system call with no captured arguments
      return UninterestingDataWord(self._current_syscall)
    else:
      argslist = list(call.args)
      argslist.append(call.ret[0])
      container = self.containerbuilder.instantiate_type(self._current_syscall.name)
      container = self._capture_args(container, argslist)
      return DataWord(self._current_syscall, container)


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