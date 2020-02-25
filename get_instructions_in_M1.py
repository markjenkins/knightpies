#!/usr/bin/env python

# Read a .s M1 file, identify macros used and print both the sym 

# You can then pipe the output to this awk script to get sed invocations
# to undo the macros in the original .s file
# awk "{print \"sed -i -e s/\" \$1 \"/\" \$2 \"/ filetochange.hex2\"}"

from sys import argv

from pythoncompat import open_ascii, COMPAT_TRUE
from M1 import \
    get_symbols_from_M1_file_objs, \
    get_symbols_used, \
    TOK_EXPR

arguments = argv[1:]

M1_file_objs = [open_ascii(filename) for filename in arguments]
symbols = get_symbols_from_M1_file_objs(
    M1_file_objs, rewind_after=COMPAT_TRUE)
symbols_used = get_symbols_used(M1_file_objs, symbols)

symlist = \
    sorted( ( (len(symbols[s][TOK_EXPR]),
               symbols[s][TOK_EXPR],
               s)
              for s in symbols_used ), reverse=True)
print('\n'.join( ("%s %s" % (symbolval, symbol)
                  for symlen, symbolval, symbol in symlist
                  if len(symbolval)>1 ) ) )
