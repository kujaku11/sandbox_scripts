# -*- coding: utf-8 -*-
"""
Created on Mon Nov 23 11:33:21 2015

@author: jpeacock
"""

import sys
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backend_bases import FigureManagerBase, key_press_handler
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar


class AppForm(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        #self.x, self.y = self.get_data()
        self.data = self.get_data2()
        self.create_main_frame()
        self.on_draw()

    def create_main_frame(self):
        self.main_frame = QWidget()

        self.fig = Figure((5.0, 4.0), dpi=100)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self.main_frame)
        self.canvas.setFocusPolicy( Qt.ClickFocus )
        self.canvas.setFocus()

        self.mpl_toolbar = NavigationToolbar(self.canvas, self.main_frame)

        self.canvas.mpl_connect('key_press_event', self.on_key_press)
        self.canvas.mpl_connect('pick_event', self.on_pick)

        vbox = QVBoxLayout()
        vbox.addWidget(self.canvas)         # the matplotlib canvas
        vbox.addWidget(self.mpl_toolbar)
        self.main_frame.setLayout(vbox)
        self.setCentralWidget(self.main_frame)

    def get_data2(self):
        return np.arange(20).reshape([4,5]).copy()

    def on_draw(self):
        self.fig.clear()
        self.axes = self.fig.add_subplot(111)
        #self.axes.plot(self.x, self.y, 'ro')
        #self.axes.imshow(self.data, interpolation='nearest')
        self.axes.plot(np.arange(40), np.random.randint(0, 10, 40), ls='--',
                       marker='s',picker=1.5)
        self.axes.set_xlim(0, 40)
        self.axes.set_ylim(0, 10)
        self.canvas.draw()

    def on_key_press(self, event):
        print 'you pressed', event.key
        # implement the default mpl key press events described at
        # http://matplotlib.sourceforge.net/users/navigation_toolbar.html#navigation-keyboard-shortcuts
        key_press_handler(event, self.canvas, self.mpl_toolbar)
        
    def on_pick(self, event):
        print 'Clicked button {0}'.format(event.mouseevent.button)
        print 'index value {0}'.format(event.ind)
        print 'coords {0}, {1}'.format(event.artist.get_xdata()[event.ind], 
                                       event.artist.get_ydata()[event.ind])
        
def main():
    app = QApplication(sys.argv)
    form = AppForm()
    form.show()
    app.exec_()

if __name__ == "__main__":
    main()