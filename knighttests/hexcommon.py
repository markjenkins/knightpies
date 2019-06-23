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
from io import BytesIO
from hashlib import sha256

from stage0dir import get_stage0_test_sha256sum

def make_get_sha256sum_of_file_after_encode(encode_func):
    def func_get_sha256sum_of_file_after_encode(filename):
        with BytesIO() as outputmemfile:
            with open(filename) as hex0file:
                encode_func(hex0file, outputmemfile)
                hexdigest = sha256(outputmemfile.getbuffer()).hexdigest()
        return hexdigest
    return func_get_sha256sum_of_file_after_encode

class HexCommon(TestCase):
    # subclasses must define
    # encoding_rom_filename
    def setUp(self):
        self.encoding_rom_binary = BytesIO()
        with open( self.encoding_rom_filename ) as encoding_rom_file:
            self.rom_encode_func(encoding_rom_file, self.encoding_rom_binary)

    def tearDown(self):
        self.encoding_rom_binary.close()

class Hex256SumMatch:
    # subclasses must define
    # get_sha256_listed_file_bytes
    # sha256sumfilename
    # compute_sha256_digest()

    def test_matches_known_sha256(self):
        target_sha256sum_HEX = get_stage0_test_sha256sum(
            self.sha256sumfilename)

        self.assertEqual(
            self.compute_sha256_digest(),
            target_sha256sum_HEX )

class Encoding_rom_256_Common(Hex256SumMatch):
    def compute_sha256_digest(self):
        s = sha256( self.encoding_rom_binary.getbuffer() )
        return s.hexdigest()
