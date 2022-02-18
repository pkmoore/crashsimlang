from __future__ import print_function
from __future__ import absolute_import
from .port_error import PORTError


def check_ast(ast):
    check_no_output_on_not_dataword(ast)
    check_no_ret_in_none_top_level_event(ast)


def check_no_output_on_not_dataword(ast):
    for node in ast:
        node_type = node[0]
        if node_type == "DATAWORD":
            not_flag = node[1]
            if not_flag and node[5] != None:
                print(node)
                raise PORTError("Output expressions are not allowed on NOT datawords")


def check_top_level_event(ast):

    top_level = {"Numeric": False, "String": False}

    for node in ast:

        # check if the node is defining a type
        if node[0] == "TYPEDEF":
            node_event_type = node[1]
            top_level[node_event_type] = True

            # if a type is used in an event, it is not a top level event
            for member in node[2]:
                top_level[member[0]] = False

    return top_level


def check_no_ret_in_none_top_level_event(ast):

    # get the top level event list
    top_level = check_top_level_event(ast)

    for node in ast:
        if node[0] == "TYPEDEF":
            node_event_type = node[1]
            for member in node[2]:
                if member[1] == "ret":
                    # check if a structure is accessing the value at ret position, which will raise an error
                    if top_level[node_event_type] == False:
                        print(node)
                        raise PORTError(
                            "A structure does not have return value position"
                        )
