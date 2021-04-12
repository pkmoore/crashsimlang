from builtins import object
import os
from argparse import Namespace
from cslang.cslang import main as cslang_main


def get_test_data_path(filename):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(dir_path, filename)


class TestOutputs(object):
    def test_outputs(self):
        syscall_definitions = get_test_data_path("../cslang/syscall_definitions.pickle")
        automaton_path = get_test_data_path("outputs.auto")
        cslang_main(
            Namespace(mode="build", cslang_path=get_test_data_path("outputs.cslang"))
        )

        automaton, datawords_after, s2d = cslang_main(
            Namespace(
                mode="run",
                format="strace",
                strace_path=get_test_data_path("outputs.strace"),
                syscall_definitions=syscall_definitions,
                automaton_path=automaton_path,
            )
        )
        assert automaton.current_state == 4
        assert "(10.0, " in s2d.get_mutated_strace(datawords_after[0])
        assert "(15.0, " in s2d.get_mutated_strace(datawords_after[1])
        assert "foo" in s2d.get_mutated_strace(datawords_after[2])
        assert "bar" in s2d.get_mutated_strace(datawords_after[2])
        assert "foo" not in s2d.get_mutated_strace(datawords_after[3])
        assert "bar" not in s2d.get_mutated_strace(datawords_after[3])
