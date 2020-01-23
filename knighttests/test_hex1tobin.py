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

from hex0tobin import write_binary_filefd_from_hex0_filefd
from hex1tobin import (
    write_binary_filefd_from_hex1_filefd,
    int_bytes_from_hex1_fd,
    )

from .hexcommon import (
    HexCommon, Encoding_rom_256_Common,
    make_get_sha256sum_of_file_after_encode,
    TestHexKnightExecuteCommon,
    CommonStage1HexEncode,
)
from .stage0 import (
    STAGE_0_HEX0_ASSEMBLER_FILEPATH,
    STAGE_0_HEX1_ASSEMBLER_FILEPATH,
    STAGE_0_HEX2_ASSEMBLER_RELATIVE_PATH,
    )
from .testflags import OPTIMIZE_SKIP, DIFF_REG_SIZE_SKIP
from constants import MEM

get_sha256sum_of_file_after_hex1_encode = \
    make_get_sha256sum_of_file_after_encode(
        write_binary_filefd_from_hex1_filefd)

class Hex1Common(HexCommon):
    encoding_rom_filename = STAGE_0_HEX0_ASSEMBLER_FILEPATH
    rom_encode_func = staticmethod(write_binary_filefd_from_hex0_filefd)

class Test_hex_assembler0_256Sum(Hex1Common, Encoding_rom_256_Common):
    sha256sumfilename = 'roms/stage1_assembler-0'

class TestHex1KnightExecuteCommon(Hex1Common, TestHexKnightExecuteCommon):
    def setUp(self):
        Hex1Common.setUp(self)
        self.setup_stack_and_tmp_files()

    def tearDown(self):
        Hex1Common.tearDown(self)
        self.remove_tmp_files()

    int_bytes_from_rom_encode_file = staticmethod(int_bytes_from_hex1_fd)

class TestStage1Hex1Encode(CommonStage1HexEncode, TestHex1KnightExecuteCommon):
    encoding_rom_filename = STAGE_0_HEX1_ASSEMBLER_FILEPATH
    def test_encode_stage1_hex2_with_stage1_hex1(self):
        self.execute_test_hex_load_published_sha256(
            STAGE_0_HEX2_ASSEMBLER_RELATIVE_PATH,
            "roms/stage1_assembler-2",
    )

class TestStage1Hex1EncodeOptimize(TestStage1Hex1Encode):
    optimize = True
    @skipIf(OPTIMIZE_SKIP, 'requested')
    def setUp(self, *args, **kargs):
        return super(TestStage1Hex1EncodeOptimize, self).setUp(*args, **kargs)

class TestStage1Hex1Encode64(TestStage1Hex1Encode):
    registersize = 64
    @skipIf(DIFF_REG_SIZE_SKIP, 'requested')
    def setUp(self, *args, **kargs):
        return super(TestStage1Hex1Encode64, self).setUp(*args, **kargs)

class TestStage1Hex1Encode64Optimize(TestStage1Hex1Encode64):
    optimize = True
    @skipIf(OPTIMIZE_SKIP, 'requested')
    def setUp(self, *args, **kargs):
        return super(TestStage1Hex1Encode64Optimize, self).setUp(
            *args, **kargs)

class TestStage1Hex1Encode16(TestStage1Hex1Encode):
    registersize = 16
    @skipIf(DIFF_REG_SIZE_SKIP, 'requested')
    def setUp(self, *args, **kargs):
        return super(TestStage1Hex1Encode16, self).setUp(*args, **kargs)

class TestStage1Hex1Encode16Optimize(TestStage1Hex1Encode16):
    optimize = True
    @skipIf(OPTIMIZE_SKIP, 'requested')
    def setUp(self, *args, **kargs):
        return super(TestStage1Hex1Encode16Optimize, self).setUp(
            *args, **kargs)
