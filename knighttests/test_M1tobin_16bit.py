from .test_M1tobin import TestStage1M0Assemble

class TestM1_16(TestStage1M0Assemble):
    registersize = 16
    def get_program_end(self):
        return 0x5e0

    def test_M0_assembler(self):
        self.execute_test_hex_load_published_sha256(
            'stage0/stage0_monitor.s',
            "roms/stage0_monitor",
        )
