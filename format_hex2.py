#!/usr/bin/env python3

# format the hex2 output of M1.py --comment which has # to
# comment on the instruction and typically ; comments after
# in the .s knight files we want to format

from sys import stdin, argv

justify_content, justify_first_comment = (int(argv[1]), int(argv[2]))

for line in stdin:
    if line[0] in ':#;':
        print(line, end='')
    elif len(line.strip())==0:
        print()
    elif '#' in line and ';' in line:
        content, comment_section = line.split('#', maxsplit=1 )
        first_comment, second_comment = comment_section.split(';', maxsplit=1)
        print( "\t%s # %s ; %s" % (
            content.strip().ljust(justify_content),
            first_comment.strip().ljust(justify_first_comment),
            second_comment.strip(),
            ),
        )
    elif '#' in line:
        content, comment_section = line.split('#', maxsplit=1 )
        print( "\t%s # %s" % (
            content.strip().ljust(justify_content),
            first_comment.strip()
            )
        )
    else:
        print(line, end='')
