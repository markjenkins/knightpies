from hex2tobin import write_binary_filefd_from_hex2_filefd
from stage0dir import get_stage0_file

from .test_parallel_execution_stage1 import Stage1

class Stage1EncodeM0(Stage1):
    encode_rom_func = staticmethod(write_binary_filefd_from_hex2_filefd)
    stack_start = 0x5e0
    # (by our count ten 4 byte registers could be on the stack [40], but we'll
    #  pad out to a nice looking number, not a bug to test more memory)
    stack_size = 48
    heap_start = 0x4000
    heap_size = 1024*8

    def test_stage1_hex2_encodes_set(self):
        self.run_execution_test(
            get_stage0_file("stage1/M0-macro.hex2"),
            self.get_tape_01_file() )

    @staticmethod
    def get_tape_01_file():
        return get_stage0_file("stage0/stage0_monitor.s")
