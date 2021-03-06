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

from stage0dir import get_stage0_file
from hex0tobin import write_binary_filefd_from_hex0_filefd
from hex1tobin import (
    write_binary_filefd_from_hex1_filefd,
    int_bytes_from_hex1_fd,
    )
from hex2tobin import write_binary_filefd_from_hex2_filefd

from .hexcommon import (
    Hex256SumMatch, HexCommon, Encoding_rom_256_Common,
    make_get_sha256sum_of_file_after_encode,
    CommonStage1HexEncode,
    TestHexKnightExecuteCommon,
    )
from .test_hex1tobin import (
    get_sha256sum_of_file_after_hex1_encode,
    )
from .stage0 import (
    STAGE_0_HEX1_ASSEMBLER_FILEPATH,
    STAGE_0_HEX2_ASSEMBLER_FILEPATH,
    )
from .util import make_optimize_and_register_size_variations

get_sha256sum_of_file_after_hex2_encode = \
    make_get_sha256sum_of_file_after_encode(
        write_binary_filefd_from_hex2_filefd)

class Test_hex_assember2_ROM_256Sum(TestCase, Hex256SumMatch):
    sha256sumfilename = 'roms/stage1_assembler-2'

    def compute_sha256_digest(self):
        return get_sha256sum_of_file_after_hex1_encode(
            STAGE_0_HEX2_ASSEMBLER_FILEPATH)

class Test_SET_256Sum(TestCase, Hex256SumMatch):
    sha256sumfilename = 'roms/SET'

    def compute_sha256_digest(self):
        return get_sha256sum_of_file_after_hex2_encode(
            get_stage0_file('stage1/SET.hex2') )

class TestStage1Hex2Encode(CommonStage1HexEncode, TestHexKnightExecuteCommon):
    encoding_rom_filename = STAGE_0_HEX2_ASSEMBLER_FILEPATH
    rom_encode_func = staticmethod(write_binary_filefd_from_hex1_filefd)
    int_bytes_from_rom_encode_file = staticmethod(int_bytes_from_hex1_fd)

    #  setUp and tearDown come from TestHexKnightExecuteCommon

    def get_end_of_memory(self):
        return 0x700+1024*4

    def test_encode_SET_with_stage1_hex2(self):
        self.execute_test_hex_load_published_sha256(
            get_stage0_file('stage1/SET.hex2'),
            "roms/SET",
    )

    def test_encode_M0_with_stage1_hex2(self):
        self.execute_test_hex_load_published_sha256(
            get_stage0_file('stage1/M0-macro.hex2'),
            "roms/M0",
    )

(TestStage1Hex2Encode32Optimise,
 TestStage1Hex2Encode64,
 TestStage1Hex2Encode64Optimise,
 TestStage1Hex2Encode16,
 TestStage1Hex2Encode16Optimise,
 ) = make_optimize_and_register_size_variations(TestStage1Hex2Encode)

