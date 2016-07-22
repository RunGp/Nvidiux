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

class Ui_Pref(QWidget):
	
	loadTab = 1
	version = ""
	versionStr = ""
	versionPilote = "331:31"
	error = -1
	warning = -2
	nbGpuNvidia = 0
	listGpuMonitor = []
	tabGpu = []
	info = ""
	startWithSystem = False
	valueStart = "0:0"
	autoUpdateValue = False
	monitorGen = 1
	updateC = False
	updateTime = 1
	home = ""
	gpuActivated = 0
	overclockEnabled = True
	overvoltEnabled = False
	sameParamGpu = True
	mainWindows = None
	language = None
	app = None
	labelOs = None
	distrib = None
	
	def __init__(self,loadTab,versionStr,version,TabLang,tabParam,mainW,parent=None):
		super (Ui_Pref, self).__init__(parent)
		self.loadTab = loadTab
		self.version = version
		self.versionStr = versionStr
		self.language = TabLang[0]
		self.app = TabLang[1]
		self.nbGpuNvidia = tabParam[0]
		self.tabGpu = tabParam[1]
		self.autoUpdateValue = tabParam[2]
		self.updateTime = tabParam[3]
		self.startWithSystem = tabParam[4]
		self.valueStart = tabParam[5]
		self.overclockEnabled = tabParam[6]
		self.overvoltEnabled = tabParam[7]
		self.versionPilote = tabParam[8]
		self.sameParamGpu = tabParam[9]
		self.home = expanduser("~")
		self.mainWindows = mainW
		self.setupUi()
		
	def closeEvent(self, event):
		self.saveMonitorConf()
		self.mainWindows.saveNvidiuxConf()
		del(self.listGpuMonitor[:])
	
	def checkSys(self,value):
		if os.path.isfile("/usr/bin/crontab") and os.path.isfile("/usr/bin/sudo"):
			if value: #Enable sys button
				self.buttonParcSys.setEnabled(True)
			else: #Disable sysButton
				self.buttonParcSys.setEnabled(False)
				if self.startWithSystem: #Disable cron
					if not self.disableCronStartup():
						self.showError(33,_translate("Form",_translate("Form","Impossible de continuer",None),self.error))
						self.buttonParcSys.setEnabled(True)
						self.checkBoxSys.setChecked(True)
				else:
					self.labelGpuSys.setText(_translate("Form","Chargement profil au demarage desactive",None))
		else:
			self.showError(32,_translate("Form",_translate("Form","Impossible de continuer",None),self.error))
			self.checkBoxSys.setChecked(False)
	
	def checkNvi(self,value):
		if value:
			self.buttonParcNvi.setEnabled(True)
		else:
			self.buttonParcNvi.setEnabled(False)
			self.labelGpuNvi.setText(_translate("Form","Auto chargement profil desactive",None))
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
			if self.updateTime <= 1:
				self.spinBox.setSuffix(_translate("Form", " seconde", None))
			else:
				self.spinBox.setSuffix(_translate("Form", " secondes", None))
		else:
			self.showError(50,_translate("Form","Echec",None),_translate("Form","Erreur Interne",None),self.error)
	
	def disableCronStartup(self):
		startUpFilePath = expanduser("~") + "/.nvidiux/startup.sh"
		cmd = "bash /usr/share/nvidiux/toRoot.sh disableStartupCron.sh " + expanduser("~") + " >> /dev/null 2>&1"
		result = sub.call(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True)
		if int(result) == 0:
			self.labelGpuSys.setText(_fromUtf8(_translate("Form","Chargement profil au demarage desactive",None)))
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
			self.showError(40,_translate("Form","Erreur non geree",None),_translate("Form","Erreur non geree",None),self.error)
			return False
		return True
		
	def enableCronStartup(self):
		offsetGpu = 0
		offsetMem = 0
		tab,fileToLoad = self.loadProfile()
		if tab == None:
			return None
		shutil.copy(fileToLoad,self.home + "/.nvidiux/StartupSys.ndi")
		os.chmod(self.home + "/.nvidiux/StartupSys.ndi",0775)
		cmd = "bash /usr/share/nvidiux/toRoot.sh enableStartupCron.sh " + self.home.split("/")[-1] + " >> /dev/null 2>&1"
		result = sub.call(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True)
		if int(result) == 0:
			self.labelGpuSys.setText(_fromUtf8(_translate("Form","Le profil:",None)) + fileToLoad + _translate("Form","\nsera chargé à chaque demarrage du systeme",None))
			self.startWithSystem = True
			self.valueStart = str(offsetGpu) + ":" + str(offsetMem)
			self.mainWindows.setStartSystem(self.startWithSystem,self.valueStart)
			self.mainWindows.saveNvidiuxConf()
			
		elif int(result) == 255:
			self.showError(37,_translate("Form","Erreur Credential",None),_translate("Form","Votre mot de passe est incorrect",None),self.error)
			return -1
		else:
			self.showError(39,_translate("Form","Erreur non geree",None),_translate("Form","Erreur non geree",None),self.error)
			return -1
		return 0
			
	def loadProfileNvi(self):
		tab,fileToLoad = self.loadProfile()
		if fileToLoad != None:
			self.labelGpuNvi.setText(_translate("Form","Fichier:",None) + fileToLoad)
		else:
			return None,None
		try:
			if os.path.isfile(fileToLoad):
				shutil.copy(fileToLoad,self.home + "/.nvidiux/Startup.ndi")
		except:
			self.showError(29,_translate("Form","Echec",None),_translate("Form","Impossible de modifier la configuration",None),self.warning)
				
	def loadProfile(self,path = ""):
		if path == "":
			profileFileName = QtGui.QFileDialog.getOpenFileName(self,'Ouvrir profil',"","*.ndi") 
			if profileFileName == "" or profileFileName == None:
				return None,None
		else:
			profileFileName = path
		try:
			profileFile = open(profileFileName, "r")
			ndiFile = minidom.parse(profileFile)
		except:
			return self.showError(-1,_translate("Form","Fichier endommage",None),_translate("Form","Impossible de charger ce fichier de configuration",None),self.warning)

		itemlist = ndiFile.getElementsByTagName('gpu')
		error = True
		errorCode = 0
		listgpu = []
		gpu =[]
		if len(itemlist) > 0:
			for item in itemlist:
				if item.hasChildNodes():
					for value in item.childNodes:
						try:
							if value.nodeType == minidom.Node.ELEMENT_NODE:
								gpu.append(value.firstChild.nodeValue)
						except:
							error = True
							self.showError(errorCode ,_translate("nvidiux","Echec",None),_translate("nvidiux","Echec chargement du profil",None),19)
							return 1
						error = False
					listgpu.append(gpu)
					gpu = []
		versionElement = ndiFile.getElementsByTagName('version')	
		if versionElement == []:
			error = True
			self.showError(errorCode ,_translate("Form","Echec",None),_translate("Form","Echec chargement du profil",None),19)
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
						if int(tempgpu[4]) < 0 or int(tempgpu[4]) > self.tabGpu[i].maxOvervolt:
							errorCode = 15
						i = i + 1
				except:
					self.showError(21,_translate("Form","Echec",None),_translate("Form","Echec chargement du profil",None),self.error)
			else:
				error = 16
		if errorCode != 0:
			self.showError(errorCode ,_translate("Form","Echec",None),_translate("Form","Echec chargement du profil",None),self.error)
			return None
		i = 0
		return listgpu,profileFileName
	
	def retranslateUi(self):
		self.setWindowTitle(_translate("Form", "Preferences", None))
		self.buttonParcNvi.setText(_translate("Form", "Parcourir", None))
		self.checkBoxNvi.setText(_translate("Form", "Appliquer ce profil au demarrage de nvidiux", None))
		self.buttonParcSys.setText(_translate("Form", "Parcourir", None))
		self.checkBoxSys.setText(_translate("Form", "Appliquer ce profil au demarrage du systeme", None))
		self.checkBoxTime.setText(_translate("Form", "Actualiser les donnees toutes les", None))
		self.spinBox.setSuffix(_translate("Form", " secondes", None))
		self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabConf), _translate("Form", "Nvidiux", None))
		self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabMoniteur), _translate("Form", "Moniteur", None))
		self.tabWidget.setTabText(self.tabWidget.indexOf(self.about), _translate("Form", "A Propos", None))
		self.labelInfo.setText(_translate("Form", "Permet d'underclocker ou d'overclocker votre gpu nvidia\n(C) 2014-2016 Payet Guillaume\nNvidiux n'est en aucun cas affilie à Nvidia\n",None) + "\n" +_translate("Form","Version : ",None) + self.versionStr + " | " + self.labelOs)
		self.labelLang.setText(_translate("Form","Langue",None))
		self.checkBoxExpert.setText(_translate("Form", "Option avancé", None))
		self.buttonLicence.setText(_translate("Form", "Licence",None))
		self.buttonDonate.setText(_translate("Form", "Faire un don",None))
		self.buttonThanks.setText(_translate("Form", "Remerciement",None)) 
		self.checkBoxSameGpu.setText(_translate("Form", "Appliquer les memes parametres a des gpus identiques",None))
		self.checkBoxVerifDriver.setText(_translate("Form", "Activer overclock meme si la version\n du driver n'est pas reconnue",None))
		self.checkBoxTurboBoost.setText(_translate("Form","Forcer l'application des parametres pour gpuboost v1 (Gt(x)6XX)", None))
	
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
	
	def setTime(self,value):
		self.mainWindows.setTimeUpdate(value)
		self.updateTime = value
		if self.updateTime <= 1:
			self.spinBox.setSuffix(_translate("Form", " seconde", None))
		else:
			self.spinBox.setSuffix(_translate("Form", " secondes", None))
		
	def setSameParamGpu(self,value):
		self.sameParamGpu = value
		self.mainWindows.setSameParamGpu(value)
		
	def setUpdateContin(self,value):
		self.updateC = value
		
	def setChangeMonitor(self,value):
		if value:
			self.monitorGen = 2
			self.groupBoxPrefGpu.setVisible(False)
			self.checkBoxUpdateMon.setVisible(False)
		else:
			self.monitorGen = 1
			self.groupBoxPrefGpu.setVisible(True)
			self.checkBoxUpdateMon.setVisible(True)
		self.mainWindows.setMonitorGen(self.monitorGen)
		
	
	def setVerifDriver(self,value):
		if value:
			if not os.path.isfile(self.home + "/.nvidiux/ntchkdriver"):
				fileTemp= open(self.home + "/.nvidiux/ntchkdriver","w")
				fileTemp.close()
		else:
			if os.path.isfile(self.home + "/.nvidiux/ntchkdriver"):
				os.remove(self.home + "/.nvidiux/ntchkdriver")
				
	def setLanguage(self,lang):
		tabLang = ["fr_FR","en_EN","de_DE","es_ES"]
		language = tabLang[lang]
		self.mainWindows.setLanguage(language)
		prefTranslator = QtCore.QTranslator()
		if prefTranslator.load("/usr/share/nvidiux/nvidiux_" + language):
			self.app.installTranslator(prefTranslator)
			self.mainWindows.setTimeUpdate(self.updateTime)
			self.retranslateUi()
		QMessageBox.information(self,_translate("Form","Information",None),_translate("Form","Veuillez redemarer nvidiux",None))
	
	def setVerifTurboBoost(self,value):
		if value:
			reply = QtGui.QMessageBox.question(self, _fromUtf8(_translate("Form","Attention",None)),_fromUtf8(_translate("Form","N'utilisez cette option que si votre carte ne respecte pas les frequences defini par nvidiux (utile que sur certaines Gtx6XX)\nContinuer?",None)), QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)
			if reply == QtGui.QMessageBox.Yes:
				cmd = "bash /usr/share/nvidiux/toRoot.sh add_xtra1.py >> /dev/null 2>&1"
				if not sub.call(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True):
					QMessageBox.information(self,_translate("Form","Information",None),_translate("Form","Veuillez redemarer nvidiux",None))
				else:
					self.checkBoxTurboBoost.setChecked(False)
					self.showError(7,_translate("nvidiux","Erreur Credential",None),_translate("nvidiux","Votre mot de passe est incorrect",None),self.error)	
		else:
			cmd = "bash /usr/share/nvidiux/toRoot.sh del_xtra1.py >> /dev/null 2>&1"
			if not sub.call(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True):
				QMessageBox.information(self,_translate("Form","Information",None),_translate("Form","Veuillez redemarer nvidiux",None))
			else:
				self.checkBoxTurboBoost.setChecked(True)
				self.showError(7,_translate("nvidiux","Erreur Credential",None),_translate("nvidiux","Votre mot de passe est incorrect",None),self.error)
			
	def setOvervolt(self,value):
		if value == True:
			reply = QtGui.QMessageBox.question(self, _translate("Form","Attention",None),_translate("Form","Fonction reserve aux experts.\nModifier le voltage du gpu peut causer des dommages irreversibles et annule la garantie.\nNvidiux n'est pas responsable des eventuels dommages due a une utilisation de cette fonction\nActiver tous de même cette fonctionnalite ?",None), QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)
			if reply == QtGui.QMessageBox.Yes:
				self.mainWindows.setShowOvervoltButton(value)
				self.overvoltEnabled = True
			else:
				self.checkBoxOverVolt.setChecked(False)
		else:
			self.mainWindows.setShowOvervoltButton(value)
			self.overvoltEnabled = False

	def setupUi(self):
		self.setObjectName(_fromUtf8("Form"))
		self.resize(580, 540)
		self.setFixedSize(580, 540)
		
		self.tabWidget = QtGui.QTabWidget(self)
		self.tabWidget.setGeometry(QtCore.QRect(0, 0, 600, 540))
		self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
		
		self.tabConf = QtGui.QWidget()
		self.tabConf.setObjectName(_fromUtf8("tabConf"))
		self.tabWidget.addTab(self.tabConf, _fromUtf8(""))
		self.groupBoxPrefProfile = QtGui.QGroupBox(self.tabConf)
		self.groupBoxPrefProfile.setGeometry(QtCore.QRect(10, 180, 535,120 ))
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
		self.checkBoxNvi.setGeometry(QtCore.QRect(10, 5, 350, 20))
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
		self.checkBoxSys.setGeometry(QtCore.QRect(10, 65, 350, 20))
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
		self.groupBoxPrefGen.setGeometry(QtCore.QRect(10, 10, 535,160 ))
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
		self.spinBox.setGeometry(QtCore.QRect(270, 46, 120, 25))
		self.spinBox.setAccelerated(True)
		self.spinBox.setPrefix(_fromUtf8(""))
		self.spinBox.setMinimum(1)
		self.spinBox.setMaximum(60)
		self.spinBox.setEnabled(self.autoUpdateValue)
		self.spinBox.setValue(self.updateTime)
		if self.updateTime <= 1:
			self.spinBox.setSuffix(_translate("Form", " seconde", None))
		else:
			self.spinBox.setSuffix(_translate("Form", " secondes", None))
		self.spinBox.setObjectName(_fromUtf8("spinBox"))
		
		self.labelLang = QtGui.QLabel(self.groupBoxPrefGen)
		self.labelLang.setGeometry(QtCore.QRect(10, 5, 220, 40))
		self.labelLang.setObjectName(_fromUtf8("labelLang"))
		self.labelLang.setText(_translate("Form","Langue",None))

		self.combolang=QComboBox(self.groupBoxPrefGen)
		self.combolang.setObjectName("List language")
		self.combolang.setGeometry(QtCore.QRect(90, 8, 200, 30))
		self.combolang.addItem("Francais")
		self.combolang.addItem("English")
		self.combolang.addItem("Deutsch")
		self.combolang.addItem("Espanol")
		if self.language == "fr_FR":
			self.combolang.setCurrentIndex(0)
		elif self.language == "de_DE":
			self.combolang.setCurrentIndex(2)
		elif self.language == "es_ES":
			self.combolang.setCurrentIndex(3)
		else:
			self.combolang.setCurrentIndex(1)
		
		self.checkBoxSameGpu = QtGui.QCheckBox(self.groupBoxPrefGen)
		self.checkBoxSameGpu.setGeometry(QtCore.QRect(10, 75, 450, 20))
		self.checkBoxSameGpu.setObjectName(_fromUtf8("checkBoxSameGpu"))
		self.checkBoxSameGpu.setChecked(self.sameParamGpu)
		self.checkBoxSameGpu.setText(_translate("Form", "Appliquer les mêmes paramètres à des gpus identiques",None))
		
		self.checkBoxVerifDriver = QtGui.QCheckBox(self.groupBoxPrefGen)
		self.checkBoxVerifDriver.setGeometry(QtCore.QRect(10, 95, 450, 35))
		self.checkBoxVerifDriver.setObjectName(_fromUtf8("checkBoxVerifDriver"))
		self.checkBoxVerifDriver.setChecked(os.path.isfile(self.home + "/.nvidiux/ntchkdriver"))
		self.checkBoxVerifDriver.setText(_translate("Form", "Activer overclock meme si la version\ndu driver n'est pas reconnue",None))
		
		self.checkBoxExpert = QtGui.QCheckBox(self.groupBoxPrefGen)
		self.checkBoxExpert.setGeometry(QtCore.QRect(10, 130, 320, 20))
		self.checkBoxExpert.setObjectName(_fromUtf8("checkBoxExpert"))
		self.checkBoxExpert.setText(_translate("Form", "Option avancé", None))
		self.checkBoxExpert.setChecked(False)	
		
		self.groupBoxPrefAdvance= QtGui.QGroupBox(self.tabConf)
		self.groupBoxPrefAdvance.setGeometry(QtCore.QRect(10, 310, 535,100 ))
		self.groupBoxPrefAdvance.setStyleSheet(_fromUtf8("QGroupBox \n"
			"{ \n"
			"border: 1px solid SlateGrey;\n"
			"border-radius: 10px;\n"
			"}"))
		self.groupBoxPrefAdvance.setTitle(_fromUtf8(""))
		self.groupBoxPrefAdvance.setVisible(False)
		self.groupBoxPrefAdvance.setObjectName(_fromUtf8("groupBoxPrefAdvance"))
		
		self.checkBoxOverVolt = QtGui.QCheckBox(self.groupBoxPrefAdvance)
		self.checkBoxOverVolt.setGeometry(QtCore.QRect(10, 5, 600, 20))
		self.checkBoxOverVolt.setObjectName(_fromUtf8("checkBoxOverVolt"))
		self.checkBoxOverVolt.setChecked(False)
		if self.versionPilote >= 346.16 and self.overclockEnabled:
			overvolt = True
			for i in range(0, self.nbGpuNvidia):
				if overvolt:
					cmd = "nvidia-settings --query [gpu:" + str(i) + "]/GPUOverVoltageOffset"
					out, err = sub.Popen(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True).communicate()
					try:
						if int(out.split('range')[1].split("(inclusive)")[0].split("-")[1]) == 0:
							overvolt = False
					except:
						overvolt = False
			self.checkBoxOverVolt.setEnabled(overvolt)
			if self.overvoltEnabled:
				self.checkBoxOverVolt.setChecked(True)
		else:
			self.checkBoxOverVolt.setEnabled(False)
		
		self.checkBoxTurboBoost= QtGui.QCheckBox(self.groupBoxPrefAdvance)
		self.checkBoxTurboBoost.setGeometry(QtCore.QRect(10, 25, 600, 20))
		self.checkBoxTurboBoost.setObjectName(_fromUtf8("checkBoxTurboBoost"))
		self.checkBoxTurboBoost.setText(_translate("Form","Forcer l'application des parametres pour gpuboost v1 (Gt(x)6XX)", None))
		self.checkBoxTurboBoost.setChecked(False)
		self.checkBoxTurboBoost.setEnabled(False)
		
		for i in range(0, self.nbGpuNvidia):#only for gt(x) 6XX card
			var_nb = int(re.findall('\d+', self.tabGpu[i].nameGpu)[0])
			if var_nb >= 600 and var_nb <= 699:
				self.checkBoxTurboBoost.setEnabled(True)
		search = "PerfLevelSrc=0x2222"
		openFile = open("/etc/X11/xorg.conf","r")
		for line in openFile:
		    if search in line:
			self.checkBoxTurboBoost.setChecked(True)
		openFile.close()
		
		self.tabMoniteur = QtGui.QWidget()
		self.tabMoniteur.setObjectName(_fromUtf8("tabMoniteur"))
		self.tabWidget.addTab(self.tabMoniteur, _fromUtf8(""))
		gpuInfo = []
		ndiFile = None
		try:
			profileFile = open(expanduser("~") + "/.nvidiux/monitor.xml", "r")
			ndiFile = minidom.parse(profileFile)
		except:
			print "Pas de fichier conf monitor"
			
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
			
		self.checkBoxUpdateMon = QtGui.QCheckBox(_translate("Form", "Rafraichissement continu",None),self.tabMoniteur)
		self.checkBoxUpdateMon.setGeometry(QtCore.QRect(10, 20, 340, 20))
		self.checkBoxUpdateMon.setObjectName(_fromUtf8("checkBoxUpdateMon"))
		self.checkBoxUpdateMon.setEnabled(False)
		self.checkBoxUpdateMon.setChecked(self.updateC)
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
			checkTemp = QtGui.QCheckBox(self.groupBoxPrefGpu)
			checkTemp.connect(checkTemp,QtCore.SIGNAL("clicked(bool)"),self.stateGpu)
			self.listCheckBoxGpu.append(checkTemp)
			self.listCheckBoxGpu[i].setGeometry(QtCore.QRect(8, 30 + i * 50, 150, 20))
			if self.listGpuMonitor[i][2] == "False":
				self.listCheckBoxGpu[i].setChecked(False)
			else:
				self.listCheckBoxGpu[i].setChecked(True)
				self.gpuActivated = self.gpuActivated + 1
			self.listCheckBoxGpu[i].setText(_translate("Form", "Afficher ce gpu", None))
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
		self.connect(mapperPref, SIGNAL("mapped(int)"),self.showColor)	
		self.colorBox = QtGui.QColorDialog(self.groupBoxPrefGpu)
		self.checkBoxChangeGenMon = QtGui.QCheckBox(_translate("Form", "Activer Moniteur Experimental",None),self.tabMoniteur)
		self.checkBoxChangeGenMon.setGeometry(QtCore.QRect(10, 70 + self.nbGpuNvidia * 50, 340, 20))
		self.checkBoxChangeGenMon.setObjectName(_fromUtf8("checkBoxChangeGenMon"))
		self.checkBoxChangeGenMon.setChecked(False)
		
		if ndiFile == None:
			self.saveMonitorConf()
			
		self.about = QtGui.QWidget()
		self.about.setObjectName(_fromUtf8("about"))
		self.tabWidget.addTab(self.about, _fromUtf8(""))
		
		#~ self.Img = QtGui.QLabel(self.about)
		#~ self.Img.move(0,120)
		#~ self.Img.setPixmap(QtGui.QPixmap("/usr/share/nvidiux/img/drivers_nvidia_linux.png"))
			
		self.title = QtGui.QLabel(self.about)
		self.title.move(180,10)
		font = QtGui.QFont()
		font.setPointSize(45)
		font.setBold(True)
		font.setUnderline(False)
		font.setWeight(75)
		font.setStrikeOut(False)
		font.setStyleStrategy(QtGui.QFont.PreferAntialias)
		self.title.setFont(font)
		self.title.setAlignment(QtCore.Qt.AlignCenter)
		self.title.setText("Nvidiux")
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
		self.buttonDonate.setVisible(False)
		
		self.buttonThanks = QtGui.QPushButton(self.groupBoxAbout)
		self.buttonThanks.setGeometry(QtCore.QRect(5, 50, 210, 40))
		self.buttonThanks.setObjectName(_fromUtf8("buttonThanks"))
		self.buttonThanks.setEnabled(True)
		
		self.buttonLicence.setText(_translate("Form", "Licence",None))
		self.buttonDonate.setText(_translate("Form", "Faire un don",None))
		self.buttonThanks.setText(_translate("Form", "Remerciement",None)) 
		
		try:
			self.linuxDistrib = platform.linux_distribution()
			if self.linuxDistrib == ('', '', ''):
				if os.path.isfile("/etc/issue"):
					with open("/etc/issue") as f:
						self.labelOs = f.read().split()[0] + " " + platform.architecture()[0]
				else:
					self.labelOs = "Unknown distrib" + platform.architecture()[0]
			else:
				self.labelOs =  self.linuxDistrib[0] + " " + self.linuxDistrib[1]
		except:
			self.labelOs = ""
		info = _translate("Form", "Permet d'underclocker ou d'overclocker votre gpu nvidia\n(C) 2014-2016 Payet Guillaume\nNvidiux n'est en aucun cas affilie à Nvidia",None) + _translate("Form","Version:",None) + self.versionStr + " | " + self.labelOs 
		self.labelInfo.setText(info)
		self.textBrowser = QtGui.QTextBrowser(self.about)
		self.textBrowser.setGeometry(QtCore.QRect(10, 280, 560, 240))
		self.textBrowser.setAlignment(QtCore.Qt.AlignCenter)
		if os.path.isfile("/usr/share/nvidiux/licences/gpl-3.0_" + self.language + ".txt"):
			txtFile = open("/usr/share/nvidiux/licences/gpl-3.0_" + self.language + ".txt", "r")
			self.textBrowser.setText(_fromUtf8(txtFile.read()))
		elif os.path.isfile("/usr/share/nvidiux/licences/gpl-3.0.txt"):
			txtFile = open('/usr/share/nvidiux/licences/gpl-3.0.txt', 'r')
			self.textBrowser.setText(_fromUtf8(txtFile.read()))
		else:
			self.textBrowser.setText(_fromUtf8("Programme distribué sous license GPL V3\nVoir http://www.gnu.org/licenses/gpl-3.0.txt"))	
		
		self.buttonParcNvi.connect(self.buttonParcNvi,SIGNAL("released()"),self.loadProfileNvi)
		self.checkBoxNvi.connect(self.checkBoxNvi,QtCore.SIGNAL("clicked(bool)"),self.checkNvi)
		self.checkBoxTime.connect(self.checkBoxTime,QtCore.SIGNAL("clicked(bool)"),self.checkTime)
		self.spinBox.connect(self.spinBox,QtCore.SIGNAL("valueChanged(int)"),self.setTime)
		self.buttonParcSys.connect(self.buttonParcSys,SIGNAL("released()"),self.enableCronStartup)
		self.checkBoxSys.connect(self.checkBoxSys,QtCore.SIGNAL("clicked(bool)"),self.checkSys)
		self.combolang.connect(self.combolang,QtCore.SIGNAL("currentIndexChanged(int)"),self.setLanguage)
		self.checkBoxOverVolt.connect(self.checkBoxOverVolt,QtCore.SIGNAL("clicked(bool)"),self.setOvervolt)
		self.checkBoxExpert.connect(self.checkBoxExpert,QtCore.SIGNAL("clicked(bool)"),self.showExpertSettings)
		self.checkBoxSameGpu.connect(self.checkBoxSameGpu,QtCore.SIGNAL("clicked(bool)"),self.setSameParamGpu)
		self.checkBoxVerifDriver.connect(self.checkBoxVerifDriver,QtCore.SIGNAL("clicked(bool)"),self.setVerifDriver)
		self.checkBoxTurboBoost.connect(self.checkBoxTurboBoost,QtCore.SIGNAL("clicked(bool)"),self.setVerifTurboBoost)
		self.checkBoxUpdateMon.connect(self.checkBoxUpdateMon,QtCore.SIGNAL("clicked(bool)"),self.setUpdateContin)
		self.checkBoxChangeGenMon.connect(self.checkBoxChangeGenMon,QtCore.SIGNAL("clicked(bool)"),self.setChangeMonitor)
		self.buttonLicence.connect(self.buttonLicence,SIGNAL("released()"),self.showLicence)
		self.buttonDonate.connect(self.buttonDonate,SIGNAL("released()"),self.showDonate)
		self.buttonThanks.connect(self.buttonThanks,SIGNAL("released()"),self.showT)
		
		self.setWindowTitle(_translate("Form", "Preferences", None))
		self.buttonParcNvi.setText(_translate("Form", "Parcourir", None))
		self.checkBoxNvi.setText(_translate("Form", "Appliquer ce profil au demarrage de nvidiux", None))
		self.buttonParcSys.setText(_translate("Form", "Parcourir", None))
		self.checkBoxSys.setText(_translate("Form", "Appliquer ce profil au demarrage du systeme", None))
		
		self.checkBoxOverVolt.setText(_translate("Form", "Activer overvoltage", None))
		self.checkBoxExpert.setText(_translate("Form", "Option avancé", None))
		self.checkBoxTime.setText(_translate("Form", "Actualiser les données toutes les", None))
		if self.updateTime <= 1:
			self.spinBox.setSuffix(_translate("Form", " seconde", None))
		else:
			self.spinBox.setSuffix(_translate("Form", " secondes", None))
		self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabConf), _translate("Form", "Nvidiux", None))
		self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabMoniteur), _translate("Form", "Moniteur", None))
		self.tabWidget.setTabText(self.tabWidget.indexOf(self.about), _translate("Form", "A Propos", None))
		
		prefTranslator = QtCore.QTranslator()
		if prefTranslator.load("/usr/share/nvidiux/nvidiux_" + self.language):
			self.app.installTranslator(prefTranslator)
			self.retranslateUi()
		self.tabWidget.setCurrentIndex(self.loadTab)
	
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
	
	def showLicence(self):
		self.buttonThanks.setEnabled(True)
		self.buttonLicence.setEnabled(False)
		if os.path.isfile("/usr/share/nvidiux/licences/gpl-3.0_" + self.language + ".txt"):
			txtFile = open("/usr/share/nvidiux/licences/gpl-3.0_" + self.language + ".txt", "r")
			self.textBrowser.setText(_fromUtf8(txtFile.read()))
		elif os.path.isfile("/usr/share/nvidiux/licences/gpl-3.0.txt"):
			txtFile = open('/usr/share/nvidiux/licences/gpl-3.0.txt', 'r')
			self.textBrowser.setText(_fromUtf8(txtFile.read()))
		else:
			self.textBrowser.setText(_fromUtf8(_translate("Form", "Programme distribué sous license GPL V3\nVoir http://www.gnu.org/licenses/gpl-3.0.txt"),None))	
		
	def showT(self):
		self.buttonLicence.setEnabled(True)
		self.buttonThanks.setEnabled(False)
		self.textBrowser.setText(_fromUtf8(_translate("Form","Special thanks to\n - @mglinux for german translation\n - @profesorfalken for spanish translation\n - @gaara @bishop @gfx @jul974 for testing and help for debug",None)))
		
	def showDonate(self):
		import webbrowser
		url = "http://docs.python.org/library/webbrowser.html"
		webbrowser.open(url,new=2)
	
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
	
	def showExpertSettings(self,value):
		self.groupBoxPrefAdvance.setVisible(value)
