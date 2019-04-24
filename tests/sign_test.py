#!/usr/bin/env python3

from unittest import TestCase

from constants import MEM, REG
from knightdecode import create_vm, grow_memory, read_and_eval

testcases = (
    '0000',
    '0001',
    '0002',
    '0003',
    '8000',
    '8001',
    '8002',
    'C000',
    'C001',
    'C002',
    'F000',
    'F001',
    'FFFF',
    '800F',
)


class EdgeCaseSignedIntegerTests(TestCase):
    registersize = 32
    optimize = True
    def setUp(self):
        self.vm = create_vm(size=0, registersize=self.registersize)
        self.vm[MEM].frombytes( bytes.fromhex('E0002D10') ) # LOADI r0

for sixteenbits_bigendian_hex_str in testcases:
    def test_function(self):
        sixteenbits = bytes.fromhex(sixteenbits_bigendian_hex_str)
        # 16 bit immediate value to finish LOADI instruction
        self.vm[MEM].frombytes( sixteenbits )
        read_and_eval(self.vm, self.optimize)
        register_as_bytes = self.vm[REG][0].to_bytes(
            self.vm[REG].itemsize,
            byteorder='big', signed=False)

        value_of_register = int.from_bytes(register_as_bytes,
                                           byteorder='big', signed=True)
        value_of_original_value = int.from_bytes(
            sixteenbits, byteorder='big', signed=True)
        self.assertEqual(
            value_of_register, value_of_original_value,
            "%d bit registers, test value %s" %
            (self.registersize, sixteenbits.hex())
        )
    setattr(EdgeCaseSignedIntegerTests,
            "test_%s" % sixteenbits_bigendian_hex_str,
            test_function)

class ThirtyTwoBitRegistersNoOptimize(EdgeCaseSignedIntegerTests):
    optimize = False

class SixteenBitRegisters(EdgeCaseSignedIntegerTests):
    registersize=16

class SixteenBitRegistersNoOptimize(SixteenBitRegisters):
    optimize = False
    
class SixtyFourBitRegisters(EdgeCaseSignedIntegerTests):
    registersize=64

class SixtyFourBitRegistersNoOptimize(SixtyFourBitRegisters):
    optimize = False

