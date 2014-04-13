from __future__ import print_function
import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
import plot_settings
from profilehooks import profile

class TracePlotItem(pg.ScatterPlotItem):
    def __init__(self, parent, df, settings):
        pg.ScatterPlotItem.__init__(self, size=1, symbol='s', pen=None, pxMode=False)

        self.settings = settings
        self.textBox = pg.TextItem(color="#ffffff", fill=(20,20,20), anchor=(1,1), border="#ffffff")

        x = settings.get_cycle_count(np.array(df.index)) + 0.5
        y = np.array(df.tag.apply(settings.get_row_pos))
        c = np.array(df.val.apply(settings.get_color))

        self.addPoints(x=x, y=y, brush=c)
        self.idx_by_tag = df.set_index('tag', append=True)

        parent.addItem(self)
        parent.addItem(self.textBox)

    def mouseClickEvent(self, ev):
        if ev.button() == QtCore.Qt.LeftButton:
            cycle = int(ev.pos().x())
            time = self.settings.get_time(cycle)
            tag = self.settings.get_tag(ev.pos().y())
            try:
                val = self.idx_by_tag.loc[time, tag].val
                self.textBox.setText('cycle: {}\n'.format(cycle) + val)
            except KeyError:
                self.textBox.setText('cycle: {}'.format(cycle))

            self.textBox.setPos(ev.pos())

def plot(df, tags, title):
    settings = plot_settings.PlotSettings(tags)

    # Qt startup
    app = pg.mkQApp()

    win = QtGui.QMainWindow()
    win.showMaximized()
    layout = pg.GraphicsLayoutWidget()
    win.setCentralWidget(layout)
    win.setWindowTitle(title)

    # Trace plot setup
    tracePlot = layout.addPlot()
    tracePlot.getAxis('left').setTicks([[(settings.get_row_pos(tag), tag) for tag in tags]])

    tracePlot.showGrid(x=True, alpha=1)
    tracePlot.setMouseEnabled(x=True, y=False)

    # Plot trace
    s1 = TracePlotItem(tracePlot, df, settings)

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
