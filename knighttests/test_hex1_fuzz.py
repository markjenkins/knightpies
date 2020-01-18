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

from unittest import TestCase, skipIf
from string import hexdigits, printable, whitespace

from hex0tobin import int_bytes_from_hex0_fd
from hex1tobin import write_binary_filefd_from_hex1_filefd

from .fuzzcommon import CommonStage1Fuzz

from .stage0 import STAGE_0_HEX1_ASSEMBLER_FILEPATH
from .testflags import OPTIMIZE_SKIP, DIFF_REG_SIZE_SKIP

printable_less_colon_at = ''.join(
    c for c in printable
    if c not in ('@', ':')
)

DEF, REF = range(2)

printable_not_whitespace = set(printable) - set(whitespace)

# 30 hexdigits for every 12 printable chars for every 1 location define
# for every 3 reference
hex_symbols_or_most_printable = ( (hexdigits,)*30 +
                                  (printable_less_colon_at,)*12,
                                  (DEF,),
                                  (REF,)*3,
)

class Hex1FuzzTest(CommonStage1Fuzz, TestCase):
    encoding_rom_filename = STAGE_0_HEX1_ASSEMBLER_FILEPATH

    # default 1024*256 runs for 2 hours on my slow machine, *10 only 10 minutes
    # plus, we're not avoiding the use of symbols too big a relative
    # offset away so we need to keep this under (2**(16-1) - 1 )*2
    # because signed 16 bit offsets and every two hex chars is a byte of output
    test_size = 1024*10

    def setUp(self):
        CommonStage1Fuzz.setUp(self)

    def tearDown(self):
        CommonStage1Fuzz.tearDown(self)

    input_encode_python_implementation = \
        staticmethod(write_binary_filefd_from_hex1_filefd)

    int_bytes_from_rom_encode_file = staticmethod(int_bytes_from_hex0_fd)

    def get_n_representative_tokens_byte_encoded(self, n):
        self.avail_symbols = list(printable_not_whitespace)
        self.used_symbols = []
        self.random_source.shuffle(self.avail_symbols)
        return self.get_n_representative_character_bytes(n)

    def get_representative_character_byte(self):
        char_set = self.random_source.choice(hex_symbols_or_most_printable)
        if char_set[0]==DEF:
            try:
                symbol = self.avail_symbols.pop()
            except IndexError: # when pop() no longer works
                return '\n'
            else:
                self.used_symbols.append(symbol)
                return '\n:%s\n' % symbol
        elif char_set[0]==REF:
            # FIXME, we need to check if these symbols are close
            # enough for use by maintaining a symbol table and a count
            # through the final binary
            # for now, test_size = 1024*10 is quite safe
            # as a relative offset of (2**(16-1) - 1 )==32767 is
            # greater than 1024*10/2
            symbol = self.random_source.choice(self.used_symbols)
            return '\n@%s\n' % symbol
        else:
            return self.random_source.choice(char_set)

    def get_n_representative_character_bytes(self, n):
        return ''.join(
            self.get_representative_character_byte()
            for i in range(n) )

class Hex1FuzzTestOptimize(Hex1FuzzTest):
    optimize = True
    @skipIf(OPTIMIZE_SKIP, 'requested')
    def setUp(self, *args, **kargs):
        return super(Hex1FuzzTestOptimize, self).setUp(*args, **kargs)

class Hex1FuzzTest64(Hex1FuzzTest):
    registersize = 64
    @skipIf(DIFF_REG_SIZE_SKIP, 'requested')
    def setUp(self, *args, **kargs):
        return super(Hex1FuzzTest64, self).setUp(*args, **kargs)

class Hex1FuzzTest64Optimize(Hex1FuzzTest64):
    optimize = True
    @skipIf(OPTIMIZE_SKIP, 'requested')
    def setUp(self, *args, **kargs):
        return super(Hex1FuzzTest64Optimize, self).setUp(*args, **kargs)

class Hex1FuzzTest16(Hex1FuzzTest):
    registersize = 16
    @skipIf(DIFF_REG_SIZE_SKIP, 'requested')
    def setUp(self, *args, **kargs):
        return super(Hex1FuzzTest16, self).setUp(*args, **kargs)

class Hex1FuzzTest16Optimize(Hex1FuzzTest16):
    optimize = True
    @skipIf(OPTIMIZE_SKIP, 'requested')
    def setUp(self, *args, **kargs):
        return super(Hex1FuzzTest16Optimize, self).setUp(*args, **kargs)
