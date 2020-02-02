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

from .stage0 import STAGE_0_HEX2_ASSEMBLER_FILEPATH

from .hexcommon import (
    Hex256SumMatch, HexCommon, Encoding_rom_256_Common,
    )

from stage0dir import get_stage0_file
from hex1tobin import write_binary_filefd_from_hex1_filefd
from M1tobin import M1_files_objs_to_bin
from pythoncompat import open_ascii

from .test_hex2tobin import (
    get_sha256sum_of_file_after_hex2_encode,
    )
from .util import sha256hexoffile

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

class M1Common(HexCommon):
    encoding_rom_filename = STAGE_0_HEX2_ASSEMBLER_FILEPATH
    rom_encode_func = staticmethod(write_binary_filefd_from_hex1_filefd)

class Test_hex_assembler2_256Sum(M1Common, Encoding_rom_256_Common):
    sha256sumfilename = 'roms/stage1_assembler-2'

class Test_M0_256Sum(M1Common, Hex256SumMatch):
    sha256sumfilename = 'roms/M0'

    def compute_sha256_digest(self):
        return get_sha256sum_of_file_after_hex2_encode(
            get_stage0_file('stage1/M0-macro.hex2'))

class M1AssembleToBin_Common_256Sum(object):
    def compute_sha256_digest(self):
        input_filelist = ['High_level_prototypes/defs'] + self.input_filelist
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
        input_filelist = ['High_level_prototypes/defs'] + self.input_filelist
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
