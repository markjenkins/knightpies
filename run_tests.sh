#!/bin/sh

if test "x$1" = 'x-v'; then \
    python3 -m unittest discover -v -s tests
else
    python3 -m unittest discover -s tests
fi
