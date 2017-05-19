import sys
from PyQt5 import QtGui, QtCore, QtWidgets
from sensor import Sensor
from datetime import datetime
import time
import functools
import os
from tinydb import TinyDB, where


class Main(QtCore.QThread):
    # this object is referenced as self.thread from SystemTrayIcon
    file_location = os.path.join("C:\\", "Users", "User", "Desktop", "temp_log.txt")
    db_folder = os.path.join("C:\\", "Data\\")
    date = None
    # self.db

    def __init__(self, sensors):
        QtCore.QThread.__init__(self)
        self.s1 = Sensor("COM4")
        self.sensors = sensors
        for k, d in self.sensors.items():
            d['on'] = True
            d['interval'] = 60

        self.update_db_date()

    def update_db_date(self):
        if self.date != self.get_current_date():
            self.date = self.get_current_date()
            self.db = TinyDB(self.db_folder + self.date + ".json", default_table='arduino',
                             sort_keys=True, indent=4)

    def get_current_date(self):
        date = datetime.now().strftime("%y-%m-%d")
        return date

    def run(self):
        '''
        Main loop of the measuring thread.
        '''
        while True:
            for k in self.sensors.keys():
                if self.sensors[k]['on']:
                    self.get_measurement(self.sensors[k]['key'])
            # We need to time stuff rather than sleep :(
            time.sleep(self.interval)

    def get_measurement(self, sensor_key):
        reading = self.s1.read(sensor_key)
        print(reading)
        reading['stamp'] = int(time.time() * 1000)
        reading['date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        self.update_db_date()
        self.db.insert(reading)

    def set_interval(self, interval):
        '''
        Sets measuring interval.
        '''
        self.interval = interval
        print("Measuring interval set to {}.".format(interval))

    # Turn ON / OFF functions -------------------------------------------------
    def turn_on(self):
        self.on = True

    def turn_off(self):
        self.on = False

    def turn(self, status):
        print("Turn received status {}".format(status))
        self.on = status


class SystemTrayIcon(QtWidgets.QSystemTrayIcon):
    s1_freq = 5  # [s]
    intervals = [60, 600]

    def __init__(self, icon, sensors, parent=None, thread=None):

        self.thread = thread
        self.sensors = sensors

        QtWidgets.QSystemTrayIcon.__init__(self, icon, parent)
        menu = QtWidgets.QMenu(parent)  # Hlavní widget

        for k, s in self.sensors.items():
            submenu = QtWidgets.QMenu(menu)
            submenu.setTitle(s['name'])

            item_interval_1 = submenu.addAction("1 m")
            item_interval_2 = submenu.addAction("10 m")

            item_start = submenu.addAction("Start")
            item_stop = submenu.addAction("Stop")
            menu.addMenu(submenu)

            item_interval_1.triggered.connect(functools.partial(
                self.thread.set_interval, self.intervals[0]))
            item_interval_2.triggered.connect(functools.partial(
                self.thread.set_interval, self.intervals[1]))

            item_start.triggered.connect(functools.partial(self.thread.turn, True))
            item_stop.triggered.connect(functools.partial(self.thread.turn, False))

        exitAction = menu.addAction("Exit")
        self.setContextMenu(menu)

        exitAction.triggered.connect(self.exit)

        print("Tray icon set up.")

    def artSleep(self, sleepTime):
        stop_time = QtCore.QTime()
        stop_time.restart()
        while stop_time.elapsed() < sleepTime:
            QtWidgets.QApplication.processEvents(QtCore.QEventLoop.AllEvents, 0)

    def exit(self):
        self.hide()
        QtCore.QCoreApplication.exit()


def main():
    app = QtWidgets.QApplication(sys.argv)
    w = QtWidgets.QWidget()

    sensors = {
        's1': {
            'name': 'Sensor 1',
            'key': b'L'
        },
        's2': {
            'name': 'Sensor 2',
            'key': b'K'
        }
    }

    mainThread = Main(sensors)  # build the thread object (it won't be running yet)
    trayIcon = SystemTrayIcon(QtGui.QIcon("Logger.png"), sensors, parent=w, thread=mainThread)

    trayIcon.show()

    mainThread.start()  # run will be executed in a separate thread

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
