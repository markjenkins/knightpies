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

if __name__ == "__main__":
    print_func("hello world!")
