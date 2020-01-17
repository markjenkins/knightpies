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
from io import BytesIO
from os.path import exists

from stage0dir import get_stage0_file
from hex0tobin import write_binary_filefd_from_hex0_filefd
from knightvm_minimal import load_hex_program

from .hexcommon import (
    Hex256SumMatch, HexCommon, Encoding_rom_256_Common,
    make_get_sha256sum_of_file_after_encode,
    TestHexKnightExecuteCommon,
    CommonStage1HexEncode,
    )
from .stage0 import (
    STAGE_0_MONITOR_HEX_FILEPATH, STAGE_0_MONITOR_RELATIVE_PATH,
    STAGE_0_HEX0_ASSEMBLER_RELATIVE_PATH, STAGE_0_HEX0_ASSEMBLER_FILEPATH,
    STAGE_0_HEX1_ASSEMBLER_RELATIVE_PATH,
    )
from .testflags import OPTIMIZE_SKIP

get_sha256sum_of_file_after_hex0_encode = \
    make_get_sha256sum_of_file_after_encode(
        write_binary_filefd_from_hex0_filefd)

ADDITIONAL_SHA256SUMS_may_not_exist_exemptions = {
    'Linux Bootstrap/xeh.hex0',
    }

ADDITIONAL_SHA256SUMS = [
    (filename,
     get_sha256sum_of_file_after_hex0_encode( get_stage0_file(filename) ) )
    for filename in (
            'stage1/more.hex0',
            'stage1/dehex.hex0',
            'Linux Bootstrap/xeh.hex0',
    ) # end tuple fed to for filename in
    if (filename not in ADDITIONAL_SHA256SUMS_may_not_exist_exemptions or
        exists(filename) )
]

class Hex0Common(HexCommon):
    encoding_rom_filename = STAGE_0_MONITOR_HEX_FILEPATH
    rom_encode_func = staticmethod(write_binary_filefd_from_hex0_filefd)

class Test_monitor_256Sum(Hex0Common, Encoding_rom_256_Common):
    sha256sumfilename = 'roms/stage0_monitor'

class Hex0EncodeSpecificFile(TestCase):
    def compute_sha256_digest(self):
        return get_sha256sum_of_file_after_hex0_encode(
            self.sha256_compare_filename)

class Test_dehex_256Sum(
        Hex256SumMatch, Hex0EncodeSpecificFile):
    sha256sumfilename = 'roms/DEHEX'
    sha256_compare_filename = get_stage0_file('stage1/dehex.hex0')

class TestHex0KnightExecuteCommon(Hex0Common, TestHexKnightExecuteCommon):
    def setUp(self):
        Hex0Common.setUp(self)
        self.setup_stack_and_tmp_files()

    def tearDown(self):
        Hex0Common.tearDown(self)
        self.remove_tmp_files()

    def load_encoding_rom(self, vm):
        load_hex_program(vm, self.encoding_rom_filename )

    def get_tape1_file_path(self, input_file_fd):
        return self.tape_01_temp_file_path

    def get_stdin_for_vm(self, input_file_fd):
        return input_file_fd

    def get_output_file_path(self):
        return self.tape_01_temp_file_path

class TestStage0Monitorexecute(TestHex0KnightExecuteCommon):
    def test_stage0_monitor_encodes_self(self):
        self.execute_test_hex_load_published_sha256(
            STAGE_0_MONITOR_RELATIVE_PATH,
            "roms/stage0_monitor")

    def test_encode_stage1_assembler_0(self):
        self.execute_test_hex_load_published_sha256(
            STAGE_0_HEX0_ASSEMBLER_RELATIVE_PATH,
            "roms/stage1_assembler-0")

    def test_encode_stage1_assembler_1(self):
        self.execute_test_hex_load_published_sha256(
            STAGE_0_HEX1_ASSEMBLER_RELATIVE_PATH,
            "roms/stage1_assembler-1")

    def test_additional_hex0_files(self):
        for filename, sha256hexdigest in ADDITIONAL_SHA256SUMS:
            self.execute_test_hex_load(filename, sha256hexdigest)
        
class TestStage0Monitorexecute32Optimize(TestStage0Monitorexecute):
    optimize = True
    @skipIf(OPTIMIZE_SKIP, 'requested')
    def setUp(self, *args, **kargs):
        return super(TestStage0Monitorexecute32Optimize, self).setUp(
            *args, **kargs)

class TestHex0ToBin64(TestStage0Monitorexecute):
    stack_size_multiplier = 2
    registersize = 64

class TestHex0ToBin64Optimize(TestHex0ToBin64):
    optimize = True
    @skipIf(OPTIMIZE_SKIP, 'requested')
    def setUp(self, *args, **kargs):
        return super(TestHex0ToBin64Optimize, self).setUp(
            *args, **kargs)

class TestHex0ToBin16(TestStage0Monitorexecute):
    registersize = 16

class TestHex0ToBin16Optimize(TestHex0ToBin16):
    optimize = True
    @skipIf(OPTIMIZE_SKIP, 'requested')
    def setUp(self, *args, **kargs):
        return super(TestHex0ToBin16Optimize, self).setUp(
            *args, **kargs)

class TestStage1Hex0Encode(CommonStage1HexEncode, TestHex0KnightExecuteCommon):
    def test_encode_stage1_hex0_encodes_self(self):
        self.execute_test_hex_load_published_sha256(
            STAGE_0_HEX0_ASSEMBLER_RELATIVE_PATH,
            "roms/stage1_assembler-0",
    )

    def test_encode_stage0_monitor_with_stage1_hex0(self):
        self.execute_test_hex_load_published_sha256(
            STAGE_0_MONITOR_HEX_FILEPATH,
            "roms/stage0_monitor",
    )

    def test_encode_stage1_hex1_with_stage1_hex0(self):
        self.execute_test_hex_load_published_sha256(
            STAGE_0_HEX1_ASSEMBLER_RELATIVE_PATH,
            "roms/stage1_assembler-1",
    )

    def test_additional_hex0_files(self):
        for filename, sha256hexdigest in ADDITIONAL_SHA256SUMS:
            self.execute_test_hex_load(filename, sha256hexdigest)

class TestStage1Hex0Encode32Optimize(TestStage1Hex0Encode):
    optimize = True
    @skipIf(OPTIMIZE_SKIP, 'requested')
    def setUp(self, *args, **kargs):
        return super(TestStage1Hex0Encode32Optimize, self).setUp(*args, **kargs)

class TestStage1Hex0ToBin64(TestStage1Hex0Encode):
    stack_size_multiplier = 2
    registersize = 64

class TestStage1Hex0ToBin64Optimize(TestStage1Hex0ToBin64):
    optimize = True
    @skipIf(OPTIMIZE_SKIP, 'requested')
    def setUp(self, *args, **kargs):
        return super(TestStage1Hex0ToBin64Optimize, self).setUp(*args, **kargs)

class TestStage1Hex0ToBin16(TestStage1Hex0Encode):
    registersize = 16

class TestStage1Hex0ToBin16Optimize(TestStage1Hex0ToBin16):
    optimize = True
    @skipIf(OPTIMIZE_SKIP, 'requested')
    def setUp(self, *args, **kargs):
        return super(TestStage1Hex0ToBin16Optimize, self).setUp(*args, **kargs)

if __name__ == '__main__':
    # to invoke, run
    # $ python3 -m knighttests.test_hex0tobin
    # or
    # $ ./runtestmodule.py knighttests/test_hex0tobin.py
    #
    # direct invocation like ./test_hex0tobin.py will not work
    from unittest import main
    main()
