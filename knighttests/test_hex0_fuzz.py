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
from unittest import TestCase, skipIf

from hex0tobin import (
    write_binary_filefd_from_hex0_filefd,
    int_bytes_from_hex0_fd,
    )

from .stage0 import (
    STAGE_0_MONITOR_HEX_FILEPATH,
    STAGE_0_HEX0_ASSEMBLER_FILEPATH,
    )

from .fuzzcommon import CommonHexFuzzTest, CommonStage1Fuzz
from .testflags import OPTIMIZE_SKIP, DIFF_REG_SIZE_SKIP

hexdigits_as_ascii_bytes = hexdigits # bytes(hexdigits, encoding='ascii')
printable_as_ascii_bytes = printable # bytes(printable, encoding='ascii')

printable_without_cr = ''.join(c for c in printable
                               if c!= '\r' )

# 7 hexdigits for every 3 printable chars
hex_or_printable = ( (hexdigits_as_ascii_bytes,)*7 +
                     (printable_as_ascii_bytes,)*3 )

hex_or_printable_without_cr = ( (hexdigits,)*7 +
                                (printable_without_cr,)*3 )

def get_representative_character_byte(random_source, top_level_char_set):
    char_set = random_source.choice(top_level_char_set)
    return random_source.choice(char_set)

def get_n_representative_character_bytes(random_source, n, top_level_char_set):
    return ''.join(
        get_representative_character_byte(random_source, top_level_char_set)
        for i in range(n) )

class Hex0FuzzCommon:
    input_encode_python_implementation = \
        staticmethod(write_binary_filefd_from_hex0_filefd)

    int_bytes_from_rom_encode_file = staticmethod(int_bytes_from_hex0_fd)

    def get_n_representative_tokens_byte_encoded(self, n):
        return get_n_representative_character_bytes(
            self.random_source, n, self.get_top_level_char_set() )

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

class Hex0FuzzTestOptimize(Hex0FuzzTest):
    optimize = True
    @skipIf(OPTIMIZE_SKIP, 'requested')
    def setUp(self, *args, **kargs):
        return super(Hex0FuzzTestOptimize, self).setUp(*args, **kargs)

class Hex0FuzzTest64(Hex0FuzzTest):
    registersize = 64
    @skipIf(DIFF_REG_SIZE_SKIP, 'requested')
    def setUp(self, *args, **kargs):
        return super(Hex0FuzzTest64, self).setUp(*args, **kargs)

class Hex0FuzzTest64Optimize(Hex0FuzzTest64):
    optimize = True
    @skipIf(OPTIMIZE_SKIP, 'requested')
    def setUp(self, *args, **kargs):
        return super(Hex0FuzzTest64Optimize, self).setUp(*args, **kargs)

class Hex0FuzzTest16(Hex0FuzzTest):
    registersize = 16
    @skipIf(DIFF_REG_SIZE_SKIP, 'requested')
    def setUp(self, *args, **kargs):
        return super(Hex0FuzzTest16, self).setUp(*args, **kargs)

class Hex0FuzzTest16Optimize(Hex0FuzzTest16):
    optimize = True
    @skipIf(OPTIMIZE_SKIP, 'requested')
    def setUp(self, *args, **kargs):
        return super(Hex0FuzzTest16Optimize, self).setUp(*args, **kargs)

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

class Hex0FuzzTestAssembler1Optimize(Hex0FuzzTestAssembler1):
    optimize = True
    @skipIf(OPTIMIZE_SKIP, 'requested')
    def setUp(self, *args, **kargs):
        return super(Hex0FuzzTestAssembler1Optimize, self).setUp(*args, **kargs)

class Hex0FuzzTestAssembler1_64(Hex0FuzzTestAssembler1):
    registersize = 64
    @skipIf(DIFF_REG_SIZE_SKIP, 'requested')
    def setUp(self, *args, **kargs):
        return super(Hex0FuzzTestAssembler1_64, self).setUp(*args, **kargs)

class Hex0FuzzTestAssembler1_64Optimize(Hex0FuzzTest64):
    optimize = True
    @skipIf(OPTIMIZE_SKIP, 'requested')
    def setUp(self, *args, **kargs):
        return super(Hex0FuzzTestAssembler1_64Optimize, self).setUp(
            *args, **kargs)

class Hex0FuzzTestAssembler1_16(Hex0FuzzTestAssembler1):
    registersize = 16
    @skipIf(DIFF_REG_SIZE_SKIP, 'requested')
    def setUp(self, *args, **kargs):
        return super(Hex0FuzzTestAssembler1_16, self).setUp(*args, **kargs)

class Hex0FuzzTestAssembler1_16Optimize(Hex0FuzzTest16):
    optimize = True
    @skipIf(OPTIMIZE_SKIP, 'requested')
    def setUp(self, *args, **kargs):
        return super(Hex0FuzzTestAssembler1_16Optimize, self).setUp(
            *args, **kargs)

if __name__ == '__main__':
    # to invoke, run
    # $ python3 -m knighttests.test_hex0tobin
    # or
    # $ ./runtestmodule.py knighttests/test_hex0_fuzz.py
    #
    # direct invocation like ./test_hex0_fuzz.py will not work
    from unittest import main
    main()
