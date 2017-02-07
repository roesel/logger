# -*- coding: utf-8 -*-
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from gui import Ui_browsergui
from gui_obsluha import GuiProgram

import numpy as np
import matplotlib
matplotlib.use("Qt5Agg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    dialog = QtWidgets.QDialog()

    prog = GuiProgram(dialog)

    fig = Figure()  # empty figure to be put into GUI
    ax1f1 = fig.add_subplot(111)  # empty plot
    prog.put_figure_into_gui(fig)

    dialog.show()
    sys.exit(app.exec_())
