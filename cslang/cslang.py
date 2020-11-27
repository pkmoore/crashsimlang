from ply import lex
from ply import yacc
from register_automaton import RegisterAutomaton
from register_automaton import State
from register_automaton import Transition
from strace2datawords import StraceToDatawords
from jsontodatawords import JSONToDatawords
from dataword import DataWord
from dataword import UninterestingDataWord
from posix_omni_parser import Trace
from adt import ContainerBuilder
from cslang_error import CSlangError
import dill as pickle
import os
import sys
import argparse
import pprint


reserved = {
    'NOT' : 'NOT',
    'ret' : 'RET',
    'type' : 'TYPE',
    'with' : 'WITH',
    'and' : 'AND'
}

tokens = ["IDENTIFIER",
          "READOP",
          "STOREOP",
          "WRITEOP",
          "EQUALSOP",
          "ASSIGNOP",
          "NUM_LITERAL",
          "STRING_LITERAL"
] + list(reserved.values())

literals = ['.', '{', '}', ':', '@', '/', '*', '-', '+', ';',',','(', ')' ]

precedence = (
    ('left', 'ASSIGNOP'),
    ('left', '+', '-'),
    ('left', '*', '/'),
 )

def t_ASSIGNOP(t):
  r"<-"
  t.value = ("OPERATOR", t.value)
  return t

def t_EQUALSOP(t):
  r"=="
  t.value = ("OPERATOR", t.value)
  return t

def t_READOP(t):
  r"\?"
  t.value = ("OPERATOR", t.value)
  return t

def t_STOREOP(t):
  r"\!"
  t.value = ("OPERATOR", t.value)
  return t

def t_WRITEOP(t):
  r"->"
  t.value = ("OPERATOR", t.value)
  return t

def t_NUM_LITERAL(t):
  r"-?[0-9][0-9]*(\.[0-9]+)?"
  t.value = ("NUM_LITERAL", t.value)
  return t

def t_STRING_LITERAL(t):
  "\"[^\"]+\""
  t.value = ("STRING", t.value[1:-1])
  return t

t_ignore = " \t\n"



# We use a function to define this function for two reasons:
# 1. Ply gives tokens defined by functions higher priority meaning this
# rule will be used for ambiguous stuff that could be an identifier or
# could be a keyword.
# 2. We can define logic to figure out if something is a keyword rather
# than an identifier and return the appropriate type
def t_IDENTIFIER(t):
  r"[A-Za-z_][a-zA-Z0-9]*"
  if t.value in reserved:
    t.type = reserved[t.value]
    t.value = ("RESERVED", t.value)
  else:
    t.type = "IDENTIFIER"
    t.value = ("IDENTIFIER", t.value)
  return t

def t_error(t):
  raise CSlangError("Lex error with: {}".format(t))

def t_COMMENT(t):
  r'\#.*'

def p_error(p):
  raise CSlangError("Parse error with: {}".format(p))

def p_statementlist(p):
  ''' statementlist : statement  statementlist
                    | statement
  '''
  automaton.states[-1].is_accepting = True
  if len(p) == 3:
    p[0] = [p[1]] + p[2]
  else:
    p[0] = [p[1]]

def p_statement(p):
  ''' statement : preamblestatement
                | bodystatement
  '''
  p[0] = p[1]

def p_preamblestatement(p):
  ''' preamblestatement : typedefinition ';'
  '''
  global in_preamble
  if not in_preamble:
    raise CSlangError("Found preamble statement after preamble processing has ended")

  p[0] = p[1]

def p_bodystatement(p):
  ''' bodystatement : dataword ';'
                    | registerassignment ';'
  '''
  global in_preamble
  global preamble
  global containerbuilder
  # If this is true, we have encountered our first body statement.
  # This means we have seen all the type definitions we are going to see
  # and it is time for the preamble object to read through the generated
  # data structure and figure out what stuff it needs to capture
  if in_preamble:
    in_preamble = False

  p[0] = p[1]


