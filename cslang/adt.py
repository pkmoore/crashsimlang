from __future__ import print_function
from cslang_error import CSlangError
import pprint


class ContainerBuilder(object):
  def __init__(self):
    self.builders = {"Numeric": self.primative, "String": self.primative}
    self.top_level = {"Numeric": False, "String": False}

  def primative(self, in_data):
    incoming_type = in_data[0]
    incoming_arg = in_data[1]
    incoming_arg_name = in_data[2]
    return {"type": incoming_type, "arg_pos": incoming_arg, "members": [], "arg_name": incoming_arg_name}

  def define_type(self, container_type, types):
    # It is an error for us to already have a builder for the type we're defining
    if container_type in self.builders:
      raise CSlangError("Illegal type redefinition for type: {}".format(container_type))

    member_types = [t[0] for t in types]

    # It is an error for types list to contain a type that has not been defined
    for t in member_types:
      if t not in self.builders:
        raise CSlangError("Type definition contains undefined type: {}".format(t))

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
        #arg = argv[i]

        # Apply the selected builder to the selected arg and add it to t
        # t's list of members
        t["members"].append(builder(types[i]))
      return t

    self.builders[str(container_type)] = t_func

  def instantiate_type(self, t):
    instance = self.builders[t](t)
    del(instance["arg_pos"])
    del(instance["arg_name"])
    return instance


#define statbuf("String":0, "Int":5)
#{"type": "statbuf", "values": [{"type": "String", "arg_pos": 0},
#                               {"type": "Int", "arg_pos": 5}
#                              ]
#}
#
#define stat(string:0, statbuf:1)
#{"type": "stat", values:[{"type": "String", "arg_pos": 0},
#                         {"type": "statbuf", "values": [{"type": "String", "arg_pos": 0},
#                                                        {"type": "Int", "arg_pos": 5}
#                                                       ]
#                         }
#                        ]
#}



if __name__ == "__main__":
  pp = pprint.PrettyPrinter(indent=2)
  c = ContainerBuilder()
  c.define_type("fakestat", [("Int", 0, "Somefield")])
  c.define_type("statbuf", [("fakestat", 3, "Fakefield"), ("String", 0, "A_str"), ("String", 1, "Another_str"), ("Int", 5, "some_val")])
  tmp = c.instantiate_type("statbuf")
  pp.pprint(tmp)
  print()
  print()
  c.define_type("stat", (("String", 0, "filename"), ("statbuf", 1, "stat_struct")))
  tmp = c.instantiate_type("stat")
  c.define_type("open", (("Int", "ret", "filedesc"),))
  tmp = c.instantiate_type("open")
  pp.pprint(tmp)
