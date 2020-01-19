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

from unittest import skipIf

from stage0dir import get_stage0_file
from hex0tobin import write_binary_filefd_from_hex0_filefd
from hex1tobin import write_binary_filefd_from_hex1_filefd
from hex2tobin import write_binary_filefd_from_hex2_filefd

from .hexcommon import (
    Hex256SumMatch, HexCommon, Encoding_rom_256_Common,
    make_get_sha256sum_of_file_after_encode
    )
from .test_hex1tobin import (
    get_sha256sum_of_file_after_hex1_encode,
    CommonStage1HexEncode, TestHex1KnightExecuteCommon,
    )
from .stage0 import (
    STAGE_0_HEX1_ASSEMBLER_FILEPATH,
    STAGE_0_HEX2_ASSEMBLER_FILEPATH,
    )
from .testflags import OPTIMIZE_SKIP, DIFF_REG_SIZE_SKIP

get_sha256sum_of_file_after_hex2_encode = \
    make_get_sha256sum_of_file_after_encode(
        write_binary_filefd_from_hex2_filefd)

class Hex2Common(HexCommon):
    encoding_rom_filename = STAGE_0_HEX1_ASSEMBLER_FILEPATH
    rom_encode_func = staticmethod(write_binary_filefd_from_hex0_filefd)

class Test_hex_assembler1_256Sum(Hex2Common, Encoding_rom_256_Common):
    sha256sumfilename = 'roms/stage1_assembler-1'

class Test_hex_assember2_256Sum(Hex2Common, Hex256SumMatch):
    sha256sumfilename = 'roms/stage1_assembler-2'

    def compute_sha256_digest(self):
        return get_sha256sum_of_file_after_hex1_encode(
            STAGE_0_HEX2_ASSEMBLER_FILEPATH)

class Test_SET_256Sum(Hex2Common, Hex256SumMatch):
    sha256sumfilename = 'roms/SET'

    def compute_sha256_digest(self):
        return get_sha256sum_of_file_after_hex2_encode(
            get_stage0_file('stage1/SET.hex2') )

class TestStage1Hex2Encode(CommonStage1HexEncode, TestHex1KnightExecuteCommon):
    encoding_rom_filename = STAGE_0_HEX2_ASSEMBLER_FILEPATH
    rom_encode_func = staticmethod(write_binary_filefd_from_hex1_filefd)

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

class TestStage1Hex2EncodeOptimise(TestStage1Hex2Encode):
    optimize = True
    @skipIf(OPTIMIZE_SKIP, 'requested')
    def setUp(self, *args, **kargs):
        return super(TestStage1Hex2EncodeOptimise, self).setUp(*args, **kargs)

class TestStage1Hex2Encode64(TestStage1Hex2Encode):
    registersize = 64
    @skipIf(DIFF_REG_SIZE_SKIP, 'requested')
    def setUp(self, *args, **kargs):
        return super(TestStage1Hex2Encode64, self).setUp(*args, **kargs)

class TestStage1Hex2Encode64Optimise(TestStage1Hex2Encode64):
    optimize = True
    @skipIf(OPTIMIZE_SKIP, 'requested')
    def setUp(self, *args, **kargs):
        return super(TestStage1Hex2Encode64Optimise, self).setUp(*args, **kargs)

class TestStage1Hex2Encode16(TestStage1Hex2Encode):
    registersize = 16
    @skipIf(DIFF_REG_SIZE_SKIP, 'requested')
    def setUp(self, *args, **kargs):
        return super(TestStage1Hex2Encode16, self).setUp(*args, **kargs)

class TestStage1Hex2Encode16Optimise(TestStage1Hex2Encode64):
    optimize = True
    @skipIf(OPTIMIZE_SKIP, 'requested')
    def setUp(self, *args, **kargs):
        return super(TestStage1Hex2Encode16Optimise, self).setUp(*args, **kargs)
