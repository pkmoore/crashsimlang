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
    self.states[self.current_state].match(incoming_dataword)


class State:
  def __init__(self, name, index):
    self.name = name
    self.index = index
    self.transitions = []

  def match(self, incoming_dataword):
    for i in self.transitions:
      if i.match(incoming_dataword):
        return True
    return False

  def __str__(self):
    tmp = ""
    tmp += "    Name: " + self.name + "\n"
    for i in self.transitions:
      tmp += "      Transition:\n" + str(i) + "\n"
    return tmp


class Transition:
  def __init__(self, dataword_name):
    self.dataword_name = dataword_name
    self.register_requirements = {}

  def __str__(self):
    tmp = ""
    tmp += "        dataword_name: " + self.dataword_name + "\n"
    return tmp

  def match(self, current_dataword):
    if current_dataword.name == self.dataword_name:
      return True
    return False


# Matching with no registers -> Does the current data word name match the data
# word name specified by one of the transitions Right now we only go forward in
# transitions, so transitioning is current_state++
# Each state only has one transition
