#!/usr/bin/env python
"""Trace converter and plotter

Usage:
    trace.py listtags <in>
    trace.py convert <in> <out> [TAG ...]
    trace.py plot <in> [TAG ...]
"""

import file_io
from docopt import docopt
import sys

args = docopt(__doc__, version='trace.py 0.2')

file_in = sys.stdin if args['<in>'] == '-' else open(args['<in>'])

# read trace file in
df = file_io.read_trace(file_in)
if args['TAG']:
    tags = args['TAG']
    df = df.query('tag in tags')
else:
    tags = list(df.tag.drop_duplicates())

if args['listtags']:
    print(tags)
elif args['convert']:
    file_out = sys.stdout if args['<out>'] == '-' else open(args['<out>'], 'w')
    file_io.write_trace_table(df, tags, file_out)
elif args['plot']:
    import gui
    win, qapp = gui.plot(df, tags, title='Trace: {}'.format(args['<in>']))
    win.show()
    qapp.exec_()
