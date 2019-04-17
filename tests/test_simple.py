#!/usr/bin/env python3

from unittest import TestCase

from constants import MEM, REG
from knightdecode import create_vm, grow_memory, read_and_eval

class SimpleInstructionTests(TestCase):
    registersize = 32

    def setUp(self):
        self.vm = create_vm(size=0, registersize=self.registersize)

    def test_FALSE(self):
        self.vm[MEM].frombytes( bytes.fromhex('0D000020') ) # FALSE r0
        read_and_eval(self.vm)
        self.assertEqual( self.vm[REG][0], 0 )
