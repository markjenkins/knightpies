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

from unittest import TestCase
from io import BytesIO
from hashlib import sha256
from os import unlink

from stage0dir import get_stage0_file, get_stage0_test_sha256sum
from hex0tobin import write_binary_filefd_from_hex0_filefd
from knightdecode import create_vm
from knightvm_minimal import load_hex_program, grow_memory, execute_vm
from constants import MEM

from .util import get_closed_named_temp_file
from .stage0 import (
    STAGE_0_MONITOR_HEX_FILEPATH, STAGE_0_MONITOR_RELATIVE_PATH,
    STAGE_0_HEX0_ASSEMBLER_RELATIVE_PATH, STAGE_0_HEX0_ASSEMBLER_FILEPATH,
    )

STACK_START = 0x600
STACK_SIZE = 8

def get_sha256sum_of_file_after_hex0_encode(filename):
    with BytesIO() as outputmemfile:
        with open(filename) as hex0file:
            write_binary_filefd_from_hex0_filefd(hex0file, outputmemfile)
            hexdigest = sha256(outputmemfile.getbuffer()).hexdigest()
    return hexdigest

ADDITIONAL_SHA256SUMS = [
    (filename,
     get_sha256sum_of_file_after_hex0_encode( get_stage0_file(filename) ) )
    for filename in (
            'stage1/more.hex0',
            'stage1/dehex.hex0',
            'Linux Bootstrap/xeh.hex0',
    ) # end tuple fed to for filename in
]

class TestHex0Common(TestCase):
    hex0_encoding_rom = STAGE_0_MONITOR_HEX_FILEPATH

    def setUp(self):
        self.stage0_bin_fd = BytesIO()
        with open( self.hex0_encoding_rom ) as stage0hex0fd:
            write_binary_filefd_from_hex0_filefd(
                stage0hex0fd, self.stage0_bin_fd)

    def tearDown(self):
        self.stage0_bin_fd.close()

class TestHex0ToBin(TestHex0Common):
    def test_monitor_matches_known_sha256(self):
        stage0_monitor_sha256sum_HEX = get_stage0_test_sha256sum(
            'roms/stage0_monitor')
        s = sha256(self.stage0_bin_fd.getbuffer())
        self.assertEqual( s.hexdigest(), stage0_monitor_sha256sum_HEX )

    def test_vm_minimal_hex_load(self):
        vm = create_vm(size=0)
        load_hex_program(vm, STAGE_0_MONITOR_HEX_FILEPATH)
        self.assertEqual( self.stage0_bin_fd.getbuffer(), vm[MEM].tobytes() )

class TestHex0KnightExectuteCommon(TestHex0Common):
    registersize = 32
    stack_size_multiplier = 1
    optimize = False

    def setUp(self):
        super().setUp()
        self.stack_end = STACK_START+STACK_SIZE*self.stack_size_multiplier
        self.tape_01_temp_file_path = get_closed_named_temp_file()
        self.tape_02_temp_file_path = get_closed_named_temp_file()

    def tearDown(self):
        super().tearDown()
        unlink(self.tape_01_temp_file_path)
        unlink(self.tape_02_temp_file_path)

    def get_tape1_file_path(self, input_file_fd):
        return self.tape_01_temp_file_path

    def get_stdin_for_vm(self, input_file_fd):
        return input_file_fd

    def get_output_file_path(self):
        return self.tape_01_temp_file_path

    def execute_test_hex_load(self, stage0hex0file, sha256hex):
        output_mem_buffer = BytesIO()

        with open(get_stage0_file(stage0hex0file), 'rb') as input_file_fd:
            vm = create_vm(
                size=0, registersize=self.registersize,
                tapefile1=self.get_tape1_file_path(input_file_fd),
                tapefile2=self.tape_02_temp_file_path,
                stdin=self.get_stdin_for_vm(input_file_fd),
                stdout=output_mem_buffer,
            )
            load_hex_program(vm, self.hex0_encoding_rom )
            self.assertEqual( self.stage0_bin_fd.getbuffer(),
                              vm[MEM].tobytes() )
            grow_memory(vm, self.stack_end)
            execute_vm(vm, optimize=self.optimize, halt_print=False)

        with open(self.get_output_file_path(), 'rb') as tape_file:
            checksum = sha256(tape_file.read())

        self.assertEqual(
            checksum.hexdigest(),
            sha256hex,
            stage0hex0file
        )

    def execute_test_hex_load_published_sha256(
            self, stage0hex0file, sha256sumentry):
        self.execute_test_hex_load(
            stage0hex0file,
            get_stage0_test_sha256sum(sha256sumentry) )

class TestStage0Monitorexecute(TestHex0KnightExectuteCommon):
    def test_stage0_monitor_encodes_self(self):
        self.execute_test_hex_load_published_sha256(
            STAGE_0_MONITOR_RELATIVE_PATH,
            "roms/stage0_monitor")

    def test_encode_stage1_assembler_0(self):
        self.execute_test_hex_load_published_sha256(
            "stage1/stage1_assembler-0.hex0",
            "roms/stage1_assembler-0")

    def test_encode_stage1_assembler_1(self):
        self.execute_test_hex_load_published_sha256(
            "stage1/stage1_assembler-1.hex0",
            "roms/stage1_assembler-1")

    def test_additional_hex0_files(self):
        for filename, sha256hexdigest in ADDITIONAL_SHA256SUMS:
            self.execute_test_hex_load(filename, sha256hexdigest)
        
class TestStage0Monitorexecute32Optimize(TestStage0Monitorexecute):
    optimize = True

class TestHex0ToBin64(TestStage0Monitorexecute):
    stack_size_multiplier = 2
    registersize = 64

class TestHex0ToBin64Optimize(TestHex0ToBin64):
    optimize = True

class TestHex0ToBin16(TestStage0Monitorexecute):
    registersize = 16

class TestHex0ToBin16Optimize(TestHex0ToBin16):
    optimize = True

class TestStage1Hex0Encode(TestHex0KnightExectuteCommon):
    hex0_encoding_rom = STAGE_0_HEX0_ASSEMBLER_FILEPATH
    def get_tape1_file_path(self, input_file_fd):
        return input_file_fd.name

    def get_stdin_for_vm(self, input_file_fd):
        return BytesIO()

    def get_output_file_path(self):
        return self.tape_02_temp_file_path

    def test_encode_stage1_hex0_encodes_self(self):
        self.execute_test_hex_load_published_sha256(
            STAGE_0_HEX0_ASSEMBLER_RELATIVE_PATH,
            "roms/stage1_assembler-0",
    )

class TestStage1Hex0Encode32Optimize(TestStage1Hex0Encode):
    optimize = True

class TestStage1Hex0ToBin64(TestStage1Hex0Encode):
    stack_size_multiplier = 2
    registersize = 64

class TestStage1Hex0ToBin64Optimize(TestStage1Hex0ToBin64):
    optimize = True

class TestStage1Hex0ToBin16(TestStage1Hex0Encode):
    registersize = 16

class TestStage1Hex0ToBin16Optimize(TestStage1Hex0ToBin16):
    optimize = True

if __name__ == '__main__':
    # to invoke, run
    # $ python3 -m knighttests.test_hex0tobin
    # or
    # $ ./runtestmodule.py knighttests/test_hex0tobin.py
    #
    # direct invocation like ./test_hex0tobin.py will not work
    from unittest import main
    main()
