# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'nvidiux/usr/share/nvidiux/monitor/Monitor2.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

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
        self.plotFan.setGeometry(QtCore.QRect(710, 80, 670, 430))
        self.plotFan.setObjectName(_fromUtf8("plotFan"))
        self.plotTemp = PlotWidget(self.centralwidget)
        self.plotTemp.setGeometry(QtCore.QRect(20, 550, 670, 430))
        self.plotTemp.setObjectName(_fromUtf8("plotTemp"))
        self.plotMem = PlotWidget(self.centralwidget)
        self.plotMem.setGeometry(QtCore.QRect(710, 550, 670, 430))
        self.plotMem.setObjectName(_fromUtf8("plotMem"))
        self.BouttonReglage = QtGui.QPushButton(self.centralwidget)
        self.BouttonReglage.setEnabled(False)
        self.BouttonReglage.setGeometry(QtCore.QRect(20, 20, 130, 50))
        self.BouttonReglage.setObjectName(_fromUtf8("BouttonReglage"))
        self.BouttoAbout = QtGui.QPushButton(self.centralwidget)
        self.BouttoAbout.setEnabled(False)
        self.BouttoAbout.setGeometry(QtCore.QRect(1250, 20, 130, 50))
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
        self.labelGpuName.setGeometry(QtCore.QRect(159, 0, 400, 80))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.labelGpuName.setFont(font)
        self.labelGpuName.setObjectName(_fromUtf8("labelGpuName"))
        self.labelInfo = QtGui.QLabel(self.centralwidget)
        self.labelInfo.setGeometry(QtCore.QRect(840, 0, 400, 80))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.labelInfo.setFont(font)
        self.labelInfo.setObjectName(_fromUtf8("labelInfo"))
        self.labelGpu = QtGui.QLabel(self.centralwidget)
        self.labelGpu.setGeometry(QtCore.QRect(20, 510, 640, 40))
        self.labelGpu.setObjectName(_fromUtf8("labelGpu"))
        self.labelFan = QtGui.QLabel(self.centralwidget)
        self.labelFan.setGeometry(QtCore.QRect(740, 510, 640, 40))
        self.labelFan.setObjectName(_fromUtf8("labelFan"))
        self.labelTemp = QtGui.QLabel(self.centralwidget)
        self.labelTemp.setGeometry(QtCore.QRect(20, 990, 640, 40))
        self.labelTemp.setObjectName(_fromUtf8("labelTemp"))
        self.labelMemory = QtGui.QLabel(self.centralwidget)
        self.labelMemory.setGeometry(QtCore.QRect(740, 990, 640, 40))
        self.labelMemory.setObjectName(_fromUtf8("labelMemory"))
        self.bouttonExport = QtGui.QPushButton(self.centralwidget)
        self.bouttonExport.setGeometry(QtCore.QRect(710, 20, 120, 50))
        self.bouttonExport.setObjectName(_fromUtf8("bouttonExport"))
        self.BouttonGpu = QtGui.QPushButton(self.centralwidget)
        self.BouttonGpu.setEnabled(False)
        self.BouttonGpu.setGeometry(QtCore.QRect(570, 20, 120, 50))
        self.BouttonGpu.setObjectName(_fromUtf8("BouttonGpu"))
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
        self.labelGpu.setText(_translate("MainWindow", "GPU", None))
        self.labelFan.setText(_translate("MainWindow", "Fan", None))
        self.labelTemp.setText(_translate("MainWindow", "Temperature", None))
        self.labelMemory.setText(_translate("MainWindow", "Memory", None))
        self.bouttonExport.setText(_translate("MainWindow", "Export", None))
        self.BouttonGpu.setText(_translate("MainWindow", "Select\n"
"Gpu", None))

from pyqtgraph import PlotWidget
