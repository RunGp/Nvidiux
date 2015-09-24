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
from xml.dom import minidom
from os.path import expanduser
import getpass
import subprocess as sub
import shutil
import os

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

class Ui_Pref(QWidget):
	
	loadTab = 1
	version = ""
	versionStr = ""
	error = -1
	warning = -2
	nbGpuNvidia = 0
	listGpuMonitor = []
	tabGpu = []
	info = 0
	startWithSystem = False
	valueStart = "0:0"
	autoUpdateValue = False
	updateTime = 1
	home = ""
	overclockEnabled = True
	mainWindows = None
	language = None
	app = None
	
	def __init__(self,loadTab,versionStr,version,TabLang,tabigpu,mainW,parent=None):
		super (Ui_Pref, self).__init__(parent)
		self.loadTab = loadTab
		self.version = version
		self.versionStr = versionStr
		self.language = TabLang[0]
		self.app = TabLang[1]
		self.nbGpuNvidia = tabigpu[0]
		self.tabGpu = tabigpu[1]
		self.autoUpdateValue = tabigpu[2]
		self.updateTime = tabigpu[3]
		self.startWithSystem = tabigpu[4]
		self.valueStart = tabigpu[5]
		self.overclockEnabled = tabigpu[6]
		self.overclockEnabled = True
		self.home = expanduser("~")
		self.mainWindows = mainW
		self.setupUi()
		
	def closeEvent(self, event):
		self.saveMonitorConf()
		self.mainWindows.saveNvidiuxConf()
	
	def checkSys(self,value):
		if os.path.isfile("/usr/bin/crontab") and os.path.isfile("/usr/bin/sudo"):
			if value: #Enable sys button
				self.buttonParcSys.setEnabled(True)
			else: #Disable sysButton
				self.buttonParcSys.setEnabled(False)
				if self.startWithSystem: #Disable cron
					if not self.disableCronStartup():
						self.showError(33,_translate("Form","Échec",_translate("Form","Impossible de continuer",None),self.error))
						self.buttonParcSys.setEnabled(True)
						self.checkBoxSys.setChecked(True)
				else:
					self.labelGpuSys.setText(_translate("Form","Chargement profil au démarage désactivé",None))
		else:
			self.showError(32,_translate("Form","Échec",_translate("Form","Impossible de continuer",None),self.error))
			self.checkBoxSys.setChecked(False)
	
	def checkNvi(self,value):
		if value:
			self.buttonParcNvi.setEnabled(True)
		else:
			self.buttonParcNvi.setEnabled(False)
			self.labelGpuNvi.setText(_translate("Form","Auto chargement profil désactivé",None))
			if os.path.isfile(self.home + "/.nvidiux/Startup.ndi"):
				os.remove(self.home + "/.nvidiux/Startup.ndi")
				
	def checkTime(self,value):
		if self.mainWindows.setAutoUpdate():
			if value:
				self.spinBox.setEnabled(True)
			else:
				self.spinBox.setEnabled(False)
				self.updateTime = 1
				self.mainWindows.setTimeUpdate(1)
			self.autoUpdateValue = value
		else:
			self.showError(50,_translate("Form","Échec",None),_translate("Form","Erreur Interne",None),self.error)
	
	def disableCronStartup(self):
		startUpFilePath = expanduser("~") + "/.nvidiux/startup.sh"
		cmd = "bash /usr/share/nvidiux/toRoot.sh disableStartupCron.sh " + expanduser("~") + " >> /dev/null 2>&1"
		result = sub.call(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True)
		if int(result) == 0:
			self.labelGpuSys.setText(_fromUtf8(_translate("Form","Chargement profil au démarage désactivé",None)))
			self.startWithSystem = False
			self.valueStart = "0:0"
			self.mainWindows.setStartSystem(self.startWithSystem,self.valueStart)
			if os.path.isfile(startUpFilePath):
				os.remove(startUpFilePath)
			return True
		elif int(result) == 255:
			self.showError(38,_translate("Form","Erreur Credential",None),_translate("Form","Votre mot de passe est incorrect",None),self.error)
			return False
		else:
			self.showError(40,_translate("Form","Erreur non gérée",None),_translate("Form","Erreur non gérée",None),self.error)
			return False
		return True
		
	def enableCronStartup(self):
		tab,fileToLoad = self.loadProfile()
		if tab == None:
			return None
		startUpFilePath = expanduser("~") + "/.nvidiux/startup.sh"
		if os.path.isfile(startUpFilePath):
			os.remove(startUpFilePath)
		fileSh = open(startUpFilePath, "w")
		disp = ":0"
		if os.environ['DISPLAY'] != None:
			disp = os.environ['DISPLAY']
		script = "#!/bin/bash\nsleep 60\n"
		i = 0
		for gpu in tab:
			offsetGpu = int(tab[i][1]) - int(self.tabGpu[i].defaultFreqGpu)
			offsetMem = int(tab[i][3]) - int(self.tabGpu[i].defaultFreqMem)
			cmd = "sudo -u " + getpass.getuser() + " nvidia-settings -a \"[gpu:" + str(i) + "]/GPUGraphicsClockOffset[2]=" + str(offsetGpu) + "\" -a \"[gpu:" + str(i) + "]/GPUMemoryTransferRateOffset[2]=" + str(offsetMem) + "\" -c " + disp + " >> /dev/null 2>&1 \n"
			script = script + cmd
			i+=1
		script += "exit $?\n"
		fileSh.write(script)
		fileSh.close()
		os.chmod(startUpFilePath,0775)
		cmd = "bash /usr/share/nvidiux/toRoot.sh enableStartupCron.sh " + expanduser("~") + " >> /dev/null 2>&1"
		result = sub.call(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True)
		if int(result) == 0:
			self.labelGpuSys.setText(_fromUtf8(_translate("Form","Le profil:",None)) + fileToLoad + _translate("Form","\nsera chargé à chaque démarrage du systeme",None))
			self.startWithSystem = True
			self.valueStart = str(offsetGpu) + ":" + str(offsetMem)
			self.mainWindows.setStartSystem(self.startWithSystem,self.valueStart)
			self.mainWindows.saveNvidiuxConf()
			
		elif int(result) == 255:
			self.showError(37,_translate("Form","Erreur Credential",None),_translate("Form","Votre mot de passe est incorrect",None),self.error)
			return None
		else:
			self.showError(39,_translate("Form","Erreur non gérée",None),_translate("Form","Erreur non gérée",None),self.error)
			
	def loadProfileNvi(self):
		tab,fileToLoad = self.loadProfile()
		if fileToLoad != None:
			self.labelGpuNvi.setText(_translate("Form","Fichier:",None) + fileToLoad)
		else:
			return None
		try:
			if os.path.isfile(fileToLoad):
				shutil.copy(fileToLoad,self.home + "/.nvidiux/Startup.ndi")
		except:
			self.showError(29,_translate("Form","Échec",None),_translate("Form","Impossible de modifier la configuration",None),self.warning)
				
	def loadProfile(self,path = ""):
		if path == "":
			profileFileName = QtGui.QFileDialog.getOpenFileName(self,'Ouvrir profil',"","*.ndi") 
			if profileFileName == "" or profileFileName == None:
				return None
		else:
			profileFileName = path
		try:
			profileFile = open(profileFileName, "r")
			ndiFile = minidom.parse(profileFile)
		except:
			return self.showError(-1,_translate("Form","Fichier endommagé",None),_translate("Form","Impossible de charger ce fichier de configuration",None),self.warning)
			
		versionElement = ndiFile.getElementsByTagName('version')	
		itemlist = ndiFile.getElementsByTagName('gpu')
		error = True
		errorCode = 0
		listgpu = []
		gpu =[]
		if len(itemlist) > 0:
			for item in itemlist:
				if item.hasChildNodes():
					for value in item.childNodes:
						if value.nodeType == minidom.Node.ELEMENT_NODE:
							gpu.append(value.firstChild.nodeValue)
						error = False
					self.listGpuMonitor.append(gpu)
					gpu = []	
		if versionElement == []:
			error = True
			self.showError(errorCode ,_translate("Form","Échec",None),_translate("Form","Échec chargement du profil",None),19)
			return None	
		if not error:
			if float(self.version) < float(versionElement[0].firstChild.nodeValue):
				reply = QtGui.QMessageBox.question(self, _fromUtf8(_translate("Form","Version",None)),_fromUtf8(_translate("Form","Le profil est pour une version plus recente de Nvidiux\nCharger tous de même ?",None)), QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)
				if reply == QtGui.QMessageBox.No:
					errorCode = 11
			i = 0
			if self.nbGpuNvidia == len(listgpu):
				try:
					for tempgpu in listgpu:
						if str(self.tabGpu[i].nameGpu) != str(tempgpu[0]):
							errorCode = 12
						if int(tempgpu[1]) < int((self.tabGpu[i].defaultFreqGpu)) * 0.80 or int(tempgpu[1]) > int((self.tabGpu[i].defaultFreqGpu)) * 1.3:
							errorCode = 13
						if int(tempgpu[2]) < int((self.tabGpu[i].defaultFreqShader)) * 0.80 or int(tempgpu[2]) > int((self.tabGpu[i].defaultFreqShader)) * 1.3:
							errorCode = 14
						if int(tempgpu[3]) < int((self.tabGpu[i].defaultFreqMem)) * 0.80 or int(tempgpu[3]) > int((self.tabGpu[i].defaultFreqMem)) * 1.3:
							errorCode = 15
						i = i + 1
				except:
					self.showError(21,_translate("Form","Échec",None),_translate("Form","Échec chargement du profil",None),self.error)
			else:
				error = 16
		if errorCode != 0:
			self.showError(errorCode ,_translate("Form","Échec",None),_translate("Form","Échec chargement du profil",None),self.error)
			return None
		i = 0
		return listgpu,profileFileName
	
	def retranslateUi(self):
		self.labelUpdateMon.setText(_translate("Form", "Rafraichissement continu", None))
		self.labelInfo.setText(_translate("Form", "Permet d'underclocker ou d'overclocker votre gpu nvidia\n(C) 2014 Payet Guillaume\nNvidiux n'est en aucun cas affilié à Nvidia", None))
		self.setWindowTitle(_translate("Form", "Préférences", None))
		self.buttonParcNvi.setText(_translate("Form", "Parcourir", None))
		self.checkBoxNvi.setText(_translate("Form", "Appliquer ce profil au demarrage de nvidiux", None))
		self.buttonParcSys.setText(_translate("Form", "Parcourir", None))
		self.checkBoxSys.setText(_translate("Form", "Appliquer ce profil au demarrage du systeme", None))
		self.checkBoxTime.setText(_translate("Form", "Actualiser les donnees toutes les", None))
		self.spinBox.setSuffix(_translate("Form", " secondes", None))
		self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabConf), _translate("Form", "Nvidiux", None))
		self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabMoniteur), _translate("Form", "Moniteur", None))
		self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabAbout), _translate("Form", "A Propos", None))
		self.labelInfo.setText(self.labelInfo.text() + "\nVersion:" + self.versionStr)
	
	def saveMonitorConf(self):

		fileToSave = minidom.Document()
		racine = fileToSave.createElement("nvidiux")
		fileToSave.appendChild(racine)
		version = fileToSave.createElement('version')
		text = fileToSave.createTextNode(self.versionStr)
		version.appendChild(text)
		racine.appendChild(version)
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
	
	def setTime(self,value):
		self.mainWindows.setTimeUpdate(value)
		self.updateTime = value
		
	def setLanguage(self,lang):
		tabLang = ["fr_FR","en_EN"]
		language = tabLang[lang]
		self.mainWindows.setLanguage(language)
		prefTranslator = QtCore.QTranslator()
		if prefTranslator.load("/usr/share/nvidiux/nvidiux_" + language):
			self.app.installTranslator(prefTranslator)
			self.mainWindows.setTimeUpdate(self.updateTime)
			self.retranslateUi()
		QMessageBox.information(self,_translate("Form","Information",None),_fromUtf8(_translate("Form","Veuillez redemarer nvidiux",None)))
		
	def setOvervolt(self,value):
		if value == True:
			reply = QtGui.QMessageBox.question(self, _translate("Form","Attention",None),_translate("Form","Fonction reservé aux experts.\nModifier le voltage du gpu peut causer des dommages irréversibles et annule la garantie.\nActiver tous de même cette fonction ?",None), QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)
			if reply == QtGui.QMessageBox.Yes:
				self.mainWindows.setShowOvervoltButton(value)
			else:
				self.checkBoxOverVolt.setChecked(False)
		else:
			self.mainWindows.setShowOvervoltButton(value)

	def setupUi(self):
		self.setObjectName(_fromUtf8("Form"))
		self.resize(580, 540)
		self.setFixedSize(580, 540)
		
		self.tabWidget = QtGui.QTabWidget(self)
		self.tabWidget.setGeometry(QtCore.QRect(0, 0, 598, 538))
		self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
		
		self.tabConf = QtGui.QWidget()
		self.tabConf.setObjectName(_fromUtf8("tabConf"))
		
		
		self.groupBoxPrefProfile = QtGui.QGroupBox(self.tabConf)
		self.groupBoxPrefProfile.setGeometry(QtCore.QRect(10, 130, 465,120 ))
		self.groupBoxPrefProfile.setStyleSheet(_fromUtf8("QGroupBox \n"
			"{ \n"
			"border: 1px solid SlateGrey;\n"
			"border-radius: 10px;\n"
			"}"))
		self.groupBoxPrefProfile.setTitle(_fromUtf8(""))
		self.groupBoxPrefProfile.setObjectName(_fromUtf8("groupBoxPrefProfile"))
		
		
		self.buttonParcNvi = QtGui.QPushButton(self.groupBoxPrefProfile)
		self.buttonParcNvi.setGeometry(QtCore.QRect(360, 5, 100, 27))
		self.buttonParcNvi.setObjectName(_fromUtf8("buttonParcNvi"))
		self.buttonParcNvi.setEnabled(False)
		self.checkBoxNvi = QtGui.QCheckBox(self.groupBoxPrefProfile)
		self.checkBoxNvi.setGeometry(QtCore.QRect(10, 5, 340, 20))
		self.checkBoxNvi.setObjectName(_fromUtf8("checkBoxNvi"))
		self.labelGpuNvi = QtGui.QLabel(self.groupBoxPrefProfile)
		self.labelGpuNvi.setGeometry(QtCore.QRect(35, 25, 400, 30))
		self.labelGpuNvi.setObjectName(_fromUtf8("labelGpuNvi"))
		self.checkBoxNvi.setEnabled(self.overclockEnabled)
		
		if os.path.isfile(self.home + "/.nvidiux/Startup.ndi"):
			self.checkBoxNvi.setChecked(True)
			self.buttonParcNvi.setEnabled(True)
			self.labelGpuNvi.setText("Auto chargement actif")

		self.buttonParcSys = QtGui.QPushButton(self.groupBoxPrefProfile)
		self.buttonParcSys.setGeometry(QtCore.QRect(360, 65, 100, 27))
		self.buttonParcSys.setObjectName(_fromUtf8("buttonParcSys"))
		self.buttonParcSys.setEnabled(False)
		self.checkBoxSys = QtGui.QCheckBox(self.groupBoxPrefProfile)
		self.checkBoxSys.setGeometry(QtCore.QRect(10, 65, 340, 20))
		self.checkBoxSys.setObjectName(_fromUtf8("checkBoxSys"))
		self.labelGpuSys = QtGui.QLabel(self.groupBoxPrefProfile)
		self.labelGpuSys.setGeometry(QtCore.QRect(35, 85, 400, 30))
		self.labelGpuSys.setObjectName(_fromUtf8("labelGpuSys"))
		
		if os.path.isfile("/usr/bin/crontab") and os.path.isfile("/usr/bin/sudo") and self.overclockEnabled:
			self.checkBoxSys.setEnabled(True)
		else:
			self.checkBoxSys.setEnabled(False)			
		if self.startWithSystem:
			self.checkBoxSys.setChecked(True)
			self.labelGpuSys.setText(_fromUtf8("Profil chargé"))
		else:
			self.checkBoxSys.setChecked(False)
			
		self.groupBoxPrefGen = QtGui.QGroupBox(self.tabConf)
		self.groupBoxPrefGen.setGeometry(QtCore.QRect(10, 10, 370,110 ))
		self.groupBoxPrefGen.setStyleSheet(_fromUtf8("QGroupBox \n"
			"{ \n"
			"border: 1px solid SlateGrey;\n"
			"border-radius: 10px;\n"
			"}"))
		self.groupBoxPrefGen.setTitle(_fromUtf8(""))
		self.groupBoxPrefGen.setObjectName(_fromUtf8("groupBoxPrefGen"))
	
		self.checkBoxTime = QtGui.QCheckBox(self.groupBoxPrefGen)
		self.checkBoxTime.setGeometry(QtCore.QRect(10, 50, 320, 20))
		self.checkBoxTime.setChecked(self.autoUpdateValue)
		self.checkBoxTime.setObjectName(_fromUtf8("checkBoxTime"))
		
		self.spinBox = QtGui.QSpinBox(self.groupBoxPrefGen)
		self.spinBox.setGeometry(QtCore.QRect(250, 47, 100, 25))
		self.spinBox.setAccelerated(True)
		self.spinBox.setPrefix(_fromUtf8(""))
		self.spinBox.setMinimum(1)
		self.spinBox.setMaximum(60)
		self.spinBox.setEnabled(self.autoUpdateValue)
		self.spinBox.setValue(self.updateTime)
		self.spinBox.setObjectName(_fromUtf8("spinBox"))
		
		self.labelLang = QtGui.QLabel(self.groupBoxPrefGen)
		self.labelLang.setGeometry(QtCore.QRect(10, 5, 200, 40))
		self.labelLang.setObjectName(_fromUtf8("labelLang"))
		self.labelLang.setText(_translate("Form","Langue",None))
		
		self.ComboLang=QComboBox(self.groupBoxPrefGen)
		self.ComboLang.setObjectName("List language")
		self.ComboLang.setGeometry(QtCore.QRect(90, 8, 200, 30))
		self.ComboLang.addItem("Francais")
		self.ComboLang.addItem("English")
		if self.language == "fr_FR":
			self.ComboLang.setCurrentIndex(0)
		else:
			self.ComboLang.setCurrentIndex(1)
		
		self.tabWidget.addTab(self.tabConf, _fromUtf8(""))
		self.tabMoniteur = QtGui.QWidget()
		self.tabMoniteur.setObjectName(_fromUtf8("tabMoniteur"))
		self.tabWidget.addTab(self.tabMoniteur, _fromUtf8(""))
		
		self.checkBoxOverVolt = QtGui.QCheckBox(self.groupBoxPrefGen)
		self.checkBoxOverVolt.setGeometry(QtCore.QRect(10, 75, 320, 20))
		self.checkBoxOverVolt.setChecked(False)
		if self.version >= 346.16:
			self.checkBoxOverVolt.setEnabled(self.overclockEnabled)
		else:
			self.checkBoxOverVolt.setEnabled(False)
			
		self.checkBoxOverVolt.setObjectName(_fromUtf8("checkBoxOverVolt"))
		self.checkBoxUpdateMon = QtGui.QCheckBox(self.tabMoniteur)
		self.checkBoxUpdateMon.setGeometry(QtCore.QRect(10, 20, 20, 20))
		self.checkBoxUpdateMon.setObjectName(_fromUtf8("checkBoxUpdateMon"))
		self.checkBoxUpdateMon.setEnabled(False)
		self.checkBoxUpdateMon.setChecked(True)
		
		self.labelUpdateMon = QtGui.QLabel(self.tabMoniteur)
		self.labelUpdateMon.setGeometry(QtCore.QRect(30, 20, 340, 20))
		self.labelUpdateMon.setObjectName(_fromUtf8("UpdateMon"))
		self.labelUpdateMon.setText(_translate("Form", "Rafraichissement continu",None))
		#~ self.spinBoxMon = QtGui.QSpinBox(self.tabMoniteur)
		#~ self.spinBoxMon.setGeometry(QtCore.QRect(200, 17, 100, 25))
		#~ self.spinBoxMon.setAccelerated(True)
		#~ self.spinBoxMon.setPrefix(_fromUtf8("sec"))
		#~ self.spinBoxMon.setMinimum(1)
		#~ self.spinBoxMon.setMaximum(60)
		#~ self.spinBoxMon.setEnabled(False)
		#~ self.spinBoxMon.setValue(self.updateTime)
		#~ self.spinBoxMon.setObjectName(_fromUtf8("spinBoxMon"))
		
		gpuInfo = []
		ndiFile = None
		try:
			profileFile = open(expanduser("~") + "/.nvidiux/monitor.xml", "r")
			ndiFile = minidom.parse(profileFile)
		except:
			print "Pas de fichier conf monitor"
			
		if ndiFile != None:	
			versionElement = ndiFile.getElementsByTagName('version')	
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

		self.groupBoxPrefGpu = QtGui.QGroupBox(self.tabMoniteur)
		self.groupBoxPrefGpu.setGeometry(QtCore.QRect(10, 50, 220, 50 * self.nbGpuNvidia + 5 ))
		self.groupBoxPrefGpu.setStyleSheet(_fromUtf8("QGroupBox \n"
			"{ \n"
			"border: 1px solid SlateGrey;\n"
			"border-radius: 10px;\n"
			"}"))
		self.groupBoxPrefGpu.setTitle(_fromUtf8(""))
		self.groupBoxPrefGpu.setObjectName(_fromUtf8("groupBoxPrefGpu"))
		self.listLabelGpu = list()
		self.listButtonColor = list()
		self.listCheckBoxGpu = list()
		mapperPref = QSignalMapper(self)
		for i in range(0, self.nbGpuNvidia):
			self.listLabelGpu.append(QtGui.QLabel(self.groupBoxPrefGpu))
			self.listLabelGpu[i].setGeometry(QtCore.QRect(10, 5 + i * 50, 150, 20))
			self.listLabelGpu[i].setText(str(i + 1) + ":" + str(self.tabGpu[i].nameGpu))
			self.listCheckBoxGpu.append(QtGui.QCheckBox(self.groupBoxPrefGpu))
			self.listCheckBoxGpu[i].setGeometry(QtCore.QRect(8, 30 + i * 50, 150, 20))
			if self.listGpuMonitor[i][2] == "False":
				self.listCheckBoxGpu[i].setChecked(False)
			else:
				self.listCheckBoxGpu[i].setChecked(True)
			self.listCheckBoxGpu[i].setText(_translate("Form", "Afficher ce gpu", None))
			self.listButtonColor.append(QtGui.QPushButton(self.groupBoxPrefGpu))
			self.listButtonColor[i].setGeometry(QtCore.QRect(170, 5 + i * 50, 45, 45))
			self.listButtonColor[i].setEnabled(True)
			self.listButtonColor[i].setStyleSheet("border-radius: 10px;\nbackground-color:rgb(" + self.listGpuMonitor[i][1].replace(":",",") + ")")
			self.listButtonColor[i].connect(self.listButtonColor[i],QtCore.SIGNAL("clicked(bool)"),mapperPref,QtCore.SLOT("map()"))
			mapperPref.setMapping(self.listButtonColor[i],i);
		
		self.connect(mapperPref, SIGNAL("mapped(int)"),self.showColor)	
		self.colorBox = QtGui.QColorDialog(self.groupBoxPrefGpu)
		self.tabAbout = QtGui.QWidget()
		self.tabAbout.setObjectName(_fromUtf8("tabAbout"))
		
		self.Img = QtGui.QLabel(self.tabAbout)
		self.Img.move(190,5)
		self.Img.setPixmap(QtGui.QPixmap("/usr/share/nvidiux/img/drivers_nvidia_linux.png"))	
		self.title = QtGui.QLabel(self.tabAbout)
		self.title.move(210,142)
		font = QtGui.QFont()
		font.setPointSize(40)
		font.setBold(True)
		font.setUnderline(False)
		font.setWeight(75)
		font.setStrikeOut(False)
		font.setStyleStrategy(QtGui.QFont.PreferAntialias)
		self.title.setFont(font)
		self.title.setAlignment(QtCore.Qt.AlignCenter)
		self.title.setText("Nvidiux")
		self.labelInfo = QtGui.QLabel(self.tabAbout)
		self.labelInfo.move(90,200)
		self.labelInfo.setAlignment(QtCore.Qt.AlignCenter)
		font = QtGui.QFont()
		font.setPointSize(11)
		font.setBold(True)
		font.setWeight(75)
		font.setStyleStrategy(QtGui.QFont.PreferAntialias)
		self.labelInfo.setFont(font)
		self.labelInfo.setText(_translate("Form", "Permet d'underclocker ou d'overclocker votre gpu nvidia\n(C) 2014 Payet Guillaume\nNvidiux n'est en aucun cas affilié à Nvidia",None) + "\nVersion : " + self.versionStr)
		self.textBrowser = QtGui.QTextBrowser(self.tabAbout)
		self.textBrowser.setGeometry(QtCore.QRect(10, 280, 560, 240))
		if os.path.isfile("/usr/share/nvidiux/licences/gpl-3.0_" + self.language + ".txt"):
			txtFile = open("/usr/share/nvidiux/licences/gpl-3.0_" + self.language + ".txt", "r")
			self.textBrowser.setText(_fromUtf8(txtFile.read()))
		elif os.path.isfile("/usr/share/nvidiux/licences/gpl-3.0.txt"):
			txtFile = open('/usr/share/nvidiux/licences/gpl-3.0.txt', 'r')
			self.textBrowser.setText(_fromUtf8(txtFile.read()))
		else:
			self.textBrowser.setText(_fromUtf8("Programme distribué sous license GPL V3\nVoir http://www.gnu.org/licenses/gpl-3.0.txt"))	
		self.tabWidget.addTab(self.tabAbout, _fromUtf8(""))
		
		self.buttonParcNvi.connect(self.buttonParcNvi,SIGNAL("released()"),self.loadProfileNvi)
		self.checkBoxNvi.connect(self.checkBoxNvi,QtCore.SIGNAL("clicked(bool)"),self.checkNvi)
		self.checkBoxTime.connect(self.checkBoxTime,QtCore.SIGNAL("clicked(bool)"),self.checkTime)
		self.spinBox.connect(self.spinBox,QtCore.SIGNAL("valueChanged(int)"),self.setTime)
		self.buttonParcSys.connect(self.buttonParcSys,SIGNAL("released()"),self.enableCronStartup)
		self.checkBoxSys.connect(self.checkBoxSys,QtCore.SIGNAL("clicked(bool)"),self.checkSys)
		self.ComboLang.connect(self.ComboLang,QtCore.SIGNAL("currentIndexChanged(int)"),self.setLanguage)
		self.checkBoxOverVolt.connect(self.checkBoxOverVolt,QtCore.SIGNAL("clicked(bool)"),self.setOvervolt)
		
		self.setWindowTitle(_translate("Form", "Préférences", None))
		self.buttonParcNvi.setText(_translate("Form", "Parcourir", None))
		self.checkBoxNvi.setText(_translate("Form", "Appliquer ce profil au demarrage de nvidiux", None))
		self.buttonParcSys.setText(_translate("Form", "Parcourir", None))
		self.checkBoxSys.setText(_translate("Form", "Appliquer ce profil au demarrage du systeme", None))
		
		self.checkBoxOverVolt.setText(_translate("Form", "Activer overvoltage", None))
		self.checkBoxTime.setText(_translate("Form", "Actualiser les donnees toutes les", None))
		self.spinBox.setSuffix(_translate("Form", " secondes", None))
		self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabConf), _translate("Form", "Nvidiux", None))
		self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabMoniteur), _translate("Form", "Moniteur", None))
		self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabAbout), _translate("Form", "A Propos", None))
		
		prefTranslator = QtCore.QTranslator()
		if prefTranslator.load("/usr/share/nvidiux/nvidiux_" + self.language):
			self.app.installTranslator(prefTranslator)
			self.retranslateUi()
		self.tabWidget.setCurrentIndex(self.loadTab)
	
	def showColor(self,idButton):
		pColor = self.colorBox.getColor()
		self.listButtonColor[idButton].setStyleSheet("border-radius: 10px;\nbackground-color:rgb(" + str(pColor.getRgb()[0]) + "," + str(pColor.getRgb()[1]) + "," + str(pColor.getRgb()[2]) + ")")

	def showError(self,errorCode,title,errorMsg,etype):
		if etype == self.error:
			errorMsg = errorMsg + "\nError Code:" + str(errorCode)
			QMessageBox.critical(self, _fromUtf8(title),_fromUtf8(errorMsg))
		elif etype == self.warning:
			QMessageBox.warning(self, _fromUtf8(title),_fromUtf8(errorMsg))	
		else:
			QMessageBox.information(self, _fromUtf8(title),_fromUtf8(errorMsg))
		return errorCode

