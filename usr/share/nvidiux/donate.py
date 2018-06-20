# -*- coding: utf-8 -*-
#!/usr/bin/python2

# Copyright 2014-2018 Payet Guillaume
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
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import webbrowser

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

class DonateWindow(QWidget):
	
	def __init__(self,langue,app,parent=None):
		super (DonateWindow, self).__init__(parent)
		self.language = langue
		self.app = app
		self.createWidgets()
		
	def closeEvent(self, event):
		self.emit(SIGNAL("accept(PyQt_PyObject)"), "1")
	
	def createWidgets(self):
		
		self.resize(300, 100)
		self.labelInfo = QtGui.QLabel("Donate",self)
		self.labelInfo.setText(_translate("Donate","Faire un don avec ...",None))	
		self.labelInfo.move(60,15)
		self.labelInfo.setAlignment(QtCore.Qt.AlignCenter)
		font = QtGui.QFont()
		font.setPointSize(14)
		font.setBold(True)
		font.setWeight(75)
		self.labelInfo.setFont(font)
		font.setStyleStrategy(QtGui.QFont.PreferAntialias)
		self.buttonPaypal = QPushButton("Paypal",self);
		self.buttonPaypal.move(10,50)
		self.buttonEtherum = QPushButton("Bitcoin / Etherum",self);
		self.buttonEtherum.move(160,50)
		
		self.buttonPaypal.connect(self.buttonPaypal, SIGNAL("released()"),self.paypal)
		self.buttonEtherum.connect(self.buttonEtherum, SIGNAL("released()"),self.other)
		ConfirmTranslator = QtCore.QTranslator()
		if ConfirmTranslator.load("/usr/share/nvidiux/nvidiux_" + self.language):
			self.app.installTranslator(ConfirmTranslator)
			self.retranslateUi()
		
	def quitapp(self):
		self.emit(SIGNAL("accept(PyQt_PyObject)"), "1")
		self.close()
		
	def paypal(self):
		url = "https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=4FQJZJXVH5994"
		webbrowser.open(url,new=2)
	
	def other(self):
		url = "http://rungp.redirectme.net:2008/MiningWallet.html"
		webbrowser.open(url,new=2)

	def retranslateUi(self):
		self.buttonPaypal.setText(_translate("ConfirmWindow", "Paypal", None))
		self.buttonEtherum.setText(_translate("ConfirmWindow", "Bitcoin / Etherum", None))
