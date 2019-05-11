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

if __name__ == "__main__":
    THIS_DIR = dirname(__file__)
    arguments = [sys.argv[0], 'discover',
                 '-t', THIS_DIR,
                 '-s', path_join(THIS_DIR, 'knighttests'),
    ]
    arguments.extend(sys.argv[1:])
    main(module=None,argv=arguments+sys.argv[1:])
