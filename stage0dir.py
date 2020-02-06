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

from os.path import dirname, join

def get_stage0_dir():
    return join(dirname(__file__), 'stage0')

def get_stage0_file(stage0_file_path):
    return join(get_stage0_dir(), stage0_file_path)

def reverse_two_element_tuple(t):
    return (t[1], t[0])

def get_all_stage0_test_sha256sums():
    sha256fd = open(get_stage0_file('test/SHA256SUMS'))
    return_value = dict(
        reverse_two_element_tuple(line.split())
        for line in sha256fd
        )
    sha256fd.close()
    return return_value

def get_stage0_test_sha256sum(testfile):
    return get_all_stage0_test_sha256sums()[testfile]

KNIGHT_DEFS_FILE_RELATIVE = 'High_level_prototypes/defs'
KNIGHT_DEFS_FILE = get_stage0_file(KNIGHT_DEFS_FILE_RELATIVE)
