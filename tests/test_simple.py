#!/usr/bin/env python3

from unittest import TestCase

from constants import MEM, REG
from knightdecode import create_vm, grow_memory, read_and_eval

class SimpleInstructionTests(TestCase):
    registersize = 32

    def setUp(self):
        self.vm = create_vm(size=0, registersize=self.registersize)

    def load_1OP_int_prefix(self):
        self.vm[MEM].frombytes( bytes.fromhex('0D0000') )

    def test_FALSE(self):
        self.load_1OP_int_prefix()
        self.vm[MEM].frombytes( bytes.fromhex('20') ) # FALSE r0
        read_and_eval(self.vm)
        self.assertEqual( self.vm[REG][0], 0 )

    def test_TRUE(self):
        self.load_1OP_int_prefix()
        self.vm[MEM].frombytes( bytes.fromhex('30') ) # TRUE r0
        read_and_eval(self.vm)
        # look for all 1 bits
        # ~ gets us a negative number that has
        # a 1 bit and zeros where the 1 bits are
        # - get us the positive version
        # and we compare that to 2**self.registersize (1 larger than max)
        self.assertEqual( -~self.vm[REG][0], 1<<self.registersize )