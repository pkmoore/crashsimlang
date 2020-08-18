from ply import lex
from ply import yacc
from register_automaton import RegisterAutomaton
from register_automaton import State
from register_automaton import Transition
import pickle
import os
import sys



tokens = ("IDENTIFIER",
          "LPAREN",
          "READOP",
          "WRITEOP",
          "ASSIGN",
          "PARAMSEP",
          "RPAREN",
          "SEMI"
)

t_IDENTIFIER = r"[a-zA-Z0-9]+"
t_LPAREN = r"\("
t_READOP = r"\?"
t_WRITEOP= r"\!"
t_ASSIGN = r"<-"
t_RPAREN = r"\)"
t_PARAMSEP = r",[\s]*"
t_SEMI = r";"
t_ignore = " \t\n"

def t_error(t):
  pass

def t_COMMENT(t):
  r'\#.*'

lexer = lex.lex()

automaton = RegisterAutomaton()


def p_expressionlist(p):
  ''' expressionlist : expression SEMI expressionlist
                     | expression SEMI
  '''

def p_expression(p):
  ''' expression : dataword
                 | registerassignment
  '''


def p_registerassignment(p):
  ''' registerassignment : IDENTIFIER ASSIGN parameter
  '''

  automaton.registers[p[1]] = p[3]


def p_dataword(p):
  ''' dataword : IDENTIFIER LPAREN parameterlist RPAREN
  '''

  register_matches = []
  register_stores = []
  for i, v in enumerate(p[3]):
    if v[0] == "?":
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
    if v[0] == "!":


      # When we see "!" it means take the value from the captured argument
      # corresponding to this parameter's position in the current dataword and
      # store it into the following register value.  We do this by specifying
      # register_store tuple that looks like (<captured_arg_position>,
      # <register_value>).  These register stores are performed whenever we
      # transition into a new state so we give them to the new State being
      # created below
      register_stores.append((i, v[1:]))

  # We encountered a new dataword so we make a new state
  automaton.states.append(State(p[1], register_stores=register_stores))

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
               | WRITEOP IDENTIFIER
               | IDENTIFIER
  '''
  if len(p) == 3:
    p[0] = p[1] + p[2]
  else:
    p[0] =  p[1]



parser = yacc.yacc()
basename = os.path.splitext(os.path.basename(sys.argv[1]))[0]
with open(sys.argv[1], "r") as f:
  parser.parse(f.read())
with open(basename + ".auto", "w") as f:
  pickle.dump(automaton, f)





# This is to parse the program that is going to read the datawords that will be incoming from the preprocessor
# each dataword parsed defines the transition requirements from the current state to the next
#  the datawords being generated will have data in them.  The program will only have identifiers
# This thing needs to generate instructions or whatever to do the transitioning and reading registers and all that
# output an automaton object



# The "choice" operatior "|" would be a case where we have a branch in the automaton.
