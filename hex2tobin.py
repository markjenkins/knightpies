#!/usr/bin/env python
#
# Copyright (C) 2020 Mark Jenkins <mark@markjenkins.ca>
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
from sys import version_info

from pythoncompat import write_byte, open_ascii, COMPAT_FALSE, COMPAT_TRUE

(STATE_MAIN, STATE_DECLARE, STATE_REL, STATE_ABS_POINT, STATE_ABS_ADDR,
 STATE_COMMENT, STATE_EOF) = range(7)
TOK_HEX, TOK_LABEL, TOK_REL, TOK_ABS_POINT, TOK_ABS_ADDR = range(5)

TRANSITIONS = {
    STATE_MAIN: {
        ';': (STATE_COMMENT, None),
        '#': (STATE_COMMENT, None),
        ':': (STATE_DECLARE, None),
        '@': (STATE_REL, None),
        '$': (STATE_ABS_POINT, None),
        '&': (STATE_ABS_ADDR, None),
        None: (STATE_MAIN, TOK_HEX)
        },

    STATE_COMMENT: {
        '\n': (STATE_MAIN, None),
        None: (STATE_COMMENT, None),
        },
}

BUFFER_TERMINATING_CHARS = {
    ' ',
    '\t',
    '\n',
    }

BUFFER_BUILDING_STATE_TRANSITIONS = {
    STATE_DECLARE: (STATE_MAIN, TOK_LABEL),
    STATE_REL: (STATE_MAIN, TOK_REL),
    STATE_ABS_POINT: (STATE_MAIN, TOK_ABS_POINT),
    STATE_ABS_ADDR: (STATE_MAIN, TOK_ABS_ADDR)
}

UPPER_HEX_TO_DECIMAL = ord('A') - int('A', 16)
assert UPPER_HEX_TO_DECIMAL == 55

def get_next_token_and_state(c, state, inputbuffer):
    assert state != STATE_EOF
    if len(c)==0:
        return ( (None, None), STATE_EOF, None )
    else:
        # return early if we're in a buffer building state
        if state in BUFFER_BUILDING_STATE_TRANSITIONS:
            if c in BUFFER_TERMINATING_CHARS:
                next_state, token_type = \
                    BUFFER_BUILDING_STATE_TRANSITIONS[state]
                token = (token_type, inputbuffer)
                # '' means reset input buffer to blank, as the buffer is
                # in the token
                return (token, next_state, '')
            else:
                token = (None, c)
                return (token, state, inputbuffer+c)

        # else, do the fancier dance for non buffer building states
        next_state, token_type = \
            TRANSITIONS[state].get( c, TRANSITIONS[state][None] )
        if token_type == None:
            token = (None, c)
        elif token_type == TOK_HEX:
            if c in hexdigits:
                token = (TOK_HEX, c)
            # we replicate the funky behavior of stage1_assembler-1 and -2
            # which treates backtick "`" (ascii decimal 96) like '9'
            # because upper and lower case A-F/a-f are handled the same
            # by way of a upper to lower case conversion by
            # masking out the 6th bit 2**5==32, comparing against
            # 'F' (ascii decimal 70), and subtracting 55
            # to convert from ascii A-F/a-f to decimal
            elif ( ord(c)>ord('F') and
                   ord(c) & int('11011111', 2) <= ord('F') ):
                # the only character in ascii that meets these conditions
                assert(c) == '`'
                lower_to_upper_conversion = ord(c) & int('11011111', 2)
                hex_to_decimal_conversion = (
                    lower_to_upper_conversion - UPPER_HEX_TO_DECIMAL) & 0xF
                decimal_to_hexchar = hex(hex_to_decimal_conversion)[2:]
                assert len(decimal_to_hexchar)==1 # the 0xF mask assures this
                token = (
                    TOK_HEX,
                    decimal_to_hexchar)
                assert token[1] == '9' # what "`" will encode to
            else:
                token = (None, c)
        else:
            token = (token_type, c)

        return (token, next_state, inputbuffer)

def read_char_and_get_next_token_and_state(fileobj, state, inputbuffer):
    assert state != STATE_EOF
    c = fileobj.read(1)
    return get_next_token_and_state(c, state, inputbuffer)

if version_info[0:2] > (2,2): # for python 2.2 and later with yield keyword
    def tokenize_file(fileobj):
        state = STATE_MAIN
        inputbuffer = ''
        while state != STATE_EOF:
            next_tok, next_state, inputbuffer = \
                read_char_and_get_next_token_and_state(
                    fileobj, state, inputbuffer)
            if next_state!=STATE_EOF and next_tok[0] != None:
                yield next_tok
            state = next_state
else: # for python 2.2, but no concern for earlier versions
    def tokenize_file(fileobj):
        # just build a list and return it all at the end
        # for better performance / avoiding that much memory use,
        # we would need to do something like
        # define an interable class and return an instance of that instance
        return_list = []
        state = STATE_MAIN
        inputbuffer = ''
        while state != STATE_EOF:
            next_tok, next_state, inputbuffer = \
                read_char_and_get_next_token_and_state(
                    fileobj, state, inputbuffer)
            if next_state!=STATE_EOF and next_tok[0] != None:
                return_list.append(next_tok)
            state = next_state
        return return_list

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
        elif token_type == TOK_REL or token_type==TOK_ABS_POINT:
            ip+=2
        elif token_type == TOK_ABS_ADDR:
            ip+=4
    return labels

def int_bytes_from_hex2_fd(input_file):
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
        elif token_type == TOK_REL:
            ip+=2
            label_abs_address = label_table[c]
            label_rel_address = label_abs_address - ip
            yield (label_rel_address>>8) & 0xFF
            yield label_rel_address & 0xFF
        elif token_type == TOK_ABS_POINT:
            ip+=2
            label_abs_address = label_table[c]
            yield (label_abs_address>>8) & 0xFF
            yield label_abs_address & 0xFF
        elif token_type == TOK_ABS_ADDR:
            ip+=4
            label_abs_address = label_table[c]
            # output most significant byte down to least significant
            for i in range(3,0-1,-1):
                yield label_abs_address>>(8*i) & 0xFF

def write_binary_filefd_from_hex2_filefd(input_file, output_file):
    for output_byte in int_bytes_from_hex2_fd(input_file):
        write_byte(output_file, output_byte)

def write_binary_file_from_hex2_file(input_filename, output_filename):
    input_file = open_ascii(input_filename)
    output_file = open(output_filename, 'wb') # binary output
    write_binary_filefd_from_hex2_filefd(input_file, output_file)
    output_file.close()
    input_file.close()

if __name__ == "__main__":
    from sys import argv
    write_binary_file_from_hex2_file(*argv[1:2+1])
