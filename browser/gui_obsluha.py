# -*- coding: utf-8 -*-
import sys
import time
import datetime
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


class GuiProgram(Ui_browsergui):

    def __init__(self, dialog):
        Ui_browsergui.__init__(self)
        self.setupUi(dialog)

        # Connect "add" button with a custom function (addInputTextToListbox)
        self.btnTest.clicked.connect(self.plot_random)
        self.btnTest2.clicked.connect(self.plot_random)

    def gui_sleep(self, sleepTime):
        ''' Sleeps for "sleepTime" seconds, but checks for events every 50 ms. '''
        stop_time = QtCore.QTime()
        stop_time.restart()
        while stop_time.elapsed() < sleepTime * 1000:
            QtWidgets.QApplication.processEvents(QtCore.QEventLoop.AllEvents, 50)

    def plot_random(self):
        self.plot_data(np.random.rand(10))

    def plot_data(self, data):
        ''' Plots the provided data onto the figure in the GUI. '''

        self.fig.clf()  # Clear contents of current figure
        ax1f1 = self.fig.add_subplot(111)  # Add a new subplot that we will be plotting into

        # Plot cosmetics
        ax1f1.set_xlabel('I [A]')
        ax1f1.set_ylabel('U [V]')
        ax1f1.set_title('Plot Title')

        ax1f1.plot(data)  # Actual plotting

        self.canvas.draw()  # Propagate changes to GUI

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
