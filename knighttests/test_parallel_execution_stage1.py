from io import BytesIO, StringIO
from ctypes import create_string_buffer
from os import link
from os.path import exists
from filecmp import cmp as file_compare

from .test_parallel_execution import \
    (ParallelExecutionTests, LILITH_REGISTER_SIZE,
     LILITH_TAPE_NAME_01, LILITH_TAPE_NAME_02,
     )
from .stage0 import STAGE_0_HEX2_ASSEMBLER_FILEPATH

from knightvm_minimal import load_program
from knightdecode import (
    create_vm, grow_memory, read_instruction, eval_instruction,
    MIN_INSTRUCTION_LEN,
    )
from hex1tobin import write_binary_filefd_from_hex1_filefd
from stage0dir import get_stage0_file
from constants import MEM

class Stage1(ParallelExecutionTests):
    encode_rom_func = staticmethod(write_binary_filefd_from_hex1_filefd)
    stack_start = 0x3f4
    stack_size = 16
    heap_start = 0x700
    heap_size = 2048

    def setUp(self):
        ParallelExecutionTests.setUp(self)
        if exists(LILITH_TAPE_NAME_01):
            self.fail("%s should be gone at the end of run" %
                      LILITH_TAPE_NAME_01)
        link(self.get_tape_01_file(), LILITH_TAPE_NAME_01)

    def load_rom(self):
        load_program(self.py_vm, self.binary_rom_filename)

    def get_output_filename(self):
        return self.tape_02_filename

    def get_vm_size(self):
        assert self.get_address_after_stack() < self.heap_start
        return self.heap_start + self.heap_size

    def get_address_after_stack(self):
        return self.stack_start+self.stack_size

    def finish_setup(self, input_file_name):
        self.py_vm = create_vm(
            size=0, registersize=LILITH_REGISTER_SIZE,
            tapefile1=input_file_name,
            tapefile2=self.tape_02_filename,
            stdin=None,
            stdout=self.output_mem_buffer,
        )

        self.load_rom()
        self.program_size = len(self.py_vm[MEM])
        grow_memory(self.py_vm, self.vm_size)

        self.rom_name_string_buffer = create_string_buffer(
            self.binary_rom_filename.encode('ascii') )
        self.c_vm.load_lilith(self.rom_name_string_buffer)

    def run_execution_test(self, romfilename_hex, stdin_filename):
        with open(romfilename_hex, 'r') as romfile_hex:
            self.encode_rom_func(romfile_hex, self.binary_rom)
        self.binary_rom.close()

        with open(stdin_filename, 'rb') as input_file_fd:
            self.finish_setup(stdin_filename)

            self.do_state_checks()
            while True:
                debug_tuple = self.advance_both_vms()
                if self.halted():
                    break # don't bother with state checks after HALT
                self.do_state_checks(debug_tuple)

        self.assertTrue(
            file_compare(self.get_output_filename(), LILITH_TAPE_NAME_02,
                         shallow=False),
            "%s vs %s" % (self.get_output_filename(), LILITH_TAPE_NAME_02)
        )
    def test_stage1_hex2_encodes_set(self):
        self.run_execution_test(
            STAGE_0_HEX2_ASSEMBLER_FILEPATH,
            self.get_tape_01_file() )

    @staticmethod
    def get_tape_01_file():
        return get_stage0_file("stage1/SET.hex2")
