from ply import lex
from ply import yacc
from register_automaton import RegisterAutomaton
from register_automaton import State
from register_automaton import Transition
from strace2datawords import Preamble
from strace2datawords import DataWord
from strace2datawords import UninterestingDataWord
from posix_omni_parser import Trace
from adt import ContainerBuilder
from cslang_error import CSlangError
import pickle
import os
import sys


reserved = {
    'predicate' : 'PREDICATE',
    'NOT' : 'NOT',
    'as' : 'AS',
    'ret' : 'RET',
    'define' : 'DEFINE',
    'Int' : 'INT',
    'String' : 'STRING'
}

tokens = ["IDENTIFIER",
          "READOP",
          "STOREOP",
          "WRITEOP",
          "EQUALSOP",
          "ASSIGNOP",
          "NUMERIC",
] + list(reserved.values())

literals = ['.', '/', '*', '-', '+', ';',',','(', ')' ]

precedence = (
    ('left', 'ASSIGNOP'),
    ('left', '+', '-', '.'),
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

def t_NUMERIC(t):
  r"[0-9][0-9]*(\.[0-9]+)?"
  t.value = ("NUMERIC", t.value)
  return t

def t_STRING(t):
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

def p_statement(p):
  ''' statement : preamblestatement
                | bodystatement
  '''

def p_preamblestatement(p):
  ''' preamblestatement : predicatestmt ';'
                        | definestmt ';'
  '''
  global in_preamble
  if not in_preamble:
    raise CSlangError("Found preamble statment after preamble processing has ended")

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
    preamble.inject_containerbuilder(containerbuilder)


def p_type(p):
  ''' type : INT NUMERIC AS IDENTIFIER
           | INT RET AS IDENTIFIER
           | STRING NUMERIC AS IDENTIFIER
           | STRING RET AS IDENTIFIER
  '''

  p[0] = (p[1][1], p[2][1], p[4][1])


def p_typelist(p):
  ''' typelist : type ',' typelist
               | type
  '''

  if len(p) == 4:
    p[0] = [p[1]] + p[3]
  else:
    p[0] = [p[1]]


def p_definestmt(p):
  ''' definestmt : DEFINE IDENTIFIER typelist

  '''

  global containerbuilder
  containerbuilder.define_type(p[2][1], p[3])



def p_predexpression(p):
  ''' predexpression : IDENTIFIER EQUALSOP NUMERIC
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
  ''' predicatestmt : PREDICATE IDENTIFIER predexpression
  '''

  global preamble
  global preamble
  preamble.predicate(p[2], p[3])


def p_registerassignment(p):
  ''' registerassignment : IDENTIFIER ASSIGNOP NUMERIC
                         | IDENTIFIER ASSIGNOP STRING
                         | IDENTIFIER ASSIGNOP registerexp
  '''

  global automaton
  if p[1][0] != 'IDENTIFIER':
    raise CSLangError("Bad type for register name: {}".format(p[1]))
  register_name = p[1][1]
  if p[3][0] == 'NUMERIC':
    automaton.registers[register_name] = float(p[3][1])
  elif p[3][0] == 'STRING':
    automaton.registers[register_name] = str(p[3][1])
  else:
    raise CSlangError("Bad type in register assignment: {}".format(p[3]))

def p_registerexp(p):
  ''' registerexp : registeradd
                  | registersub
                  | registermul
                  | registerdiv
                  | registerconcat
  '''

  p[0] = p[1]

def p_registerconcat(p):
  ''' registerconcat : IDENTIFIER '.' IDENTIFIER
                     | IDENTIFIER '.' STRING
                     | STRING '.' IDENTIFIER
                     | STRING '.' STRING
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
  ''' registeradd : IDENTIFIER '+' IDENTIFIER
                  | IDENTIFIER '+' NUMERIC
                  | NUMERIC '+' IDENTIFIER
                  | NUMERIC '+' NUMERIC
  '''

  if p[1][0] == 'IDENTIFIER':
    lhs = automaton.registers[p[1][1]]
  elif p[1][0] == 'NUMERIC':
    lhs = p[1][1]
  else:
    raise CSlangError("Bad type in substraction: {}".format(p[1]))

  if p[3][0] == 'IDENTIFIER':
    rhs = automaton.registers[p[3][1]]
  elif p[3][0] == 'NUMERIC':
    rhs = p[3][1]
  else:
    raise CSlangError("Bad type in substraction: {}".format(p[3]))

  p[0] = ('NUMERIC', float(lhs) + float(rhs))

def p_registersub(p):
  ''' registersub : IDENTIFIER '-' IDENTIFIER
                  | IDENTIFIER '-' NUMERIC
                  | NUMERIC '-' IDENTIFIER
                  | NUMERIC '-' NUMERIC
  '''

  if p[1][0] == 'IDENTIFIER':
    lhs = automaton.registers[p[1][1]]
  elif p[1][0] == 'NUMERIC':
    lhs = p[1][1]
  else:
    raise CSlangError("Bad type in substraction: {}".format(p[1]))

  if p[3][0] == 'IDENTIFIER':
    rhs = automaton.registers[p[3][1]]
  elif p[3][0] == 'NUMERIC':
    rhs = p[3][1]
  else:
    raise CSlangError("Bad type in substraction: {}".format(p[3]))

  p[0] = ('NUMERIC', float(lhs) - float(rhs))

def p_registermul(p):
  ''' registermul : IDENTIFIER '*' IDENTIFIER
                  | IDENTIFIER '*' NUMERIC
                  | NUMERIC '*' IDENTIFIER
                  | NUMERIC '*' NUMERIC
  '''

  if p[1][0] == 'IDENTIFIER':
    lhs = automaton.registers[p[1][1]]
  elif p[1][0] == 'NUMERIC':
    lhs = p[1][1]
  else:
    raise CSlangError("Bad type in substraction: {}".format(p[1]))

  if p[3][0] == 'IDENTIFIER':
    rhs = automaton.registers[p[3][1]]
  elif p[3][0] == 'NUMERIC':
    rhs = p[3][1]
  else:
    raise CSlangError("Bad type in substraction: {}".format(p[3]))

  p[0] = ('NUMERIC', float(lhs) * float(rhs))

def p_registerdiv(p):
  ''' registerdiv : IDENTIFIER '/' IDENTIFIER
                  | IDENTIFIER '/' NUMERIC
                  | NUMERIC '/' IDENTIFIER
                  | NUMERIC '/' NUMERIC
  '''
  if p[1][0] == 'IDENTIFIER':
    lhs = automaton.registers[p[1][1]]
  elif p[1][0] == 'NUMERIC':
    lhs = p[1][1]
  else:
    raise CSlangError("Bad type in substraction: {}".format(p[1]))

  if p[3][0] == 'IDENTIFIER':
    rhs = automaton.registers[p[3][1]]
  elif p[3][0] == 'NUMERIC':
    rhs = p[3][1]
  else:
    raise CSlangError("Bad type in substraction: {}".format(p[3]))

  p[0] = ('NUMERIC', float(lhs) / float(rhs))


def p_dataword(p):
  ''' dataword : NOT IDENTIFIER '(' parameterlist ')'
               | IDENTIFIER '(' parameterlist ')'
  '''

  global preamble
  global automaton
  if p[1][1] == "NOT":
    not_dataword = True
    syscall_name = p[2][1]
    params = p[4]
  else:
    not_dataword = False
    syscall_name = p[1][1]
    params = p[3]

  register_matches = []
  register_stores = []
  register_writes = []
  for i, v in enumerate(params):
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
      if not_dataword:
        raise CSlangError("Register stores are illegal in NOT datawords")
      # When we see "!" it means take the value from the captured argument
      # corresponding to this parameter's position in the current dataword and
      # store it into the following register value.  We do this by specifying
      # register_store tuple that looks like (<captured_arg_position>,
      # <register_value>).  These register stores are performed whenever we
      # transition into a new state so we give them to the new State being
      # created below
      register_stores.append((i, v[1:]))

    if v.startswith("->"):
      if not_dataword:
        raise CSlangError("Write operations are illegal in NOT datawords")
      register_writes.append((i, v[2:]))

  if not_dataword:
    #  This is a not dataword so we create our NOT state
    automaton.states.append(State(syscall_name, tags=["NOT"]))

    # And make a transition to it with appropriate register_matches
    automaton.states[-2].transitions.append(Transition(syscall_name,
                                            register_matches,
                                            len(automaton.states) - 1))

  else:
    # We encountered a new dataword so we make a new state
    automaton.states.append(State(syscall_name,
                            register_stores=register_stores,
                            register_writes=register_writes))

    # We create a transition to this state on the previous state

    # The state we just added is in automaton.states[-1] so we need to start
    # with automaton.states[-2] and keep searching back until we hit a non-NOT
    # state.  This is the state to which we will add a transition to the new state
    # we just added.

    neg_index = -2
    while "NOT" in automaton.states[neg_index].tags:
      neg_index -= 1

    automaton.states[neg_index].transitions.append(Transition(syscall_name,
                                                              register_matches,
                                                              len(automaton.states) - 1))


def p_parameterlist(p):
  '''parameterlist : parameter ',' parameterlist
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
    p[0] = p[1][1] + p[2][1]
  else:
    p[0] =  p[1][1]




def main(name, parse_only=False):
  global t_ignore
  global reserved
  global tokens
  global in_preamble
  global lexer
  global parser
  global automaton
  global preamble
  global containerbuilder


  in_preamble = True
  lexer = lex.lex()
  parser = yacc.yacc()
  automaton = RegisterAutomaton()
  preamble = Preamble()
  containerbuilder = ContainerBuilder()
  with open(name, "r") as f:
    parser.parse(f.read())

  if not parse_only:
    basename = os.path.splitext(os.path.basename(name))[0]
    dirname = os.path.dirname(name)
    strace_path = os.path.join(dirname, basename + ".strace")
    datawords_path = os.path.join(dirname, basename + ".dw")
    pickle_path = os.path.join(dirname, basename + ".pickle")
    automaton_path = os.path.join(dirname, basename + ".auto")

    t = Trace.Trace(strace_path, "./syscall_definitions.pickle")

    datawords = []
    with open(datawords_path, "w") as f:
      for i in t.syscalls:
        d = preamble.handle_syscall(i)
        f.write(d.get_dataword() + "\n")
        datawords.append(d)

    with open(pickle_path, "w") as f:
      pickle.dump(datawords, f)

    with open(automaton_path, "w") as f:
      pickle.dump(automaton, f)





  # This is to parse the program that is going to read the datawords that will be incoming from the preprocessor
  # each dataword parsed defines the transition requirements from the current state to the next
  #  the datawords being generated will have data in them.  The program will only have identifiers
  # This thing needs to generate instructions or whatever to do the transitioning and reading registers and all that
  # output an automaton object



# The "choice" operatior "|" would be a case where we have a branch in the automaton.

in_preamble = None
lexer = None
parser = None
automaton = None
preamble = None
containerbuilder = None

if __name__ == "__main__":
  main(sys.argv[1])

