# -*- coding: utf-8 -*-
#!/usr/bin/python2

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from xml.dom import minidom
from os.path import expanduser
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
		self.home = expanduser("~")
		self.setupUi()
		self.mainWindows = mainW
		
	def closeEvent(self, event):
		self.mainWindows.saveNvidiuxConf()
		
	def checkNvi(self,value):
		if value:
			self.buttonParcNvi.setEnabled(True)
		else:
			self.buttonParcNvi.setEnabled(False)
			self.labelGpuNvi.setText("Aucun profil")
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
		
		self.tab = QtGui.QWidget()
		self.tab.setObjectName(_fromUtf8("tab"))
		
		self.buttonParcNvi = QtGui.QPushButton(self.tab)
		self.buttonParcNvi.setGeometry(QtCore.QRect(340, 20, 90, 27))
		self.buttonParcNvi.setObjectName(_fromUtf8("buttonParcNvi"))
		self.buttonParcNvi.setEnabled(False)
		self.checkBoxNvi = QtGui.QCheckBox(self.tab)
		self.checkBoxNvi.setGeometry(QtCore.QRect(10, 20, 321, 20))
		self.checkBoxNvi.setObjectName(_fromUtf8("checkBoxNvi"))
		self.labelGpuNvi = QtGui.QLabel(self.tab)
		self.labelGpuNvi.setGeometry(QtCore.QRect(70, 20, 90, 80))
		self.labelGpuNvi.setObjectName(_fromUtf8("labelGpuNvi"))
		
		if os.path.isfile(self.home + "/.nvidiux/Startup.ndi"):
			temp = self.loadProfile(self.home + "/.nvidiux/Startup.ndi")
			if temp != None:
				self.checkBoxNvi.setChecked(True)
				self.buttonParcNvi.setEnabled(True)
				self.labelGpuNvi.setText("Gpu:" + temp[0] + "\nMem:" + temp[2])

		self.buttonParcSys = QtGui.QPushButton(self.tab)
		self.buttonParcSys.setGeometry(QtCore.QRect(340, 100, 90, 27))
		self.buttonParcSys.setObjectName(_fromUtf8("buttonParcSys"))
		self.buttonParcSys.setEnabled(False)
		self.checkBoxSys = QtGui.QCheckBox(self.tab)
		self.checkBoxSys.setGeometry(QtCore.QRect(10, 100, 321, 20))
		self.checkBoxSys.setObjectName(_fromUtf8("checkBoxSys"))
		self.checkBoxSys.setEnabled(False)
		#~ self.labelGpuSys = QtGui.QLabel(self.tab)
		#~ self.labelGpuSys.setGeometry(QtCore.QRect(70, 140, 91, 21))
		#~ self.labelGpuSys.setObjectName(_fromUtf8("labelGpuSys"))
		
		self.checkBoxTime = QtGui.QCheckBox(self.tab)
		self.checkBoxTime.setGeometry(QtCore.QRect(10, 200, 281, 20))
		self.checkBoxTime.setChecked(self.autoUpdateValue)
		self.checkBoxTime.setObjectName(_fromUtf8("checkBoxTime"))
		
		self.spinBox = QtGui.QSpinBox(self.tab)
		self.spinBox.setGeometry(QtCore.QRect(250, 196, 100, 25))
		self.spinBox.setAccelerated(True)
		self.spinBox.setPrefix(_fromUtf8(""))
		self.spinBox.setMinimum(1)
		self.spinBox.setMaximum(60)
		self.spinBox.setEnabled(self.autoUpdateValue)
		self.spinBox.setValue(self.updateTime)
		self.spinBox.setObjectName(_fromUtf8("spinBox"))
		
		self.tabWidget.addTab(self.tab, _fromUtf8(""))
		
		self.tab_moniteur = QtGui.QWidget()
		self.tab_moniteur.setObjectName(_fromUtf8("tab_moniteur"))
		self.tabWidget.addTab(self.tab_moniteur, _fromUtf8(""))
		
		self.tab_about = QtGui.QWidget()
		self.tab_about.setObjectName(_fromUtf8("tab_about"))
		
		self.Img = QtGui.QLabel(self.tab_about)
		self.Img.move(190,5)
		self.Img.setPixmap(QtGui.QPixmap("/usr/share/nvidiux/img/drivers_nvidia_linux.png"))	
		self.title = QtGui.QLabel(self.tab_about)
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
		self.labelInfo = QtGui.QLabel(self.tab_about)
		self.labelInfo.move(90,200)
		self.labelInfo.setAlignment(QtCore.Qt.AlignCenter)
		font = QtGui.QFont()
		font.setPointSize(11)
		font.setBold(True)
		font.setWeight(75)
		font.setStyleStrategy(QtGui.QFont.PreferAntialias)
		self.labelInfo.setFont(font)
		self.labelInfo.setText(_fromUtf8("Permet d'underclocker ou d'overclocker votre gpu nvidia\nVersion:" + str(self.version) + "\n(C) 2014 Payet Guillaume\nNvidiux n'est en aucun cas affilié à Nvidia"))
		self.textBrowser = QtGui.QTextBrowser(self.tab_about)
		self.textBrowser.setGeometry(QtCore.QRect(10, 280, 580, 240))
		txtFile = open('/usr/share/nvidiux/gpl-3.0.txt', 'r')
		if txtFile != None:
			self.textBrowser.setText(_fromUtf8(txtFile.read()))
		else:
			self.textBrowser.setText(_fromUtf8("Programme distribué sous license GPL V3\nVoir http://www.gnu.org/licenses/gpl-3.0.txt"))
		self.retranslateUi()

		self.tabWidget.addTab(self.tab_about, _fromUtf8(""))
		
		self.buttonParcNvi.connect(self.buttonParcNvi,SIGNAL("released()"),self.loadProfileNvi)
		self.checkBoxNvi.connect(self.checkBoxNvi,QtCore.SIGNAL("clicked(bool)"),self.checkNvi)
		self.checkBoxTime.connect(self.checkBoxTime,QtCore.SIGNAL("clicked(bool)"),self.checkTime)
		self.spinBox.connect(self.spinBox,QtCore.SIGNAL("valueChanged(int)"),self.changeTime)
		
		self.retranslateUi()
		self.tabWidget.setCurrentIndex(self.loadTab)
		
	def loadProfileNvi(self):
		tab = self.loadProfile()
		if tab != None:
			self.labelGpuNvi.setText("Gpu:" + tab[0] + "\nMem:" + tab[2])
		else:
			self.showError(29,"Échec","Echec",self.warning)
		try:
			if os.path.isfile(tab[3]):
				shutil.copy(tab[3],self.home + "/.nvidiux/Startup.ndi")
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
		tabinf = list()
		tabinf.append(str(tempgpu[1]))
		tabinf.append(str(tempgpu[2]))
		tabinf.append(str(tempgpu[3]))
		tabinf.append(profileFileName)
		return tabinf
	
	
	def showError(self,errorCode,title,errorMsg,etype):
		if etype == self.error:
			errorMsg = errorMsg + "\nError Code:" + str(errorCode)
			QMessageBox.critical(self, _fromUtf8(title),_fromUtf8(errorMsg))
		elif etype == self.warning:
			QMessageBox.warning(self, _fromUtf8(title),_fromUtf8(errorMsg))	
		else:
			QMessageBox.information(self, _fromUtf8(title),_fromUtf8(errorMsg))
		return errorCode
	
	
	def retranslateUi(self):
		self.setWindowTitle(_translate("Form", "Préférences", None))
		self.buttonParcNvi.setText(_translate("Form", "Parcourir", None))
		self.checkBoxNvi.setText(_translate("Form", "Appliquer ce profil au demarrage de nvidiux", None))
		self.buttonParcSys.setText(_translate("Form", "Parcourir", None))
		self.checkBoxSys.setText(_translate("Form", "Appliquer ce profil au demarrage du systeme", None))
		#~ self.labelGpuSys.setText(_translate("Form", "Aucun profil", None))
		self.checkBoxTime.setText(_translate("Form", "Actualiser les données toutes les", None))
		self.spinBox.setSuffix(_translate("Form", " secondes", None))
		self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("Form", "Nvidiux", None))
		self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_moniteur), _translate("Form", "Moniteur", None))
		self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_about), _translate("Form", "A Propos", None))

