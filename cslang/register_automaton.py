from __future__ import absolute_import
from builtins import str
from builtins import object
from copy import deepcopy
from copy import copy
from . import adt


class RegisterAutomaton(object):
    def __init__(self):
        self.states = []
        self.states.append(State("startstate"))
        self.current_state = 0
        self.registers = {}
        self.events = []
        self.events_iter = None
        self.parent = None
        self.subautomata = []

    def __str__(self):
        tmp = ""
        tmp += "Automaton:\n"
        tmp += "  Current State: " + str(self.current_state) + "\n"
        for i in self.states:
            tmp += "  State:\n" + str(i) + "\n"
        return tmp

    def match(self, incoming_dataword):
        to_state = self.states[self.current_state].match(
            incoming_dataword, self.registers
        )
        if to_state != -1:
            self.current_state = to_state
            # We've moved into a new state so we need to "enter" it.
            # This executes the register store operations required by the new state
            self.states[self.current_state].enter(incoming_dataword, self.registers)

    def is_accepting(self):
        return self.states[self.current_state].is_accepting


class State(object):
    def __init__(
        self,
        name,
        operations=None,
        outputs=None,
        transitions=None,
        is_accepting=False,
        tags=None,
    ):
        self.name = name
        self.transitions = transitions if transitions is not None else []
        self.is_accepting = is_accepting
        self.operations = operations if operations is not None else []
        self.outputs = outputs if outputs is not None else []
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
                match_paths = _extract_paths("", (i,), "!")
                if match_paths:
                    for i in match_paths:
                        self._store_path_to_register(
                            incoming_dataword, i[0], registers, i[1]
                        )

        for i in self.operations:
            # REGISTER WRITES
            for i in self.operations:
                match_paths = _extract_paths("", (i,), "->")
                if match_paths:
                    for i in match_paths:
                        self._write_register_to_path(
                            incoming_dataword, i[0], registers, i[1]
                        )

        for i in self.outputs:
            # OUTPUTS
            for i in self.outputs:
                match_paths = _extract_paths("", (i,), "->")
                if match_paths:
                    for i in match_paths:
                        self._write_register_to_path(
                            incoming_dataword, i[0], registers, i[1]
                        )

    def _write_register_to_path(self, dataword, path, registers, register):
        adt.write_nested_member_for_path(
            dataword.captured_arguments, path, registers[register]
        )

    def _store_path_to_register(self, dataword, path, registers, register):
        member = adt.get_nested_member_for_path(dataword.captured_arguments, path)[1]
        registers[register] = member

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


