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

from unittest import TestCase, skipIf

from constants import MEM, REG
from knightdecode import create_vm, grow_memory, read_and_eval
from .testflags import OPTIMIZE_SKIP, DIFF_REG_SIZE_SKIP

class SimpleInstructionTests(TestCase):
    registersize = 32
    optimize = False

    def setUp(self):
        self.vm = create_vm(size=0, registersize=self.registersize)

    def load_1OP_int_prefix(self):
        self.vm[MEM].frombytes( bytes.fromhex('0D0000') )

    def load_2OP_int_prefix(self):
        self.vm[MEM].frombytes( bytes.fromhex('0900') )

    def load_3OP_int_prefix(self):
        self.vm[MEM].frombytes( bytes.fromhex('05') )

    def load_2OPI_prefix(self):
        self.vm[MEM].frombytes( bytes.fromhex('E100') )

    def test_FALSE(self):
        self.load_1OP_int_prefix()
        self.vm[MEM].frombytes( bytes.fromhex('20') ) # FALSE r0
        read_and_eval(self.vm)
        self.assertEqual( self.vm[REG][0], 0 )

    def test_TRUE(self):
        self.load_1OP_int_prefix()
        self.vm[MEM].frombytes( bytes.fromhex('30') ) # TRUE r0
        read_and_eval(self.vm, optimize=self.optimize)
        # look for all 1 bits
        # ~ gets us a negative number that has
        # a 1 bit and zeros where the 1 bits are
        # - get us the positive version
        # and we compare that to 2**self.registersize (1 larger than max)
        self.assertEqual( -~self.vm[REG][0], 1<<self.registersize )
        self.assertEqual( self.vm[REG][0], (1<<self.registersize)-1 )

    def test_NOT(self):
        self.load_2OP_int_prefix()
        self.vm[MEM].frombytes( bytes.fromhex('0601') ) # NOT r0 r1
        read_and_eval(self.vm)
        self.assertEqual( self.vm[REG][0], 2**(self.registersize)-1)

    def test_LOADX16_STOREX16(self):
        self.vm[MEM].frombytes( bytes.fromhex('00000000') ) # NOP
        self.load_3OP_int_prefix()
        self.vm[MEM].frombytes( bytes.fromhex('04A012') ) # STOREX16 r0 r1 r2
        self.load_3OP_int_prefix()
        self.vm[MEM].frombytes( bytes.fromhex('03C312') ) # LOADXU16 r3 r1 r2
        self.vm[REG][0] = 0xDE
        self.vm[REG][1] = 0
        self.vm[REG][2] = 0
        self.vm = read_and_eval(self.vm) # run the NOP
        self.vm = read_and_eval(self.vm) # run the STOREX16
        self.vm = read_and_eval(self.vm) # run the LOADXU16
        self.assertEqual(
            self.vm[REG][0], self.vm[REG][3]
        )

    def test_SUB(self):
        self.load_3OP_int_prefix()
        self.vm[MEM].frombytes( bytes.fromhex('002012') ) # SUB r0 r1 r2
        self.vm[REG][1] = 0
        self.vm[REG][2] = 1
        read_and_eval(self.vm)
        self.assertEqual(
            self.vm[REG][0], (2**self.registersize)-1
        )

    def test_ADDUI(self):
        self.load_2OPI_prefix()
        self.vm[MEM].frombytes( bytes.fromhex('0F010001') ) # ADDUI r0 r1 1
        read_and_eval(self.vm)
        self.assertEqual( self.vm[REG][0], 1)
        
class SimpleInstructionTests32Optimize(SimpleInstructionTests):
    optimize = True
    @skipIf(OPTIMIZE_SKIP, 'requested')
    def setUp(self, *args, **kargs):
        return super(SimpleInstructionTests32Optimize, self).setUp(
            *args, **kargs)

class SimpleInstructionTests64(SimpleInstructionTests):
    registersize = 64
    @skipIf(DIFF_REG_SIZE_SKIP, 'requested')
    def setUp(self, *args, **kargs):
        return super(SimpleInstructionTests64, self).setUp(*args, **kargs)

class SimpleInstructionTests64Optimize(SimpleInstructionTests64):
    optimize = True
    def setUp(self, *args, **kargs):
        return super(SimpleInstructionTests64Optimize, self).setUp(
            *args, **kargs)

class SimpleInstructionTests16(SimpleInstructionTests):
    registersize = 16
    @skipIf(DIFF_REG_SIZE_SKIP, 'requested')
    def setUp(self, *args, **kargs):
        return super(SimpleInstructionTests16, self).setUp(*args, **kargs)

class SimpleInstructionTests16Optimize(SimpleInstructionTests16):
    optimize = True
    def setUp(self, *args, **kargs):
        return super(SimpleInstructionTests16Optimize, self).setUp(
            *args, **kargs)

if __name__ == '__main__':
    # to invoke, run
    # $ python3 -m knighttests.test_simple
    # or
    # $ ./runtestmodule.py knighttests/test_simple.py
    #
    # direct invocation like ./test_simple.py will not work
    # PYTHONPATH=. ./knighttests/test_simple.py still works
    # but don't count on it staying that way
    from unittest import main
    main()
