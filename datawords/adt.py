from __future__ import print_function
import pprint



class ContainerBuilder(object):
  def __init__(self):
    self.builders = {"Int": self.primative, "String": self.primative}

  def primative(self, in_data):
    incoming_type = in_data[0]
    incoming_arg = in_data[1]
    return {"type": incoming_type, "argpos": incoming_arg, "members": []}

  def define_type(self, container_type, types):
    member_builders = [self.builders[t[0]] for t in types]

    c_type = container_type
    def t_func(argv):
      t = {"type": str(c_type)}
      t["members"] = []
      t["argpos"] = argv[1]

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
    del(instance["argpos"])
    return instance


#define statbuf("String":0, "Int":5)
#{"type": "statbuf", "values": [{"type": "String", "argpos": 0},
#                               {"type": "Int", "argpos": 5}
#                              ]
#}
#
#define stat(string:0, statbuf:1)
#{"type": "stat", values:[{"type": "String", "argpos": 0},
#                         {"type": "statbuf", "values": [{"type": "String", "argpos": 0},
#                                                        {"type": "Int", "argpos": 5}
#                                                       ]
#                         }
#                        ]
#}



if __name__ == "__main__":
  pp = pprint.PrettyPrinter(indent=2)
  c = ContainerBuilder()
  c.define_type("fakestat", [("Int", 0)])
  c.define_type("statbuf", [("fakestat", 3), ("String", 0), ("String", 1), ("Int", 5)])
  tmp = c.instantiate_type("statbuf")
  pp.pprint(tmp)
  print()
  print()
  c.define_type("stat", (("String", 0), ("statbuf", 1)))
  tmp = c.instantiate_type("stat")
  pp.pprint(tmp)
