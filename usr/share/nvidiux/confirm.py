# -*- coding: utf-8 -*-
#!/usr/bin/python2

# Copyright 2014 Payet Guillaume
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

class ConfirmWindow(QWidget):
	acceptedEula = False
	def __init__(self,text,tabLang,nbGpu=1,showEula=True,parent=None):
		super (ConfirmWindow, self).__init__(parent)
		self.nbGpu = nbGpu
		self.language = tabLang[0]
		self.app = tabLang[1]
		self.showEula = showEula
		self.createWidgets(text)
		
	def closeEvent(self, event):
		if not self.acceptedEula:
			self.emit(SIGNAL("reject(PyQt_PyObject)"), "1")
	
	def createWidgets(self,text):
		y = 50 + 120 * self.nbGpu
		self.resize(500, y)
		self.labelInfo = QtGui.QLabel(text,self)
		if text == "":
			self.labelInfo.setText(_translate("nvidiux","Pour utiliser nvidiux vous devez accepter\nle contrat de licence",None))	
		self.labelInfo.move(60,15)
		self.labelInfo.setAlignment(QtCore.Qt.AlignCenter)
		font = QtGui.QFont()
		font.setPointSize(14)
		font.setBold(True)
		font.setWeight(75)
		self.labelInfo.setFont(font)
		font.setStyleStrategy(QtGui.QFont.PreferAntialias)
		self.buttonConfirm = QPushButton("Confirmer",self);
		self.buttonConfirm.move(370,y -40)
		self.buttonCancel = QPushButton("Annuler",self);
		self.buttonCancel.move(50,y - 40)
		if self.showEula:
			self.checkBox = QCheckBox("Je comprend les risques et j'accepte les termes du contrat",self)
			self.checkBox.move(40,435)
			self.checkBox.connect(self.checkBox, SIGNAL("clicked(bool)"),self.acceptEula)
			self.texteula = QPlainTextEdit(self)
			self.texteula.move(0,150)
			self.texteula.resize(520,270)
			self.texteula.setPlainText(_translate("ConfirmWindow","Attention cette pratique peut annuler la garantie du produit et reste à l'entière responsabilité de l'utilisateur du logiciel. Ni le concepteur du logiciel ni la communauté gnu ne pourra pas être tenu responsable de toutes mauvaises manipulations ayant entrainé un quelconque dégât direct ou en conséquence de l'utilisation de Nvidiux.\nNvidiux n'est en aucun cas affilié à Nvidia", None))
			self.texteula.setReadOnly(True)
			self.buttonConfirm.setEnabled(False)
			self.setWindowTitle("Contrat d'utilisation")
		else:
			self.buttonConfirm.setEnabled(True)
			self.setWindowTitle("Confirmatioon changement")
		self.buttonConfirm.connect(self.buttonConfirm, SIGNAL("released()"),self.confirm)
		self.buttonCancel.connect(self.buttonCancel, SIGNAL("released()"),self.quitapp)
		ConfirmTranslator = QtCore.QTranslator()
		if ConfirmTranslator.load("/usr/share/nvidiux/nvidiux_" + self.language):
			self.app.installTranslator(ConfirmTranslator)
			self.retranslateUi()
		
	def quitapp(self):
		self.emit(SIGNAL("reject(PyQt_PyObject)"), "1")
		self.close()
		
	def acceptEula(self,response):
		self.buttonConfirm.setEnabled(response)
		
	def confirm(self):
		self.acceptedEula = True
		self.emit(SIGNAL("accept(PyQt_PyObject)"), "1")
		self.close()
		
	def retranslateUi(self):
		if self.showEula:
			self.setWindowTitle(_translate("ConfirmWindow", "Contrat d'utilisation", None))
			self.checkBox.setText(_translate("ConfirmWindow", "Je comprend les risques et j'accepte les termes du contrat", None))
			self.texteula.setPlainText(_translate("ConfirmWindow","Attention cette pratique peut annuler la garantie du produit et reste à l'entière responsabilité de l'utilisateur du logiciel. Ni le concepteur du logiciel ni la communauté gnu ne pourra pas être tenu responsable de toutes mauvaises manipulations ayant entrainé un quelconque dégât direct ou en conséquence de l'utilisation de Nvidiux.\nNvidiux n'est en aucun cas affilié à Nvidia", None))
			self.labelInfo.setText(_translate("nvidiux","Pour utiliser nvidiux vous devez accepter\nle contrat de licence",None))
		else:
			self.setWindowTitle(_translate("ConfirmWindow", "Confirmation changement", None))
			
		self.buttonConfirm.setText(_translate("ConfirmWindow", "Confirmer", None))
		self.buttonCancel.setText(_translate("ConfirmWindow", "Annuler", None))
