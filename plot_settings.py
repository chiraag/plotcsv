import re
from pyqtgraph import mkBrush

class PlotSettings(object):
    def __init__(self, tags):
        self.f = re.compile(r'tileId: (\d)') 
        colors = '#377eb8,#7b3294,#c2a5cf,#a6dba0,#008837'.split(',')
        self.colors = [mkBrush(col) for col in colors]
        self.tags = tags

    def get_cycle_count(self, time):
        return (time - 0.0) / 10.0

    def get_time(self, cycle):
        return int(cycle) * 10

    def get_row_pos(self, tag):
        return self.tags.index(tag)

    def get_tag(self, row):
        return self.tags[int(row + 0.5)]

    def get_color(self, val):
        m = self.f.search(val)
        if m:
            return self.colors[int(m.group(1)) + 1]
        else:
            return self.colors[0]
