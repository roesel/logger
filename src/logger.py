import sys
from PyQt5 import QtGui, QtCore, QtWidgets
from datetime import datetime
import time
import functools
import os
import errno
import json
from tinydb import TinyDB, where

from thread import Main
from trayicon import SystemTrayIcon

# DONE: rozdělit do více souborů po objektech
# TODO: přejmenovat objekty (Sensor->Arduino)
# TODO: vyhodit formátovací fce pryč od logickejch
# TODO: conf: více cest kam ukládat
# TODO: pojmenovat senzory, každýmu vlastní soubor
# DONE: zatím jsem neudělal persistent saving - asi z principu nechceme?


def load_config():
    config_filename = "config.json"
    config_sample_filename = "config.sample.json"

    if os.path.isfile(config_filename):  # If config exists, load it
        with open(config_filename) as jsonfile:
            config = json.load(jsonfile)

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

    mainThread = Main(config)  # build the thread object (it won't be running yet)
    trayIcon = SystemTrayIcon(QtGui.QIcon("images/logs.png"), config, parent=w, thread=mainThread)

    trayIcon.show()

    mainThread.start()  # run will be executed in a separate thread

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
