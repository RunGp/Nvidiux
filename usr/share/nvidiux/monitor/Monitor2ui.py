# -*- coding: utf-8 -*-
#!/usr/bin/python2

# Copyright 2014-2016 Payet Guillaume
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 3, as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranties of
# MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR
# PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(1413, 1034)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.plotGpu = PlotWidget(self.centralwidget)
        self.plotGpu.setGeometry(QtCore.QRect(20, 80, 670, 430))
        self.plotGpu.setObjectName(_fromUtf8("plotGpu"))
        self.plotFan = PlotWidget(self.centralwidget)
        self.plotFan.setGeometry(QtCore.QRect(710, 80, 671, 431))
        self.plotFan.setObjectName(_fromUtf8("plotFan"))
        self.plotTemp = PlotWidget(self.centralwidget)
        self.plotTemp.setGeometry(QtCore.QRect(20, 550, 670, 430))
        self.plotTemp.setObjectName(_fromUtf8("plotTemp"))
        self.plotMem = PlotWidget(self.centralwidget)
        self.plotMem.setGeometry(QtCore.QRect(710, 550, 670, 430))
        self.plotMem.setObjectName(_fromUtf8("plotMem"))
        self.BouttonReglage = QtGui.QPushButton(self.centralwidget)
        self.BouttonReglage.setGeometry(QtCore.QRect(70, 20, 93, 27))
        self.BouttonReglage.setObjectName(_fromUtf8("BouttonReglage"))
        self.BouttoAbout = QtGui.QPushButton(self.centralwidget)
        self.BouttoAbout.setEnabled(False)
        self.BouttoAbout.setGeometry(QtCore.QRect(1280, 20, 93, 27))
        self.BouttoAbout.setObjectName(_fromUtf8("BouttoAbout"))
        self.labelTime = QtGui.QLabel(self.centralwidget)
        self.labelTime.setGeometry(QtCore.QRect(443, 515, 491, 31))
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.labelTime.setFont(font)
        self.labelTime.setObjectName(_fromUtf8("labelTime"))
        self.labelGpuName = QtGui.QLabel(self.centralwidget)
        self.labelGpuName.setGeometry(QtCore.QRect(270, 0, 270, 70))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.labelGpuName.setFont(font)
        self.labelGpuName.setObjectName(_fromUtf8("labelGpuName"))
        self.labelInfo = QtGui.QLabel(self.centralwidget)
        self.labelInfo.setGeometry(QtCore.QRect(890, 0, 270, 70))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.labelInfo.setFont(font)
        self.labelInfo.setObjectName(_fromUtf8("labelInfo"))
        self.labelGpu = QtGui.QLabel(self.centralwidget)
        self.labelGpu.setGeometry(QtCore.QRect(20, 510, 641, 41))
        self.labelGpu.setObjectName(_fromUtf8("labelGpu"))
        self.labelFan = QtGui.QLabel(self.centralwidget)
        self.labelFan.setGeometry(QtCore.QRect(740, 510, 641, 41))
        self.labelFan.setObjectName(_fromUtf8("labelFan"))
        self.labelTemp = QtGui.QLabel(self.centralwidget)
        self.labelTemp.setGeometry(QtCore.QRect(20, 990, 641, 41))
        self.labelTemp.setObjectName(_fromUtf8("labelTemp"))
        self.labelMemory = QtGui.QLabel(self.centralwidget)
        self.labelMemory.setGeometry(QtCore.QRect(740, 990, 641, 41))
        self.labelMemory.setObjectName(_fromUtf8("labelMemory"))
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "Nvidiux Monitor beta 1", None))
        self.BouttonReglage.setText(_translate("MainWindow", "Settings", None))
        self.BouttoAbout.setText(_translate("MainWindow", "About", None))
        self.labelTime.setText(_translate("MainWindow", "<html><head/><body><p align=\"center\">Time : 0 sec</p></body></html>", None))
        self.labelGpuName.setText(_translate("MainWindow", "Gpu Name", None))
        self.labelInfo.setText(_translate("MainWindow", "Machine info", None))
        self.labelGpu.setText(_translate("MainWindow", "<html><head/><body><p align=\"center\">GPU</p></body></html>", None))
        self.labelFan.setText(_translate("MainWindow", "<html><head/><body><p align=\"center\">Fan</p></body></html>", None))
        self.labelTemp.setText(_translate("MainWindow", "<html><head/><body><p align=\"center\">Temperature</p></body></html>", None))
        self.labelMemory.setText(_translate("MainWindow", "<html><head/><body><p align=\"center\">Memory</p></body></html>", None))

from pyqtgraph import PlotWidget