def p_typeexpression(p):
  ''' typeexpression :  IDENTIFIER ':' IDENTIFIER '@' NUM_LITERAL
                     |  IDENTIFIER ':' IDENTIFIER '@' RET
  '''
        # Type     Position Name
  p[0] = (p[3][1], p[5][1], p[1][1])


def p_typeexpressionlist(p):
  ''' typeexpressionlist : typeexpression ',' typeexpressionlist
                         | typeexpression
  '''

  if len(p) == 4:
    p[0] = [p[1]] + p[3]
  else:
    p[0] = [p[1]]


def p_typedefinition(p):
  ''' typedefinition : TYPE IDENTIFIER '{' typeexpressionlist '}'

  '''

  global containerbuilder
  containerbuilder.define_type(p[2][1], p[4])
  p[0] = ("TYPEDEF", p[2][1], p[4])


def p_predpath(p):
  ''' predpath : IDENTIFIER "." predpath
               | IDENTIFIER
  '''

  if len(p) == 4:
    p[0] = ("PREDPATH", p[1][1] + p[2] + p[3][1])
  else:
    p[0] = ("PREDPATH", p[1][1])


def p_predexpressionlist(p):
  ''' predexpressionlist : predexpression AND predexpressionlist
                         | predexpression
  '''

  if len(p) == 4:
    p[0] = ("PREDEXPRESSIONLIST", p[1][1:]) + p[3][1:]
  else:
    p[0] = ("PREDEXPRESSIONLIST", p[1][1:])



def p_predexpression(p):
  ''' predexpression : predpath EQUALSOP NUM_LITERAL
                     | predpath EQUALSOP STRING_LITERAL
  '''

  p[0] = ("PREDICATEEXPRESSION", p[1][1], p[2][1], p[3][1])




def p_registerassignment(p):
  ''' registerassignment : IDENTIFIER ASSIGNOP NUM_LITERAL
                         | IDENTIFIER ASSIGNOP STRING_LITERAL
                         | IDENTIFIER ASSIGNOP IDENTIFIER
                         | IDENTIFIER ASSIGNOP registerexp
  '''

  global automaton
  register_name = p[1][1]
  if p[3][0] == 'IDENTIFIER':
    automaton.registers[register_name] = automaton.registers[p[3][1]]
  elif p[3][0] in ['NUM_LITERAL', 'NUMERIC']:
    automaton.registers[register_name] = float(p[3][1])
  elif p[3][0] == 'STRING':
    automaton.registers[register_name] = str(p[3][1])
  else:
    raise CSlangError("Bad type in register assignment: {}".format(p[3]))

  p[0] = ('REGASSIGN', p[1], p[3])

def p_registerexp(p):
  ''' registerexp : registeradd
                  | registersub
                  | registermul
                  | registerdiv
                  | registerconcat
                  | registeraddorconcat
  '''

  p[0] = p[1]

def p_registeraddorconcat(p):
  ''' registeraddorconcat : IDENTIFIER '+' IDENTIFIER
  '''

  lhs = automaton.registers[p[1][1]]
  rhs = automaton.registers[p[3][1]]

  if type(lhs) != type(rhs):
    raise CSlangError("Type mismatch between registers {} and {}"
                      .format(p[1][1], p[3][1]))

  if type(lhs) == str:
    p[0] = ('STRING', str(lhs) + str(rhs))
  elif type(rhs) == float:
    p[0] = ('NUMERIC', float(lhs) + float(rhs))
  else:
    raise CSlangError("Bad type in string concatenation: {}".format(p[1]))


def p_registerconcat(p):
  ''' registerconcat : IDENTIFIER '+' STRING_LITERAL
                     | STRING_LITERAL '+' IDENTIFIER
                     | STRING_LITERAL '+' STRING_LITERAL
  '''

  if p[1][0] == "IDENTIFIER":
    lhs = automaton.registers[p[1][1]]
  elif p[1][0] == "STRING":
    lhs = p[1][1]
  else:
    raise CSlangError("Bad type in string concatenation: {}".format(p[1]))

  if p[3][0] == "IDENTIFIER":
    rhs = automaton.registers[p[3][1]]
  elif p[3][0] == "STRING":
    rhs = p[3][1]
  else:
    raise CSlangError("Bad type in string concatenation: {}".format(p[1]))

  p[0] = ('STRING', str(lhs) + str(rhs))


