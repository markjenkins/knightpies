# Copyright (C) 2020 Mark Jenkins <mark@markjenkins.ca>
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
from io import BytesIO
from hashlib import sha256
from tempfile import NamedTemporaryFile

from knightdecode import create_vm
from knightvm_minimal import grow_memory, execute_vm
from constants import MEM
from stage0dir import \
    get_stage0_file, KNIGHT_DEFS_FILE, KNIGHT_DEFS_FILE_RELATIVE
from hex1tobin import write_binary_filefd_from_hex1_filefd
from hex2tobin import (
    write_binary_filefd_from_hex2_filefd,
    int_bytes_from_hex2_fd,
    )
from M1tobin import M1_files_objs_to_bin
from pythoncompat import open_ascii

from .hexcommon import (
    Hex256SumMatch, HexCommon, Encoding_rom_256_Common,
    TestHexKnightExecuteCommon,
    CommonStage1HexEncode,
    )

from .test_hex2tobin import (
    get_sha256sum_of_file_after_hex2_encode,
    write_binary_filefd_from_hex2_filefd,
)

from .util import sha256hexoffile, make_optimize_and_register_size_variations

from .stage0 import (
    STAGE_0_HEX2_ASSEMBLER_FILEPATH,
    STAGE_0_M0_ASSEMBLER_RELATIVE_PATH,
    STAGE_0_M0_ASSEMBLER_FILEPATH,
    )

def binfile_obj_after_M1_and_hex2(*filenames):
    outputmemfile = BytesIO()
    input_fileobjs = [ open_ascii(filename)
                       for filename in filenames ]
    M1_files_objs_to_bin(input_fileobjs, outputmemfile )
    for f in input_fileobjs:
        f.close()
    return outputmemfile

def get_sha256sum_of_file_after_files_are_M1_assembled_and_hex2_linked(
        *filenames):
    outputmemfile = binfile_obj_after_M1_and_hex2(*filenames)
    hexdigest = sha256(outputmemfile.getbuffer()).hexdigest()
    outputmemfile.close()
    return hexdigest

class Test_hex_assembler2_ROM_256Sum(HexCommon, Encoding_rom_256_Common):
    encoding_rom_filename = STAGE_0_HEX2_ASSEMBLER_FILEPATH
    rom_encode_func = staticmethod(write_binary_filefd_from_hex1_filefd)
    sha256sumfilename = 'roms/stage1_assembler-2'

class M0_ROM_SHA256_Common_Ref:
    sha256sumfilename = 'roms/M0'

class Test_M0_ROM_256Sum(TestCase, M0_ROM_SHA256_Common_Ref, Hex256SumMatch):
    def compute_sha256_digest(self):
        return get_sha256sum_of_file_after_hex2_encode(
            get_stage0_file('stage1/M0-macro.hex2'))

class Test_M0_ROM_from_assembler_256Sum(
        TestCase, M0_ROM_SHA256_Common_Ref, Hex256SumMatch):
    def compute_sha256_digest(self):
        return sha256(
            binfile_obj_after_M1_and_hex2(
                KNIGHT_DEFS_FILE,
                get_stage0_file('stage1/M0-macro.s')
            ).getbuffer()).hexdigest()

class M1AssembleToBin_Common_256Sum(object):
    def compute_sha256_digest(self):
        input_filelist = [KNIGHT_DEFS_FILE_RELATIVE] + self.input_filelist
        return \
            get_sha256sum_of_file_after_files_are_M1_assembled_and_hex2_linked(
                *[get_stage0_file(filename) for filename in input_filelist ]
            )


class Test_M1AssemblerToBin_stage0_monitor(
        M1AssembleToBin_Common_256Sum, Hex256SumMatch, TestCase):
    sha256sumfilename = 'roms/stage0_monitor'
    input_filelist = ['stage0/stage0_monitor.s']

class Test_M1AssemblerToBin_stage1_assembler_0(
        M1AssembleToBin_Common_256Sum, Hex256SumMatch, TestCase):
    sha256sumfilename = 'roms/stage1_assembler-0'
    input_filelist = ['stage1/stage1_assembler-0.s']

class Test_M1AssemblerToBin_stage1_assembler_1(
        M1AssembleToBin_Common_256Sum, Hex256SumMatch, TestCase):
    sha256sumfilename = 'roms/stage1_assembler-1'
    input_filelist = ['stage1/stage1_assembler-1.s']

class Test_M1AssemblerToBin_stage0_cc86(
        M1AssembleToBin_Common_256Sum, Hex256SumMatch, TestCase):
    sha256sumfilename = 'roms/cc_x86'
    input_filelist = ['stage2/cc_x86.s']

class Test_M1AssemblerToBin_stage0_dehex(
        M1AssembleToBin_Common_256Sum, Hex256SumMatch, TestCase):
    sha256sumfilename = 'roms/DEHEX'
    input_filelist = ['stage1/dehex.s']

