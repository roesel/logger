import sys
from PyQt5 import QtGui, QtCore, QtWidgets
from datetime import datetime
import time
import functools
import os
import errno
import json
from tinydb import TinyDB, where
from sensor import Arduino

import tools


class Thread(QtCore.QThread):
    # this object is referenced as self.thread from SystemTrayIcon
    date = None

    def __init__(self, config):
        QtCore.QThread.__init__(self)
        self.s1 = Arduino(config['port'])
        self.sensors = config['sensors']
        self.db_folders = config['db_folders']

        for db_folder in self.db_folders:
            self.make_sure_path_exists(db_folder)
            for k in self.sensors:
                self.make_sure_path_exists(db_folder + "/" + k + "_json")
                self.make_sure_path_exists(db_folder + "/" + k + "_txt")

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
        for key in self.sensors:
            self.sensors[key]['dbs'] = []
            self.sensors[key]['txts'] = []
            for db_folder in self.db_folders:
                db_object = TinyDB(db_folder + key + "_json/" + key + "_" + self.date +
                                   ".json", default_table='arduino', sort_keys=True, indent=4)
                self.sensors[key]['dbs'].append(db_object)
                txt_name = db_folder + key + "_txt/" + key + "_" + self.date + ".txt"
                self.sensors[key]['txts'].append(txt_name)

    def get_current_date(self):
        date = datetime.now().strftime("%y-%m-%d")
        return date

    def run(self):
        '''
        Main loop of the measuring thread.
        '''
        while True:
            for k in self.sensors:
                if self.sensors[k]['on']:
                    if time.time() - self.sensors[k]['last_measurement'] > self.sensors[k]['interval']:
                        self.get_measurement(k)
                        self.sensors[k]['last_measurement'] = time.time()
            # Maximum measuring frequency
            time.sleep(1)

    def insert(self, sensor_key, reading):
        # TinyDB local storage
        for db in self.sensors[sensor_key]['dbs']:
            db.insert(reading)
        # TXT local storage
        for txt in self.sensors[sensor_key]['txts']:
            self.insert_txt(txt, sensor_key, reading)

    def insert_txt(self, fname, sensor_key, reading):
        if not os.path.isfile(fname):
            with open(fname, "w", encoding="utf-8") as f:
                header = "# "
                header += '\t'.join(reading.keys())
                header += "\n"
                f.write(header)
        with open(fname, "a", encoding="utf-8") as f:
            line = '\t'.join(str(e) for e in reading.values())
            line += "\n"
            f.write(line)

    def get_measurement(self, sensor_key):
        reading = self.s1.read(str.encode(self.sensors[sensor_key]["key"]))
        # print(reading)
        reading['stamp'] = int(time.time() * 1000)
        reading['date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        self.update_db_date()
        self.insert(sensor_key, reading)

    def set_interval(self, key, interval):
        '''
        Sets measuring interval.
        '''
        self.sensors[key]['interval'] = interval
        print("Interval sensoru `{}` nastaven na {}.".format(
            self.sensors[key]['name'], tools.pretty_time(interval)))

    def turn(self, k, status):
        st = ['vypnut', 'zapnut']
        if self.sensors[k]['on'] != status:
            self.sensors[k]['on'] = status
            print("{} byl {}.".format(self.sensors[k]['name'], st[status]))
        else:
            print("{} byl už {}, žádná změna.".format(self.sensors[k]['name'], st[status]))
