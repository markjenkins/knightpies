#!/usr/bin/env python3

from sys import stdin, argv

justify_content, justify_first_comment = (int(argv[1]), int(argv[2]))

for line in stdin:
    if line[0] == '\t':
        linesplit = line[1:].split('#', maxsplit=1)
        if len(linesplit)==1 or linesplit[1].strip()=='':
            print(line, end='')
        else:
            content, comment = linesplit
            comment = comment.strip() # remove newline
            print( '\t', end='')
            print( content.strip().ljust(justify_content), end='')
            print( ' # ', end='')
            commentsplit = comment.split(' ;', maxsplit=1)
            if len(commentsplit)==1 or commentsplit[1].strip()=='':
                print(commentsplit[0].strip()) # include newline
            else:
                comment1, comment2 = commentsplit
                print(comment1.strip().ljust(justify_first_comment), end='')
                print(' ; ', end='')
                print(comment2.strip()) # include newline
    else:
        print(line, end='')
