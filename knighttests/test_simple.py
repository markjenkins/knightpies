#!/usr/bin/env python3

from unittest import TestCase

from constants import MEM, REG
from knightdecode import create_vm, grow_memory, read_and_eval

class SimpleInstructionTests(TestCase):
    registersize = 32
    optimize = True

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
        read_and_eval(self.vm, optimize=self.optimize)
        # look for all 1 bits
        # ~ gets us a negative number that has
        # a 1 bit and zeros where the 1 bits are
        # - get us the positive version
        # and we compare that to 2**self.registersize (1 larger than max)
        self.assertEqual( -~self.vm[REG][0], 1<<self.registersize )
        self.assertEqual( self.vm[REG][0], (1<<self.registersize)-1 )

class SimpleInstructionTests32NoOptimize(SimpleInstructionTests):
    optimize = False
        
class SimpleInstructionTests64(SimpleInstructionTests):
    registersize = 64

class SimpleInstructionTests64NoOptimize(SimpleInstructionTests64):
    optimize = False   

class SimpleInstructionTests16(SimpleInstructionTests):
    registersize = 16

class SimpleInstructionTests16NoOptimize(SimpleInstructionTests16):
    optimize = False

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
