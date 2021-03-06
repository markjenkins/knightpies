#!/usr/bin/env python3
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

from unittest import main
from os.path import dirname, join as path_join
import sys

import knighttests.testflags

if __name__ == "__main__":
    THIS_DIR = dirname(__file__)
    sys_argv_after_prog = sys.argv[1:]
    if '--skip-parallel' in sys_argv_after_prog:
        knighttests.testflags.PARALLEL_SKIP = True
        sys_argv_after_prog = [ a for a in sys_argv_after_prog
                                if a != '--skip-parallel' ]
    if '--skip-optimize' in sys_argv_after_prog:
        knighttests.testflags.OPTIMIZE_SKIP = True
        sys_argv_after_prog = [ a for a in sys_argv_after_prog
                                if a != '--skip-optimize' ]
    if '--skip-diff-reg-size' in sys_argv_after_prog:
        knighttests.testflags.DIFF_REG_SIZE_SKIP = True
        sys_argv_after_prog = [ a for a in sys_argv_after_prog
                                if a != '--skip-diff-reg-size' ]
    arguments = [sys.argv[0], 'discover',
                 '-t', THIS_DIR,
                 '-s', path_join(THIS_DIR, 'knighttests'),
    ]
    arguments.extend(sys_argv_after_prog)
    main(module=None,argv=arguments)
