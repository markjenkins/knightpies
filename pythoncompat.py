# A compatibility library that's simpler than six and python-future
# with the aim to remain compatible with python 2.2
#
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

import sys
from array import array

from constants import \
    ARRAY_TYPE_UNSIGNED_INT_LONG, ARRAY_TYPE_UNSIGNED_LONG_LONG

if sys.version_info[0] >= 3:
    if isinstance(__builtins__, dict):
        print_func = __builtins__["print"]
    else:
        print_func = getattr(__builtins__, "print")

    gen_range = range
else:
    def print_func(*args, **kargs):
        sep = kargs.get('sep', " ")
        end = kargs.get('end', "\n")
        fd = kargs.get('file', sys.stdout)
        for i, arg in enumerate(args):
            if i != 0:
                fd.write(sep) 
            fd.write(arg)
        if end=='':
            fd.write(sep)
        else:
            fd.write(end)
        fd.flush()

    gen_range = xrange

def write_byte(fd, byte_write):
    if sys.version_info[0] >= 3:
        value_to_write = bytes( (byte_write,) )
    else:
        value_to_write = chr(byte_write)
    fd.write(value_to_write)

def try_to_make_8_byte_long_int_array():
    a = array(ARRAY_TYPE_UNSIGNED_INT_LONG)
    if a.itemsize==8: # this works on x86_64 python2
        return a
    else:
        return None

def init_array_itemsize_8():
    # ARRAY_TYPE_UNSIGNED_LONG_LONG available on python 3.3 if the c compiler
    # supports the long long or type or __int64 on Windows
    if sys.version_info[0:1+1] >= (3, 3):
        try:
            a = array(ARRAY_TYPE_UNSIGNED_LONG_LONG)
        # Exception possible on some python >= 3.3 platforms without
        # long long or __int64 on Windows
        except ValueError:
            return try_to_make_8_byte_long_int_array()

        if a.itemsize == 8:
            return a
        elif a.itemsize > 8:
            # there are probably few platforms where
            # ARRAY_TYPE_UNSIGNED_INT_LONG will be 8 bytes when
            # ARRAY_TYPE_UNSIGNED_LONG_LONG isn't but might as well try
            # (on the 32bit x86 python2 and python3 implementations I've
            # tested int long is 4 bytes / 32 bits)
            return try_to_make_8_byte_long_int_array
        else: # ARRAY_TYPE_UNSIGNED_LONG_LONG 'Q' will not be <8
            assert False
    else:
        # this works on x86_64 python2
        return try_to_make_8_byte_long_int_array()

if __name__ == "__main__":
    print_func("hello world!")
