from __future__ import print_function
from __future__ import absolute_import
from builtins import str
from builtins import range
from builtins import object
from .cslang_error import CSlangError
import pprint


def get_nested_member_for_path(container, path):
    # HACK: Fix the recursion so we don't have to do the below
    if path.startswith("."):
        path = path[1:]
    steps = path.split(".")
    current_argument = _get_member_for_name(container, steps[0])
    for i in steps[1:]:
        current_argument = _get_member_for_name(current_argument["members"], i)
    # HACK: Returning a tuple with the type in the first element might be bad?
    return (current_argument["type"], current_argument["members"][0])


def write_nested_member_for_path(container, path, value):
    # HACK: Fix the recursion so we don't have to do the below
    if path.startswith("."):
        path = path[1:]
    steps = path.split(".")
    current_argument = _get_member_for_name(container, steps[0])
    for i in steps[1:]:
        current_argument = _get_member_for_name(current_argument["members"], i)
    if current_argument["type"] == "Numeric":
        current_argument["members"][0] = float(value)
    elif current_argument["type"] == "String":
        current_argument["members"][0] = str(value)
    else:
        raise CSlangError(
            "Bad type found ({}) when writing value {}".format(
                current_argument["type"], value
            )
        )


def _get_member_for_name(current_argument, name):
    for i in current_argument:
        if i["arg_name"] == name:
            return i
    raise CSlangError("Couldn't find member with name {}".format(name))


class ContainerBuilder(object):
    def __init__(self):
        self.builders = {"Numeric": self.primative, "String": self.primative}
        self.primatives = ["Numeric", "String"]
        self.top_level = {"Numeric": False, "String": False}
        self.variants = {}

    def primative(self, in_data):
        incoming_type = in_data[0]
        incoming_arg = in_data[1]
        incoming_arg_name = in_data[2]
        return {
            "type": incoming_type,
            "arg_pos": incoming_arg,
            "members": [],
            "arg_name": incoming_arg_name,
        }

    def define_variant(self, variant_name, variant_definition):
        if variant_name in self.variants:
            raise CSlangError(
                "Illegal variant redefinition for variant: {}".format(variant_name)
            )
        self.variants[variant_name] = []
        for i in variant_definition:
            self.variants[variant_name].append(i[0])

    def define_type(self, container_type, types):
        # It is an error for us to already have a builder for the type we're defining
        if container_type in self.builders:
            raise CSlangError(
                "Illegal type redefinition for type: {}".format(container_type)
            )

        member_types = [t[0] for t in types]

        # It is an error for types list to contain a type that has not been defined
        for t in member_types:
            if t not in self.builders:
                raise CSlangError(
                    "Type definition contains undefined type: {}".format(t)
                )

        # Newly created types are considered top_level until used as a member type
        self.top_level[container_type] = True

        # If a type is used as a member in the type being defined, it is no longer
        # a "top level" type for capturing purposes
        for t in member_types:
            self.top_level[t] = False

        member_builders = [self.builders[t[0]] for t in types]

        def t_func(in_data):
            incoming_type = container_type
            incoming_arg = in_data[1]
            incoming_arg_name = in_data[2]
            t = {}
            t["type"] = incoming_type
            t["arg_pos"] = incoming_arg
            t["arg_name"] = incoming_arg_name
            t["members"] = []

            # Step through each type and apply the appropriate builder
            # this takes our arguents and makes members out of them
            for i in range(len(types)):
                # get the appropriate builder
                builder = self.builders[types[i][0]]

                # get the appropriate argument.  All builders expect arguments
                # as a list so we need to wrap argv[i]
                # arg = argv[i]

                # Apply the selected builder to the selected arg and add it to t
                # t's list of members
                t["members"].append(builder(types[i]))
            return t

        self.builders[str(container_type)] = t_func

    def instantiate_type(self, t):
        instance = self.builders[t](t)
        del instance["arg_pos"]
        del instance["arg_name"]
        return instance


# define statbuf("String":0, "Int":5)
# {"type": "statbuf", "values": [{"type": "String", "arg_pos": 0},
#                               {"type": "Int", "arg_pos": 5}
#                              ]
# }
#
# define stat(string:0, statbuf:1)
# {"type": "stat", values:[{"type": "String", "arg_pos": 0},
#                         {"type": "statbuf", "values": [{"type": "String", "arg_pos": 0},
#                                                        {"type": "Int", "arg_pos": 5}
#                                                       ]
#                         }
#                        ]
# }


#  Example Usage:
#  pp = pprint.PrettyPrinter(indent=2)
#  c = ContainerBuilder()
#  c.define_type("fakestat", [("Int", 0, "Somefield")])
#  c.define_type("statbuf", [("fakestat", 3, "Fakefield"), ("String", 0, "A_str"), ("String", 1, "Another_str"), ("Int", 5, "some_val")])
#  tmp = c.instantiate_type("statbuf")
#  pp.pprint(tmp)
#  print()
#  print()
#  c.define_type("stat", (("String", 0, "filename"), ("statbuf", 1, "stat_struct")))
#  tmp = c.instantiate_type("stat")
#  c.define_type("open", (("Int", "ret", "filedesc"),))
#  tmp = c.instantiate_type("open")
#  pp.pprint(tmp)
