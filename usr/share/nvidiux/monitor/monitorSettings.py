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
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from xml.dom import minidom
from os.path import expanduser
import getpass
import subprocess as sub
import shutil
import os
import platform
import re

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

class Ui_Pref_Monitor(QWidget):
	
	loadTab = 1
	version = ""
	versionStr = ""
	versionPilote = "331:31"
	nbGpuNvidia = 1
	error = -1
	warning = -2
	gpuActivated = 0
	mainWindows = None
	app = None
	listGpuMonitor = []
	tabGpu = []
	language = None
	labelOs = None
	distrib = None
	
	def __init__(self,loadTab,tabParam,mainW,parent=None):
		super (Ui_Pref_Monitor, self).__init__(parent)
		self.loadTab = loadTab
		self.version = tabParam[0]
		self.versionStr = tabParam[1]
		self.nbGpuNvidia = tabParam[2]
		self.tabGpu = tabParam[3]
		self.pref.language = tabParam[4]
		self.app = tabParam[5]
		self.home = expanduser("~")
		self.mainWindows = mainW
		self.setupUi()
		
	def closeEvent(self, event):
		del(self.listGpuMonitor[:])	
	
	def retranslateUi(self):
		self.setWindowTitle(_translate("Pref_Mon", "Settings", None))
		self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabMoniteur), _translate("Pref_Mon", "Monitor", None))
		self.tabWidget.setTabText(self.tabWidget.indexOf(self.about), _translate("Pref_Mon", "About", None))
		self.labelInfo.setText(_translate("Pref_Mon", "Monitor your nvidia gpu\n(C) 2014-2016 Payet Guillaume\nNvidiux monitor is no way affiliated to nvidia\n",None) + _translate("Pref_Mon","Version : ",None) + self.versionStr + " | " + self.labelOs)
		self.buttonLicence.setText(_translate("Pref_Mon", "Licence",None))
		self.buttonDonate.setText(_translate("Pref_Mon", "Make a donation",None))
		self.buttonThanks.setText(_translate("Pref_Mon", "Thanks to",None)) 
		
	def saveMonitorConf(self):

		fileToSave = minidom.Document()
		racine = fileToSave.createElement("nvidiux")
		fileToSave.appendChild(racine)
		version = fileToSave.createElement('version')
		text = fileToSave.createTextNode(self.versionStr)
		version.appendChild(text)
		racine.appendChild(version)
		update = fileToSave.createElement('update')
		text = fileToSave.createTextNode(str(self.updateC))
		update.appendChild(text)
		racine.appendChild(update)
		i = 0
		for gpu in self.tabGpu:
			gpuElem = fileToSave.createElement('gpu')
			idGpu = fileToSave.createElement('id')
			text = fileToSave.createTextNode(str(i))
			idGpu.appendChild(text)
			gpuElem.appendChild(idGpu)
			colorGpu = fileToSave.createElement('color')
			pColor = self.listButtonColor[i].palette().color(1)
			text = fileToSave.createTextNode(str(pColor.getRgb()[0]) + ":" + str(pColor.getRgb()[1]) + ":" + str(pColor.getRgb()[2]))
			colorGpu.appendChild(text)
			gpuElem.appendChild(colorGpu)
			showGpu = fileToSave.createElement('show')
			text = fileToSave.createTextNode(str(self.listCheckBoxGpu[i].isChecked()))
			showGpu.appendChild(text)
			gpuElem.appendChild(showGpu)
			racine.appendChild(gpuElem)
			i = i + 1
		try:	
			filexml = open(expanduser("~") + "/.nvidiux/monitor.xml", "w")
			filexml.write(fileToSave.toprettyxml())
			filexml.close()
		except:
			return 1
		return 0

	def setupUi(self):
		self.setObjectName(_fromUtf8("Pref_Mon"))
		self.resize(580, 540)
		self.setFixedSize(580, 540)
		
		self.tabWidget = QtGui.QTabWidget(self)
		self.tabWidget.setGeometry(QtCore.QRect(0, 0, 600, 540))
		self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
		
		self.tabMoniteur = QtGui.QWidget()
		self.tabMoniteur.setObjectName(_fromUtf8("tabMoniteur"))
		self.tabWidget.addTab(self.tabMoniteur, _fromUtf8(""))
		
		gpuInfo = []
		ndiFile = None
		try:
			profileFile = open(expanduser("~") + "/.nvidiux/monitor.xml", "r")
			ndiFile = minidom.parse(profileFile)
		except:
			print "Monitor conf file missing"
			
		if ndiFile != None:
			versionElement = ndiFile.getElementsByTagName('version')
			updateCo = ndiFile.getElementsByTagName('update')
			if updateCo != []:
				if updateCo[0].firstChild.nodeValue == "False":
					self.updateC = False
				else:
					self.updateC = True
			else:
				self.updateC = True
			itemlist = ndiFile.getElementsByTagName('gpu')
			errorCode = 0
			if len(itemlist) > 0:
				for item in itemlist:
					if item.hasChildNodes():
						for value in item.childNodes:
							if value.nodeType == minidom.Node.ELEMENT_NODE:
								gpuInfo.append(value.firstChild.nodeValue)
							error = False
						
						self.listGpuMonitor.append(gpuInfo)
						gpuInfo = []
		else:
			i = 0
			for gpu in self.tabGpu:
				gpuInfo.append(str(i))
				gpuInfo.append("255:255:0")
				gpuInfo.append("True")
				self.listGpuMonitor.append(gpuInfo)
				gpuInfo = []
				i = i + 1
		
		self.checkBoxUpdateMon = QtGui.QCheckBox(_translate("Pref_Mon", "Continuous refresh",None),self.tabMoniteur)
		self.checkBoxUpdateMon.setGeometry(QtCore.QRect(10, 20, 340, 20))
		self.checkBoxUpdateMon.setObjectName(_fromUtf8("checkBoxUpdateMon"))
		self.checkBoxUpdateMon.setEnabled(False)
		self.checkBoxUpdateMon.setChecked(True)
		self.groupBoxPrefGpu = QtGui.QGroupBox(self.tabMoniteur)
		self.groupBoxPrefGpu.setGeometry(QtCore.QRect(10, 50, 220, 50 * self.nbGpuNvidia + 5 ))
		self.groupBoxPrefGpu.setStyleSheet(_fromUtf8("QGroupBox \n"
			"{ \n"
			"border: 1px solid SlateGrey;\n"
			"border-radius: 10px;\n"
			"}"))
		self.groupBoxPrefGpu.setTitle(_fromUtf8(""))
		self.groupBoxPrefGpu.setObjectName(_fromUtf8("groupBoxPrefGpu"))
		self.groupBoxPrefGpu.setEnabled(False)
		
		self.listLabelGpu = list()
		self.listButtonColor = list()
		self.listCheckBoxGpu = list()
		mapperPref = QSignalMapper(self)
		for i in range(0, self.nbGpuNvidia):
			self.listLabelGpu.append(QtGui.QLabel(self.groupBoxPrefGpu))
			self.listLabelGpu[i].setGeometry(QtCore.QRect(10, 5 + i * 50, 150, 20))
			self.listLabelGpu[i].setText(str(i + 1) + ":" + str(self.tabGpu[i].nameGpu))
			checkTemp = QtGui.QCheckBox(self.groupBoxPrefGpu)
			checkTemp.connect(checkTemp,QtCore.SIGNAL("clicked(bool)"),self.stateGpu)
			self.listCheckBoxGpu.append(checkTemp)
			self.listCheckBoxGpu[i].setGeometry(QtCore.QRect(8, 30 + i * 50, 150, 20))
			if self.listGpuMonitor[i][2] == "False":
				self.listCheckBoxGpu[i].setChecked(False)
			else:
				self.listCheckBoxGpu[i].setChecked(True)
				self.gpuActivated = self.gpuActivated + 1
			self.listCheckBoxGpu[i].setText(_translate("Pref_Mon", "See this gpu", None))
			self.listButtonColor.append(QtGui.QPushButton(self.groupBoxPrefGpu))
			self.listButtonColor[i].setGeometry(QtCore.QRect(170, 5 + i * 50, 45, 45))
			self.listButtonColor[i].setEnabled(True)
			self.listButtonColor[i].setStyleSheet("border-radius: 10px;\nbackground-color:rgb(" + self.listGpuMonitor[i][1].replace(":",",") + ")")
			self.listButtonColor[i].connect(self.listButtonColor[i],QtCore.SIGNAL("clicked(bool)"),mapperPref,QtCore.SLOT("map()"))
			mapperPref.setMapping(self.listButtonColor[i],i);
		if self.gpuActivated == 1:
			for i in range(0, self.nbGpuNvidia):
				if self.listCheckBoxGpu[i].isChecked():
					self.listCheckBoxGpu[i].setEnabled(False)
				else:
					self.listCheckBoxGpu[i].setEnabled(True)
					
		#self.connect(mapperPref, SIGNAL("mapped(int)"),self.showColor)	
		self.colorBox = QtGui.QColorDialog(self.groupBoxPrefGpu)
		self.about = QtGui.QWidget()
		self.about.setObjectName(_fromUtf8("about"))
		self.tabWidget.addTab(self.about, _fromUtf8(""))
		self.title = QtGui.QLabel(self.about)
		self.title.move(40,10)
		font = QtGui.QFont()
		font.setPointSize(38)
		font.setBold(True)
		font.setUnderline(False)
		font.setWeight(75)
		font.setStrikeOut(False)
		font.setStyleStrategy(QtGui.QFont.PreferAntialias)
		self.title.setFont(font)
		self.title.setAlignment(QtCore.Qt.AlignCenter)
		self.title.setText("Nvidiux Monitor 2")
		self.labelInfo = QtGui.QLabel(self.about)
		self.labelInfo.move(100,80)
		self.labelInfo.setAlignment(QtCore.Qt.AlignCenter)
		font = QtGui.QFont()
		font.setPointSize(11)
		font.setBold(True)
		font.setWeight(75)
		font.setStyleStrategy(QtGui.QFont.PreferAntialias)
		self.labelInfo.setFont(font)
		
		self.groupBoxAbout = QtGui.QGroupBox(self.about)
		self.groupBoxAbout.setGeometry(QtCore.QRect(190, 160, 220, 95))
		self.groupBoxAbout.setStyleSheet(_fromUtf8("QGroupBox \n"
			"{ \n"
			"border: 2px solid SlateGrey;\n"
			"border-radius: 10px;\n"
			"}"))
		self.groupBoxAbout.setTitle(_fromUtf8(""))
		self.groupBoxAbout.setObjectName(_fromUtf8("groupBoxAbout"))
		
		self.buttonLicence = QtGui.QPushButton(self.groupBoxAbout)
		self.buttonLicence.setGeometry(QtCore.QRect(5, 5, 105, 40))
		self.buttonLicence.setObjectName(_fromUtf8("buttonLicence"))
		self.buttonLicence.setEnabled(False)
		
		self.buttonDonate = QtGui.QPushButton(self.groupBoxAbout)
		self.buttonDonate.setGeometry(QtCore.QRect(110, 5, 105, 40))
		self.buttonDonate.setObjectName(_fromUtf8("buttonDonate"))
		self.buttonDonate.setEnabled(False)
		self.buttonDonate.setVisible(False)
		
		self.buttonThanks = QtGui.QPushButton(self.groupBoxAbout)
		self.buttonThanks.setGeometry(QtCore.QRect(5, 50, 210, 40))
		self.buttonThanks.setObjectName(_fromUtf8("buttonThanks"))
		self.buttonThanks.setEnabled(True)
		
		self.buttonLicence.setText(_translate("Pref_Mon", "Licence",None))
		self.buttonDonate.setText(_translate("Pref_Mon", "Make a donation",None))
		self.buttonThanks.setText(_translate("Pref_Mon", "Thanks to...",None)) 
		
		try:
			self.linuxDistrib = platform.linux_distribution()
			if self.linuxDistrib == ('', '', ''):
				if os.path.isfile("/etc/issue"):
					with open("/etc/issue") as f:
						self.labelOs = f.read().split()[0] + " " + platform.architecture()[0]
				else:
					self.labelOs = "Unknow distrib " + platform.architecture()[0]
			else:
				self.labelOs =  self.linuxDistrib[0] + " " + self.linuxDistrib[1]
		except:
			self.labelOs = ""
		info = _translate("Pref_Mon", "Monitor your nvidia gpu\n(C) 2014-2016 Payet Guillaume\nNvidiux monitor is no way affiliated to nvidia",None) + _translate("Pref_Mon","Version:",None) + self.versionStr + " | " + self.labelOs 
		self.labelInfo.setText(info)
		self.textBrowser = QtGui.QTextBrowser(self.about)
		self.textBrowser.setGeometry(QtCore.QRect(10, 280, 560, 240))
		self.textBrowser.setAlignment(QtCore.Qt.AlignCenter)
		
		if os.path.isfile("/usr/share/nvidiux/licences/gpl-3.0_" + self.pref.language + ".txt"):
			txtFile = open("/usr/share/nvidiux/licences/gpl-3.0_" + self.pref.language + ".txt", "r")
			self.textBrowser.setText(_fromUtf8(txtFile.read()))
		elif os.path.isfile("/usr/share/nvidiux/licences/gpl-3.0.txt"):
			txtFile = open('/usr/share/nvidiux/licences/gpl-3.0.txt', 'r')
			self.textBrowser.setText(_fromUtf8(txtFile.read()))
		else:
			self.textBrowser.setText(_fromUtf8("Program share under license GPL V3\nSee http://www.gnu.org/licenses/gpl-3.0.txt"))	
		
		#self.checkBoxUpdateMon.connect(self.checkBoxUpdateMon,QtCore.SIGNAL("clicked(bool)"),self.setUpdateContin)
		self.buttonLicence.connect(self.buttonLicence,SIGNAL("released()"),self.showLicence)
		self.buttonDonate.connect(self.buttonDonate,SIGNAL("released()"),self.showDonate)
		self.buttonThanks.connect(self.buttonThanks,SIGNAL("released()"),self.showT)
		self.setWindowTitle(_translate("Pref_Mon", "Settings", None))
		self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabMoniteur), _translate("Pref_Mon", "Monitor", None))
		self.tabWidget.setTabText(self.tabWidget.indexOf(self.about), _translate("Pref_Mon", "About", None))
		
		prefTranslator = QtCore.QTranslator()
		if prefTranslator.load("/usr/share/nvidiux/nvidiux_" + self.pref.language):
			self.app.installTranslator(prefTranslator)
			self.retranslateUi()
		self.tabWidget.setCurrentIndex(self.loadTab)

	def showLicence(self):
		self.buttonThanks.setEnabled(True)
		self.buttonLicence.setEnabled(False)
		if os.path.isfile("/usr/share/nvidiux/licences/gpl-3.0_" + self.pref.language + ".txt"):
			txtFile = open("/usr/share/nvidiux/licences/gpl-3.0_" + self.pref.language + ".txt", "r")
			self.textBrowser.setText(_fromUtf8(txtFile.read()))
		elif os.path.isfile("/usr/share/nvidiux/licences/gpl-3.0.txt"):
			txtFile = open('/usr/share/nvidiux/licences/gpl-3.0.txt', 'r')
			self.textBrowser.setText(_fromUtf8(txtFile.read()))
		else:
			self.textBrowser.setText(_fromUtf8(_translate("Pref_Mon", "Program sharing under GPL V3 license \nSee http://www.gnu.org/licenses/gpl-3.0.txt"),None))	
		
	def showT(self):
		self.buttonLicence.setEnabled(True)
		self.buttonThanks.setEnabled(False)
		self.textBrowser.setText(_fromUtf8(_translate("Pref_Mon","Special thanks to\n - @mglinux for german translation\n - @profesorfalken for spanish translation\n - @gaara @bishop @gfx @jul974 for testing and help for debug",None)))
		
	def showDonate(self):
		import webbrowser
		url = "http://docs.python.org/library/webbrowser.html"
		webbrowser.open(url,new=2)
	
	def showError(self,errorCode,title,errorMsg,etype):
		if etype == self.error:
			errorMsg = errorMsg + "\nError Code:" + str(errorCode)
			QMessageBox.critical(self, _fromUtf8(title),_fromUtf8(errorMsg))
		elif etype == self.warning:
			QMessageBox.warning(self, _fromUtf8(title),_fromUtf8(errorMsg))	
		else:
			QMessageBox.information(self, _fromUtf8(title),_fromUtf8(errorMsg))
		return errorCode
		
	def stateGpu(self,value):
		if value:
			self.gpuActivated = self.gpuActivated + 1
		else:
			self.gpuActivated = self.gpuActivated - 1
		if self.gpuActivated == 1:
			for i in range(0, self.nbGpuNvidia):
				if self.listCheckBoxGpu[i].isChecked():
					self.listCheckBoxGpu[i].setEnabled(False)
				else:
					self.listCheckBoxGpu[i].setEnabled(True)
