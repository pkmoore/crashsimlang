from __future__ import absolute_import
from builtins import str
from .register_automaton import RegisterAutomaton
from .register_automaton import State
from .register_automaton import Transition
from .dataword import DataWord
from .adt import ContainerBuilder
from .cslang_error import CSlangError
import dill as pickle


def process_root(ast_root):
    automaton = RegisterAutomaton()
    container_builder = ContainerBuilder()
    for i in ast_root:
        if i[0] == "REGASSIGN":
            # identifier, value
            handle_regassign(automaton, i[1][1], i[2])
        elif i[0] == "TYPEDEF":
            # type_name, list of contained types
            handle_typedef(container_builder, i[1], i[2])
        elif i[0] == "VARIANTDEF":
            handle_variantdef(container_builder, i[1], i[2])
        elif i[0] == "DATAWORD":
            # HACK: "the rest of the stuff to build a dataword"
            handle_dataword(automaton, container_builder, i[1:])
        elif i[0] == "REPETITION":
            raise NotImplementedError("We hit a repitition")
        else:
            raise NotImplementedError("Not implemented node: {}".format(i[0]))

    # At this point we have finished building the automaton and can do any
    # post-build configuration and cleanup

    # If the last state is a NOT state, we need to search backward through
    # the states until we reach a non-NOT state and make that our accepting state
    if "NOT" in automaton.states[-1].tags:
        non_NOT_state = _find_first_non_NOT_state(automaton)
        automaton.states[non_NOT_state].is_accepting = True
    else:
        automaton.states[-1].is_accepting = True
    return automaton, container_builder


def _find_first_non_NOT_state(automaton):
    cur = -1
    # This loop is safe because the starting state is always a non-NOT state
    # In the case where every dataword statement creates a NOT state
    # we will end up only accepting inputs that never advance out of the starting state
    while "NOT" in automaton.states[cur].tags:
        cur -= 1
    return cur


def handle_regassign(automaton, register_name, value):
    if value[0] == "IDENTIFIER":
        automaton.registers[register_name] = automaton.registers[value[1]]
    elif value[0] in ["NUM_LITERAL", "NUMERIC"]:
        automaton.registers[register_name] = float(value[1])
    elif value[0] == "STRING_LITERAL":
        automaton.registers[register_name] = str(value[1])
    elif value[0] == "REGEXP":
        automaton.registers[register_name] = _get_expression_value(automaton, value[1])
    else:
        raise CSlangError("Bad type in register assignment: {}".format(value[0]))


def _get_expression_value(automaton, exp):
    lhs = exp[1]
    rhs = exp[3]

    if lhs[0] == "REGEXP":
        lhs = _get_expression_value(automaton, lhs)

    if rhs[0] == "REGEXP":
        rhs = _get_expression_value(automaton, rhs)

    if lhs[0] == "IDENTIFIER":
        lhs = _value_from_register(automaton, lhs[1])
    else:
        lhs = _to_num_or_str(lhs)

    if rhs[0] == "IDENTIFIER":
        rhs = _value_from_register(automaton, rhs[1])
    else:
        rhs = _to_num_or_str(rhs)

    if lhs[0] != rhs[0]:
        raise CSlangError(
            "Type mismatch between registers {} and {}".format(exp[1], exp[1])
        )

    if exp[0] in ["REGADD", "REGCONCAT"]:
        if lhs[0] == "String":
            return str(lhs[1]) + str(rhs[1])
        elif lhs[0] == "Numeric":
            return float(lhs[1]) + float(rhs[1])
        else:
            raise CSlangError("Bad type in addition/concatination: {}".format(lhs[0]))
    elif exp[0] == "REGSUB":
        if lhs[0] != "Numeric" or rhs[0] != "Numeric":
            raise CSlangError("Bad type in subtraction: {}".format(lhs[0]))
        return float(lhs[1]) - float(rhs[1])
    elif exp[0] == "REGMUL":
        if lhs[0] != "Numeric" or rhs[0] != "Numeric":
            raise CSlangError("Bad type in multiplication: {}".format(lhs[0]))
        return float(lhs[1]) * float(rhs[1])
    elif exp[0] == "REGDIV":
        if lhs[0] != "Numeric" or rhs[0] != "Numeric":
            raise CSlangError("Bad type in division: {}".format(lhs[0]))
        return float(lhs[1]) / float(rhs[1])
    else:
        raise CSlangError("Bad expression operation: {}".format(exp[0]))


def _value_from_register(automaton, reg):
    val = automaton.registers[reg]
    if type(val) == str:
        return ("String", val)
    elif type(val) == float:
        return ("Numeric", val)
    else:
        raise CSlangError(
            "Got bad type out of register value: {}, {}".format(val, type(val))
        )


def _to_num_or_str(val):
    if val[0] in ["Numeric", "NUM_LITERAL"]:
        return ("Numeric", val[1])
    elif val[0] in ["String", "STRING_LITERAL"]:
        return ("String", val[1])
    else:
        raise CSlangError("Bad type in cast to String or Numeric: {}".format(val[0]))


def handle_typedef(cb, type_name, type_definition):
    cb.define_type(type_name, type_definition)


def handle_variantdef(cb, variant_name, variant_definition):
    for i in variant_definition:
        # Define a type for each of the variant's possiblities
        # i[0] -> the type's name i[1] -> the type's definition
        cb.define_type(i[0], i[1])
    cb.define_variant(variant_name, variant_definition)


def _get_name_or_variants(container_builder, name):
    if name in container_builder.variants:
        return container_builder.variants[name]
    else:
        # HACK: do we need to check if the name exists as a type here?
        return [name]


def handle_dataword(automaton, container_builder, params):
    not_dataword = params[0] and params[0][1] == "NOT"
    type_name = params[1][1]
    operations = params[2][1]
    if params[3]:
        predicates = tuple(x[1] for x in params[3][1:])
    else:
        predicates = None
    if params[4]:
        outputs = params[4][2][1]
    else:
        outputs = None
    if not_dataword:
        #  This is a not dataword so we create our NOT state
        automaton.states.append(
            State(type_name, tags=["NOT"], operations=operations, outputs=outputs)
        )

        # And make a transition to it with appropriate register_matches
        automaton.states[-2].transitions.append(
            Transition(
                _get_name_or_variants(container_builder, type_name),
                len(automaton.states) - 1,
                operations=operations,
                predicates=predicates,
            )
        )

    else:
        # We encountered a new dataword so we make a new state
        automaton.states.append(
            State(type_name, operations=operations, outputs=outputs)
        )

        # We create a transition to this state on the previous state

        # The state we just added is in automaton.states[-1] so we need to start
        # with automaton.states[-2] and keep searching back until we hit a non-NOT
        # state.  This is the state to which we will add a transition to the new state
        # we just added.

        neg_index = -2
        while "NOT" in automaton.states[neg_index].tags:
            neg_index -= 1

        automaton.states[neg_index].transitions.append(
            Transition(
                _get_name_or_variants(container_builder, type_name),
                len(automaton.states) - 1,
                operations=operations,
                predicates=predicates,
            )
        )
