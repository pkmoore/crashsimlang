from __future__ import print_function
import sys
import pickle
import os
from collections import OrderedDict

from posix_omni_parser import Trace





class DataWord:
  def __init__(self, system_call, captured_arguments, predicate_results):
    self.original_system_call = system_call
    self.captured_arguments = captured_arguments
    self.predicate_results = predicate_results


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
    tmp += ', '.join(self.captured_arguments)
    tmp += ')'
    return tmp


  def get_mutated_strace(self):
    tmp = ''
    tmp += self.original_system_call.pid
    tmp += '  '
    tmp += self.original_system_call.name
    tmp += '('

    coalesced_args = [str(v) for v in list(self.original_system_call.args)]
    args_without_name = [v for k, v in self.captured_arguments.iteritems()]
    modified_ret = None
    for i in args_without_name:
      if i["arg_pos"] == "ret":
        modified_ret = i
        continue
      coalesced_args[i["arg_pos"]] = i["value"].value
    tmp += ', '.join(coalesced_args)
    tmp += ')'
    tmp += '  =  '

    if modified_ret:
      tmp += str(i["value"])
    else:
      tmp += str(self.original_system_call.ret[0])

    return tmp




class Preamble:
  def __init__(self):
    self.predicates = {}
    self.captures = {}
    self._current_captured_args = None
    self._current_predicate_results = None
    self._current_syscall = None


  def handle_syscall(self, call):
    self._current_syscall = call
    self._current_captured_args = OrderedDict()
    self._current_predicate_results = []
    self._capture_args()
    self._apply_predicates()
    return DataWord(self._current_syscall, self._current_captured_args, self._current_predicate_results)


  def _apply_predicates(self):
    if self._current_syscall.name in self.predicates:
      for i in self.predicates[self._current_syscall.name]:
        self._current_predicate_results.append(i(self._current_captured_args))


  def _capture_args(self):
    for i in self.captures[self._current_syscall.name]:
      self._current_captured_args[i["arg_name"]] = {
        "arg_pos": i["arg_pos"],
        "value": self._current_syscall.args[i["arg_pos"]] if i["arg_pos"] != "ret" else self._current_syscall.ret[0]}


  def capture(self, syscall_name, arg_name, arg_pos):
    if syscall_name not in self.captures:
      self.captures[syscall_name] = []
    self.captures[syscall_name].append({"arg_name": arg_name, "arg_pos": arg_pos})


  def predicate(self, syscall_name, f):
    if syscall_name not in self.predicates:
      self.predicates[syscall_name] = []
    self.predicates[syscall_name].append(f)




if __name__ == "__main__":
  strace_path_base = os.path.splitext(os.path.basename(sys.argv[1]))[0]
  datawords_path = strace_path_base + ".dw"
  pickle_path = strace_path_base + ".pickle"

  t = Trace.Trace(sys.argv[1], "./syscall_definitions.pickle")

  pre = Preamble()
  pre.predicate("open", lambda args: args["filename"]["value"].value == "\"test.txt\"")
  pre.capture("open", "filename", 0)

  pre.predicate("read", lambda args: args["result"]["value"] == 10)
  pre.capture("read", "result", "ret")

  datawords = []
  with open(datawords_path, "w") as f:
    for i in t.syscalls:
      d = pre.handle_syscall(i)
      f.write(d.get_dataword() + "\n")
      datawords.append(d)

  with open(pickle_path, "w") as f:
    pickle.dump(datawords, f)
