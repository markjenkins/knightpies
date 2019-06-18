#!/usr/bin/env python
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

from string import hexdigits

from pythoncompat import write_byte, open_ascii, COMPAT_FALSE, COMPAT_TRUE

STATE_MAIN, STATE_DECLARE, STATE_REF, STATE_COMMENT, STATE_EOF = range(5)
TOK_HEX, TOK_LABEL, TOK_REF = range(3)

TRANSITIONS = {
    STATE_MAIN: {
        ';': (STATE_COMMENT, None),
        '#': (STATE_COMMENT, None),
        ':': (STATE_DECLARE, None),
        '@': (STATE_REF, None),
        None: (STATE_MAIN, TOK_HEX)
        },
    STATE_DECLARE: {
        None: (STATE_MAIN, TOK_LABEL)
        },
    STATE_REF: {
        None: (STATE_MAIN, TOK_REF)
        },
    STATE_COMMENT: {
        '\n': (STATE_MAIN, None),
        '\r': (STATE_MAIN, None),
        None: (STATE_COMMENT, None),
        },
    }

def get_next_token_and_state(c, state):
    assert state != STATE_EOF
    if len(c)==0:
        return (None, None), STATE_EOF
    else:
        next_state, token_type = \
            TRANSITIONS[state].get( c, TRANSITIONS[state][None] )
        if token_type == None:
            token = (None, c)
        elif token_type == TOK_HEX:
            if c in hexdigits:
                token = (TOK_HEX, c)
            else:
                token = (None, c)
        else:
            token = (token_type, c)

        return (token, next_state)

def read_char_and_get_next_token_and_state(fileobj, state):
    assert state != STATE_EOF
    c = fileobj.read(1)
    return get_next_token_and_state(c, state)

def tokenize_file(fileobj):
    state = STATE_MAIN
    while state != STATE_EOF:
        next_tok, next_state = read_char_and_get_next_token_and_state(
            fileobj, state)
        if next_state!=STATE_EOF and next_tok[0] != None:
            yield next_tok
        state = next_state

def get_label_table(input_file):
    input_file.seek(0)
    ip = 0
    first_nyble = COMPAT_TRUE
    labels = {}
    for token_type, c in tokenize_file(input_file):
        if token_type == TOK_HEX:
            if first_nyble:
                first_nyble = COMPAT_FALSE
            else:
                first_nyble = COMPAT_TRUE
                ip+=1
        elif token_type == TOK_LABEL:
            labels[c] = ip
        elif token_type == TOK_REF:
            ip+=2
    return labels

def int_bytes_from_hex1_fd(input_file):
    label_table = get_label_table(input_file)
    input_file.seek(0) # start again for a second pass
    ip = 0
    first_nyble = COMPAT_TRUE
    accumulator = 0
    for token_type, c in tokenize_file(input_file):
        if token_type == TOK_HEX:
            accumulator += int(c, 16)
            if first_nyble:
                accumulator = accumulator << 4
                first_nyble = COMPAT_FALSE
            else:
                first_nyble = COMPAT_TRUE
                yield accumulator
                accumulator = 0
                ip+=1
        elif token_type == TOK_REF:
            ip+=2
            label_abs_address = label_table[c]
            label_rel_address = label_abs_address - ip
            yield (label_rel_address>>8) & 0xFF
            yield label_rel_address & 0xFF

def write_binary_filefd_from_hex1_filefd(input_file, output_file):
    for output_byte in int_bytes_from_hex1_fd(input_file):
        write_byte(output_file, output_byte)

def write_binary_file_from_hex1_file(input_filename, output_filename):
    input_file = open_ascii(input_filename)
    output_file = open(output_filename, 'wb') # binary output
    write_binary_filefd_from_hex1_filefd(input_file, output_file)
    output_file.close()
    input_file.close()

if __name__ == "__main__":
    from sys import argv
    write_binary_file_from_hex1_file(*argv[1:2+1])
