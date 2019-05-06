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

class OutsideOfWorldException(Exception):
    def __init__(self, exception_msg, outsidemsg):
        Exception.__init__(self, exception_msg)
        self.exception_msg = exception_msg
        self.outsidemsg = outsidemsg

def outside_of_world(vm, place, message):
    if len(vm[MEM]) <= place:
        raise OutsideOfWorldException(
            "Invalid state reached after: %d instructions\n"
            "%d: %s" % ( vm[PERF_COUNT], place, message),
            message
        )
