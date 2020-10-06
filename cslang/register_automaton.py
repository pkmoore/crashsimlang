class RegisterAutomaton:
  def __init__(self):
    self.states = []
    self.states.append(State("startstate"))
    self.current_state = 0
    self.registers = {}


  def __str__(self):
    tmp = ""
    tmp += "Automaton:\n"
    tmp += "  Current State: " + str(self.current_state) + "\n"
    for i in self.states:
      tmp += "  State:\n" + str(i) + "\n"
    return tmp


  def match(self, incoming_dataword):
    to_state = self.states[self.current_state].match(incoming_dataword, self.registers)
    if to_state != -1:
      self.current_state = to_state
      # We've moved into a new state so we need to "enter" it.
      # This executes the register store operations required by the new state
      self.states[self.current_state].enter(incoming_dataword, self.registers)


  def is_accepting(self):
    return self.states[self.current_state].is_accepting


class State:
  def __init__(self, name, operations=None, transitions=None, is_accepting=False, tags=None):
    self.name = name
    self.transitions = transitions if transitions is not None else []
    self.is_accepting = is_accepting
    self.operations = operations if operations is not None else []
    self.tags = tags if tags is not None else []

  def match(self, incoming_dataword, registers):
    for i in self.transitions:
      to_state = i.match(incoming_dataword, registers)
      if to_state != -1:
        return to_state
    return -1

  def enter(self, incoming_dataword, registers):
    for i in self.operations:
    # REGISTER STORES
      for i in self.operations:
        match_paths = _extract_paths("", (i, ), "!")
        if match_paths:
          for i in match_paths:
            self._store_path_to_register(incoming_dataword, i[0], registers, i[1])

    for i in self.operations:
    # REGISTER WRITES
      for i in self.operations:
        match_paths = _extract_paths("", (i, ), "->")
        if match_paths:
          for i in match_paths:
            self._write_register_to_path(incoming_dataword, i[0], registers, i[1])

  def _write_register_to_path(self, dataword, path, registers, register):
    # HACK: Fix the recursion so we don't have to do the below
    # HACK HACK: This was stolen from around line 159! REFACTOR OUT!
    path = path[1:]
    steps = path.split(".")
    current_argument = _get_member_for_name(dataword.captured_arguments, steps[0])
    for i in steps[1:]:
      current_argument = _get_member_for_name(current_argument["members"], i)
    current_argument["members"][0] = registers[register]

  def _store_path_to_register(self, dataword, path, registers, register):
    # HACK: Fix the recursion so we don't have to do the below
    # HACK HACK: This was stolen from around line 159! REFACTOR OUT!
    path = path[1:]
    steps = path.split(".")
    current_argument = _get_member_for_name(dataword.captured_arguments, steps[0])
    for i in steps[1:]:
      current_argument = _get_member_for_name(current_argument["members"], i)
    registers[register] = current_argument["members"][0]


  def __str__(self):
    tmp = ""
    tmp += "    Name: " + self.name + "\n"
    tmp += "    Tags: "
    for i in self.tags:
      tmp += i
    tmp += "\n"
    for i in self.transitions:
      tmp += "      Transition:\n" + str(i) + "\n"
    return tmp


class Transition:
  def __init__(self, dataword_name, to_state, operations=None):
    self.dataword_name = dataword_name
    self.to_state = to_state
    self.operations = operations if operations is not None else []

  def __str__(self):
    tmp = ""
    tmp += "        dataword_name: " + self.dataword_name + "\n"
    tmp += "        operations: " + str() + "\n"
    tmp += "        to_state: " + str(self.to_state) + "\n"
    return tmp

  def match(self, current_dataword, registers):
    if current_dataword.get_name() == self.dataword_name and self._pass_operations(current_dataword, registers):
      return self.to_state
    return -1

  def _pass_operations(self, incoming_dataword, registers):
    for i in self.operations:
      match_paths = _extract_paths("", (i, ), "?")
      if match_paths:
        # HACK:  Fix the recusion so we don't have to do the next line
        for i in match_paths:
          if not self._path_matches_register(incoming_dataword, i[0], registers, i[1]):
            return False
    return True

  def _path_matches_register(self, dataword, path, registers, register):
    # HACK: Fix the recursion so we don't have to do the below
    path = path[1:]
    steps = path.split(".")
    current_argument = _get_member_for_name(dataword.captured_arguments, steps[0])
    for i in steps[1:]:
      current_argument = _get_member_for_name(current_argument["members"], i)
    return current_argument["members"][0] == registers[register]

def _get_member_for_name(current_argument, name):
  for i in current_argument:
    if i["arg_name"] == name:
      return i

def _extract_paths(in_path, objs_list, op):
  paths = []
  for i in objs_list:
    if i[0] == "#":
      paths.extend(_extract_paths(in_path + "." + i[1], i[2], op))
    elif i[0] == op:
      paths.append((in_path + "." + i[1], i[2]))
  return paths
