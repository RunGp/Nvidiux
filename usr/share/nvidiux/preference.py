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
	error = -1
	warning = -2
	nbGpuNvidia = 0
	tabGpu = []
	info = 0
	startWithSystem = False
	valueStart = "0:0"
	autoUpdateValue = False
	updateTime = 1
	home = ""
	mainWindows = None
	
	def __init__(self,loadTab,version,tabigpu,mainW,parent=None):
		super (Ui_Pref, self).__init__(parent)
		self.loadTab = loadTab
		self.version = version
		self.nbGpuNvidia = tabigpu[0]
		self.tabGpu = tabigpu[1]
		self.autoUpdateValue = tabigpu[2]
		self.updateTime = tabigpu[3]
		self.startWithSystem = tabigpu[4]
		self.valueStart = tabigpu[5]
		self.home = expanduser("~")
		self.setupUi()
		self.mainWindows = mainW
		
	def closeEvent(self, event):
		self.mainWindows.saveNvidiuxConf()
	
	def checkSys(self,value):
		if os.path.isfile("/etc/rc.local"):
			if value:
				self.buttonParcSys.setEnabled(True)
			else:
				self.buttonParcSys.setEnabled(False)
				if self.startWithSystem:
					if not self.delRcEntry():
						cmd = "bash /usr/share/nvidiux/toRoot.sh resetRc.py >> /dev/null 2>&1"
						result = sub.call(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True)
						if int(result) > 0:
							self.checkBoxSys.setChecked(True)
							return self.showError(40,"Erreur non gérée","Erreur non gérée ResetRC\nAssurez vous d'avoir taper le bon mot de passe",self.error)
					else:
						cmd = "bash /usr/share/nvidiux/toRoot.sh delRc.py >> /dev/null 2>&1"
						result = sub.call(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True)
						if int(result) == 0:
							self.labelGpuSys.setText(_fromUtf8("Profil au demarrage désactivé"))
							self.startWithSystem = False
							self.valueStart = "0:0"
							self.mainWindows.setStartSystem(self.startWithSystem,self.valueStart)
						else:
							self.checkBoxSys.setChecked(True)
							return self.showError(41,"Erreur non gérée","Erreur non gérée DelRC\nAssurez vous d'avoir taper le bon mot de passe",self.error)
		else:
			self.showError(32,"Échec","Impossible de continuer",self.error)
			self.checkBoxSys.setChecked(False)
	
	def checkNvi(self,value):
		if value:
			self.buttonParcNvi.setEnabled(True)
		else:
			self.buttonParcNvi.setEnabled(False)
			self.labelGpuNvi.setText(_fromUtf8("Auto chargement profil désactivé"))
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
			self.showError(50,"Échec","Erreur Interne",self.error)
	
	def changeTime(self,value):
		self.mainWindows.setTimeUpdate(value)
			
	def setupUi(self):
		self.setObjectName(_fromUtf8("Form"))
		self.resize(600, 540)
		self.setFixedSize(600, 540)
		
		self.tabWidget = QtGui.QTabWidget(self)
		self.tabWidget.setGeometry(QtCore.QRect(0, 0, 598, 538))
		self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
		
		self.tabConf = QtGui.QWidget()
		self.tabConf.setObjectName(_fromUtf8("tabConf"))
		
		self.buttonParcNvi = QtGui.QPushButton(self.tabConf)
		self.buttonParcNvi.setGeometry(QtCore.QRect(360, 18, 100, 27))
		self.buttonParcNvi.setObjectName(_fromUtf8("buttonParcNvi"))
		self.buttonParcNvi.setEnabled(False)
		self.checkBoxNvi = QtGui.QCheckBox(self.tabConf)
		self.checkBoxNvi.setGeometry(QtCore.QRect(10, 20, 340, 20))
		self.checkBoxNvi.setObjectName(_fromUtf8("checkBoxNvi"))
		self.labelGpuNvi = QtGui.QLabel(self.tabConf)
		self.labelGpuNvi.setGeometry(QtCore.QRect(60, 40, 500, 80))
		self.labelGpuNvi.setObjectName(_fromUtf8("labelGpuNvi"))
		
		if os.path.isfile(self.home + "/.nvidiux/Startup.ndi"):
			self.checkBoxNvi.setChecked(True)
			self.buttonParcNvi.setEnabled(True)
			self.labelGpuNvi.setText("Auto chargement actif")

		self.buttonParcSys = QtGui.QPushButton(self.tabConf)
		self.buttonParcSys.setGeometry(QtCore.QRect(360, 98, 100, 27))
		self.buttonParcSys.setObjectName(_fromUtf8("buttonParcSys"))
		self.buttonParcSys.setEnabled(False)
		self.checkBoxSys = QtGui.QCheckBox(self.tabConf)
		self.checkBoxSys.setGeometry(QtCore.QRect(10, 100, 340, 20))
		self.checkBoxSys.setObjectName(_fromUtf8("checkBoxSys"))
		self.labelGpuSys = QtGui.QLabel(self.tabConf)
		self.labelGpuSys.setGeometry(QtCore.QRect(60, 120, 500, 80))
		self.labelGpuSys.setObjectName(_fromUtf8("labelGpuSys"))
		
		if os.path.isfile("/etc/rc.local"):
			self.checkBoxSys.setEnabled(True)
		else:
			self.checkBoxSys.setEnabled(False)
		if self.startWithSystem:
			self.checkBoxSys.setChecked(True)
			self.labelGpuSys.setText(_fromUtf8("Profil chargé:" + str(self.valueStart)))
		else:
			self.checkBoxSys.setChecked(False)
			
		
		self.checkBoxTime = QtGui.QCheckBox(self.tabConf)
		self.checkBoxTime.setGeometry(QtCore.QRect(10, 200, 340, 20))
		self.checkBoxTime.setChecked(self.autoUpdateValue)
		self.checkBoxTime.setObjectName(_fromUtf8("checkBoxTime"))
		
		self.spinBox = QtGui.QSpinBox(self.tabConf)
		self.spinBox.setGeometry(QtCore.QRect(260, 196, 100, 25))
		self.spinBox.setAccelerated(True)
		self.spinBox.setPrefix(_fromUtf8(""))
		self.spinBox.setMinimum(1)
		self.spinBox.setMaximum(60)
		self.spinBox.setEnabled(self.autoUpdateValue)
		self.spinBox.setValue(self.updateTime)
		self.spinBox.setObjectName(_fromUtf8("spinBox"))
		
		self.tabWidget.addTab(self.tabConf, _fromUtf8(""))
		
		self.tabMoniteur = QtGui.QWidget()
		self.tabMoniteur.setObjectName(_fromUtf8("tabMoniteur"))
		self.tabWidget.addTab(self.tabMoniteur, _fromUtf8(""))
		self.checkBoxUpdateMon = QtGui.QCheckBox(self.tabMoniteur)
		self.checkBoxUpdateMon.setGeometry(QtCore.QRect(10, 20, 340, 20))
		self.checkBoxUpdateMon.setObjectName(_fromUtf8("checkBoxUpdateMon"))
		self.labelUpdateMon = QtGui.QLabel(self.tabMoniteur)
		self.labelUpdateMon.setGeometry(QtCore.QRect(40, 20, 340, 20))
		self.labelUpdateMon.setObjectName(_fromUtf8("UpdateMon"))
		self.checkBoxUpdateMon.setEnabled(False)
		self.labelUpdateMon.setText("Rafraichissement continu")
		self.spinBoxMon = QtGui.QSpinBox(self.tabMoniteur)
		self.spinBoxMon.setGeometry(QtCore.QRect(100, 100, 100, 25))
		self.spinBoxMon.setAccelerated(True)
		self.spinBoxMon.setPrefix(_fromUtf8(""))
		self.spinBoxMon.setMinimum(1)
		self.spinBoxMon.setMaximum(60)
		self.spinBoxMon.setEnabled(False)
		self.spinBoxMon.setValue(self.updateTime)
		self.spinBoxMon.setObjectName(_fromUtf8("spinBoxMon"))
		
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
		self.labelInfo.setText(_fromUtf8("Permet d'underclocker ou d'overclocker votre gpu nvidia\nVersion " + self.version + "\n(C) 2014 Payet Guillaume\nNvidiux n'est en aucun cas affilié à Nvidia"))
		self.textBrowser = QtGui.QTextBrowser(self.tabAbout)
		self.textBrowser.setGeometry(QtCore.QRect(10, 280, 580, 240))
		txtFile = open('/usr/share/nvidiux/gpl-3.0.txt', 'r')
		if txtFile != None:
			self.textBrowser.setText(_fromUtf8(txtFile.read()))
		else:
			self.textBrowser.setText(_fromUtf8("Programme distribué sous license GPL V3\nVoir http://www.gnu.org/licenses/gpl-3.0.txt"))
		self.retranslateUi()

		self.tabWidget.addTab(self.tabAbout, _fromUtf8(""))
		
		self.buttonParcNvi.connect(self.buttonParcNvi,SIGNAL("released()"),self.loadProfileNvi)
		self.checkBoxNvi.connect(self.checkBoxNvi,QtCore.SIGNAL("clicked(bool)"),self.checkNvi)
		self.checkBoxTime.connect(self.checkBoxTime,QtCore.SIGNAL("clicked(bool)"),self.checkTime)
		self.spinBox.connect(self.spinBox,QtCore.SIGNAL("valueChanged(int)"),self.changeTime)
		self.buttonParcSys.connect(self.buttonParcSys,SIGNAL("released()"),self.verifyRcConf)
		self.checkBoxSys.connect(self.checkBoxSys,QtCore.SIGNAL("clicked(bool)"),self.checkSys)
		
		self.retranslateUi()
		self.tabWidget.setCurrentIndex(self.loadTab)
	
	def delRcEntry(self):
		try:
			contenu = ""	
			chaine = "nvidia-settings"
			fichier = open("/etc/rc.local","r")
			for ligne in fichier:
				if not(chaine in ligne):
					contenu += ligne
			fichier.close()
			fichier = open('/tmp/nvidiux.rcfile', 'w')
			fichier.write(contenu)
			fichier.close()
			return True
		except:
			return False
	
	def verifyRcConf(self):
		if os.path.isfile("/etc/rc.local"):
			tab,fileToLoad = self.loadProfile()
			if tab == None:
				return None
			if self.delRcEntry():
				try:
					contenu = ""
					fichier = open("/tmp/nvidiux.rcfile","r")
					for ligne in fichier:
						if not("exit" in ligne):
							contenu += ligne
					fichier.close()
					i = 0
					for gpu in self.tabGpu:
						offsetGpu = int(tab[i][1]) - int(self.tabGpu[i].defaultFreqGpu)
						offsetMem = int(tab[i][3]) - int(self.tabGpu[i].defaultFreqMem)
						cmd = "nvidia-settings -a \"[gpu:" + str(i) + "]/GPUGraphicsClockOffset[2]=" + str(offsetGpu) + "\" -a \"[gpu:" + str(i) + "]/GPUMemoryTransferRateOffset[2]=" + str(offsetMem) + "\" >> /dev/null 2>&1 \n"
						contenu = contenu + cmd
						i+=1
					contenu += "exit 0\n"
					fichierW = open('/tmp/nvidiuxOk.rcfile', 'w')
					fichierW.write(contenu)
					fichierW.close()
					cmd = "bash /usr/share/nvidiux/toRoot.sh changeRc.py >> /dev/null 2>&1"
					result = sub.call(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True)
					if int(result) == 0:
						self.labelGpuSys.setText("Fichier au demarrage\n" + fileToLoad)
						self.startWithSystem = True
						self.valueStart = str(offsetGpu) + ":" + str(offsetMem)
						self.mainWindows.setStartSystem(self.startWithSystem,self.valueStart)
						self.mainWindows.saveNvidiuxConf()	
					elif int(result) == 255:
						self.showError(37,"Erreur Credential","Votre mot de passe est incorrect",self.error)
						return None
					elif int(result) >= 1 and int(result) <= 2:
						self.showError(38,"Erreur Configuration","Erreur Interne annulation\ncode mineur:" + str(result),self.error)
						return None
					else:
						self.showError(39,_fromUtf8("Erreur non gérée"),_fromUtf8("Erreur non gérée DelRC"),self.error)
						return None
				except:
					self.buttonParcSys.setChecked(False)
					self.buttonParcSys.setEnabled(False)
					self.showError(36,"Échec","Echec modification configuration",self.error)
			else:
				self.showError(34,"Échec","Echec modification configuration",self.error)
				self.buttonParcSys.setChecked(False)
				self.buttonParcSys.setEnabled(False)
		else:
			self.showError(35,"Échec","Echec modification configuration",self.error)
			self.buttonParcSys.setChecked(False)
			self.buttonParcSys.setEnabled(False)
		
	def loadProfileNvi(self):
		tab,fileToLoad = self.loadProfile()
		if fileToLoad != None:
			self.labelGpuNvi.setText("Fichier:"+ fileToLoad)
		else:
			return None
		try:
			if os.path.isfile(fileToLoad):
				shutil.copy(fileToLoad,self.home + "/.nvidiux/Startup.ndi")
		except:
			self.showError(29,"Échec","Impossible de modifier la configuration",self.warning)
				
	def loadProfile(self,path = ""):
		if path == "":
			profileFileName = QtGui.QFileDialog.getOpenFileName(self,'Ouvrir profil',"","*.ndi") 
			if profileFileName == "":
				return None
		else:
			profileFileName = path
		try:
			profileFile = open(profileFileName, "r")
			ndiFile = minidom.parse(profileFile)
		except:
			return self.showError(-1,"Fichier endommagé","Impossible de charger ce fichier de configuration",self.warning)
			
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
					listgpu.append(gpu)
					gpu = []	
		if versionElement == []:
			error = True
			self.showError(errorCode ,"Échec","Échec chargement du profil",19)
			return None	
		if not error:
			if float(self.version) < float(versionElement[0].firstChild.nodeValue):
				reply = QtGui.QMessageBox.question(self, _fromUtf8("Version"),_fromUtf8("Le profil est pour une version plus recente de Nvidiux\nCharger tous de même ?"), QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)
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
					self.showError(21,"Échec","Échec chargement du profil",self.error)
			else:
				error = 16
		if errorCode != 0:
			self.showError(errorCode ,"Échec","Échec chargement du profil",self.error)
			return None
		i = 0
		#~ tabinf = list()
		#~ tabinf.append(str(tempgpu[1]))
		#~ tabinf.append(str(tempgpu[2]))
		#~ tabinf.append(str(tempgpu[3]))
		#~ tabinf.append(profileFileName)
		return listgpu,profileFileName
	
	def retranslateUi(self):
		self.setWindowTitle(_translate("Form", "Préférences", None))
		self.buttonParcNvi.setText(_translate("Form", "Parcourir", None))
		self.checkBoxNvi.setText(_translate("Form", "Appliquer ce profil au demarrage de nvidiux", None))
		self.buttonParcSys.setText(_translate("Form", "Parcourir", None))
		self.checkBoxSys.setText(_translate("Form", "Appliquer ce profil au demarrage du systeme", None))
		#~ self.labelGpuSys.setText(_translate("Form", "Aucun profil", None))
		self.checkBoxTime.setText(_translate("Form", "Actualiser les données toutes les", None))
		self.spinBox.setSuffix(_translate("Form", " secondes", None))
		self.spinBoxMon.setSuffix(_translate("Form", " secondes", None))
		self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabConf), _translate("Form", "Nvidiux", None))
		self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabMoniteur), _translate("Form", "Moniteur", None))
		self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabAbout), _translate("Form", "A Propos", None))
		
	def showError(self,errorCode,title,errorMsg,etype):
		if etype == self.error:
			errorMsg = errorMsg + "\nError Code:" + str(errorCode)
			QMessageBox.critical(self, _fromUtf8(title),_fromUtf8(errorMsg))
		elif etype == self.warning:
			QMessageBox.warning(self, _fromUtf8(title),_fromUtf8(errorMsg))	
		else:
			QMessageBox.information(self, _fromUtf8(title),_fromUtf8(errorMsg))
		return errorCode

