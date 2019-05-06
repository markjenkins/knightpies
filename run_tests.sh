#!/bin/sh

TESTDIR=knighttests

if test "x$1" = 'x-v'; then \
    python3 -m unittest discover -v -t . -s $TESTDIR
else
    python3 -m unittest discover -t . -s $TESTDIR
fi
