from __future__ import print_function
import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore

import plot_settings

class TagAxisItem(pg.AxisItem):
    def setTickStrings(self, strings):
        self._tickStr = dict(enumerate(strings))

    def tickStrings(self, values, scale, spacing):
        return [self._tickStr.get(va*scale, '') for va in values]

class TracePlotItem(pg.ScatterPlotItem):
    def __init__(self, df, settings, textBox):
        pg.ScatterPlotItem.__init__(self, size=1, symbol='s', pen=None, pxMode=False)
        self.textBox = textBox
        self.settings = settings

        x = settings.get_cycle_count(np.array(df.index)) + 0.5
        y = np.array(df.tag.apply(settings.get_row_pos))
        c = np.array(df.val.apply(settings.get_color))

        self.addPoints(x=x, y=y, brush=c)
        self.idx_by_tag = df.set_index('tag', append=True)

    def mouseClickEvent(self, ev):
        time = self.settings.get_time(ev.pos().x())
        tag = self.settings.get_tag(ev.pos().y())
        try:
            val = self.idx_by_tag.loc[time, tag].val
            self.textBox.setText('cycle: {}\n'.format(time) + val)
        except KeyError:
            self.textBox.setText('cycle: {}'.format(time))

        self.textBox.setPos(ev.pos())

def plot(df, tags, title):
    tags = list(reversed(tags))
    settings = plot_settings.PlotSettings(tags)

    # Qt startup
    try:
        app = QtGui.QApplication([])
    except RuntimeError:
        app = QtCore.QCoreApplication.instance()

    win = QtGui.QMainWindow()
    win.resize(1600,800)
    layout = pg.GraphicsLayoutWidget()
    win.setCentralWidget(layout)
    win.setWindowTitle(title)

    # Trace plot setup
    tagAxis = TagAxisItem('left')
    tagAxis.setTickStrings(tags)
    tracePlot = layout.addPlot(axisItems={'left':tagAxis})

    tracePlot.showGrid(x=True, alpha=1)
    tracePlot.setMouseEnabled(x=True, y=False)

    # Click text
    text = pg.TextItem(color="#ffffff", fill=(20,20,20), anchor=(1,1), border="#ffffff")

    # Plot trace
    s1 = TracePlotItem(df, settings, text)

    tracePlot.addItem(s1)
    tracePlot.addItem(text)

    # Scroller setup
    layout.nextRow()
    scroller = layout.addPlot()
    scroller.hideAxis('left')
    t0 = settings.get_cycle_count(df.index[0])
    t1 = settings.get_cycle_count(df.index[-1])
    scroller.plot(x=[t0, t1], y=[1, 1])

    lr = pg.LinearRegionItem([t0, t1])
    lr.setZValue(-10)
    scroller.addItem(lr)
    scroller.setMaximumHeight(50)
    scroller.setMouseEnabled(x=True, y=False)

    def updatePlot():
        tracePlot.setXRange(*lr.getRegion(), padding=0)

    def updateRegion():
        lr.setRegion(tracePlot.getViewBox().viewRange()[0])

    lr.sigRegionChanged.connect(updatePlot)
    tracePlot.sigXRangeChanged.connect(updateRegion)

    updateRegion()

    return win, app
