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
      tmp += " ".join([str(x) for x in self.original_system_call.ret if x])

    return tmp





class UninterestingDataWord(DataWord):
  def __init__(self, system_call):
    super(UninterestingDataWord, self).__init__(system_call, {}, [])

  def is_interesting(self):
    return False




class Preamble:
  def __init__(self):
    self.predicates = {}
    self.captures = {}
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
        self.captures[cur_type] = []
      for j in i["members"]:
        self.captures[cur_type].append({"arg_name": j["arg_name"], "arg_pos": j["arg_pos"]})



  def handle_syscall(self, call):
    self._current_syscall = call
    self._current_captured_args = OrderedDict()
    self._current_predicate_results = []
    self._apply_predicates()
    if len(self.captures) == 0:
      # Right now, we define a system call we aren't interested in as
      # any system call with no captured arguments
      return UninterestingDataWord(self._current_syscall)
    else:
      return DataWord(self._current_syscall, self._capture_args(), self._current_predicate_results)


  def _apply_predicates(self):
    if self._current_syscall.name in self.predicates:
      for i in self.predicates[self._current_syscall.name]:
        self._current_predicate_results.append(i(self._current_captured_args))


  def _capture_args(self):
    if self._current_syscall.name in self.captures:
      container = self.containerbuilder.instantiate_type(self._current_syscall.name)
      for i in range(len(self.captures[self._current_syscall.name])):
        current_capture = self.captures[self._current_syscall.name][i]
        # Note this works because self.captures was built based on the layout of container
        # as determined when inject_containerbuilder was called
        if current_capture["arg_pos"] == "ret":
          container["members"][i]["members"].append(self._get_arg_as_type("ret", container["members"][i]["type"]))
        else:
          container["members"][i]["members"].append(self._get_arg_as_type(int(current_capture["arg_pos"]), container["members"][i]["type"]))
      return container


  def _get_arg_as_type(self, arg_pos, out_type):
    funcs = {"String": str,
             "Numeric": int
     }
    if arg_pos == "ret":
      return funcs[out_type](self._current_syscall.ret[0])
    else:
      return funcs[out_type](self._current_syscall.args[arg_pos].value)





  def predicate(self, syscall_name, f):
    if syscall_name not in self.predicates:
      self.predicates[syscall_name] = []
    self.predicates[syscall_name].append(f)
