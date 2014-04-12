from __future__ import print_function
import re, sys
import pandas as pd

def read_trace(file_in):
    def clean_input(f):
        valid_line = re.compile(r'^(\s*\d+)\t(.*?)\t(.*)')
        for line in f:
            match = valid_line.match(line)
            if not match:
                print(line, end='', file=sys.stderr)
            else:
                m = match.groups()
                yield (int(m[0]), m[1:])

    return pd.DataFrame.from_items(clean_input(file_in), columns=['tag', 'val'], orient='index')

def write_trace_table(df, tags, file_out):
    dtable = pd.concat([df.val[df.tag == tag] for tag in tags], axis=1)
    dtable.columns = tags
    dtable.to_csv(file_out, sep='\t')
