from __future__ import print_function
from __future__ import absolute_import
from builtins import str
from ply import lex
from ply import yacc
from .register_automaton import RegisterAutomaton
from .register_automaton import State
from .register_automaton import Transition
from .strace2datawords import StraceToDatawords
from .jsontodatawords import JSONToDatawords
from .xmltodatawords import XMLToDatawords
from .csvtodatawords import CSVToDatawords
from .usbjsontodatawords import USBJSONToDatawords
from posix_omni_parser import Trace
from .adt import ContainerBuilder
from . import automaton_builder
from . import type_checker
from .port_error import PORTError
import dill as pickle
import os
import sys
import argparse
import pprint


reserved = {"NOT": "NOT", "ret": "RET", "event": "EVENT", "with": "WITH", "and": "AND"}

tokens = [
    "IDENTIFIER",
    "READOP",
    "STOREOP",
    "WRITEOP",
    "EQUALSOP",
    "ASSIGNOP",
    "NUM_LITERAL",
    "STRING_LITERAL",
] + list(reserved.values())

literals = [
    ".",
    "{",
    "}",
    ":",
    "@",
    "/",
    "*",
    "-",
    "+",
    ";",
    ",",
    "(",
    ")",
    "|",
    "[",
    "]",
]

precedence = (
    ("left", "ASSIGNOP"),
    ("left", "+", "-"),
    ("left", "*", "/"),
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
    '"[^"]+"'
    t.value = ("STRING_LITERAL", t.value[1:-1])
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
    raise PORTError("Lex error with: {}".format(t))


def t_COMMENT(t):
    r"\#.*"


def p_error(p):
    raise PORTError("Parse error with: {}".format(p))


def p_statementlist(p):
    """statementlist : statement  statementlist
    | statement
    """
    if len(p) == 3:
        p[0] = [p[1]] + p[2]
    else:
        p[0] = [p[1]]


def p_statement(p):
    """statement : preamblestatement
    | bodystatement
    """
    p[0] = p[1]


def p_preamblestatement(p):
    """preamblestatement : typedefinition ';'
    | variantdefinition ';'
    """
    global in_preamble
    if not in_preamble:
        raise PORTError("Found preamble statement after preamble processing has ended")

    p[0] = p[1]


def p_repetition(p):
    """repetition : '[' datawordlist ']' NUM_LITERAL
    | '[' datawordlist ']' '*'"""

    if p[4] == "*":
        p[0] = ("REPETITION", p[2], p[4])
    else:
        p[0] = ("REPETITION", p[2], p[4][1])


def p_datawordlist(p):
    """datawordlist : dataword ',' datawordlist
    | dataword
    """
    if len(p) == 4:
        p[0] = (p[1],) + p[3]
    else:
        p[0] = (p[1],)


def p_bodystatement(p):
    """bodystatement : dataword ';'
    | registerassignment ';'
    | repetition ';'
    """
    global in_preamble
    # If this is true, we have encountered our first body statement.
    # This means we have seen all the type definitions we are going to see
    # and it is time for the preamble object to read through the generated
    # data structure and figure out what stuff it needs to capture
    if in_preamble:
        in_preamble = False

    p[0] = p[1]


def p_typeexpression(p):
    """typeexpression :  IDENTIFIER ':' IDENTIFIER '@' NUM_LITERAL
    |  IDENTIFIER ':' IDENTIFIER '@' RET
    """
    # Type     Position Name
    p[0] = (p[3][1], p[5][1], p[1][1])


def p_typeexpressionlist(p):
    """typeexpressionlist : typeexpression ',' typeexpressionlist
    | typeexpression
    """

    if len(p) == 4:
        p[0] = (p[1],) + p[3]
    else:
        p[0] = (p[1],)


def p_typedefinition(p):
    """typedefinition : EVENT IDENTIFIER '{' typeexpressionlist '}'"""
    p[0] = ("TYPEDEF", p[2][1], p[4])


def p_variantdefinition(p):
    """variantdefinition : EVENT IDENTIFIER variantlist"""
    p[0] = ("VARIANTDEF", p[2][1], p[3])


def p_variantlist(p):
    """variantlist : variant '|' variantlist
    | variant
    """
    if len(p) == 4:
        p[0] = ((p[1][1], p[1][2]),) + p[3]
    else:
        p[0] = (
            (
                p[1][1],
                p[1][2],
            ),
        )


def p_variant(p):
    """variant : '{' IDENTIFIER typeexpressionlist '}'"""
    p[0] = ("VARIANT", p[2][1], p[3])


def p_predpath(p):
    """predpath : IDENTIFIER "." predpath
    | IDENTIFIER
    """

    if len(p) == 4:
        p[0] = ("PREDPATH", p[1][1] + p[2] + p[3][1])
    else:
        p[0] = ("PREDPATH", p[1][1])


def p_predexpressionlist(p):
    """predexpressionlist : predexpression AND predexpressionlist
    | predexpression
    """

    if len(p) == 4:
        p[0] = ("PREDEXPRESSIONLIST", p[1][1:]) + p[3][1:]
    else:
        p[0] = ("PREDEXPRESSIONLIST", p[1][1:])


def p_predexpression(p):
    """predexpression : predpath EQUALSOP NUM_LITERAL
    | predpath EQUALSOP STRING_LITERAL
    """

    p[0] = ("PREDICATEEXPRESSION", p[1][1], p[2][1], p[3][1])


def p_registerassignment(p):
    """registerassignment : IDENTIFIER ASSIGNOP NUM_LITERAL
    | IDENTIFIER ASSIGNOP STRING_LITERAL
    | IDENTIFIER ASSIGNOP IDENTIFIER
    | IDENTIFIER ASSIGNOP registerexp
    """

    p[0] = ("REGASSIGN", p[1], p[3])


def p_registerexp(p):
    """registerexp : registeradd
    | registersub
    | registermul
    | registerdiv
    | registerconcat
    | registeraddorconcat
    """

    p[0] = ("REGEXP", p[1])


def p_registeraddorconcat(p):
    """registeraddorconcat : IDENTIFIER '+' IDENTIFIER"""

    p[0] = ("REGADD", p[1], p[2], p[3])


def p_registerconcat(p):
    """registerconcat : IDENTIFIER '+' STRING_LITERAL
    | STRING_LITERAL '+' IDENTIFIER
    | STRING_LITERAL '+' STRING_LITERAL
    """

    p[0] = ("REGCONCAT", p[1], p[2], p[3])


def p_registeradd(p):
    """registeradd : IDENTIFIER '+' NUM_LITERAL
    | NUM_LITERAL '+' IDENTIFIER
    | NUM_LITERAL '+' NUM_LITERAL
    """

    p[0] = ("REGADD", p[1], p[2], p[3])


def p_registersub(p):
    """registersub : IDENTIFIER '-' IDENTIFIER
    | IDENTIFIER '-' NUM_LITERAL
    | NUM_LITERAL '-' IDENTIFIER
    | NUM_LITERAL '-' NUM_LITERAL
    """

    p[0] = ("REGSUB", p[1], p[2], p[3])


def p_registermul(p):
    """registermul : IDENTIFIER '*' IDENTIFIER
    | IDENTIFIER '*' NUM_LITERAL
    | NUM_LITERAL '*' IDENTIFIER
    | NUM_LITERAL '*' NUM_LITERAL
    """

    p[0] = ("REGMUL", p[1], p[2], p[3])


def p_registerdiv(p):
    """registerdiv : IDENTIFIER '/' IDENTIFIER
    | IDENTIFIER '/' NUM_LITERAL
    | NUM_LITERAL '/' IDENTIFIER
    | NUM_LITERAL '/' NUM_LITERAL
    """
    p[0] = ("REGDIV", p[1], p[2], p[3])


def p_empty(p):
    """empty :"""
    pass


def p_withexpression(p):
    """withexpression : WITH predexpressionlist"""
    p[0] = ("WITHEXPRESSION", p[2])


def p_outputexpression(p):
    """outputexpression : WRITEOP IDENTIFIER '(' parameterexpression ')'"""
    p[0] = ("OUTPUTEXPRESSION", p[2], p[4])


def p_withoutputexpression(p):
    """withoutputexpression : empty
    | withexpression
    | outputexpression
    | withexpression outputexpression
    """
    if not p[1]:
        p[0] = (None, None)
    elif len(p) == 2:
        if p[1][0] == "WITHEXPRESSION":
            p[0] = (p[1], None)
        elif p[1][0] == "OUTPUTEXPRESSION":
            p[0] = (None, p[1])
        else:
            p[0] = (None, None)
    else:
        p[0] = (p[1], p[2])


def p_datawordidentifier(p):
    """datawordidentifier : NOT IDENTIFIER
    | IDENTIFIER
    """
    if len(p) == 3:
        p[0] = (p[1], p[2])
    else:
        p[0] = (None, p[1])


def p_dataword(p):
    """dataword : datawordidentifier '(' parameterexpression ')' withoutputexpression"""

    result = ("DATAWORD",)
    result += (p[1][0], p[1][1])

    result += (p[3],)

    result += p[5]

    p[0] = result


def p_parameterexpression(p):
    """parameterexpression : '{' parameterlist '}'
    | '{' '}'
    """
    if len(p) == 3:
        p[0] = ("PARAMETEREXPRESSION", None)
    else:
        p[0] = ("PARAMETEREXPRESSION", p[2])


def p_parameterlist(p):
    """parameterlist : parameter ',' parameterlist
    | parameter
    """

    if len(p) == 4:
        p[0] = (p[1],) + p[3]
    else:
        p[0] = (p[1],)


def p_parameter(p):
    """parameter : IDENTIFIER ':' READOP IDENTIFIER
    | IDENTIFIER ':' STOREOP  IDENTIFIER
    | IDENTIFIER ':' WRITEOP IDENTIFIER
    | IDENTIFIER ':' parameterexpression
    """

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

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="mode", help="input mode")

    parse_argparser = subparsers.add_parser("parse")
    parse_argparser.add_argument(
        "-c",
        "--port-path",
        required=False,
        type=str,
        help="PORT file to be parsed",  # should I change it to -p
    )
    parse_argparser.add_argument(
        "-s", "--string", required=False, type=str, help="String to parse"
    )
    parse_argparser.add_argument(
        "-k",
        "--check",
        required=False,
        action="store_true",
        help="Perform type checking after parsing",
    )

    build_argparser = subparsers.add_parser("build")

    build_argparser.add_argument(
        "-c",  # same question
        "--port-path",
        required=True,
        type=str,
        help="PORT file to be compiled",
    )

    run_subparsers = subparsers.add_parser("run")
    run_subparsers = run_subparsers.add_subparsers(dest="format", help="input format")

    strace_run_argparser = run_subparsers.add_parser("strace")

    strace_run_argparser.add_argument(
        "-a",
        "--automaton-path",
        required=True,
        type=str,
        help="Location of PORT automaton to be used in processing the specified strace file.",
    )
    strace_run_argparser.add_argument(
        "-s",
        "--strace-path",
        required=True,
        type=str,
        help="Location of strace recording to execute against",
    )
    strace_run_argparser.add_argument(
        "-d",
        "--syscall-definitions",
        required=True,
        type=str,
        help="Location of posix-omni-parser syscall definitions file",
    )
    strace_run_argparser.add_argument(
        "-k",
        "--skip",
        required=False,
        type=int,
        help="Number of system calls in trace to skip before processing",
    )

    jsonrpc_run_argparser = run_subparsers.add_parser("jsonrpc")

    jsonrpc_run_argparser.add_argument(
        "-a",
        "--automaton-path",
        required=True,
        type=str,
        help="Location of PORT automaton to be used in processing the specified strace file.",
    )
    jsonrpc_run_argparser.add_argument(
        "-j",
        "--json-path",
        required=True,
        type=str,
        help="Location of jsonrpc recording to execute against",
    )

    xmlrpc_run_argparser = run_subparsers.add_parser("xmlrpc")

    xmlrpc_run_argparser.add_argument(
        "-a",
        "--automaton-path",
        required=True,
        type=str,
        help="Location on of PORT automaton to be used",
    )

    xmlrpc_run_argparser.add_argument(
        "-x",
        "--xml-path",
        required=True,
        type=str,
        help="Location of xmlrpc recording to execute against",
    )

    csvrpc_run_argparser = run_subparsers.add_parser("csv")

    csvrpc_run_argparser.add_argument(
        "-a",
        "--automaton-path",
        required=True,
        type=str,
        help="Location of PORT automaton to be used in processing the specified strace file.",
    )
    csvrpc_run_argparser.add_argument(
        "-c",
        "--csv-path",
        required=True,
        type=str,
        help="Location of csv recording to execute against",
    )

    usbjson_run_argparser = run_subparsers.add_parser("usbjson")
    usbjson_run_argparser.add_argument(
        "-a",
        "--automaton-path",
        required=True,
        type=str,
        help="Location of PORT automaton to be used in processing the specified strace file.",
    )
    usbjson_run_argparser.add_argument(
        "-u",
        "--usbjson-path",
        required=True,
        type=str,
        help="Location of usbjson recording to execute against",
    )

    if not args:
        args = parser.parse_args()

    if (hasattr(args, "port_path") and args.port_path is not None) and (
        hasattr(args, "string") and args.string is not None
    ):
        parse_argparser.print_help()
        raise PORTError("-c and -s may not be used together")

    in_preamble = True
    lexer = lex.lex()
    parser = yacc.yacc()

    if args.mode == "parse":
        data = None
        ast = None
        if hasattr(args, "port_path") and args.port_path is not None:
            with open(args.port_path, "r") as f:
                data = f.read()

        if hasattr(args, "string") and args.string is not None:
            data = args.string

        if data:
            ast = parser.parse(data, debug=True)
            pp = pprint.PrettyPrinter(indent=2)
            pp.pprint(ast)

            if hasattr(args, "check") and args.check == True:
                type_checker.check_ast(ast)

        return ast

    if args.mode == "build":
        basename = os.path.splitext(os.path.basename(args.port_path))[0]
        dirname = os.path.dirname(args.port_path)
        automaton_path = os.path.join(dirname, basename + ".auto")
        cb_path = os.path.join(dirname, basename + ".cb")

        with open(args.port_path, "r") as f:
            ast = parser.parse(f.read(), debug=False)

        type_checker.check_ast(ast)
        automaton, containerbuilder = automaton_builder.process_root(ast)

        with open(automaton_path, "wb") as f:
            pickle.dump((automaton, containerbuilder), f)

        return automaton, containerbuilder

    elif args.mode == "run":

        automaton_path = args.automaton_path

        # Load in the automaton
        with open(automaton_path, "rb") as f:
            automaton, cb = pickle.load(f)

        if args.format == "strace":

            strace_path = args.strace_path
            syscall_definitions = args.syscall_definitions

            if hasattr(args, "skip") and args.skip is not None:
                skip = args.skip
            else:
                skip = 0
            datawords = StraceToDatawords(cb, syscall_definitions, strace_path, skip)

        elif args.format == "jsonrpc":

            json_path = args.json_path
            datawords = JSONToDatawords(cb, json_path)

        elif args.format == "xmlrpc":

            xml_path = args.xml_path
            datawords = XMLToDatawords(cb, xml_path)

        elif args.format == "csv":

            csv_path = args.csv_path
            datawords = CSVToDatawords(cb, csv_path)

        elif args.format == "usbjson":
            usbjson_path = args.usbjson_path
            datawords = USBJSONToDatawords(cb, usbjson_path)

        automaton.events = datawords.get_datawords()
        automaton.events_iter = iter(automaton.events)

        # Pass each dataword in the list in series into the automaton
        # HACK: we need events in automaton so we can hand off to subautomaton
        try:
            while True:
                automaton.match(next(automaton.events_iter))
        except StopIteration:
            pass

        # At the end of everything we have a transformed set of datawords.
        # We either use them if we ended in an accepting state or drop ignore
        # them if we haven't ended in an accepting state
        # Some print goes here
        print("Automaton ended in state: " + str(automaton.current_state))
        print("With registers: " + str(automaton.registers))

        for i in automaton.events:
            print(datawords.get_mutated_event(i))

        return automaton, automaton.events, datawords


in_preamble = None
lexer = None
parser = None


# We need this function to be an entry point to call main and exit with
# a proper exit code.
# We can't use main for this purpose because tests expect to return objects
# for inspection and NOT exit
def run_port():
    main()
    sys.exit(0)


if __name__ == "__main__":
    run_port()
    sys.exit(0)
