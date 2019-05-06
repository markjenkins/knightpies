from unittest import TestCase
from io import BytesIO
from hashlib import sha256
from os import unlink

from stage0dir import get_stage0_file, get_stage0_test_sha256sum
from hex0tobin import write_binary_filefd_from_hex0_filefd
from knightdecode import create_vm
from knightvm_minimal import load_hex_program, grow_memory, execute_vm
from constants import MEM

from tempfile import mktemp

STACK_START = 0x600
STACK_SIZE = 8

STAGE_0_MONITOR_HEX_FILEPATH = get_stage0_file('stage0/stage0_monitor.hex0')

class TestHex0ToBin(TestCase):
    def setUp(self):
        stage0hex0fd = open( STAGE_0_MONITOR_HEX_FILEPATH )
        self.stage0_bin_fd = BytesIO()
        write_binary_filefd_from_hex0_filefd(stage0hex0fd, self.stage0_bin_fd)
        stage0hex0fd.close()

    def tearDown(self):
        self.stage0_bin_fd.close()

    def test_monitor_matches_known_sha256(self):
        stage0_monitor_sha256sum_HEX = get_stage0_test_sha256sum(
            'roms/stage0_monitor')
        s = sha256(self.stage0_bin_fd.getbuffer())
        self.assertEqual( s.hexdigest(), stage0_monitor_sha256sum_HEX )

    def test_vm_minimal_hex_load(self):
        vm = create_vm(size=0)
        load_hex_program(vm, STAGE_0_MONITOR_HEX_FILEPATH)
        self.assertEqual( self.stage0_bin_fd.getbuffer(), vm[MEM].tobytes() )

    def test_execute_hex_load(self):
        output_mem_buffer = BytesIO()
        input_file_fd = open(
            get_stage0_file("stage0/stage0_monitor.hex0"), 'rb')
        tape_01_temp_file_path = mktemp() # deprecated due to security issues
        tape_02_temp_file_path = mktemp() # deprecated due to security issues
        vm = create_vm(
            size=0, registersize=32,
            tapefile1=tape_01_temp_file_path, tapefile2=tape_02_temp_file_path,
            stdin=input_file_fd,
            stdout=output_mem_buffer,
        )
        load_hex_program(vm, STAGE_0_MONITOR_HEX_FILEPATH)
        self.assertEqual( self.stage0_bin_fd.getbuffer(), vm[MEM].tobytes() )
        grow_memory(vm, STACK_START+STACK_SIZE)
        execute_vm(vm, halt_print=False)
        input_file_fd.close()
        tape_file = open(tape_01_temp_file_path, 'rb')
        checksum = sha256(tape_file.read())
        tape_file.close()
        unlink(tape_01_temp_file_path)
        unlink(tape_02_temp_file_path)

        self.assertEqual(
            checksum.hexdigest(),
            get_stage0_test_sha256sum('roms/stage0_monitor') )
