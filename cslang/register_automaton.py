from __future__ import absolute_import
from builtins import str
from builtins import object
from . import adt


class RegisterAutomaton(object):
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


class Transition(object):
    def __init__(self, acceptable_names, to_state, operations=None, predicates=None):
        self.acceptable_names = acceptable_names
        self.to_state = to_state
        self.operations = operations if operations is not None else []
        self.predicates = predicates if predicates is not None else []

    def __str__(self):
        tmp = ""
        tmp += "        acceptable_names: " + self.acceptable_names + "\n"
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
