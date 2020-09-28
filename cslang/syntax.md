```ASSIGNOP: <-

EQUALSOP: ==

READOP: ?

STOREOP: !

_WRITEOP: ->

_NUM_LITERAL: -?[0-9][0-9]*(\.[0-9]+)?

STRING_LITERAL: "[^"]+"

IDENTIFIER: [A-Za-z_][a-zA-Z0-9]*

COMMENT: #

statementlist : statement  statementlist  
                 | statement  

statement : preamblestatement
          | bodystatement

preamblestatement : predicatestmt ';'
                  | definestmt ';'

bodystatement : dataword ';'
              | registerassignment ';'

type : IDENTIFIER NUM_LITERAL AS IDENTIFIER
     | IDENTIFIER RET AS IDENTIFIER

typelist : type ',' typelist
         | type

definestmt : DEFINE IDENTIFIER typelist

predexpression : IDENTIFIER EQUALSOP NUM_LITERAL

predicatestmt : PREDICATE IDENTIFIER predexpression

registerassignment : IDENTIFIER ASSIGNOP NUM_LITERAL
                   | IDENTIFIER ASSIGNOP STRING_LITERAL
                   | IDENTIFIER ASSIGNOP IDENTIFIER
                   | IDENTIFIER ASSIGNOP registerexp

registerexp : registeradd
            | registersub
            | registermul
            | registerdiv
            | registerconcat
            | registeraddorconcat

registeraddorconcat : IDENTIFIER '+' IDENTIFIER

registerconcat : IDENTIFIER '+' STRING_LITERAL
               | STRING_LITERAL '+' IDENTIFIER
               | STRING_LITERAL '+' STRING_LITERAL

registeradd : IDENTIFIER '+' NUM_LITERAL
            | NUM_LITERAL '+' IDENTIFIER
            | NUM_LITERAL '+' NUM_LITERAL

registersub : IDENTIFIER '-' IDENTIFIER
            | IDENTIFIER '-' NUM_LITERAL
            | NUM_LITERAL '-' IDENTIFIER
            | NUM_LITERAL '-' NUM_LITERAL

registermul : IDENTIFIER '*' IDENTIFIER
            | IDENTIFIER '*' NUM_LITERAL
            | NUM_LITERAL '*' IDENTIFIER
            | NUM_LITERAL '*' NUM_LITERAL

registerdiv : IDENTIFIER '/' IDENTIFIER
            | IDENTIFIER '/' NUM_LITERAL
            | NUM_LITERAL '/' IDENTIFIER
            | NUM_LITERAL '/' NUM_LITERAL

dataword : NOT IDENTIFIER '(' parameterlist ')'
         | IDENTIFIER '(' parameterlist ')'

parameterlist : parameter ',' parameterlist
              | parameter

parameter : READOP IDENTIFIER
          | STOREOP IDENTIFIER
          | WRITEOP IDENTIFIER
          | IDENTIFIER

```
