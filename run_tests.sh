#!/bin/sh

TESTDIR=knighttests

if test "x$1" = 'x-v'; then \
    python3 -m unittest discover -v -s $TESTDIR
else
    python3 -m unittest discover -s $TESTDIR
fi
