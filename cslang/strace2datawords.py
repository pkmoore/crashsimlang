from __future__ import print_function
import sys
import pickle
import os
from collections import OrderedDict

from posix_omni_parser import Trace





class DataWord(object):
  def __init__(self, system_call, container, predicate_results):
    self.original_system_call = system_call
    self.container = container
    self.type = container["type"]
    self.captured_arguments = container["members"]
    self.predicate_results = predicate_results


  def is_interesting(self):
    return True


  def get_name(self):
    return self.original_system_call.name


  def get_dataword(self):
    tmp = ''
    for i in self.predicate_results:
      if i:
        tmp += '[T]'
      else:
        tmp += '[F]'
    tmp += self.original_system_call.name
    tmp += '('
    tmp += ', '.join([str(x["members"][0]) for x in self.captured_arguments])
    tmp += ')'
    return tmp


  def get_mutated_strace(self):
    tmp = ''
    tmp += self.original_system_call.pid
    tmp += '  '
    tmp += self.type
    tmp += '('

    coalesced_args = [str(v) for v in list(self.original_system_call.args)]
    modified_ret = None
    for i in self.captured_arguments:
      if i["arg_pos"] == "ret":
        modified_ret = i
        continue
      coalesced_args[int(i["arg_pos"])] = str(i["members"][0])
    tmp += ', '.join(coalesced_args)
    tmp += ')'
    tmp += '  =  '

    if modified_ret:
      tmp += str(i["members"][0])
    else:
      tmp += " ".join([str(x) for x in self.original_system_call.ret if x != None])

    return tmp





class UninterestingDataWord(DataWord):
  def __init__(self, system_call):
    super(UninterestingDataWord, self).__init__(system_call, {}, [])

  def is_interesting(self):
    return False




class Preamble:
  def __init__(self):
    self.predicates = {}
    self.captures = []
    self.containerbuilder = None
    self._current_captured_args = None
    self._current_predicate_results = None
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
    self._current_captured_args = OrderedDict()
    self._current_predicate_results = []
    self._apply_predicates()
    if self._current_syscall.name in self.captures:
      argslist = list(call.args)
      argslist.append(call.ret[0])
      container = self.containerbuilder.instantiate_type(self._current_syscall.name)
      container = self._capture_args(container, argslist)
    if len(self.captures) == 0:
      # Right now, we define a system call we aren't interested in as
      # any system call with no captured arguments
      return UninterestingDataWord(self._current_syscall)
    else:
      return DataWord(self._current_syscall, container, self._current_predicate_results)


  def _apply_predicates(self):
    if self._current_syscall.name in self.predicates:
      for i in self.predicates[self._current_syscall.name]:
        self._current_predicate_results.append(i(self._current_captured_args))


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





  def predicate(self, syscall_name, f):
    if syscall_name not in self.predicates:
      self.predicates[syscall_name] = []
    self.predicates[syscall_name].append(f)
