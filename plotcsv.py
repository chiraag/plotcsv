from __future__ import print_function
import re, sys
import numpy as np
import itertools as it
import pandas as pd
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
import types

def get_cycle_count(time):
    return (time - 0.0) / 10.0

def get_time(cycle):
    return int(cycle) * 10

valid_line = re.compile(r'^(\s*\d+)\t(.*?)\t(.*)')
file_in = sys.argv[1]
tags = sys.argv[2:]

def clean_input(f):
    for line in f:
        match = valid_line.match(line)
        if not match:
            print(line, end='', file=sys.stderr)
        else:
            m = match.groups()
            yield (int(m[0]), m[1:])

df = pd.DataFrame.from_items(clean_input(open(file_in)), columns=['tag', 'val'], orient='index')
if not tags:
    tags = list(df.tag.drop_duplicates())

tags.reverse()

def get_row_pos(tag):
    return tags.index(tag)

def get_tag(row):
    return tags[int(row + 0.5)]

f = re.compile(r'tileId: (\d)') 
colors = '#377eb8,#4daf4a,#e41a1c,#984ea3,#ff7f00'.split(',')
def get_color(val):
    m = f.search(val)
    if m:
        return colors[int(m.group(1)) + 1]
    else:
        return colors[0]

class MyAxis(pg.AxisItem):
    def setTickStrings(self, strings):
        self._tickStr = dict(enumerate(strings))

    def tickStrings(self, values, scale, spacing):
        return [self._tickStr.get(va*scale, '') for va in values]

try:
    app = QtGui.QApplication([])
except RuntimeError:
    app = QtCore.QCoreApplication.instance()

mw = QtGui.QMainWindow()
mw.resize(1600,800)
view = pg.GraphicsLayoutWidget()  ## GraphicsView with GraphicsLayout inserted by default
mw.setCentralWidget(view)
mw.show()
mw.setWindowTitle('Trace: {}'.format(file_in))

leftAxis = MyAxis('left')
leftAxis.setTickStrings(tags)

w1 = view.addPlot(colspan=2, axisItems={'left':leftAxis})
w1.showGrid(x=True, alpha=1)

text = pg.TextItem(color="#ffffff", fill=(20,20,20), anchor=(1,1), border="#ffffff")

idx_by_tag = df.set_index('tag', append=True)
def mouseClickEvent(obj, ev):
    time = get_time(ev.pos().x())
    tag = get_tag(ev.pos().y())
    try:
        val = idx_by_tag.loc[time, tag].val
    except KeyError:
        return

    text.setText(val)
    text.setPos(ev.pos())

s1 = pg.ScatterPlotItem(size=1, symbol='s', pen=None, pxMode=False)
x = get_cycle_count(np.array(df.index)) + 0.5
y = np.array(df.tag.apply(get_row_pos))
c = np.array(df.val.apply(get_color))

s1.addPoints(x=x, y=y, brush=c)

s1.mouseClickEvent = types.MethodType(mouseClickEvent, s1)
w1.addItem(s1)
w1.addItem(text)

view.nextRow()
w2 = view.addPlot()
w2.hideAxis('left')
t0, t1 = x.min(), x.max()
w2.plot(x=[t0, t1], y=[1, 1])
lr = pg.LinearRegionItem([t0, t1])
lr.setZValue(-10)
w2.addItem(lr)
w2.setMaximumHeight(50)

def updatePlot():
    w1.setXRange(*lr.getRegion(), padding=0)

def updateRegion():
    lr.setRegion(w1.getViewBox().viewRange()[0])

lr.sigRegionChanged.connect(updatePlot)
w1.sigXRangeChanged.connect(updateRegion)
updatePlot()

w1.setMouseEnabled(x=True, y=False)
w2.setMouseEnabled(x=True, y=False)
## Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()




