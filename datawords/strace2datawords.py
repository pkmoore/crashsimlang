from __future__ import print_function
import sys

from posix_omni_parser import Trace

class Preamble:
  def __init__(self):
    self.predicates = {}
    self.captures = {}
    self._current_captured_args = {}
    self._current_syscall = None

  def _apply_predicates(self):
    for i in self.predicates[self._current_syscall.name]:
      if(i(self._current_captured_args)):
        print("[T]", end="")
      else:
        print("[F]", end=""),

  def _capture_args(self):
    self._current_captured_args = self.captures[self._current_syscall.name](self._current_syscall)

  def handle_syscall(self, call):
    self._current_syscall = call
    self._capture_args()
    self._apply_predicates()
    print(self._current_syscall.name, end="")
    print("(", end="")
    print(", ".join(self._current_captured_args.values()), end="")
    print("); \n", end="")



def capture(call, dest, arg, name):
  dest[name] = call.args[arg].value




if __name__ == "__main__":
  t = Trace.Trace(sys.argv[1], "./syscall_definitions.pickle")

  pre = Preamble()
  pre.predicates["open"] = [lambda captured: captured["filename"] == "test.txt"]
  pre.captures["open"] = lambda call: {"filename": call.args[0].value}

  pre.predicates["read"] = []
  pre.captures["read"] = lambda call: {"fd": str(call.args[0].value),
                                       "ret": str(call.ret[0])}


  for i in t.syscalls:
    pre.handle_syscall(i)
