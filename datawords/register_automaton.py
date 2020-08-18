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
    to_state = self.states[self.current_state].match(incoming_dataword)
    if to_state != -1:
      self.current_state = to_state


class State:
  def __init__(self, name):
    self.name = name
    self.transitions = []

  def match(self, incoming_dataword):
    for i in self.transitions:
      to_state = i.match(incoming_dataword)
      if to_state != -1:
        return to_state
    return -1

  def __str__(self):
    tmp = ""
    tmp += "    Name: " + self.name + "\n"
    for i in self.transitions:
      tmp += "      Transition:\n" + str(i) + "\n"
    return tmp


class Transition:
  def __init__(self, dataword_name, to_state):
    self.dataword_name = dataword_name
    self.register_requirements = {}
    self.to_state = to_state

  def __str__(self):
    tmp = ""
    tmp += "        dataword_name: " + self.dataword_name + "\n"
    tmp += "        to_state: " + str(self.to_state) + "\n"
    return tmp

  def match(self, current_dataword):
    if current_dataword.get_name() == self.dataword_name:
      return self.to_state
    return -1


# Matching with no registers -> Does the current data word name match the data
# word name specified by one of the transitions Right now we only go forward in
# transitions, so transitioning is current_state++
# Each state only has one transition