class Test_M1AssemblerToBin_stage0_cat(
        M1AssembleToBin_Common_256Sum, Hex256SumMatch, TestCase):
    sha256sumfilename = 'roms/CAT'
    input_filelist = ['stage1/CAT.s']

class Test_M1AssemblerToBin_stage0_set(
        M1AssembleToBin_Common_256Sum, Hex256SumMatch, TestCase):
    sha256sumfilename = 'roms/SET'
    input_filelist = ['stage1/SET.s']

class Test_M1AssemblerToBin_stage0_lisp(
        M1AssembleToBin_Common_256Sum, Hex256SumMatch, TestCase):
    sha256sumfilename = 'roms/lisp'
    input_filelist = ['stage2/lisp.s']

class Test_M1AssemblerToBin_stage0_forth(
        M1AssembleToBin_Common_256Sum, Hex256SumMatch, TestCase):
    sha256sumfilename = 'roms/forth'
    input_filelist = ['stage2/forth.s']

MONKEY_PATCHES = {
    # stage1_assembler-2.s from stage0 Release 0.2.0
    'a30a60b1020f8e004096fad7ca8d3c810a64beb6dd79d4ccae1e844bda4096b2',
    # stage1_assembler-2.s from stage0 Release 0.3.0
    'a4279c0e0144bb32e22fcb71608001a26f0a4762253ce2f542c8aed27d049b8b'
    } 

DONT_MONKEY_PATCH = {
    # stage1_assembler-2.s after fix for consistency with .hex1 on
    # stack start
    # from stage0 git commit git commit 67b61a541942e4fb6a72422183129d83a5bb26a1
    'ac857f2a7295ccc14aaf2cbb376ab7fbf1b7ac540c85e2d354e88e7306931c71'
    }

def on_override_list(filename_to_lookup):
    hexdigest = sha256hexoffile(filename_to_lookup)
    return hexdigest in MONKEY_PATCHES or hexdigest in DONT_MONKEY_PATCH

class Test_M1AssemblerToBin_stage1_assembler_2(
        M1AssembleToBin_Common_256Sum, Hex256SumMatch, TestCase):
    sha256sumfilename = 'roms/stage1_assembler-2'
    input_filelist = ['stage1/stage1_assembler-2.s']

    @skipIf(
        not on_override_list(get_stage0_file(input_filelist[0])),
        'file does not match binary monkey patch'
    )
    def setUp(self, *args, **kargs):
        return super(Test_M1AssemblerToBin_stage1_assembler_2, self).setUp(
            *args, **kargs)

    def compute_sha256_digest(self):
        input_filelist = [KNIGHT_DEFS_FILE_RELATIVE] + self.input_filelist
        output_binfile = binfile_obj_after_M1_and_hex2(
            *[get_stage0_file(filename)
              for filename in input_filelist ] )
        # patch the location of the start of stack in the 16 bit immediate value
        # of the first instruction LOADUI R15 $stack
        # stage1_assembler-2.s has a label :stack for this, but it ends up
        # a bit before 0x400 when $stack is assembled and linked
        # whereas stage1_assembler-2.hex1 just refers to the cleaner address
        # 0x400 because absolute references are not available in hex1 files
        #
        # but skip patched versions of stage1_assembler-2.s
        if (sha256hexoffile(get_stage0_file(self.input_filelist[0]))
            not in DONT_MONKEY_PATCH):
            output_binfile.getbuffer()[4] = 0x04
            output_binfile.getbuffer()[5] = 0x00
        hexdigest = sha256(output_binfile.getbuffer()).hexdigest()
        output_binfile.close()
        return hexdigest

class TestStage1M0Assemble(CommonStage1HexEncode, TestHexKnightExecuteCommon):
    encoding_rom_filename = STAGE_0_M0_ASSEMBLER_FILEPATH
    rom_encode_func = staticmethod(write_binary_filefd_from_hex2_filefd)
    int_bytes_from_rom_encode_file = staticmethod(int_bytes_from_hex2_fd)

    def setUp(self):
        # TestHexKnightExecuteCommon is the only superclass with setUp()
        TestHexKnightExecuteCommon.setUp(self)
        self.concat_input_file_fd = NamedTemporaryFile('wb', delete=True)

    def tearDown(self):
        # TestHexKnightExecuteCommon is the only superclass with tearDown()
        TestHexKnightExecuteCommon.tearDown(self)
        self.concat_input_file_fd.close()

    def get_end_of_memory(self):
        # start of heap seen in M0-macro.s
        start_of_heap = 0x4000
        # guess for size of heap
        minimum_heap_size = 1024*24
        # recommended amount for small binaries seen in stage0/makefile
        end_of_memory = 48*1024

        # pick the larger of the above two
        return max(start_of_heap+minimum_heap_size, end_of_memory)

    def get_tape1_file_path(self, input_file_fd):
        return self.concat_input_file_fd.name

    def generate_input_fd(self, primary_input_file_path):
        with open(KNIGHT_DEFS_FILE, 'rb') as kdf:
            self.concat_input_file_fd.write( kdf.read() )

        with open(primary_input_file_path, 'rb') as input_file_fd:
            self.concat_input_file_fd.write( input_file_fd.read() )
            self.concat_input_file_fd.seek(0)
        return self.concat_input_file_fd

    def generate_bytes_from_output(self):
        outputbin = BytesIO()
        with open(self.get_output_file_path(), 'r') as tape_file:
            write_binary_filefd_from_hex2_filefd(tape_file,
                                                 outputbin)
            outputbin.flush()
        return outputbin.getbuffer()

