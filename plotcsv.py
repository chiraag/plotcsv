import sys
import numpy as np
import itertools as it
import pandas as pd
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
import types

file_in = sys.argv[1]
to_plot = sys.argv[2:]

clock_offset = 0.0
clock_period = 10.0

data = pd.read_csv(file_in, sep='\t', skipinitialspace=True)
# remove rows with dashes
data = data[data.idx != '---']
data.time = (data.time.astype(float) - clock_offset + (clock_period/2)) / clock_period

if not to_plot:
    headings = list(data.axes[1])
    to_plot = headings[2:]

to_plot.reverse()

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
leftAxis.setTickStrings(to_plot)

w1 = view.addPlot(colspan=2, axisItems={'left':leftAxis})
w1.showGrid(x=True, alpha=0.5)

text = pg.TextItem(color="#ffffff", fill=(20,20,20), anchor=(1,1), border="#ffffff")

time_indexed = data.set_index('time')
def mouseClickEvent(obj, ev):
    time = int(ev.pos().x()) + 0.5
    row_num = int(ev.pos().y() + 0.5)
    row = to_plot[row_num]
    data = time_indexed.loc[time, row]
    if pd.notnull(data):
        text.setText(str(data))
        text.setPos(ev.pos())

colors = '#377eb8,#4daf4a,#e41a1c,#984ea3,#ff7f00'.split(',')


for yi, (row, color) in enumerate(it.izip(to_plot, it.cycle(colors))):
    s1 = pg.ScatterPlotItem(size=1, symbol='s', pen=pg.mkPen(None), brush=pg.mkBrush(color), pxMode=False)
    x = data.time[data[row].notnull()]
    y = np.repeat(yi, x.shape)
    s1.addPoints(x=x, y=y)
    s1.mouseClickEvent = types.MethodType(mouseClickEvent, s1)
    w1.addItem(s1)
w1.addItem(text)

view.nextRow()
w2 = view.addPlot()
w2.hideAxis('left')
t0, t1 = data.time.min(), data.time.max()
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