class SubautomatonTransition(object):
    def __init__(self, to_state, automaton, iterations=1):
        self.to_state = to_state
        self.automaton = automaton
        self.iterations = iterations

    def __str__(self):
        tmp = ""
        tmp += "Subautomaton: " + str(self.automaton)
        tmp += "Iterations: " + str(self.iterations)
        return tp

    def match(self, incoming_dataword, registers):
        # Load subautomaton's registers with current values from parent automaton
        # These registers are updated throughout subautomaton iterations
        # but only commited over the parent automaton's values if we end up in an accepting
        # state after all iterations are complete.
        self.automaton.registers = deepcopy(registers)

        # Copy our parent's event list iterator so we can advance down the list without messing it up
        self.automaton.events_iter = copy(self.automaton.parent.events_iter)

        accepted_iterations = 0
        i = 0
        # Because we must match precisely, we know the exact number of
        # events we must lookahead and examine.  This is used for populating
        # tmpevents (the buffer of events to be examined) and to calculate
        # how far to advance the parent's event iterator if the lookahead'd
        # events put the subautomaton into an accepting state
        # -2 because:
        # first event in tmpevents has already been next()'d from the parent
        # event iterator and passed in as incoming_dataword to maintain
        # compatibility with a normal transition's match function
        # first state in self.automaton is the starting state meaning
        # an automaton always has numevents + 1 states in it.
        num_lookahead_events = len(self.automaton.states) - 2

        while self.iterations == -1 or i < self.iterations:
            self.automaton.current_state = 0
            # Get the next set of events to try
            # The number of events we get equals the number of states the subautomaton has
            # If we don't have enough events, then we automatically fail out of the subautomaton
            tmpevents = [incoming_dataword]
            try:
                tmpevents += [
                    next(self.automaton.events_iter)
                    for _ in range(num_lookahead_events)
                ]
            except StopIteration:
                break
            for j in tmpevents:
                self.automaton.match(j)
            if self.automaton.is_accepting():
                accepted_iterations += 1
            else:
                break
            i += 1
        # if we are in unbounded mode (i.e. self.iterations == -1) then
        # we return successfully if we have any positive number of accepted
        # iterations
        if self.iterations == -1 and accepted_iterations > 0:
            for i in range(accepted_iterations * num_lookahead_events):
                print("SKIP: ", next(self.automaton.parent.events_iter).get_name())
            return self.to_state
        # Otherwise if we are not in unbounded mode then we return
        # successfully if we have the correct numnber of accepted iterations
        # (i.e. accepted_iterations == self.iterations)
        elif accepted_iterations == self.iterations:
            for i in range(accepted_iterations * num_lookahead_events):
                print("SKIP: ", next(self.automaton.parent.events_iter).get_name())
            return self.to_state
        else:
            return -1


class Transition(object):
    def __init__(self, acceptable_names, to_state, operations=None, predicates=None):
        self.acceptable_names = acceptable_names
        self.to_state = to_state
        self.operations = operations if operations is not None else []
        self.predicates = predicates if predicates is not None else []

    def __str__(self):
        tmp = ""
        tmp += "        acceptable_names: " + str(self.acceptable_names) + "\n"
        tmp += "        operations: " + str() + "\n"
        tmp += "        to_state: " + str(self.to_state) + "\n"
        return tmp

    def match(self, current_dataword, registers):
        # First we must determine whether the name we are matching against is a concrete type
        # If this check fails, we need to see if we have a variant name and match using either of the variants
        if (
            current_dataword.get_name() in self.acceptable_names
            and self._pass_predicates(current_dataword)
            and self._pass_operations(current_dataword, registers)
        ):
            return self.to_state
        return -1

    def _pass_predicates(self, incoming_dataword):
        predicate_results = []
        for i in self.predicates:
            member = adt.get_nested_member_for_path(
                incoming_dataword.captured_arguments, i[0]
            )
            if i[1] == "==":
                if member[0] == "Numeric":
                    predicate_results.append(
                        ((i[0] + i[1] + str(i[2])), member[1] == int(i[2]))
                    )
                if member[0] == "String":
                    predicate_results.append(
                        ((i[0] + i[1] + str(i[2])), member[1] == str(i[2]))
                    )
            else:
                raise CSlangError("Bad operator in predicate: {}".format(i[1]))
        # All predicate results must be True for us to return True here
        # the all() function handles this nicely
        return all([x[1] for x in predicate_results])

    def _pass_operations(self, incoming_dataword, registers):
        for i in self.operations:
            match_paths = _extract_paths("", (i,), "?")
            if match_paths:
                for i in match_paths:
                    if not self._path_matches_register(
                        incoming_dataword, i[0], registers, i[1]
                    ):
                        return False
        return True

    def _path_matches_register(self, dataword, path, registers, register):
        member = adt.get_nested_member_for_path(dataword.captured_arguments, path)[1]
        return member == registers[register]


def _extract_paths(in_path, objs_list, op):
    paths = []
    for i in objs_list:
        if i[0] == "#":
            paths.extend(_extract_paths(in_path + "." + i[1], i[2], op))
        elif i[0] == op:
            paths.append((in_path + "." + i[1], i[2]))
    return paths
