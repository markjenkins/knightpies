#!/usr/bin/env python
#
# A derivitive port of:
# https://github.com/oriansj/mescc-tools/M1-macro.c
#
# Copyright (C) 2016 Jeremiah Orians
# Copyright (C) 2017 Jan Nieuwenhuizen <janneke@gnu.org>
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

from __future__ import generators # for yield keyword in python 2.2

from pythoncompat import \
    open_ascii, print_func, COMPAT_TRUE, COMPAT_FALSE, int_as_hex

TOK_TYPE_MACRO, TOK_TYPE_ATOM, TOK_TYPE_STR, TOK_TYPE_NEWLINE = range(4)
TOK_TYPE, TOK_EXPR, TOK_FILENAME, TOK_LINENUM = range(4)
MACRO_NAME, MACRO_VALUE = 0, 1

class MultipleDefinitionsException(Exception):
    pass

def read_atom(first_char, f):
    buf = first_char
    while COMPAT_TRUE:
        c = f.read(1)
        if c in ('', "\n", "\t", " "):
            break
        else:
            buf += c
    return buf, c

def read_until_newline_or_EOF(f):
    while COMPAT_TRUE:
        c = f.read(1)
        if c == '' or c=='\n' or c=='\r':
            return c

def tokenize_file(f):
    line_num = 1
    string_char, string_buf = None, None
    while COMPAT_TRUE:
        c = f.read(1)
        if c=='':
            if string_char != None:
                raise Exception("unmatched %s quote in %s line %s",
                                string_char, f.name, line_num)
            break
        # look for being in string stage first, as these are not
        # interupted by newline or comments
        elif (string_char != None):
            if string_char == c:
                yield (TOK_TYPE_STR, string_buf, f.name, line_num)
                string_char, string_buf = None, None
            else:
                string_buf += c
        elif c == '#' or c == ';':
            c = read_until_newline_or_EOF(f)
            if c!= '':
                yield (TOK_TYPE_NEWLINE, '\n', f.name, line_num)
                line_num+=1
            else:
                break
        elif (string_char == None) and (c == '"' or c == "'"):
            string_char = c
            string_buf  = ''
        elif c == '\n':
            yield (TOK_TYPE_NEWLINE, '\n', f.name, line_num)
            line_num+=1
        elif c == ' ' or c == '\t':
            pass
        else:
            atom, trailing_char = read_atom(c, f)
            yield (TOK_TYPE_ATOM, atom, f.name, line_num)
            if trailing_char == '':
                break
            elif trailing_char == '\n':
                yield (TOK_TYPE_NEWLINE, '\n', f.name, line_num)
                line_num+=1
                
    yield (TOK_TYPE_NEWLINE, '\n', f.name, line_num)

def get_symbols_used(file_objs, symbols):
    symbols_used = {}
    for f in file_objs:
        for tok_type, tok_expr, tok_filename, tok_linenum in \
            upgrade_token_stream_to_include_macro(tokenize_file(f)):
            if tok_type == TOK_TYPE_ATOM and tok_expr in symbols:
                symbols_used[tok_expr] = None
    return list(symbols_used.keys())

def get_macros_defined_and_add_to_sym_table(f, symbols=None):
    # start a new dictionary if one wasn't provided, putting this in the
    # function definition would cause there to be one dictionary at build time
    if symbols == None:
        symbols = {}

    for tok in upgrade_token_stream_to_include_macro(tokenize_file(f)):
        if tok[TOK_TYPE] == TOK_TYPE_MACRO:
            tok_type, tok_expr, tok_filename, tok_linenum = tok
            macro_name = tok_expr[MACRO_NAME][TOK_EXPR]
            if macro_name in symbols:
                raise MultipleDefinitionsException(
                    "DEFINE %s on line %s of %s is a duplicate definition"
                    % (macro_name, tok_linenum, tok_filename) )
            symbols[macro_name] = tok_expr[MACRO_VALUE]
    return symbols

def upgrade_token_stream_to_include_macro(input_tokens):
    input_tokens_iter = iter(input_tokens)
    while COMPAT_TRUE:
        try:
            tok = next(input_tokens_iter)
        except StopIteration:
            break

        tok_type, tok_expr, tok_filename, tok_linenum = tok
        # if we have a DEFINE atom we're going to yield a TOK_TYPE_MACRO
        # based on the next two tokens
        if tok_type == TOK_TYPE_ATOM and tok_expr == "DEFINE":
            # look ahead to token after DEFINE
            try:
                macro_name_tok = next(input_tokens_iter)
            except StopIteration:
                raise Exception(
                    "%s ended with uncompleted DEFINE" % tok_filename
                )

            # enforce next token after DEFINE atom must be an atom,
            # not newline or string
            if macro_name_tok[TOK_TYPE] == TOK_TYPE_STR:
                raise Exception(
                    "Using a string for macro name %s not supported "
                    "line %s from %s" % (
                        tok_expr, tok_linenum, tok_filename) )
            elif macro_name_tok[TOK_TYPE] == TOK_TYPE_NEWLINE:
                raise Exception(
                    "You can not have a newline in a DEFINE "
                    "line %s from %s" % (
                        tok_expr, tok_linenum, tok_filename) )
            assert macro_name_tok[TOK_TYPE] == TOK_TYPE_ATOM

            # look ahead to second token after DEFINE
            try:
                macro_value_tok = next(input_tokens_iter)
            except StopIteration:
                raise Exception(
                    "%s ended with uncompleted DEFINE" % tok_filename
                )

            # enforce second token after DEFINE atom must be atom or string
            if macro_value_tok[TOK_TYPE] == TOK_TYPE_NEWLINE:
                raise Exception(
                    "You can not have a newline in a DEFINE "
                    "line %s from %s" % (
                        tok_expr, tok_linenum, tok_filename) )

            # make a macro type token which has a two element tuple
            # of name token and value token as the TOK_EXPR component
            yield (
                TOK_TYPE_MACRO,
                (macro_name_tok, macro_value_tok),
                tok_filename, tok_linenum
            )
        # else any atom token that's not DEFINE and two tokens after it
        # or any str or newline token, we just pass it through
        else:
            yield tok

