# A derivitive port of:
# https://github.com/oriansj/stage0/blob/master/vm_instructions.c
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

from sys import stderr

from constants import MEM, PERF_COUNT
from pythoncompat import print_func

def outside_of_world(vm, place, message):
    from knightdecode import halt_vm
    if len(vm[MEM]) <= place:
        print_func("Invalid state reached after: %d instructions" %
                   vm[PERF_COUNT],
                   file=stderr)
        print_func("%d: %s" % (place, message), file=stderr)
        vm = halt_vm(vm)
        # if TRACE: TODO
        #    pass # TODO
        exit(message)
