# Copyright (C) 2019 Mark Jenkins <mark@markjenkins.ca>
# This file is part of knightpies
#
# knightpies is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# knightpies is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with knightpies.  If not, see <http://www.gnu.org/licenses/>.

from random import Random
from string import hexdigits, printable
from copy import copy
from io import StringIO, BytesIO

from hex0tobin import write_binary_filefd_from_hex0_filefd
from knightdecode import create_vm
from knightvm_minimal import load_hex_program, grow_memory, execute_vm
from constants import MEM

from .stage0 import STAGE_0_MONITOR_HEX_FILEPATH
from .hexcommon import TestHexKnightExecuteCommonSetup, CommonStage1HexEncode

def get_random_for_str(seed_str):
    r = Random()
    r.seed(seed_str)
    return r

GNU_MANIFESTO_RANDOM = get_random_for_str(
    "What's GNU? Gnu's Not Unix!")

class CommonHexFuzzTest(TestHexKnightExecuteCommonSetup):
    # implementing sub-classes to provide
    # get_n_representative_tokens_byte_encode()
    # encode_input_bytes_w_python_implementation()
    # get_top_level_char_set()

    random_source_orig = GNU_MANIFESTO_RANDOM

    test_size = 1024*256

    def setUp(self):
        self.setup_stack_and_tmp_files()

        self.random_source = copy(self.random_source_orig)

        self.input_bytes = StringIO()
        self.python_output_bytes = BytesIO()
        self.input_bytes.write(
            self.get_n_representative_tokens_byte_encoded(self.test_size) )
        self.input_bytes.write('\n')
        self.input_bytes.seek(0)
        self.encode_input_bytes_w_python_implementation()
        self.input_bytes.seek(0)

    def tearDown(self):
        self.remove_tmp_files()

    def get_end_of_memory(self):
        return self.stack_end

    def encode_input_bytes_w_python_implementation(self):
        self.input_encode_python_implementation(
            self.input_bytes, self.python_output_bytes)

    def write_random_input_to_file(self, filename):
        with open(filename, 'w') as randominputfile:
            self.input_bytes.seek(0)
            for c in self.input_bytes:
                randominputfile.write(c)
            self.input_bytes.seek(0)

    def execute_fuzz_test(self):
        vm = create_vm(
            size=0, registersize=self.registersize,
            tapefile1=self.get_tape1_file_path(),
            tapefile2=self.tape_02_temp_file_path,
            stdin=self.get_stdin_for_vm(self.input_bytes),
            stdout=BytesIO(),
        )
        self.load_encoding_rom(vm)
        grow_memory(vm, self.get_end_of_memory())
        execute_vm(vm, optimize=self.optimize, halt_print=False)

    def test_output_match(self):
        self.execute_fuzz_test()
        with open(self.get_output_file_path(), 'rb') as tape_file:
            tape_out = tape_file.read()
            py_out = self.python_output_bytes.getvalue()
            self.assertEqual(
                tape_out,
                py_out,
            )

    def get_tape1_file_path(self):
        return self.tape_01_temp_file_path

class CommonStage1Fuzz(CommonHexFuzzTest, CommonStage1HexEncode):
    def setUp(self):
        CommonHexFuzzTest.setUp(self)
        self.write_random_input_to_file(self.tape_01_temp_file_path)

    def get_tape1_file_path(self):
        return CommonHexFuzzTest.get_tape1_file_path(self)
