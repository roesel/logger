# -*- coding: utf-8 -*-
import sys
import os
import time
from datetime import datetime
import pickle
from PyQt5 import QtCore, QtGui, QtWidgets

from gui import Ui_browsergui

import numpy as np
import matplotlib
matplotlib.use("Qt5Agg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)

from tinydb import TinyDB, where, Query


class GuiProgram(Ui_browsergui):
    data = ''

    def __init__(self, dialog):
        Ui_browsergui.__init__(self)
        self.setupUi(dialog)

        # Connect "Open File" button with a custom function
        self.btnOpenFile.clicked.connect(self.open_measurement)

    def open_measurement(self):
        # Qt Dialog to open file
        open_file_name, _ = QtWidgets.QFileDialog.getOpenFileName(
            None,
            'Otevřít měření',
            os.path.join('C:\\', 'Data'),
            'Text Files (*.txt);JSON Files (*.json);;All Files (*)'
        )

        # Actual opening of file
        # try:
        self.db = TinyDB(open_file_name, default_table='arduino')
        data = self.db.table('arduino').all()
        x, y = self.load_variable(data)
        self.plot_data(x, y)
        # except:
        #     print("File failed to open.")

    def load_variable(self, data):
        x, y = [], []
        for row in data:
            x.append(datetime.fromtimestamp(row['stamp'] / 1e3))
            y.append(row['temperature'])
        return x, y

    # Plotting functions

    def plot_random(self):
        self.plot_data(np.random.rand(10))

    def plot_data(self, x, y):
        ''' Plots the provided data onto the figure in the GUI. '''

        self.fig.clf()  # Clear contents of current figure
        ax1f1 = self.fig.add_subplot(111)  # Add a new subplot that we will be plotting into

        # Plot cosmetics
        # ax1f1.set_xlabel('')
        ax1f1.set_ylabel('T [° C]')
        ax1f1.set_title('Plot Title')

        ax1f1.plot(x, y)  # Actual plotting
        self.fig.autofmt_xdate()

        self.canvas.draw()  # Propagate changes to GUI

    # Initialization and system functions

    def gui_sleep(self, sleepTime):
        ''' Sleeps for "sleepTime" seconds, but checks for events every 50 ms. '''
        stop_time = QtCore.QTime()
        stop_time.restart()
        while stop_time.elapsed() < sleepTime * 1000:
            QtWidgets.QApplication.processEvents(QtCore.QEventLoop.AllEvents, 50)

    def put_figure_into_gui(self, fig):
        ''' Creates a figure and places it inside the GUI container. '''

        # Figure
        self.fig = fig

        # Canvas
        self.canvas = FigureCanvas(self.fig)
        self.mplvl.addWidget(self.canvas)
        self.canvas.draw()

        # Toolbar
        self.toolbar = NavigationToolbar(self.canvas, self.mplwindow, coordinates=True)
        self.mplvl.addWidget(self.toolbar)

    def remove_figure_from_gui(self,):
        ''' Deletes the figure from the GUI. '''

        # Canvas
        self.mplvl.removeWidget(self.canvas)
        self.canvas.close()
        self.canvas.deleteLater()  # this prevents memory leaks

        # Toolbar
        self.mplvl.removeWidget(self.toolbar)
        self.toolbar.close()
        self.toolbar.deleteLater()  # this prevent memory leaks

    # def memory(self):
    #     import os
    #     from wmi import WMI
    #     w = WMI('.')
    #     result = w.query("SELECT WorkingSet FROM Win32_PerfRawData_PerfProc_Process WHERE IDProcess=%d" % os.getpid())
    #     return int(result[0].WorkingSet)
