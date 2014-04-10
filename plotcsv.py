import csv
import sys
import numpy as np
from bokeh.plotting import *
from bokeh.objects import Range1d, HoverTool
from collections import OrderedDict
import itertools as it

file_in = sys.argv[1]
file_out = sys.argv[2]
tags = sys.argv[3:]

clock_offset = 0
clock_period = 10

class PlotRow(object):
    def __init__(self, name):
        self.rectStarts = []
        self.rectStops = []
        self.name = name

    def addValAt(self, time, val):
        if not val.isspace():
            if (not self.rectStops) or (time - self.rectStops[-1] != 0):
                self.rectStarts.append(time)
                self.rectStops.append(time + clock_period)
            else:
                self.rectStops[-1] = time + clock_period

    def __str__(self):
        return self.name + ' starts: ' + str(self.rectStarts) + ' stops: ' + str(self.rectStops)

    def __repr__(self):
        return self.__str__()

a = csv.reader(open(file_in), delimiter='\t')
headings = map(str.strip, next(a))
next(a) # dashes
time_col = headings.index('time')

if tags:
    tag_cols = [headings.index(tag) for tag in tags]
else:
    tags = headings[2:]
    tag_cols = range(2, len(headings))

plotRows = [PlotRow(name=tag) for (col, tag) in zip(tag_cols, tags)]

for line in a:
    try:
        time = int(line[time_col])
    except ValueError: # done parsing the file
        break
    for tag_col, plotRow in zip(tag_cols, plotRows):
        plotRow.addValAt(time, line[tag_col])

output_file(file_out)

N = sum(len(row.rectStarts) for row in plotRows)
tStart = np.zeros(shape=(N,))
tStop = np.zeros(shape=(N,))
y = np.zeros(shape=(N,))
names = []
colors = []
colorsAvailable = '#377eb8,#4daf4a,#e41a1c,#984ea3,#ff7f00'.split(',')

yi = 0
for row, color in it.izip(plotRows, it.cycle(colorsAvailable)):
    startIdx = len(names)
    n = len(row.rectStarts)
    stopIdx = startIdx + n

    tStart[startIdx:stopIdx] = row.rectStarts
    tStop[startIdx:stopIdx] = row.rectStops
    y[startIdx:stopIdx] = yi
    names.extend(it.repeat(row.name, n))
    colors.extend(it.repeat(color, n))

    yi += 1

tStart = (tStart - clock_offset) / clock_period
tStop = (tStop - clock_offset) / clock_period
x = (tStart + tStop) / 2
w = (tStop - tStart)

data = ColumnDataSource(data=dict(x=x, y=y, w=w, start=tStart, stop=tStop, color=colors, name=names))
rect('x', 'y', 'w', 0.9, source=data, color='color', plot_width=1480, plot_height=800, tools="pan,resize,wheel_zoom,box_zoom,reset,hover")

plot = curplot()

for tool in plot.tools:
    if isinstance(tool, HoverTool):
        hover = tool
        break

hover.tooltips = OrderedDict(name="@name", start="@start", cycles='@w', stop="@stop")
show(browser='firefox')
