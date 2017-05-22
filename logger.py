import sys
from PyQt5 import QtGui, QtCore, QtWidgets
from sensor import Sensor
from datetime import datetime
import time
import functools
import os
import errno
from tinydb import TinyDB, where

# move db_folder, COM4, ... into settings passed + autosave


class Main(QtCore.QThread):
    # this object is referenced as self.thread from SystemTrayIcon
    date = None
    # self.db

    def __init__(self, config):
        QtCore.QThread.__init__(self)
        self.s1 = Sensor(config['port'])
        self.db_folder = config['db_folder']
        self.make_sure_path_exists(self.db_folder)
        self.sensors = config['sensors']
        for k, d in self.sensors.items():
            d['on'] = False
            d['interval'] = 60
            d['last_measurement'] = 0

        self.update_db_date()

    def make_sure_path_exists(self, path):
        try:
            os.makedirs(path)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise

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
                    if time.time() - self.sensors[k]['last_measurement'] > self.sensors[k]['interval']:
                        self.get_measurement(self.sensors[k]['key'])
                        self.sensors[k]['last_measurement'] = time.time()
            # Maximum measuring frequency
            time.sleep(1)

    def get_measurement(self, sensor_key):
        reading = self.s1.read(sensor_key)
        # print(reading)
        reading['stamp'] = int(time.time() * 1000)
        reading['date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        self.update_db_date()
        self.db.insert(reading)

    def min_label(self, minutes):
        return {1: 'minuta', 2: 'minuty', 3: 'minuty', 4: 'minuty'}.get(minutes, 'minut')

    def sec_label(self, minutes):
        return {1: 'vteřina', 2: 'vteřiny', 3: 'vteřiny', 4: 'vteřiny'}.get(minutes, 'vtěřin')

    def pretty_time(self, seconds):
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        if h == 0:
            if m != 0 and s == 0:
                return "{} ".format(m) + self.min_label(m)
            elif s != 0 and m == 0:
                return "{} ".format(s) + self.sec_label(m)
            else:
                return "%02d:%02d" % (m, s)
        elif h == 0 and m == 0 and s > 0:
            return "%02d min" % m
        else:
            return "%d:%02d:%02d" % (h, m, s)

    def set_interval(self, key, interval):
        '''
        Sets measuring interval.
        '''
        self.sensors[key]['interval'] = interval
        print("Interval sensoru `{}` nastaven na {}.".format(
            self.sensors[key]['name'], self.pretty_time(interval)))

    def turn(self, k, status):
        st = ['vypnut', 'zapnut']
        if self.sensors[k]['on'] != status:
            self.sensors[k]['on'] = status
            print("{} byl {}.".format(self.sensors[k]['name'], st[status]))
        else:
            print("{} byl už {}, žádná změna.".format(self.sensors[k]['name'], st[status]))


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
                item_interval = submenu.addAction(self.thread.pretty_time(i))
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

    config = {
        'db_folder': os.path.join("C:\\", "LoggerData\\"),
        'port': "COM4",
        'intervals': [10, 30, 60, 300],
        'sensors': {
            's1': {
                'name': 'Sensor 1',
                'key': b'L'
            },
            's2': {
                'name': 'Sensor 2',
                'key': b'K'
            },
        },
    }

    mainThread = Main(config)  # build the thread object (it won't be running yet)
    trayIcon = SystemTrayIcon(QtGui.QIcon("images/logs.png"), config, parent=w, thread=mainThread)

    trayIcon.show()

    mainThread.start()  # run will be executed in a separate thread

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