def p_registeradd(p):
  ''' registeradd : IDENTIFIER '+' NUM_LITERAL
                  | NUM_LITERAL '+' IDENTIFIER
                  | NUM_LITERAL '+' NUM_LITERAL
  '''

  if p[1][0] == 'IDENTIFIER':
    lhs = automaton.registers[p[1][1]]
  elif p[1][0] == 'NUM_LITERAL':
    lhs = p[1][1]
  else:
    raise CSlangError("Bad type in addition: {}".format(p[1]))

  if p[3][0] == 'IDENTIFIER':
    rhs = automaton.registers[p[3][1]]
  elif p[3][0] == 'NUM_LITERAL':
    rhs = p[3][1]
  else:
    raise CSlangError("Bad type in addition: {}".format(p[3]))

  p[0] = ('NUMERIC', float(lhs) + float(rhs))

def p_registersub(p):
  ''' registersub : IDENTIFIER '-' IDENTIFIER
                  | IDENTIFIER '-' NUM_LITERAL
                  | NUM_LITERAL '-' IDENTIFIER
                  | NUM_LITERAL '-' NUM_LITERAL
  '''

  if p[1][0] == 'IDENTIFIER':
    lhs = automaton.registers[p[1][1]]
  elif p[1][0] == 'NUM_LITERAL':
    lhs = p[1][1]
  else:
    raise CSlangError("Bad type in substraction: {}".format(p[1]))

  if p[3][0] == 'IDENTIFIER':
    rhs = automaton.registers[p[3][1]]
  elif p[3][0] == 'NUM_LITERAL':
    rhs = p[3][1]
  else:
    raise CSlangError("Bad type in substraction: {}".format(p[3]))

  p[0] = ('NUMERIC', float(lhs) - float(rhs))

def p_registermul(p):
  ''' registermul : IDENTIFIER '*' IDENTIFIER
                  | IDENTIFIER '*' NUM_LITERAL
                  | NUM_LITERAL '*' IDENTIFIER
                  | NUM_LITERAL '*' NUM_LITERAL
  '''

  if p[1][0] == 'IDENTIFIER':
    lhs = automaton.registers[p[1][1]]
  elif p[1][0] == 'NUM_LITERAL':
    lhs = p[1][1]
  else:
    raise CSlangError("Bad type in substraction: {}".format(p[1]))

  if p[3][0] == 'IDENTIFIER':
    rhs = automaton.registers[p[3][1]]
  elif p[3][0] == 'NUM_LITERAL':
    rhs = p[3][1]
  else:
    raise CSlangError("Bad type in substraction: {}".format(p[3]))

  p[0] = ('NUMERIC', float(lhs) * float(rhs))

def p_registerdiv(p):
  ''' registerdiv : IDENTIFIER '/' IDENTIFIER
                  | IDENTIFIER '/' NUM_LITERAL
                  | NUM_LITERAL '/' IDENTIFIER
                  | NUM_LITERAL '/' NUM_LITERAL
  '''
  if p[1][0] == 'IDENTIFIER':
    lhs = automaton.registers[p[1][1]]
  elif p[1][0] == 'NUM_LITERAL':
    lhs = p[1][1]
  else:
    raise CSlangError("Bad type in substraction: {}".format(p[1]))

  if p[3][0] == 'IDENTIFIER':
    rhs = automaton.registers[p[3][1]]
  elif p[3][0] == 'NUM_LITERAL':
    rhs = p[3][1]
  else:
    raise CSlangError("Bad type in substraction: {}".format(p[3]))

  p[0] = ('NUMERIC', float(lhs) / float(rhs))


