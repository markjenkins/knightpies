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

from .hexcommon import (
    TestHexKnightExecuteCommon,
)

from .test_hex0tobin import (
    TestHex0KnightExecuteCommon, 
    get_sha256sum_of_file_after_hex0_encode,
    CommonStage1HexEncode,
    )

TARGET_SHA256SUMS = {
    filename: get_sha256sum_of_file_after_hex0_encode(
        get_stage0_file(filename) )
    for filename in (
        'Linux Bootstrap/xeh.hex0',
        'Linux Bootstrap/Legacy_pieces/xeh.hex0',
    ) # end tuple fed to for filename in
    if exists( get_stage0_file(filename) )
}

class TestHex0KnightSubmoduleExecuteCommon(TestHex0KnightExecuteCommon):
    def execute_test_hex0_load_against_computed_SHA256SUM(self, filename):
        self.execute_test_hex0_load_against_computed_SHA256SUM_dict(
            filename, TARGET_SHA256SUMS)

class TestStage0Monitorexecute(TestHex0KnightSubmoduleExecuteCommon):
    @skipIf( 'Linux Bootstrap/xeh.hex0' not in TARGET_SHA256SUMS,
             'Linux Bootstrap/xeh.hex0 not available for testing'
    )
    def test_encode_linux_bootstrap_xeh_s(self):
        self.execute_test_hex0_load_against_computed_SHA256SUM(
            'Linux Bootstrap/xeh.hex0')

    @skipIf( 'Linux Bootstrap/Legacy_pieces/xeh.hex0' not in TARGET_SHA256SUMS,
             'Linux Bootstrap/Legacy_pieces/xeh.hex0 not available for testing'
    )
    def test_encode_linux_bootstrap_legacy_xeh_s(self):
        self.execute_test_hex0_load_against_computed_SHA256SUM(
            'Linux Bootstrap/Legacy_pieces/xeh.hex0')

class TestStage1Hex0Encode(
        CommonStage1HexEncode, TestHex0KnightSubmoduleExecuteCommon):
    @skipIf( 'Linux Bootstrap/xeh.hex0' not in TARGET_SHA256SUMS,
             'Linux Bootstrap/xeh.hex0 not available for testing'
    )
    def test_encode_linux_bootstrap_xeh_s(self):
        self.execute_test_hex0_load_against_computed_SHA256SUM(
            'Linux Bootstrap/xeh.hex0')    

    @skipIf( 'Linux Bootstrap/Legacy_pieces/xeh.hex0' not in TARGET_SHA256SUMS,
             'Linux Bootstrap/Legacy_pieces/xeh.hex0 not available for testing'
    )
    def test_encode_linux_bootstrap_legacy_xeh_s(self):
        self.execute_test_hex0_load_against_computed_SHA256SUM(
            'Linux Bootstrap/Legacy_pieces/xeh.hex0')
