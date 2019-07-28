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

from string import hexdigits, printable
from unittest import TestCase

from hex0tobin import (
    write_binary_filefd_from_hex0_filefd,
    int_bytes_from_hex0_fd,
    )

from .stage0 import (
    STAGE_0_MONITOR_HEX_FILEPATH,
    STAGE_0_HEX0_ASSEMBLER_FILEPATH,
    )

from .fuzzcommon import CommonHexFuzzTest, CommonStage1Fuzz

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

class Hex0FuzzCommon:
    input_encode_python_implementation = \
        staticmethod(write_binary_filefd_from_hex0_filefd)

    int_bytes_from_rom_encode_file = staticmethod(int_bytes_from_hex0_fd)

class Hex0FuzzTest(Hex0FuzzCommon, CommonHexFuzzTest, TestCase):
    encoding_rom_filename = STAGE_0_MONITOR_HEX_FILEPATH

    test_size = 1024*256

    def setUp(self):
        CommonHexFuzzTest.setUp(self)

    def tearDown(self):
        CommonHexFuzzTest.tearDown(self)

    def get_stdin_for_vm(self, input_file_fd):
        return input_file_fd

    def get_output_file_path(self):
        return self.tape_01_temp_file_path

    @staticmethod
    def get_top_level_char_set():
        return hex_or_printable

class Hex0FuzzTestAssembler1(CommonStage1Fuzz, Hex0FuzzCommon, TestCase):
    encoding_rom_filename = STAGE_0_HEX0_ASSEMBLER_FILEPATH

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
