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

from stage0dir import get_stage0_file
from unittest import skipIf
from os.path import exists
from hashlib import sha256

from .hexcommon import (
    TestHexKnightExecuteCommon,
)

from .test_hex0tobin import (
    TestHex0KnightExecuteCommon, 
    get_sha256sum_of_file_after_hex0_encode,
    CommonStage1HexEncode,
    )

LINUX_BOOTSTRAP_HEX0_FILES = [
    ('xeh_orig', 'Linux Bootstrap/xeh.hex0'),
    ('xeh', 'Linux Bootstrap/Legacy_pieces/xeh.hex0'),
    ('exec_enable', 'Linux Bootstrap/Legacy_pieces/exec_enable.hex0'),
    ('hex0_x86', 'Linux Bootstrap/x86/hex0_x86.hex0'),
    ('hex1_x86', 'Linux Bootstrap/x86/hex1_x86.hex0'),
    ('catm_x86', 'Linux Bootstrap/x86/catm_x86.hex0'),
    ('hex0_amd64', 'Linux Bootstrap/AMD64/hex0_AMD64.hex0'),
    ('hex1_amd64', 'Linux Bootstrap/AMD64/hex1_AMD64.hex0'),
    ('catm_amd64', 'Linux Bootstrap/AMD64/catm_AMD64.hex0'),
    ]

TARGET_SHA256SUMS = {
    filename: get_sha256sum_of_file_after_hex0_encode(
        get_stage0_file(filename) )
    for shortfilename, filename in LINUX_BOOTSTRAP_HEX0_FILES
    if exists( get_stage0_file(filename) )
}

# these versions of 'Linux Bootstrap/Legacy_pieces/read.hex0' have an
# appropriate patch
legacy_pieces_read_newline_fixes = {
    '7eb77fdf6db920ed5188baf1d3af8ef08ba2ff802048dce2ee9995af39acbc9c'
    }

# and so if that file xists and matches a sha256sum above, we include
# it as a target for the test suite
LINUX_BOOTSTRAP_LEGACY_PIECES_READ = 'Linux Bootstrap/Legacy_pieces/read.hex0'
LINUX_BOOTSTRAP_LEGACY_PIECES_READ_FULL = \
    get_stage0_file(LINUX_BOOTSTRAP_LEGACY_PIECES_READ)
if exists(LINUX_BOOTSTRAP_LEGACY_PIECES_READ_FULL):
    with open(LINUX_BOOTSTRAP_LEGACY_PIECES_READ_FULL, 'rb') as f:
        if sha256(f.read()).hexdigest() in legacy_pieces_read_newline_fixes:
            TARGET_SHA256SUMS[LINUX_BOOTSTRAP_LEGACY_PIECES_READ] = \
                get_sha256sum_of_file_after_hex0_encode(
                    LINUX_BOOTSTRAP_LEGACY_PIECES_READ_FULL)
# and then we add that file to the list no matter what, the idea being
# the test will be added, but the @skipIf will skip it if it is not in
# TARGET_SHA256SUMS
LINUX_BOOTSTRAP_HEX0_FILES.append(
    ('read', LINUX_BOOTSTRAP_LEGACY_PIECES_READ)
)

def make_linux_bootstrap_test_case(filename):
    @skipIf( filename not in TARGET_SHA256SUMS,
             '%s not available for testing' % filename )
    def test_encode_linux_bootstrap_file(self):
        self.execute_test_hex0_load_against_computed_SHA256SUM(
            filename)
    return test_encode_linux_bootstrap_file

class TestHex0KnightSubmoduleExecuteCommon(TestHex0KnightExecuteCommon):
    def execute_test_hex0_load_against_computed_SHA256SUM(self, filename):
        self.execute_test_hex0_load_against_computed_SHA256SUM_dict(
            filename, TARGET_SHA256SUMS)

class LinuxBootStrapTests():
    pass

for shortfilename, filename in LINUX_BOOTSTRAP_HEX0_FILES:
    setattr(LinuxBootStrapTests,
            "test_encode_linux_bootstrap_%s" % shortfilename,
            make_linux_bootstrap_test_case(filename) )

class TestStage0Monitorexecute(
        TestHex0KnightSubmoduleExecuteCommon,
        LinuxBootStrapTests):
    pass

class TestStage1Hex0Encode(
        CommonStage1HexEncode, TestHex0KnightSubmoduleExecuteCommon,
        LinuxBootStrapTests):
    pass

