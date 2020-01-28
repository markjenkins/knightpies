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

from unittest import TestCase
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

def get_sha256sum_of_file_after_files_are_M1_assembled_and_hex2_linked(
        *filenames):
    with BytesIO() as outputmemfile:
        input_fileobjs = [ open_ascii(filename)
                           for filename in filenames ]
        M1_files_objs_to_bin(input_fileobjs, outputmemfile )
        for f in input_fileobjs:
            f.close()
        hexdigest = sha256(outputmemfile.getbuffer()).hexdigest()
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
