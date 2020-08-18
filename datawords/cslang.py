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

  # We encountered a new dataword so we make a new state
  automaton.states.append(State(p[1]))
  # We create a transition to this state on the previous state
  automaton.states[-2].transitions.append(Transition(p[1], len(automaton.states) - 1))


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
