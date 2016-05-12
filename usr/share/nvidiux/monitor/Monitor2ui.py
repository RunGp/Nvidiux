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
        MainWindow.resize(1413, 975)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.plotGpu = PlotWidget(self.centralwidget)
        self.plotGpu.setGeometry(QtCore.QRect(30, 20, 641, 431))
        self.plotGpu.setObjectName(_fromUtf8("plotGpu"))
        self.plotFan = PlotWidget(self.centralwidget)
        self.plotFan.setGeometry(QtCore.QRect(740, 20, 641, 431))
        self.plotFan.setObjectName(_fromUtf8("plotFan"))
        self.plotTemp = PlotWidget(self.centralwidget)
        self.plotTemp.setGeometry(QtCore.QRect(30, 490, 641, 431))
        self.plotTemp.setObjectName(_fromUtf8("plotTemp"))
        self.plotMem = PlotWidget(self.centralwidget)
        self.plotMem.setGeometry(QtCore.QRect(740, 490, 641, 431))
        self.plotMem.setObjectName(_fromUtf8("plotMem"))
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "Nvidiux Monitor beta 1", None))

from pyqtgraph import PlotWidget