def output_string_as_hex(output_file, string_msg):
    # remove leading and trailing quote chars
    for c in string_msg:
        output_file.write("%.2x" % ord(c))
    output_file.write('00')

def output_regular_atom(output_file, atomstr):
    if atomstr[0:2] == '0x': # atom's prefixed with 0x are hex
        try:
            hexatom_int = int(atomstr[2:], 16)
        except ValueError:
            raise Exception("%s can't be parsed to hex" % atomstr)
        output_file.write( int_as_hex(hexatom_int, 2, big_endian=COMPAT_TRUE) )
    elif atomstr[0] in "!@$~%&:^":
        if atomstr[0] != ':':
            output_file.write(' ')
        output_file.write(atomstr)
    else:
        # other regular atoms are treated as decimal values
        try:
            a = int(atomstr)
        except ValueError:
            raise Exception("%s can't be parsed to decimal" % atomstr)
        output_file.write(
            int_as_hex(a, 2, big_endian=COMPAT_TRUE) )
        
def output_file_from_tokens_with_macros_sub_and_string_sub(
    input_tokens, output_file, symbols):

    for tok_type, tok_expr, tok_filename, tok_linenum in input_tokens:
        if tok_type == TOK_TYPE_ATOM:
            if tok_expr in symbols: # exact match only
                macro_value_token = symbols[tok_expr]
                if (macro_value_token[TOK_TYPE] == TOK_TYPE_ATOM or
                    macro_value_token[TOK_TYPE] == TOK_TYPE_STR ):
                    output_file.write( macro_value_token[TOK_EXPR] )
                else:
                    assert COMPAT_FALSE
            else:
                output_regular_atom(output_file, tok_expr)
        elif tok_type == TOK_TYPE_NEWLINE:
            output_file.write('\n')
        elif tok_type == TOK_TYPE_STR:
            output_string_as_hex(
                output_file, tok_expr
                )
        else:
            assert tok_type == TOK_TYPE_MACRO

def get_symbols_from_M1_file_objs(file_objs, rewind_after=COMPAT_TRUE):
    symbols = {}
    # first pass get the symbols
    for f in file_objs:
        get_macros_defined_and_add_to_sym_table(f, symbols)
        if rewind_after:
            f.seek(0) # return to start of file for next pass
    return symbols

def M1_file_objs_to_hex2_file(M1_file_objs, hex2_file_obj, symbols=None):
    if symbols == None:
        symbols = get_symbols_from_M1_file_objs(
            M1_file_objs, rewind_after=COMPAT_TRUE)

    for f in M1_file_objs:
        output_file_from_tokens_with_macros_sub_and_string_sub(
            upgrade_token_stream_to_include_macro(tokenize_file(f)),
            hex2_file_obj, symbols)

def main():
    from sys import argv, stdout
    dump_defs_used = COMPAT_FALSE
    output_filename = None # default case will mean stdout
    arguments = []
    arg_iter = iter(argv[1:])
    while COMPAT_TRUE:
        try:
            arg = next(arg_iter)
        except StopIteration:
            break # break while COMPAT_TRUE
        if arg == '--dump-defs-used':
            dump_defs_used = COMPAT_TRUE
        elif arg == '-o' or arg == '--output':
            try:
                output_filename = next(arg_iter)
            except StopIteration:
                raise Exception('--output (-o) followed by end of arguments')
        else:
            arguments.append(arg)

    M1_file_objs = [open_ascii(filename) for filename in arguments]
    symbols = get_symbols_from_M1_file_objs(
        M1_file_objs, rewind_after=COMPAT_TRUE)

    if dump_defs_used:
        # second pass figure out which symbols are used
        symbols_used = get_symbols_used(M1_file_objs, symbols)
        symbols_used.sort()
        for symbol in symbols_used:
            print_func(symbol)
    # this will be the default case, outputting a processed version of the file
    else:
        if output_filename == None:
            output_file_obj = stdout
        else:
            output_file_obj = open(output_filename, 'w')

        M1_file_objs_to_hex2_file(
            M1_file_objs, output_file_obj, symbols=symbols)

    for f in M1_file_objs:
        f.close()

    if output_filename != None: # not stdout, but an open file
        output_file_obj.close()

if __name__ == '__main__':
    main()
