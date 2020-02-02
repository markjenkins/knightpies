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

from tempfile import NamedTemporaryFile
from hashlib import sha256
from unittest import skipIf
from .testflags import OPTIMIZE_SKIP, DIFF_REG_SIZE_SKIP

def get_closed_named_temp_file():
    return_file = NamedTemporaryFile(delete=False)
    return_file.close()
    return return_file.name

def sha256hexoffile(filename):
    with open(filename, 'rb') as f:
        checksum = sha256(f.read())
    return checksum.hexdigest()

def make_optimize_and_register_size_variations(class_to_sub):
    class TestVariation32Optimize(class_to_sub):
        optimize = True
        @skipIf(OPTIMIZE_SKIP, 'requested')
        def setUp(self, *args, **kargs):
            return super(TestVariation32Optimize, self).setUp(
                *args, **kargs)

    class TestVariation64(class_to_sub):
        registersize = 64
        @skipIf(DIFF_REG_SIZE_SKIP, 'requested')
        def setUp(self, *args, **kargs):
            return super(TestVariation64, self).setUp(*args, **kargs)

    class TestVariation64Optimize(TestVariation64):
        optimize = True
        @skipIf(OPTIMIZE_SKIP, 'requested')
        def setUp(self, *args, **kargs):
            return super(TestVariation64Optimize, self).setUp(
                *args, **kargs)

    class TestVariation16(class_to_sub):
        registersize = 16
        @skipIf(DIFF_REG_SIZE_SKIP, 'requested')
        def setUp(self, *args, **kargs):
            return super(TestVariation16, self).setUp(*args, **kargs)

    class TestVariation16Optimize(TestVariation16):
        optimize = True
        @skipIf(OPTIMIZE_SKIP, 'requested')
        def setUp(self, *args, **kargs):
            return super(TestVariation16Optimize, self).setUp(
                *args, **kargs)

    return (
        TestVariation32Optimize,
        TestVariation64,
        TestVariation64Optimize,
        TestVariation16,
        TestVariation16Optimize,
        )
