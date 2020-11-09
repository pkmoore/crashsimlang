# CSlang Compiler and Runner

# Installation
```
git clone https://github.com/pkmoore/crashsimlang
cd crashsimlang
pip install setuptools
pip install .
```
Installing in this fashion makes the command "cslang" available globally.
It also provides a "parse\_syscall\_definitions" command for generating a
syscall\_definitions.pickle file needed for working with strace.

# Execute Test Suite
```
git clone https://github.com/pkmoore/crashsimlang
cd crashsimlang
pip install setuptools tox
tox
```

# Compiling CSlang files
```
cslang build -c <path to cslang file>
```
This command builds an automaton from the specified cslang file.


# Running CSlang Automata
```
cslang run <strace OR jsonrpc> <format specific options>

```
## Run an automaton against an strace file

```
cslang run strace -a <path to automaton> -s <path to strace file> -d <path
to syscall_definitions.pickle file>
```

## Run an automaton against a json-rpc file
```
cslang run jsonrpc -a <path to automaton> -j <path to json file>
```


Note:  For now, it is an error to run an automaton against a format it was
not built for.