def p_dataword(p):
  ''' dataword : NOT IDENTIFIER '(' parameterexpression ')'
               | IDENTIFIER '(' parameterexpression ')'
               | NOT IDENTIFIER '(' parameterexpression ')' WITH predexpressionlist
               | IDENTIFIER '(' parameterexpression ')' WITH predexpressionlist
  '''


  global preamble
  global automaton
  if p[1][1] == "NOT":
    not_dataword = True
    syscall_name = p[2][1]
    operations = p[4][1]
    if len(p) == 8:
      predicates = p[7][1:]
      p[0] = (p[1][1], p[2][1], p[4], p[7])
    else:
      predicates = None
      p[0] = (p[1][1], p[2][1], p[4])
  else:
    not_dataword = False
    syscall_name = p[1][1]
    operations = p[3][1]
    if len(p) == 7:
      predicates = p[6][1:]
      p[0] = (p[1][1], p[3], p[6])
    else:
      predicates = None
      p[0] = (p[1][1], p[3])


  if not_dataword:
    #  This is a not dataword so we create our NOT state
    automaton.states.append(State(syscall_name, tags=["NOT"]))

    # And make a transition to it with appropriate register_matches
    automaton.states[-2].transitions.append(Transition(syscall_name,
                                            len(automaton.states) - 1,
                                            operations=operations))

  else:
    # We encountered a new dataword so we make a new state
    automaton.states.append(State(syscall_name, operations))

    # We create a transition to this state on the previous state

    # The state we just added is in automaton.states[-1] so we need to start
    # with automaton.states[-2] and keep searching back until we hit a non-NOT
    # state.  This is the state to which we will add a transition to the new state
    # we just added.

    neg_index = -2
    while "NOT" in automaton.states[neg_index].tags:
      neg_index -= 1

    automaton.states[neg_index].transitions.append(Transition(syscall_name,
                                                              len(automaton.states) - 1,
                                                              operations=operations,
                                                              predicates=predicates))

def p_parameterexpression(p):
  ''' parameterexpression : '{' parameterlist '}'
                          | '{' '}'
  '''
  if len(p) == 3:
    p[0] = ("PARAMETEREXPRESSION", None)
  else:
    p[0] = ("PARAMETEREXPRESSION", p[2])



def p_parameterlist(p):
  '''parameterlist : parameter ',' parameterlist
                   | parameter
  '''

  if len(p) == 4:
    p[0] = (p[1], ) + p[3]
  else:
    p[0] = (p[1], )



def p_parameter(p):
  '''parameter : IDENTIFIER ':' READOP IDENTIFIER
               | IDENTIFIER ':' STOREOP  IDENTIFIER
               | IDENTIFIER ':' WRITEOP IDENTIFIER
               | IDENTIFIER ':' parameterexpression
  '''

  if p[3][0] == "PARAMETEREXPRESSION":
    # HACK: We use # to denote that this parameter has a non-primative type
    p[0] = ("#", p[1][1], p[3][1])
  else:
    p[0] = (p[3][1], p[1][1], p[4][1])





