#!/usr/bin/env python
"""Trace converter
  Convert an interleaved time series from stdin into a table at stdout

  Usage:
    trace.py [--block NROWS] [--for FUNC] [TAG ...]
    trace.py [--block NROWS] [--while FUNC] [TAG ...]
    trace.py --listtags
    trace.py --help
    trace.py --version

  Options:
    --help, -h          Show this screen.
    --listtags, -l      List tags as they appear
    --block, -b NROWS   Number of rows in a block. 0 implies all rows
                        in a single block. [default: 0]
    --for, -f FUNC      A Python expression in 't' that evaluates to
                        True/False. Only True entries are displayed.
    --while, -w FUNC    Similar to -f except that program will stop
                        on the first False entry after a True entry.
                        Faster than -f at displaying a time interval.
    TAG ...             Output only these tags in the given order. If
                        not specified, output all tags in order of
                        appearance. TAG can be a glob pattern.

  Example:
    Run simulation and pipe its output to trace with tags tag1 tag2
      ./out | trace.py tag1 tag2

    Convert file in.tsv to out.tsv
      trace.py tag1 tag2 < in.tsv > out.tsv

    Convert only times that are multiples of 50
      trace.py -f 't % 50 == 0' tag1 tag2 < in.tsv

    Convert only from time 100 to 200
      trace.py -w '100 <= t <= 200' tag1 tag2 < in.tsv

    Input and output are in tab-separated-value format. Input should
    be of the form: <time> <tag> <value>
    where <time> increases monotonically.

"""
from __future__ import print_function
import docopt
import sys
import re
from fnmatch import fnmatch
import string
import itertools as it

args = docopt.docopt(__doc__, version='trace.py 0.1')
tags = args['TAG']
block_size = int(args['--block'])
no_tags = tags == []

# Parse each line for pattern
pat = re.compile(r'^(\s*\d+)\t(.*?)\t(.*)')
def get_val(iter_in):
    for line in iter_in:
        match = pat.match(line)
        if match:
            if no_tags or any(fnmatch(match.group(2), tag) for tag in tags):
                yield match.groups()
        else:
            print(line, end='', file=sys.stderr)

if args['--listtags']:
    seen_tags = []
    for (_, tag, _) in get_val(sys.stdin):
        if tag not in seen_tags:
            print('Tag found: ' + tag)
            seen_tags.append(tag)
    exit(0)

def filtf(expr):
    fexp = compile(expr, 'trace.py', 'eval')
    def f(val):
        t = int(val[0])
        return eval(fexp)# Set up time filters
    return f

if args['--for']:
    def filtered(vals):
        return it.ifilter(filtf(args['--for']), vals)

elif args['--while']:
    def filtered(vals):
        f1 = filtf(args['--while'])
        for _ in it.takewhile(lambda v: not f1(v), vals):
            pass
        return it.takewhile(f1, vals)
else:
    def filtered(vals):
        return vals

# Put together values with same time in a single row
# with extra column for time
col_idx = {tag:(i+1) for (i, tag) in enumerate(tags)}

def get_row(vals):
    row = [None] + [''] * len(tags)

    for (time, tag, val) in vals:
        if time != row[0]:
            if row[0] is not None: yield row
            row = [time] + [''] * len(tags)

        if tag not in tags:
            tags.append(tag)
            col_idx[tag] = len(tags)
            row.append(val)
        else:
            row[col_idx[tag]] += val
    # Add last row
    if row[0] is not None: yield row

# Blockify
def blockify(rows):
    if block_size == 0:
        return [list(rows)]
    else:
        return iter(lambda: list(it.islice(rows, block_size)), [])

formatter = string.Formatter()
def fprint(fmt_str, args):
    print(formatter.vformat(fmt_str, args, {}))

vals = get_val(sys.stdin)
filt_vals = filtered(vals)
rows = get_row(filt_vals)
blocks = blockify(rows)

row_id = 0
for block in blocks:
    cols = ['time'] + tags
    # Figure out width of each column for pretty printing
    col_widths = map(len, cols)
    for row in block:
        col_widths = map(max, col_widths, map(len, row))
    # Construct format string
    fmt_str = '{0:>8}\t' + '\t'.join('{'+str(i+1)+':>'+str(w)+'}' for i, w in enumerate(col_widths))

    dashes = ['---'] + ['-'*w for w in col_widths]
    fprint(fmt_str, ['idx'] + cols)
    fprint(fmt_str, dashes)
    for row in block:
        spaces = [""] * (len(cols) - len(row))
        row += spaces
        fprint(fmt_str, [row_id] + row)
        row_id += 1
    fprint(fmt_str, dashes)
