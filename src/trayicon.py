# -*- coding: utf-8 -*-
import sys
from PyQt5 import QtGui, QtCore, QtWidgets
from datetime import datetime
import time
import functools
import os
import errno
import json
from tinydb import TinyDB, where

import tools


class SystemTrayIcon(QtWidgets.QSystemTrayIcon):

    def __init__(self, icon, config, parent=None, thread=None):

        self.thread = thread
        self.sensors = config['sensors']
        self.intervals = config['intervals']
        self.interval_items = {}

        QtWidgets.QSystemTrayIcon.__init__(self, icon, parent)
        menu = QtWidgets.QMenu(parent)  # Hlavní widget

        for k, s in self.sensors.items():
            submenu = QtWidgets.QMenu(menu)
            submenu.setTitle(s['name'])

            item_start = submenu.addAction("Začít měřit")
            item_stop = submenu.addAction("Přestat měřit")

            red_icon = QtGui.QIcon("images/red.png")
            green_icon = QtGui.QIcon("images/green.png")

            item_start.triggered.connect(functools.partial(self.thread.turn, k, True))
            item_start.triggered.connect(functools.partial(item_start.setEnabled, False))
            item_start.triggered.connect(functools.partial(item_stop.setEnabled, True))
            item_start.triggered.connect(functools.partial(
                submenu.setIcon, green_icon))

            item_stop.triggered.connect(functools.partial(self.thread.turn, k, False))
            item_stop.triggered.connect(functools.partial(item_start.setEnabled, True))
            item_stop.triggered.connect(functools.partial(item_stop.setEnabled, False))
            item_stop.triggered.connect(functools.partial(
                submenu.setIcon, red_icon))

            submenu.addSeparator()

            self.interval_items[k] = {}
            for i in self.intervals:
                item_interval = submenu.addAction(tools.pretty_time(i))
                item_interval.triggered.connect(functools.partial(self.thread.set_interval, k, i))
                item_interval.triggered.connect(functools.partial(self.updateIntervals, k, i))
                self.interval_items[k][i] = item_interval

            menu.addMenu(submenu)

            # ------------------------------------------------------------------
            submenu.setIcon(QtGui.QIcon("images/green.png"))
            item_start.setEnabled(False)
            self.thread.set_interval(k, self.intervals[-1])
            self.interval_items[k][self.intervals[-1]].setIcon(QtGui.QIcon("images/check.png"))
            self.thread.turn(k, True)

        exitAction = menu.addAction("Ukončit")
        self.setContextMenu(menu)

        exitAction.triggered.connect(self.exit)

        print("Tray icon set up.")

    def updateIntervals(self, key, interval):
        for k, v in self.interval_items[key].items():
            if k == interval:
                v.setIcon(QtGui.QIcon("images/check.png"))
            else:
                v.setIcon(QtGui.QIcon())

    def art_sleep(self, sleepTime):
        stop_time = QtCore.QTime()
        stop_time.restart()
        while stop_time.elapsed() < sleepTime:
            QtWidgets.QApplication.processEvents(QtCore.QEventLoop.AllEvents, 0)

    def exit(self):
        self.hide()
        QtCore.QCoreApplication.exit()