def main(args=None):
  global t_ignore
  global reserved
  global tokens
  global in_preamble
  global lexer
  global parser
  global automaton
  global preamble
  global containerbuilder

  parser = argparse.ArgumentParser()
  subparsers = parser.add_subparsers(dest="mode", help="input mode")

  parse_argparser = subparsers.add_parser("parse")
  parse_argparser.add_argument("-c", "--cslang-path",
                                        required=False,
                                        type=str,
                                        help="CSlang file to be parsed"
  )
  parse_argparser.add_argument("-s", "--string",
                                        required=False,
                                        type=str,
                                        help="String to parse"
  )

  build_argparser = subparsers.add_parser("build")

  build_argparser.add_argument("-c", "--cslang-path",
                                        required=True,
                                        type=str,
                                        help="CSlang file to be compiled"
  )

  run_subparsers = subparsers.add_parser("run")
  run_subparsers = run_subparsers.add_subparsers(dest="format", help="input format")

  strace_run_argparser = run_subparsers.add_parser("strace")

  strace_run_argparser.add_argument("-a", "--automaton-path",
                                    required=True,
                                    type=str,
                                    help="Location of CSlang automaton to be used in processing the specified strace file."
  )
  strace_run_argparser.add_argument("-s", "--strace-path",
                                    required=True,
                                    type=str,
                                    help="Location of strace recording to execute against"
  )
  strace_run_argparser.add_argument("-d", "--syscall-definitions",
                                        required=True,
                                        type=str,
                                        help="Location of posix-omni-parser syscall definitions file"
  )

  jsonrpc_run_argparser = run_subparsers.add_parser("jsonrpc")


  jsonrpc_run_argparser.add_argument("-a", "--automaton-path",
                                     required=True,
                                     type=str,
                                     help="Location of CSlang automaton to be used in processing the specified strace file."
  )
  jsonrpc_run_argparser.add_argument("-j", "--json-path",
                                     required=True,
                                     type=str,
                                     help="Location of strace recording to execute against"
  )


  if not args:
    args = parser.parse_args()


  in_preamble = True
  lexer = lex.lex()
  parser = yacc.yacc()
  automaton = RegisterAutomaton()
  containerbuilder = ContainerBuilder()


  if args.mode == "parse":
    if args.cslang_path:
      with open(args.cslang_path, "r") as f:
        data = f.read()

    if args.string:
      data = args.string

    result = parser.parse(data)
    pp = pprint.PrettyPrinter(indent=2)
    pp.pprint(result)
    return result

  if args.mode == "build":
      basename = os.path.splitext(os.path.basename(args.cslang_path))[0]
      dirname = os.path.dirname(args.cslang_path)
      automaton_path = os.path.join(dirname, basename + ".auto")
      cb_path = os.path.join(dirname, basename + ".cb")

      with open(args.cslang_path, "r") as f:
        parser.parse(f.read(), debug=False)

      with open(automaton_path, "w") as f:
        pickle.dump((automaton, containerbuilder), f)

      return automaton, containerbuilder






  elif args.mode == "run":
    if args.format == "strace":

      strace_path = args.strace_path
      automaton_path = args.automaton_path
      syscall_definitions = args.syscall_definitions


      # Load in the automaton
      with open(automaton_path, "r") as f:
        automaton, cb = pickle.load(f)

      s2d = StraceToDatawords(cb, syscall_definitions, strace_path)
      datawords = s2d.get_datawords()

      # Pass each dataword in the list in series into the automaton
      for i in datawords:
        automaton.match(i)


      # At the end of everything we have a transformed set of datawords.
      # We either use them if we ended in an accepting state or drop ignore
      # them if we haven't ended in an accepting state
      # Some print goes here
      print("Automaton ended in state: " + str(automaton.current_state))
      print("With registers: " + str(automaton.registers))

      for i in datawords:
        print(s2d.get_mutated_strace(i))

      return automaton, datawords, s2d

    elif args.format == "jsonrpc":

      json_path = args.json_path
      automaton_path = args.automaton_path

      # Load in the automaton
      with open(automaton_path, "r") as f:
        automaton, cb = pickle.load(f)


      j2d = JSONToDatawords(cb, json_path)
      datawords = j2d.get_datawords()

      # Pass each dataword in the list in series into the automaton
      for i in datawords:
        automaton.match(i)


      # At the end of everything we have a transformed set of datawords.
      # We either use them if we ended in an accepting state or drop ignore
      # them if we haven't ended in an accepting state
      # Some print goes here
      print("Automaton ended in state: " + str(automaton.current_state))
      print("With registers: " + str(automaton.registers))


      for i in datawords:
        print(j2d.get_mutated_json(i))


      return automaton, datawords, j2d


in_preamble = None
lexer = None
parser = None
automaton = None
containerbuilder = None

if __name__ == "__main__":
  main()

