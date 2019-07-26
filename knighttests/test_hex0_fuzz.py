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
from unittest import TestCase

from hex0tobin import (
    write_binary_filefd_from_hex0_filefd,
    int_bytes_from_hex0_fd,
    )
from knightdecode import create_vm
from knightvm_minimal import load_hex_program, grow_memory, execute_vm

from .stage0 import (
    STAGE_0_MONITOR_HEX_FILEPATH,
    STAGE_0_HEX1_ASSEMBLER_FILEPATH,
    )
from .test_hex0tobin import TestHex0KnightExecuteCommon
from .fuzzcommon import CommonStage1Fuzz

def get_random_for_str(seed_str):
    r = Random()
    r.seed(seed_str)
    return r

GNU_MANIFESTO_RANDOM = get_random_for_str(
    "What's GNU? Gnu's Not Unix!")

hexdigits_as_ascii_bytes = hexdigits # bytes(hexdigits, encoding='ascii')
printable_as_ascii_bytes = printable # bytes(printable, encoding='ascii')

printable_without_cr = ''.join(c for c in printable
                               if c!= '\r' )

# 7 hexdigits for every 3 printable chars
hex_or_printable = ( (hexdigits_as_ascii_bytes,)*7 +
                     (printable_as_ascii_bytes,)*3 )

hex_or_printable_without_cr = ( (hexdigits,)*7 +
                                (printable_without_cr,)*3 )

def get_representative_character_byte(random_source):
    char_set = random_source.choice(hex_or_printable)
    return random_source.choice(char_set)

def get_n_representative_character_bytes(random_source, n):
    return ''.join( get_representative_character_byte(random_source)
                    for i in range(n) )

class Hex0FuzzTest(TestHex0KnightExecuteCommon):
    random_source_orig = GNU_MANIFESTO_RANDOM
    hex0_encoding_rom = STAGE_0_MONITOR_HEX_FILEPATH

    def setUp(self):
        super().setUp()
        self.random_source = copy(self.random_source_orig)

        self.input_bytes = StringIO()
        self.python_output_bytes = BytesIO()
        self.input_bytes.write(
            get_n_representative_character_bytes(
                self.random_source, 1024*256) )
        self.input_bytes.write( '\n' )
        self.input_bytes.seek(0)
        write_binary_filefd_from_hex0_filefd(
            self.input_bytes, self.python_output_bytes)
        self.input_bytes.seek(0)

    def execute_fuzz_test(self):
        vm = create_vm(
            size=0, registersize=self.registersize,
            tapefile1=self.get_tape1_file_path(None),
            tapefile2=self.tape_02_temp_file_path,
            stdin=self.get_stdin_for_vm(self.input_bytes),
            stdout=BytesIO(),
        )
        load_hex_program(vm, self.hex0_encoding_rom )
        grow_memory(vm, self.stack_end)
        execute_vm(vm, optimize=True, halt_print=False)

    def test_output_match(self):
        self.execute_fuzz_test()
        with open(self.get_output_file_path(), 'rb') as tape_file:
            tape_out = tape_file.read()
            py_out = self.python_output_bytes.getvalue()
            self.assertEqual(
                tape_out,
                py_out,
            )

class Hex0FuzzCommon:
    input_encode_python_implementation = \
        staticmethod(write_binary_filefd_from_hex0_filefd)

    int_bytes_from_rom_encode_file = staticmethod(int_bytes_from_hex0_fd)

class Hex0FuzzTestAssembler1(CommonStage1Fuzz, Hex0FuzzCommon, TestCase):
    encoding_rom_filename = STAGE_0_HEX1_ASSEMBLER_FILEPATH

    test_size = 1024*256

    def setUp(self):
        CommonStage1Fuzz.setUp(self)

    def tearDown(self):
        CommonStage1Fuzz.tearDown(self)

    @staticmethod
    def get_top_level_char_set():
        return hex_or_printable_without_cr

if __name__ == '__main__':
    # to invoke, run
    # $ python3 -m knighttests.test_hex0tobin
    # or
    # $ ./runtestmodule.py knighttests/test_hex0_fuzz.py
    #
    # direct invocation like ./test_hex0_fuzz.py will not work
    from unittest import main
    main()
