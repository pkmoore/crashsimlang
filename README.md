# PORT Compiler and Runner

# Installation
```
git clone https://github.com/pkmoore/crashsimlang
cd crashsimlang
pip install setuptools
pip install .
```
Installing in this fashion makes the command "port" available globally.
It also provides a "parse\_syscall\_definitions" command for generating a
syscall\_definitions.pickle file needed for working with strace.

# Execute Test Suite
```
git clone https://github.com/pkmoore/crashsimlang
cd crashsimlang
pip install setuptools tox
tox
```

# Compiling PORT files
```
port build -c <path to port file>
```
This command builds an automaton from the specified port file.


# Running PORT Automata
```
port run <strace OR jsonrpc> <format specific options>

```
## Run an automaton against an strace file

```
port run strace -a <path to automaton> -s <path to strace file> -d <path
to syscall_definitions.pickle file>
```

## Run an automaton against a json-rpc file
```
port run jsonrpc -a <path to automaton> -j <path to json file>
```


Note:  For now, it is an error to run an automaton against a format it was
not built for.

# Writing PORT Programs

## The Simplest Case

Matching a sequence of open(), read, close() without regard
for parameters and return values.
```
# These lines define the types "read", "open", and "close"

type open {};
type read {};
type close {};

# These expressions use the defined types to describe a sequence that we
# want to accept.
open({});
read({});
close({});
```

The automaton described above will match the following example traces:
```
strace

35388 open("test.txt", O_RDONLY, 0) = 3
35388 read(3, "Hello world", 11) = 11
35388 close(3) = 0
```

```
JSONRPC

[
  {"jsonrpc": "2.0", "method": "open", "params": ["test.txt"], "id": 1},
  {"jsonrpc": "2.0", "method": "read", "params": [3], "id": 2},
  {"jsonrpc": "2.0", "method": "close", "params": [3], "id": 3}
]
```

```
XMLRPC

<calls>
<methodCall>
    <methodName>open</methodName>
    <params>
        <param>
            <value><string>test.txt</string></value>
        </param>
        </params>
</methodCall>
<methodCall>
    <methodName>read</methodName>
    <params>
        <param>
            <value><string>3</string></value>
        </param>
        </params>
</methodCall>
<methodCall>
    <methodName>close</methodName>
    <params>
        <param>
            <value><i4>3</i4></value>
        </param>
        </params>
</methodCall>
</calls>
```

## Parameters and Operators

Similar to above, but we increase specificity by tracking which files are
open()'d and insuring that we match their associated read() and close()
calls.

To accomplish this, we enhance our declarations of open(), read(), and
close() to include member values.  These member values have the primative
types "String" or "Numeric."  Each parameter has a position (following @)
which denotes its corresponding argument from the original call.  During
execution, members are automatically populated from the trace being
processed.

We use the "!" operator to store the filename and descriptor returned by
open() into the fn and fd registers respectively.  This value is used in
the subsequent read() and close() calls with the "?" operator to describe a
state that can only be entered if a we encounter a read() (or close())
call with the appropriate file descriptor.

```

# Define open() calls as having the members filename and filedescriptor.
# When an open() is encountered, an instance is opened with is members
# populated from arguments 0 and "ret" respectively.
type open {filename: String@0, filedesc: Numeric@ret};

# Similarly, read() now has a filedesc member
type read {filedesc: Numeric@0};

# And close() has a filedesc and retval
type close {filedesc: Numeric@0, retval: Numeric@ret};

# Store the value of filename to the fn register
# Store the value of filedesc to the fd register
open({filename: !fn, filedesc: !fd});

# Only accept read() calls where the value in filedesc matches the value in
# fd
read({filedesc: ?fd});

# Only accept close() calls where the value in filedesc matches the value
# in fd
close({filedesc: ?fd});
```

This automaton accepts the following trace:
```
35388 open("test.txt", O_RDONLY, 0) = 3
35388 read(3, "Hello World" 11) = 34355
35388 close(3) = 0
```
It will NOT accept this trace:
```
35388 open("test.txt", O_RDONLY, 0) = 3

# read() is being called on file descriptor 4 which is not
# the value stored from the above open()'s return value
35388 read(4, "Hello World", 11) = 34355
#          ^---REJECT!

35388 close(3) = 0
```

## Assigning to Registers and Modifying the Output Trace

Building further upon the above, modifications to the output trace are
achieved by using the "->" operator to insert register values into a
parameter.


This is shown in the close() call below.  The "->" operator is used to
write the value from the retval register into the output trace.

The value in retval comes from a register assignment statement.  These
statments allow values to be stored directly into registers.  These values
may be literals or the results of arithmetic expressions performed on a
combination of literals and the register values.  Numeric and String values
are supported.


```
# We keep the same type definisions as above
type open {filename: String@0, filedesc: Numeric@ret};
type read {filedesc: Numeric@0};
type close {filedesc: Numeric@0, retval: Numeric@ret};

# Store the numeric value -1 into the retval register
retval <- -1

# Store the value of filename to the fn register
# Store the value of filedesc to the fd register
open({filename: !fn, filedesc: !fd});

# Only accept read() calls where the value in filedesc matches the value in
# fd
read({filedesc: ?fd});

# Only accept close() calls where the value in filedesc matches the value
# in fd

# NOTE: we use the -> operator to write the value in the retval register
# to the close() call's retval parameter
close({retval: ->retval, filedesc: ?fd});
```

The above automaton transforms:

```
35388 open("test.txt", O_RDONLY, 0) = 3
35388 read(3, "Hello World" 11) = 34355
35388 close(3) = 0
```
into:

```
35388 open("test.txt", O_RDONLY, 0) = 3
35388 read(3, "Hello World" 11) = 34355
35388 close(3) = -1
                  ^---- close() now has -1 as a return value signaling
                  failure
```
