import sys
from PyQt5 import QtGui, QtCore, QtWidgets
from datetime import datetime
import time
import functools
import os
import errno
import json
from tinydb import TinyDB, where

from thread import Thread
from trayicon import SystemTrayIcon

# DONE: rozdělit do více souborů po objektech
# DONE: přejmenovat objekty (Sensor->Arduino)
# DONE: vyhodit formátovací fce pryč od logickejch
# DONE: conf: více cest kam ukládat
# DONE: conf: více formátů, do kterých ukládat
# DONE: pojmenovat senzory, každýmu vlastní soubor/složku
# DONE: zatím jsem neudělal persistent saving - asi z principu nechceme?
# TODO: cleanup: s1/sensor/arduino
# TODO: cleanup: místo db_names save_locations
# TODO: cleanup: formáty ukládání (jako parametr)


def load_config():
    config_filename = "config.json"
    config_sample_filename = "config.sample.json"

    if os.path.isfile(config_filename):  # If config exists, load it
        with open(config_filename) as jsonfile:
            config = json.load(jsonfile)

        #print(config)

    else:  # If it doesn't exist, load sample and save config
        with open(config_sample_filename) as jsonfile:
            config = json.load(jsonfile)
        with open(config_filename, 'w') as fp:
            json.dump(config, fp, indent=2)
    return config


def main():
    app = QtWidgets.QApplication(sys.argv)
    w = QtWidgets.QWidget()

    config = load_config()

    mainThread = Thread(config)  # build the thread object (it won't be running yet)
    trayIcon = SystemTrayIcon(QtGui.QIcon("images/logs.png"), config, parent=w, thread=mainThread)

    trayIcon.show()

    mainThread.start()  # run will be executed in a separate thread

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
