# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'gui.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_browsergui(object):
    def setupUi(self, browsergui):
        browsergui.setObjectName("browsergui")
        browsergui.resize(900, 663)
        browsergui.setMinimumSize(QtCore.QSize(900, 0))
        self.gridLayout = QtWidgets.QGridLayout(browsergui)
        self.gridLayout.setObjectName("gridLayout")
        self.mplwindow = QtWidgets.QWidget(browsergui)
        self.mplwindow.setMinimumSize(QtCore.QSize(0, 0))
        self.mplwindow.setBaseSize(QtCore.QSize(0, 0))
        self.mplwindow.setObjectName("mplwindow")
        self.mplvl = QtWidgets.QVBoxLayout(self.mplwindow)
        self.mplvl.setContentsMargins(0, 0, 0, 0)
        self.mplvl.setObjectName("mplvl")
        self.gridLayout.addWidget(self.mplwindow, 0, 0, 4, 1)
        self.btnOpenFile = QtWidgets.QPushButton(browsergui)
        self.btnOpenFile.setObjectName("btnOpenFile")
        self.gridLayout.addWidget(self.btnOpenFile, 3, 1, 1, 1)

        self.retranslateUi(browsergui)
        QtCore.QMetaObject.connectSlotsByName(browsergui)

    def retranslateUi(self, browsergui):
        _translate = QtCore.QCoreApplication.translate
        browsergui.setWindowTitle(_translate("browsergui", "Browser"))
        self.btnOpenFile.setText(_translate("browsergui", "Open File"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    browsergui = QtWidgets.QDialog()
    ui = Ui_browsergui()
    ui.setupUi(browsergui)
    browsergui.show()
    sys.exit(app.exec_())

