import sys
from PyQt5 import QtGui, QtCore, QtWidgets
from datetime import datetime
import time
import functools
import os
import errno
import json
from tinydb import TinyDB, where
from sensor import Sensor

from tools import *


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
                        self.get_measurement(str.encode(self.sensors[k]['key']))
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

    def set_interval(self, key, interval):
        '''
        Sets measuring interval.
        '''
        self.sensors[key]['interval'] = interval
        print("Interval sensoru `{}` nastaven na {}.".format(
            self.sensors[key]['name'], pretty_time(interval)))

    def turn(self, k, status):
        st = ['vypnut', 'zapnut']
        if self.sensors[k]['on'] != status:
            self.sensors[k]['on'] = status
            print("{} byl {}.".format(self.sensors[k]['name'], st[status]))
        else:
            print("{} byl už {}, žádná změna.".format(self.sensors[k]['name'], st[status]))
