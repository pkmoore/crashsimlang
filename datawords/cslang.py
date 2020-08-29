from ply import lex
from ply import yacc
from register_automaton import RegisterAutomaton
from register_automaton import State
from register_automaton import Transition
from strace2datawords import Preamble
from strace2datawords import DataWord
from strace2datawords import UninterestingDataWord
from posix_omni_parser import Trace
import pickle
import os
import sys


class CSlangError(Exception):
  pass


reserved = {
    'capture' : 'CAPTURE',
    'predicate' : 'PREDICATE',
    'as' : 'AS',
    'ret' : 'RET'
}

tokens = ["IDENTIFIER",
          "LPAREN",
          "READOP",
          "STOREOP",
          "WRITEOP",
          "EQUALSOP",
          "ASSIGN",
          "NUMERIC",
          "ASSIGNVALUE",
          "PARAMSEP",
          "RPAREN",
          "SEMI"
] + list(reserved.values())


t_LPAREN = r"\("
t_READOP = r"\?"
t_STOREOP = r"\!"
t_WRITEOP = r"->"
t_EQUALSOP = r"=="
t_ASSIGN = r"<-"
t_NUMERIC = r"[0-9][0-9]*"
t_RPAREN = r"\)"
t_PARAMSEP = r",[\s]*"
t_SEMI = r";"
t_ignore = " \t\n"

# We use a function to define this function for two reasons:
# 1. Ply gives tokens defined by functions higher priority meaning this
# rule will be used for ambiguous stuff that could be an identifier or
# could be a keyword.
# 2. We can define logic to figure out if something is a keyword rather
# than an identifier and return the appropriate type
def t_IDENTIFIER(t):
  r"[A-Za-z_][a-zA-Z0-9]*"
  t.type = reserved.get(t.value, 'IDENTIFIER')
  return t

def t_ASSIGNVALUE(t):
  r"\".*\""
  tmp = t.value
  if tmp.startswith("\"") and tmp.endswith("\""):
    tmp = tmp[1:-1]

  t.value = tmp
  return t

def t_error(t):
  pass

def t_COMMENT(t):
  r'\#.*'

lexer = lex.lex()

automaton = RegisterAutomaton()
preamble = Preamble()
in_preamble = True

def p_error(p):
  print("Error with:")
  print(p)

def p_statementlist(p):
  ''' statementlist : statement  statementlist
                    | statement
  '''

def p_statement(p):
  ''' statement : dataword SEMI
                | registerassignment SEMI
                | capturestmt SEMI
                | predicatestmt SEMI
  '''


def p_capturestmt(p):
  ''' capturestmt : CAPTURE IDENTIFIER NUMERIC AS IDENTIFIER
                  | CAPTURE IDENTIFIER RET AS IDENTIFIER
  '''


  global in_preamble
  if in_preamble:
    if p[3] == "ret":
      preamble.capture(p[2], p[5], "ret")
    else:
      preamble.capture(p[2], p[5], p[3])
  else:
    raise CSlangError("Found capture statement after preamble processing has ended")


def p_expression(p):
  ''' expression : IDENTIFIER EQUALSOP ASSIGNVALUE
  '''

  if p[2] == "==":
    # Form a closure over p[1] and p[3] using new names i and v so copies of these
    # values are available when the predicate is called elsewhere during evaluation
    i = p[1]
    v = p[3]
    def equalsexpression(args):
      return args[i]["value"].value == v
    p[0] = equalsexpression


def p_predicatestmt(p):
  ''' predicatestmt : PREDICATE IDENTIFIER expression
  '''

  global in_preamble
  if in_preamble:
    preamble.predicate(p[2], p[3])
  else:
    raise CSlangError("Found predicate statement after preamble processing has ended")


def p_registerassignment(p):
  ''' registerassignment : IDENTIFIER ASSIGN ASSIGNVALUE
  '''

  global in_preamble
  in_preamble = False
  automaton.registers[p[1]] = p[3]


def p_dataword(p):
  ''' dataword : IDENTIFIER LPAREN parameterlist RPAREN
  '''

  global in_preamble
  in_preamble = False
  register_matches = []
  register_stores = []
  register_writes = []
  for i, v in enumerate(p[3]):
    if v.startswith("?"):
      # When we see the "?" operator it means in order to get into this state,
      # the register name following "?" needs to have the same value as the
      # captured argument in the same position in the data word.  For example:
      #
      # open(?filedesc);
      #
      # means that in order to transition to the next state, the current
      # dataword must represent an open system call with captured argument 0
      # matching the value in the filedesc register.  Captured argument order
      # is important and comes from the order the captures are specified in the
      # preamble
      register_matches.append((i, v[1:]))

    if v.startswith("!"):
      # When we see "!" it means take the value from the captured argument
      # corresponding to this parameter's position in the current dataword and
      # store it into the following register value.  We do this by specifying
      # register_store tuple that looks like (<captured_arg_position>,
      # <register_value>).  These register stores are performed whenever we
      # transition into a new state so we give them to the new State being
      # created below
      register_stores.append((i, v[1:]))

    if v.startswith("->"):
      register_writes.append((i, v[2:]))

  # We encountered a new dataword so we make a new state
  automaton.states.append(State(p[1],
                          register_stores=register_stores,
                          register_writes=register_writes))

  # We create a transition to this state on the previous state
  automaton.states[-2].transitions.append(Transition(p[1],
                                          register_matches,
                                          len(automaton.states) - 1))


def p_parameterlist(p):
  '''parameterlist : parameter PARAMSEP parameterlist
                   | parameter
  '''

  if len(p) == 4:
    p[0] = [p[1]] + p[3]
  else:
    p[0] = [p[1]]



def p_parameter(p):
  '''parameter : READOP IDENTIFIER
               | STOREOP IDENTIFIER
               | WRITEOP IDENTIFIER
               | IDENTIFIER
  '''
  if len(p) == 3:
    p[0] = p[1] + p[2]
  else:
    p[0] =  p[1]



parser = yacc.yacc()
with open(sys.argv[1], "r") as f:
  parser.parse(f.read())

basename = os.path.splitext(os.path.basename(sys.argv[1]))[0]
strace_path = basename + ".strace"
datawords_path = basename + ".dw"
pickle_path = basename + ".pickle"

t = Trace.Trace(strace_path, "./syscall_definitions.pickle")

datawords = []
with open(datawords_path, "w") as f:
  for i in t.syscalls:
    d = preamble.handle_syscall(i)
    f.write(d.get_dataword() + "\n")
    datawords.append(d)

with open(pickle_path, "w") as f:
  pickle.dump(datawords, f)

with open(basename + ".auto", "w") as f:
  pickle.dump(automaton, f)





# This is to parse the program that is going to read the datawords that will be incoming from the preprocessor
# each dataword parsed defines the transition requirements from the current state to the next
#  the datawords being generated will have data in them.  The program will only have identifiers
# This thing needs to generate instructions or whatever to do the transitioning and reading registers and all that
# output an automaton object



# The "choice" operatior "|" would be a case where we have a branch in the automaton.
