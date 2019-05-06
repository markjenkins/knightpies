#!/usr/bin/env python3
#
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

from constants import MEM, REG
from knightdecode import create_vm, grow_memory, read_and_eval
from knightinstructions import readin_bytes

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


def make_LOADI_test_case(sixteenbits_bigendian_hex_str):
    def LOADI_test_function(self):
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
    return LOADI_test_function

def make_readin_bytes_test_case(sixteenbits_bigendian_hex_str):
    def readin_bytes_test_function(self):
        sixteenbits = bytes.fromhex(sixteenbits_bigendian_hex_str)
        self.vm[MEM].frombytes( sixteenbits )
        self.assertEqual(
            sixteenbits,
            readin_bytes(self.vm[MEM], 4, True, 2).to_bytes(
                2, 'big', signed=True),
            )
    return readin_bytes_test_function

class EdgeCaseSignedIntegerTests(TestCase):
    registersize = 32
    optimize = True
    def setUp(self):
        self.vm = create_vm(size=0, registersize=self.registersize)
        self.vm[MEM].frombytes( bytes.fromhex('E0002D10') ) # LOADI r0

for sixteenbits_bigendian_hex_str in testcases:
    setattr(EdgeCaseSignedIntegerTests,
            "test_%s" % sixteenbits_bigendian_hex_str,
            make_LOADI_test_case(sixteenbits_bigendian_hex_str) )

class ThirtyTwoBitRegistersNoOptimize(EdgeCaseSignedIntegerTests):
    optimize = False

class SixteenBitRegistersNoOptimize(EdgeCaseSignedIntegerTests):
    registersize=16
    optimize = False
    
class SixteenBitRegistersOptimize(SixteenBitRegistersNoOptimize):
    optimize = True

for sixteenbits_bigendian_hex_str in testcases:
    setattr(SixteenBitRegistersOptimize,
            "test_readin_%s" % sixteenbits_bigendian_hex_str,
            make_readin_bytes_test_case(sixteenbits_bigendian_hex_str) )

class SixtyFourBitRegisters(EdgeCaseSignedIntegerTests):
    registersize=64

class SixtyFourBitRegistersNoOptimize(SixtyFourBitRegisters):
    optimize = False

if __name__ == '__main__':
    # to invoke, run
    # $ python3 -m knighttests.test_sign_extension
    # or
    # $ ./runtestmodule.py knighttests/test_sign_extension.py
    #
    # direct invocation like ./test_sign_extension.py will not work
    # PYTHONPATH=. ./knighttests/test_sign_extension.py still works
    # but don't count on it staying that way
    from unittest import main
    main()
