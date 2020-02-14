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

from knightdecode import create_vm
from knightvm_minimal import \
    set_top_of_prog_mem, load_hex_program, grow_memory, execute_vm
from stage0dir import get_stage0_file, get_stage0_test_sha256sum
from constants import MEM

from .stage0 import (
    STAGE_0_MONITOR_HEX_FILEPATH, STAGE_0_MONITOR_RELATIVE_PATH,
    STAGE_0_HEX0_ASSEMBLER_RELATIVE_PATH, STAGE_0_HEX0_ASSEMBLER_FILEPATH,
    )
from .util import get_closed_named_temp_file

STACK_START = 0x600
STACK_SIZE = 8

def make_get_sha256sum_of_file_after_encode(encode_func):
    def func_get_sha256sum_of_file_after_encode(filename):
        with BytesIO() as outputmemfile:
            with open(filename) as hex0file:
                encode_func(hex0file, outputmemfile)
                hexdigest = sha256(outputmemfile.getbuffer()).hexdigest()
        return hexdigest
    return func_get_sha256sum_of_file_after_encode

class HexCommon(TestCase):
    # subclasses must define
    # encoding_rom_filename and rom_encoding_func
    def setUp(self):
        self.encoding_rom_binary = BytesIO()
        with open( self.encoding_rom_filename ) as encoding_rom_file:
            self.rom_encode_func(encoding_rom_file, self.encoding_rom_binary)

    def tearDown(self):
        self.encoding_rom_binary.close()

class Hex256SumMatch:
    # subclasses must define
    # get_sha256_listed_file_bytes
    # sha256sumfilename
    # compute_sha256_digest()

    def test_matches_known_sha256(self):
        target_sha256sum_HEX = get_stage0_test_sha256sum(
            self.sha256sumfilename)

        self.assertEqual(
            self.compute_sha256_digest(),
            target_sha256sum_HEX )

class Encoding_rom_256_Common(Hex256SumMatch):
    def compute_sha256_digest(self):
        s = sha256( self.encoding_rom_binary.getbuffer() )
        return s.hexdigest()

class TestHexKnightExecuteCommonSetup:
    registersize = 32
    stack_size_multiplier = 1
    optimize = False

    def get_stack_start(self):
        # By default returning None will telling a caller that a stack_start
        # isn't defined. This will spare us from having to implement
        # in all sub-classes/tests right away.
        # where this becomes relevant is
        # TestHexKnightExecuteCommon.execute_test_hex_load
        # which calls get_program_end() to figure out where the program
        # ends so it can lock down memory address m that are
        # 0 <= m < get_program_end() using knightvm_minimal.set_top_of_prog_mem
        return None

    def get_program_end(self):
        # assume the program ends where the stack starts, which assumes
        # all read/write memory use by the program is on the stack or
        # heap (after the stack), e.g. no globals defined between where the
        # program is loaded and where the stack starts
        #
        # see TestHexKnightExecuteCommonSetup.get_program_end() comment
        return self.get_stack_start()

    def setup_stack_and_tmp_files(self):
        stack_start = self.get_stack_start()
        if stack_start==None:
            stack_start = STACK_START
        self.stack_end = stack_start+STACK_SIZE*self.stack_size_multiplier
        self.tape_01_temp_file_path = get_closed_named_temp_file()
        self.tape_02_temp_file_path = get_closed_named_temp_file()

    def remove_tmp_files(self):
        unlink(self.tape_01_temp_file_path)
        unlink(self.tape_02_temp_file_path)

    def load_encoding_rom(self, vm):
        with open(self.encoding_rom_filename) as encoding_rom_file:
            for input_byte in self.int_bytes_from_rom_encode_file(
                    encoding_rom_file):
                vm[MEM].append(input_byte)

class TestHexKnightExecuteCommon(HexCommon, TestHexKnightExecuteCommonSetup):
    def setUp(self):
        HexCommon.setUp(self)
        self.setup_stack_and_tmp_files()

    def tearDown(self):
        HexCommon.tearDown(self)
        self.remove_tmp_files()

    def get_end_of_memory(self):
        return self.stack_end

    def generate_input_fd(self, primary_input_file_path):
        return open(primary_input_file_path, 'rb')

    def generate_bytes_from_output(self):
        with open(self.get_output_file_path(), 'rb') as output_file_fd:
            output_bytes = output_file_fd.read()
        return output_bytes

    def execute_test_hex_load(self, stage0hexfile, sha256hex):
        output_mem_buffer = BytesIO()
        with self.generate_input_fd(get_stage0_file(stage0hexfile) ) as \
             input_file_fd:

            vm = create_vm(
                size=0, registersize=self.registersize,
                tapefile1=self.get_tape1_file_path(input_file_fd),
                tapefile2=self.tape_02_temp_file_path,
                stdin=self.get_stdin_for_vm(input_file_fd),
                stdout=output_mem_buffer,
            )
            self.load_encoding_rom(vm)

            # protect code address from writes, only allow after where it
            # ends. We can only do this if get_program_end() returns a useful
            # value
            prog_end = self.get_program_end()
            if prog_end!=None:
                vm = set_top_of_prog_mem(vm, prog_end)

            self.assertEqual( self.encoding_rom_binary.getbuffer(),
                              vm[MEM].tobytes() )
            grow_memory(vm, self.get_end_of_memory())
            execute_vm(vm, optimize=self.optimize, halt_print=False)

        checksum_hex = sha256(
            self.generate_bytes_from_output() ).hexdigest()

        self.assertEqual(
            checksum_hex,
            sha256hex,
            stage0hexfile
        )

    def execute_test_hex_load_published_sha256(
            self, stage0hexfile, sha256sumentry):
        self.execute_test_hex_load(
            stage0hexfile,
            get_stage0_test_sha256sum(sha256sumentry) )
        
class CommonStage1HexEncode:
    encoding_rom_filename = STAGE_0_HEX0_ASSEMBLER_FILEPATH
    def get_tape1_file_path(self, input_file_fd):
        return input_file_fd.name

    def get_stdin_for_vm(self, input_file_fd):
        return BytesIO()

    def get_output_file_path(self):
        return self.tape_02_temp_file_path
