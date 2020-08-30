from __future__ import print_function
import pickle
import sys
import os
from strace2datawords import DataWord
from register_automaton import RegisterAutomaton
from register_automaton import State
from register_automaton import Transition

if __name__ == "__main__":
  basename = os.path.basename(sys.argv[1])

  # Load in the dataword list (we might not even use this)
  # dataword list is in the .dw file
  with open(basename + ".dw", "r") as f:
    datawords = f.readlines()


  # Load in the List of dataword objects (we might just use this)
  with open(basename + ".pickle", "r") as f:
    dataword_objs = pickle.load(f)


  # Load in the automaton
  with open(basename + ".auto", "r") as f:
    automaton = pickle.load(f)


  # Pass each dataword in the list in series into the automaton

  for i in dataword_objs:
    automaton.match(i)


  # At the end of everything we have a transformed set of datawords.
  # We either use them if we ended in an accepting state or drop ignore
  # them if we haven't ended in an accepting state
  # Some print goes here
  print("Automaton ended in state: " + str(automaton.current_state))
  print("With registers: " + str(automaton.registers))
  print("Automaton is accepting: " + str(automaton.states[automaton.current_state].is_accepting))

  print("Mutated strace: ")

  for i in dataword_objs:
    print(i.get_mutated_strace())
