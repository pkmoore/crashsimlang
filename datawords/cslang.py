from ply import lex

from ply import yacc

class RegisterAutomaton:
  def __init__(self):
    self.states = []
    self.states.append(State("startstate"))
    self.registers = {}

class State:
  def __init__(self, name):
    self.name = name
    self.transitions = []


class Transition:
  def __init__(self, dataword_name):
    self.dataword_name = None
    self.register_requirements = {}




tokens = ("IDENTIFIER",
          "LPAREN",
          "READOP",
          "WRITEOP",
          "PARAMSEP",
          "RPAREN",
          "SEMI"
)

t_IDENTIFIER = r"[a-zA-Z0-9]+"
t_LPAREN = r"\("
t_READOP = r"\?"
t_WRITEOP= r"\!"
t_RPAREN = r"\)"
t_PARAMSEP = r",[\s]*"
t_SEMI = r";"
t_ignore = r" "

lexer = lex.lex()

test = """testword(!param1, ?param2);"""


lexer.input(test)

#while True:
#  tok = lexer.token()
#  if not tok:
#    break
#  print(tok)


automaton = RegisterAutomaton()

temp_params = []

def p_datawordlist(p):
  ''' datawordlist : dataword SEMI datawordlist
                   | dataword SEMI
  '''


def p_dataword(p):
  ''' dataword : IDENTIFIER LPAREN parameterlist RPAREN
  '''

  automaton.states.append(State(p[1]))
  automaton.states[-1].transitions.append(Transition(p[1])


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
parser.parse('testword(!alpha, ?bob);')





# This is to parse the program that is going to read the datawords that will be incoming from the preprocessor
# each dataword parsed defines the transition requirements from the current state to the next
#  the datawords being generated will have data in them.  The program will only have identifiers
# This thing needs to generate instructions or whatever to do the transitioning and reading registers and all that
# output an automaton object