class TestSmallMemoryStage1M0Assemble(TestStage1M0Assemble):
    pass

def make_M0_test(testname, assemblerfile, SHA256_rom_file):
    def test_M0_assembler(self):
        self.execute_test_hex_load_published_sha256(
            assemblerfile, SHA256_rom_file
        )
    return test_M0_assembler

for testname, assemblerfile, SHA256_rom_file in (
        ('stage0monitor',
         'stage0/stage0_monitor.s',
         "roms/stage0_monitor"),
        ('stage1assembler0',
         'stage1/stage1_assembler-0.s',
         "roms/stage1_assembler-0"),
        ('stage1assembler1',
         'stage1/stage1_assembler-1.s',
         "roms/stage1_assembler-1"),
        ('cat',
         'stage1/CAT.s',
         "roms/CAT"),
):
    setattr( TestSmallMemoryStage1M0Assemble,
             "test_M0_assembler_%s" % testname,
             make_M0_test(testname, assemblerfile, SHA256_rom_file) )

# Make a 32 bit optimized version of the above test
# Don't do 16 bit and 64 bit variations
# As of 0.4.0 release:
#  - 16 bit variations hit illegal instruction or produces wrong result
#    depending on test run
#  - Some 64 bit variations run out of memory regardless of how much is added
TestSmallMemoryStage1M0Assemble32Optimize = \
    make_optimize_and_register_size_variations(
        TestSmallMemoryStage1M0Assemble)[0]

class TestSmallMemoryStage1M0Assemble_hex2(TestStage1M0Assemble):
    # skip unless the upstream patched version of stage1_assembler-2.s
    # is present, we're not going to bother patching the binary for
    # earlier versions like we did when testing our python hex2tobin
    @skipIf( sha256hexoffile(get_stage0_file('stage1/stage1_assembler-2.s'))
             not in DONT_MONKEY_PATCH,
             'stage1_assembler-2.s is not patched version'
    )
    def setUp(self, *args, **kargs):
        return super(TestSmallMemoryStage1M0Assemble_hex2, self).setUp(
            *args, **kargs)

    def test_M0_assemble_hex2(self):
        self.execute_test_hex_load_published_sha256(
            'stage1/stage1_assembler-2.s',
            'roms/stage1_assembler-2'
        )

# Make a 32 bit optimized version of the above test
# Don't do 16 bit and 64 bit variations
# As of 0.4.0 release:
#  - 16 bit variations hit illegal instruction or produces wrong result
#    depending on test run
#  - Some 64 bit variations run out of memory regardless of how much is added
TestSmallMemM0Assemblerhex2_32Optimize = \
    make_optimize_and_register_size_variations(
        TestSmallMemoryStage1M0Assemble_hex2)[0]

class TestBigMemoryStage1M0Assemble(TestStage1M0Assemble):
    def get_end_of_memory(self):
        # start of heap seen in M0-macro.s
        start_of_heap = 0x4000
        # guess for size of heap
        minimum_heap_size = 1024*24
        # recommended amount for big binaries seen in stage0/makefile
        end_of_memory = 256*1024

        # pick the larger of the above two
        return max(start_of_heap+minimum_heap_size, end_of_memory)

for testname, assemblerfile, SHA256_rom_file in (
    ('lisp',
     'stage2/lisp.s',
     "roms/lisp"),
    ('cc_x86',
     'stage2/cc_x86.s',
     "roms/cc_x86"),
    ('forth',
     'stage2/forth.s',
     "roms/forth"),
):
    setattr( TestBigMemoryStage1M0Assemble,
             "test_M0_assembler_%s" % testname,
             make_M0_test(testname, assemblerfile, SHA256_rom_file) )

# Make a 32 bit optimized version of the above test
# Don't do 16 bit and 64 bit variations
# As of 0.4.0 release:
#  - 16 bit variations hit illegal instruction or produces wrong result
#    depending on test run
#  - Some 64 bit variations run out of memory regardless of how much is added
TestBigMemoryStage1M0Assemble32Optimize = \
    make_optimize_and_register_size_variations(
        TestBigMemoryStage1M0Assemble)[0]
