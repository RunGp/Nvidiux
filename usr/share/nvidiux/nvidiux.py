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


from PyQt4.QtCore import *
from PyQt4.QtGui import *
from xml.dom import minidom
from PyQt4 import QtCore, QtGui
from windows import Ui_MainWindow
from confirm import ConfirmWindow
from about import Ui_About
from os.path import expanduser
import subprocess as sub
import sys
import os
import threading
import time

muttex = threading.RLock()

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

class Gpuinfo():
	defaultFreqShader = 0
	defaultFreqGpu = 0
	defaultFreqMem = 0
	freqShader = 0
	freqGpu = 0
	freqMem = 0 
	fanSpeed = 0
	nameGpu = ""
	videoRam = ""
	cudaCores = ""
	openGlVersion = ""
	version = ""

class Mythread(threading.Thread):
 
    def __init__(self, duree, fonction, args=[], kwargs={}):
        threading.Thread.__init__(self)
        self.duree = duree
        self.fonction = fonction
        self.args = args
        self.kwargs = kwargs
        self.infinite = True 
 
    def run(self,args=0):
        while self.infinite:
            self.timer = threading.Timer(self.duree, self.fonction, self.args, self.kwargs)
            self.timer.setDaemon(True)
            self.timer.start()
            self.timer.join()
 
    def stop(self):
        self.infinite = False
        if self.timer.isAlive():
            self.timer.cancel()

def majGpu(numGpu,fen):
	with muttex: 
		output=os.popen("nvidia-settings --query [gpu:" + str(numGpu) + "]/GPUCoreTemp | grep GPUCore | head -1", "r").read() 
		fen.ui.Temp.setText(_fromUtf8("Température\n" + str(output.split(':')[-1].split('.')[0]) + " °C"))
		output=os.popen("nvidia-settings --query [gpu:" + str(numGpu) + "]/GPUUtilization | grep GPUUtilization | head -1", "r").read()
		fen.ui.UPCIE.setText(_fromUtf8("Utilisation Bus PCIE\n" + str(output.split('=')[-1].replace('\n','').replace(',','')) + " %"))
		fen.ui.UGPU.setText(_fromUtf8("Utilisation Gpu\n" + str(output.split('=')[1].split(',')[0]) + "%"))
		output=os.popen("nvidia-settings --query [gpu:" + str(numGpu) + "]/UsedDedicatedGPUMemory | grep UsedDedicatedGPUMemory | head -1", "r").read()
		fen.ui.UMem.setText(_fromUtf8("Utilisation Memoire\n" + str(output.split(':')[-1].split('.')[0]) + " Mo"))

class ShipHolderApplication(QMainWindow):
	
	numGpu = 0
	tabGpu = []
	nbGpu = -1
	nbGpuNvidia = -1
	optimus = 0
	nvidiuxVersion = 0.84
	change = 0
	isFermiArch = []
	form = ""
	threadInfoGpu = None
	isSli= False
	error = -1
	warning = -2
	info = 0
	argv = []
	
	def __init__(self,argv,parent=None):
		super (ShipHolderApplication, self).__init__(parent)
		self.argv = argv
		self.createWidgets()
		
	def about(self):
		self.form = Ui_About()
		self.form.show()
		
	def applyNewClock(self):
		text = "Confirmation( "
		i = 0
		size = 0
		for gpu in self.tabGpu:
			text = text + str(self.tabGpu[i].nameGpu) + "," + str((i+1)) + " )\nGpu : " + str(self.tabGpu[i].freqGpu) + " Mhz\nMémoire : " + str(self.tabGpu[self.numGpu].freqMem) + " Mhz\n"
			i = i + 1
		if len(self.tabGpu) == 1:
			size = 16
		elif len(self.tabGpu) == 2:
			size = 12
		else:
			size = 10
		self.form = ConfirmWindow(_fromUtf8(text),size)
		self.connect(self.form, SIGNAL("accept(PyQt_PyObject)"), self.overclock)
		self.form.show()
		
	def changeGpu(self,item):
		self.numGpu = int(item.text().split(':')[0]) - 1
		self.threadInfoGpu.stop()
		self.threadInfoGpu = Mythread(1, majGpu, [self.numGpu], {"fen":myapp})
		self.threadInfoGpu.setDaemon(True)
		self.threadInfoGpu.start()
		self.ui.lcdShader.display(self.tabGpu[self.numGpu].freqShader)
		self.ui.SliderShader.setSliderPosition(int(self.tabGpu[self.numGpu].freqShader))
		self.ui.SliderMem.setSliderPosition(int(self.tabGpu[self.numGpu].freqMem))
		self.ui.lcdMem.display(int(self.tabGpu[self.numGpu].freqMem))
		self.ui.SliderGpu.setSliderPosition(int(self.tabGpu[self.numGpu].freqGpu))
		self.ui.lcdGPU.display(int(self.tabGpu[self.numGpu].freqGpu))
		self.ui.nomGpu.setText(self.tabGpu[self.numGpu].nameGpu)
		self.ui.MemGpu.setText(_fromUtf8("Memoire video\n" + str(self.tabGpu[self.numGpu].videoRam) + " Go"))
		self.ui.CudaCore.setText(_fromUtf8("NB coeur cuda\n" + str(self.tabGpu[self.numGpu].cudaCores)))
		self.ui.PiloteVersion.setText(_fromUtf8("Version du Pilote\n" + str(self.tabGpu[self.numGpu].version)))
		self.ui.OpenGlSupport.setText(_fromUtf8("OpenGl Support\n"	+ str(self.tabGpu[self.numGpu].openGlVersion)))
		self.ui.label_Dfreq_Gpu.setText(str(self.tabGpu[self.numGpu].defaultFreqGpu) + _fromUtf8("Mhz →"))
		self.ui.label_Dfreq_Shader.setText(str(self.tabGpu[self.numGpu].defaultFreqShader) + _fromUtf8("Mhz →"))
		self.ui.label_Dfreq_Mem.setText(str(self.tabGpu[self.numGpu].defaultFreqMem) + _fromUtf8("Mhz →"))
		
	def closeEvent(self, event):
		if self.change:
			reply = QtGui.QMessageBox.question(self, _fromUtf8("Message"),_fromUtf8("Etes vous sur de vouloir quitter sans appliquer les modifications ?"), QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)
			if reply == QtGui.QMessageBox.Yes:
				self.threadInfoGpu.stop()
				time.sleep(0.5)
				event.accept()
			else:
				event.ignore()
				self.applyNewClock()
		else:
			self.threadInfoGpu.stop()
			time.sleep(0.5)
			event.accept()
	
	def createWidgets(self):
		self.ui = Ui_MainWindow()
		self.ui.setupUi(self)
		self.initialiseData()
		self.ui.buttonReset.connect(self.ui.buttonReset,SIGNAL("released()"),self.reset)
		self.ui.buttonAbout.connect(self.ui.buttonAbout,SIGNAL("released()"),self.about)
		self.ui.buttonLoadProfile.connect(self.ui.buttonLoadProfile,SIGNAL("released()"),self.loadProfile)
		self.ui.buttonSaveProfile.connect(self.ui.buttonSaveProfile,SIGNAL("released()"),self.saveProfile)
		#~ self.ui.buttonStartMonitor.connect(self.ui.buttonStartMonitor,SIGNAL("released()"),self.startMonitor)
		#~ self.ui.buttonConfigureMonitor.connect(self.ui.buttonConfigureMonitor,SIGNAL("released()"),self.configureMonitor)
		self.ui.buttonApply.connect(self.ui.buttonApply,SIGNAL("released()"),self.applyNewClock)
		self.ui.SliderShader.connect(self.ui.SliderShader, SIGNAL("sliderMoved(int)"),self.updateshader)
		self.ui.SliderMem.connect(self.ui.SliderMem, SIGNAL("sliderMoved(int)"),self.updateMem)
		self.ui.SliderGpu.connect(self.ui.SliderGpu, SIGNAL("sliderMoved(int)"),self.updateGpu)
		self.ui.SliderFan.connect(self.ui.SliderFan, SIGNAL("sliderMoved(int)"),self.changeFanSpeed)
		self.ui.actionQuitter.connect(self.ui.actionQuitter, SIGNAL("triggered()"),self.quitapp)
		self.ui.actionLoadProfile.connect(self.ui.actionLoadProfile, SIGNAL("triggered()"),self.loadProfile)
		self.ui.actionSaveProfile.connect(self.ui.actionSaveProfile, SIGNAL("triggered()"),self.saveProfile)
		self.ui.checkBoxFan.connect(self.ui.checkBoxFan,QtCore.SIGNAL("clicked(bool)"),self.stateFan)
		self.ui.checkBoxVSync.connect(self.ui.checkBoxVSync,QtCore.SIGNAL("clicked(bool)"),self.stateVSync)
		#~ self.ui.actionStartMonitor.connect(self.ui.actionStartMonitor, SIGNAL("triggered()"),self.startMonitor)
		#~ self.ui.actionConfigureMonitor.connect(self.ui.actionConfigureMonitor, SIGNAL("triggered()"),self.configureMonitor)
		self.ui.actionAbout.connect(self.ui.actionAbout, SIGNAL("triggered()"),self.about)
		self.ui.listWidgetGpu.itemClicked.connect(self.changeGpu)

		cmd = "vainfo | wc -l"
		if int(sub.Popen(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True).communicate()[0].replace('\n','')) > 6:
			self.ui.checkBoxVaapi.setChecked(1)
		i = 0
		for gpu in self.tabGpu:
			self.ui.listWidgetGpu.addItem(str(i + 1) + ":" + gpu.nameGpu)
			i = i + 1
		if len(self.argv) == 2:
			if os.path.exists(self.argv[1]):
				self.loadProfile(self.argv[1])
	
	def configureMonitor(self):
		print "todo configure interface"
		
	def changeFanSpeed(self,value):
		cmd = "nvidia-settings -a [fan:" + str(self.numGpu) + "]/GPUCurrentFanSpeed="+ str(value)
		if not sub.call(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True):
			self.ui.labelFanVitesse.setText(str(value) + "%")
		else:
			self.ui.Message.setText(_fromUtf8("Echec\nchangement vitesse ventillo"))			
		
	def defineDefaultFreqGpu(self,gpuName):
		home = expanduser("~")
		try:
			if not os.path.exists(home + "/.nvidiux/"):
				os.makedirs(home + "/.nvidiux/")
			
			if os.path.isfile(home + "/.nvidiux/" + gpuName + ".ndi"):
				self.loadProfile(home + "/.nvidiux/" + gpuName + ".ndi",True)
			else:
				if self.saveProfile(home + "/.nvidiux/" + gpuName + ".ndi") != 0:
					return self.showError(21,"Droit insuffisant","Impossible d'ecrire le fichier !",self.error)
				self.loadProfile(home + "/.nvidiux/" + gpuName + ".ndi",True)		
			if os.path.isfile(home + "/.nvidiux/Startup.ndi"):
				self.loadProfile(home +"/.nvidiux/Startup.ndi",False)	
		except:
			return self.showError(20,"Erreur","Erreur Chargement configuration",self.error)					
		
	def iscompaptible(self):
		if len(os.popen("ls -l /usr/lib | grep nvidia", "r").read()) == 0:#find better way...
			return self.showError(1,"Non supporte","Driver introuvable \nVeuillez installer les pilotes proprietaires",self.error)
		if os.popen("file /usr/bin/nvidia-settings", "r").read().find('executable') == -1:
			return self.showError(2,"Non supporte","Nvidia settings introuvable \nveuillez installer les pilotes proprietaires et nvidia settings",self.error)
		ListeGpu = os.popen("lspci -vnn | egrep 'VGA|3D'", "r").read()
		self.nbGpuNvidia = ListeGpu.count('NVIDIA')
		self.nbGpu = len(ListeGpu)

		if self.nbGpu >= 2: #MultiGpu
			if ListeGpu.count('Intel') == 1 and self.nbGpuNvidia == 1 : #optimus
				if os.popen("prime-supported 2>> /dev/null", "r").read().replace('\n','') != "yes":
					return self.showError(3,"Prime","Seul prime est supporté pour les configurations optimus",self.error)	
				if os.popen("prime-select query", "r").read().replace('\n','') != "nvidia":
					return self.showError(-1,"Mode intel","Configuration Prime\nVeuillez passer en mode nvidia svp",self.info)
				self.optimus = 1
				self.ui.checkBoxOptimus.setChecked(1)
		if self.nbGpuNvidia == 0:
			return self.showError(4,"Gpu Nvidia introuvable","Gpu Nvidia introuvable",self.error)
		
		if not os.path.isfile("/etc/X11/xorg.conf"):
			reply = QtGui.QMessageBox.question(self, _fromUtf8("Xorg.conf"),_fromUtf8("Pas de fichier xorg.conf en générer un ?"), QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)
			if reply == QtGui.QMessageBox.No:
				return self.showError(6,"Erreur","Vous devez avoir un fichier xorg.conf",self.error)
			else:
				os.popen("bash /usr/share/nvidiux/toRoot.sh >> /dev/null 2>&1 ;echo $?", "r").read()
				try:
					tempFile = open('/tmp/.reboot_nvidiux','a')
					tempFile.write('Nvidiux temp file')
					tempFile.close()
					return self.showError(-1,"Redémarrage Requis","Configuration effectué\nVous devez redémarrer votre machine",self.info)
				except:
					return self.showError(5,"Erreur","Erreur configuration nvidiux",self.error)

		if int(os.popen("cat /etc/X11/xorg.conf | grep Coolbits | wc -l", "r").read()) == 0:
			self.showError(-1,"Configuration","La configuration du fichier xorg n'est pas effectué !\nEntrer votre mot de passe administrateur pour effectuer la configuration",self.info)
			if int(os.popen("bash /usr/share/nvidiux/toRoot.sh >> /dev/null 2>&1 ;echo $?", "r").read()) != 0:
				return self.showError(7,"Erreur Credential","Votre mot de passe est incorrect",self.info)
			else:
				try:
					tempFile = open('/tmp/.reboot_nvidiux','a')
					tempFile.write('Nvidiux temp file')
					tempFile.close()
					return self.showError(-1,"Redémarrage Requis","Configuration effectué\nVous devez redémarrer votre machine",self.info)
				except:
					return self.showError(5,"Erreur","Erreur configuration nvidiux",self.error)
		else:
			if os.path.isfile("/tmp/.reboot_nvidiux"):
				return self.showError(-1,"Redémarrage Requis","Configuration effectué\nVous devez redémarrer votre machine",self.info)
		return 0
		
	def initialiseData(self):
		info = ""
		err = ""
		out = ""
		compatibility = self.iscompaptible()
		if compatibility >= 1 and  compatibility <= 7:
			sys.exit(compatibility)
		if compatibility == -1:
			sys.exit(0)
		
		cmd = "nvidia-settings --query [gpu:0]/NvidiaDriverVersion"
		if not sub.call(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True):
			out, err = sub.Popen(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True).communicate()
			versionPilote = float(out.split(':')[-1][1:])
		else:
			self.showError(29,"Échec","Impossible de determiner la version des drivers",self.error)
		if versionPilote > 346.47:
			info = "Driver non testé\n"
		if versionPilote <= 337.12:
			self.ui.SliderMem.setEnabled(False)
			self.ui.SliderGpu.setEnabled(False)
			self.ui.buttonReset.setEnabled(False)
			self.ui.buttonApply.setEnabled(False)
			self.ui.SliderFan.setEnabled(False)
			self.ui.checkBoxFan.setCheckable(False)
			
			self.ui.Message.setText(_fromUtf8("Driver non supporté (trop ancien)!\nOverclock desactivé"))
			QMessageBox.information(self, _fromUtf8("Driver"),_fromUtf8("Driver non supporté:trop ancien\nOverclock desactivé\nIl vous faut la version 337.19 ou plus recent pour overclocker"))
		for i in range(0, self.nbGpuNvidia):
			self.tabGpu.append(Gpuinfo())
			if i == 0: #si un seul pas de retour ligne
				cmd = "lspci -vnn | grep NVIDIA | grep -v Audio | head -n " + str(i + 1)
				out, err = sub.Popen(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True).communicate()
			else:
				cmd = "lspci -vnn | grep NVIDIA | grep -v Audio | head -n " + str(i + 1)
				out, err = sub.Popen(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True).communicate()
				out = out.split('\n')[-1]	
			self.tabGpu[i].nameGpu = out.split(':')[-2].split('[')[-2].split(']')[0].replace('/','|')
			cmd =  "nvidia-settings -a [gpu:" + str(i) + "]/GPUPowerMizerMode=1"
			sub.call(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True)
			cmd = "nvidia-settings --query [gpu:" + str(i) + "]/videoRam"
			if not sub.call(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True):
				out, err = sub.Popen(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True).communicate()
				self.tabGpu[i].videoRam = float(out.split(': ')[1].split('.')[0]) / 1048576
			else:
				self.tabGpu[i].videoRam = "N/A"
			
			cmd = "nvidia-settings --query [gpu:" + str(i) + "]/cudaCores"
			if not sub.call(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True):
				out, err = sub.Popen(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True).communicate()
				self.tabGpu[i].cudaCores = int(out.split(': ')[1].split('.')[0])
			else:
				self.tabGpu[i].cudaCores = "N/A"
			
			cmd = "nvidia-settings --query [gpu:" + str(i) + "]/GPUPerfModes | grep memTransferRatemax= | tail -1"
			if not sub.call(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True):
				out, err = sub.Popen(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True).communicate()
				self.tabGpu[i].freqMem = out.split(',')[1].split('=')[1]
			else:
				self.showError(31,"Échec","Échec chargement des parametres Gpu",self.error)
				
			cmd = "nvidia-settings --query [gpu:" + str(i) + "]/NvidiaDriverVersion"
			if not sub.call(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True):
				out, err = sub.Popen(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True).communicate()
				self.tabGpu[i].version = float(out.split(':')[-1][1:])
			else:
				self.showError(32,"Échec","Échec chargement des parametres Gpu",self.error)
				
			cmd = "nvidia-settings --query all | grep OpenGLVersion"
			if not sub.call(cmd + "| head -1",stdout=sub.PIPE,stderr=sub.PIPE,shell=True):
				out, err = sub.Popen(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True).communicate()
				self.tabGpu[i].openGlVersion = out.split('NVIDIA')[0].split(':')[-1]
			else:
				self.tabGpu[i].openGlVersion = "N/A"
			
			cmd = "nvidia-settings --query [gpu:" + str(i) + "]/GPU3DClockFreqs"
			if not sub.call(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True):
				out, err = sub.Popen(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True).communicate()
				self.tabGpu[i].freqGpu = out.split(': ')[1].split(',')[0]
			else:
				cmd = "nvidia-settings --query [gpu:" + str(i) + "]/GPUCurrentClockFreqs"
				if not sub.call(cmd + " | head -1",stdout=sub.PIPE,stderr=sub.PIPE,shell=True):
					out, err = sub.Popen(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True).communicate()
					self.tabGpu[i].freqGpu = out.split(': ')[1].split(',')[0]
				else:
					self.showError(33,"Échec","Échec chargement des parametres Gpu",self.error)
			cmd = "nvidia-settings --query [gpu:" + str(i) + "]/GPUCurrentProcessorClockFreqs"
			if not sub.call(cmd + " | head -2",stdout=sub.PIPE,stderr=sub.PIPE,shell=True):
				out, err = sub.Popen(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True).communicate()
				self.tabGpu[i].freqShader = out.split(': ')[1].split('.')[0]
			else:
				self.showError(34,"Échec","Échec chargement des parametres Gpu",self.error)		
			if int(self.tabGpu[i].freqShader) == int(self.tabGpu[i].freqGpu) * 2 or int(self.tabGpu[i].freqShader) == int(self.tabGpu[i].freqGpu) * 2 + 1:
				self.isFermiArch.append(True);
			else:
				self.isFermiArch.append(False);
			
			cmd = "nvidia-settings --query all | grep SyncToVBlank"
			out, err = sub.Popen(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True).communicate()
			if out != "":
				if out.split(': ')[1].split('.')[0]:
					self.ui.checkBoxVSync.setChecked(True)
					self.ui.SliderFan.setEnabled(True)
				else:
					self.checkBoxVSync.setChecked(False)
					self.ui.SliderFan.setEnabled(True)
			else:
				self.ui.checkBoxVSync.setChecked(False)
				self.ui.SliderFan.setEnabled(False)
			
			
			cmd = "nvidia-settings --query [fan:" + str(i) + "]/GPUCurrentFanSpeed"
			if not sub.call(cmd ,stdout=sub.PIPE,stderr=sub.PIPE,shell=True):
				out, err = sub.Popen(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True).communicate()
				self.tabGpu[i].fanSpeed = out.split(': ')[1].split('.')[0]
			else:
				self.tabGpu[i].fanSpeed = 30
				
			cmd = "nvidia-settings --query [gpu:" + str(i) + "]/GPUFanControlState"
			out,err = sub.Popen(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True).communicate()
			if int(out.split(': ')[1].split('.')[0]) == 0:
				self.ui.SliderFan.setEnabled(False)
				self.ui.checkBoxFan.setChecked(False)
			else:
				self.ui.SliderFan.setEnabled(True)
				self.ui.checkBoxFan.setChecked(True)
				self.ui.labelFanVitesse.setText(str(self.tabGpu[i].fanSpeed)+ "%")
				self.ui.SliderFan.setSliderPosition(int(self.tabGpu[i].fanSpeed))
			
			cmd =  "nvidia-settings -a [gpu:" + str(i) + "]/GPUPowerMizerMode=0"
			sub.call(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True)
		
		for gpu in self.tabGpu:
			self.defineDefaultFreqGpu(gpu.nameGpu)	
			
		self.ui.label_Img.setPixmap(QtGui.QPixmap("/usr/share/nvidiux/img/drivers_nvidia_linux.png"))	
		self.ui.SliderShader.setMinimum(int(self.tabGpu[self.numGpu].defaultFreqShader) * 0.85)
		self.ui.SliderShader.setMaximum(int(self.tabGpu[self.numGpu].defaultFreqShader) * 1.25)
		self.ui.SliderShader.setSliderPosition(int(self.tabGpu[self.numGpu].freqShader))
		self.ui.lcdShader.display(int(self.tabGpu[self.numGpu].freqShader))
		self.ui.SliderFan.setMinimum(30)
		self.ui.SliderFan.setMaximum(100)
		self.ui.SliderMem.setMinimum(int(self.tabGpu[self.numGpu].defaultFreqMem) * 0.85)
		self.ui.SliderMem.setMaximum(int(self.tabGpu[self.numGpu].defaultFreqMem) * 1.25)
		self.ui.SliderMem.setSliderPosition(int(self.tabGpu[self.numGpu].freqMem))
		self.ui.lcdMem.display(int(self.tabGpu[self.numGpu].freqMem))
		self.ui.SliderGpu.setMinimum(int(self.tabGpu[self.numGpu].defaultFreqGpu) * 0.85)
		self.ui.SliderGpu.setMaximum(int(self.tabGpu[self.numGpu].defaultFreqGpu) * 1.25)
		self.ui.SliderGpu.setSliderPosition(int(self.tabGpu[self.numGpu].freqGpu))
		self.ui.lcdGPU.display(int(self.tabGpu[self.numGpu].freqGpu))
		self.ui.label_Dfreq_Gpu.setText(str(self.tabGpu[self.numGpu].defaultFreqGpu) + _fromUtf8("Mhz →"))
		self.ui.label_Dfreq_Shader.setText(str(self.tabGpu[self.numGpu].defaultFreqShader) + _fromUtf8("Mhz →"))
		self.ui.label_Dfreq_Mem.setText(str(self.tabGpu[self.numGpu].defaultFreqMem) + _fromUtf8("Mhz →"))
		self.ui.nomGpu.setText(self.tabGpu[self.numGpu].nameGpu)
		self.ui.MemGpu.setText(_fromUtf8("Memoire video\n" + str(self.tabGpu[self.numGpu].videoRam) + " Go"))
		self.ui.CudaCore.setText(_fromUtf8("NB coeur cuda\n" + str(self.tabGpu[self.numGpu].cudaCores)))
		self.ui.PiloteVersion.setText(_fromUtf8("Version du Pilote\n" + str(versionPilote)))
		self.ui.OpenGlSupport.setText(_fromUtf8("OpenGl Support\n" + str(self.tabGpu[self.numGpu].openGlVersion)))
		self.ui.checkBoxSli.setChecked(0)
		if self.nbGpuNvidia >= 2: #detect sli 2 card with same name
			if len(list(set(self.tabGpu[i].nameGpu))) == 1:
				self.ui.checkBoxSli.setChecked(1)
				self.isSli = True
		i = self.verifyGpu(self.tabGpu[0].nameGpu)
		if i == -1:
			info = info + "Ce gpu n'est pas dans la base des gpu compatibles"
		if i == 1:
			info = info + "Ce gpu n'est pas compatibles"
			self.ui.SliderMem.setEnabled(0)
			self.ui.SliderGpu.setEnabled(0)
			self.ui.SliderShader.setEnabled(0)
			self.ui.buttonReset.setEnabled(0)
			self.ui.buttonApply.setEnabled(0)
			self.ui.Message.setText(_fromUtf8("Gpu non supporté\nOverclock desactivé"))
		if info != "":
			QMessageBox.warning(self, _fromUtf8("Warning"),_fromUtf8(info))
		majGpu(0,self)
		self.ui.SliderShader.setEnabled(0)
	
	def loadProfile(self,path="",defaultOnly=False):
		if path == "":
			profileFileName = QtGui.QFileDialog.getOpenFileName(self,'Ouvrir profil',"","*.ndi") 
			if profileFileName == '':
				return 0
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
		if not error and not defaultOnly:
			if float(self.nvidiuxVersion) < float(versionElement[0].firstChild.nodeValue):
				reply = QtGui.QMessageBox.question(self, _fromUtf8("Version"),_fromUtf8("Le profil est pour une version plus recente de Nvidiux\nCharger tous de même ?"), QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)
				if reply == QtGui.QMessageBox.No:
					errorCode = 11
			i = 0
			if self.nbGpuNvidia == len(listgpu):
				try:
					for tempgpu in listgpu:
						if str(self.tabGpu[i].nameGpu) != str(tempgpu[0]):
							errorCode = 12
						if int(tempgpu[1]) < int((self.tabGpu[i].defaultFreqGpu)) * 0.85 or int(tempgpu[1]) > int((self.tabGpu[i].defaultFreqGpu)) * 1.25:
							errorCode = 13
						if int(tempgpu[2]) < int((self.tabGpu[i].defaultFreqShader)) * 0.85 or int(tempgpu[2]) > int((self.tabGpu[i].defaultFreqShader)) * 1.25:
							errorCode = 14
						if int(tempgpu[3]) < int((self.tabGpu[i].defaultFreqMem)) * 0.85 or int(tempgpu[3]) > int((self.tabGpu[i].defaultFreqMem)) * 1.25:
							errorCode = 15
						i = i + 1
				except:
					self.showError(21,"Échec","Échec chargement du profil",self.error)
			else:
				error = 16
		if errorCode != 0:
			self.showError(errorCode ,"Échec","Échec chargement du profil",self.error)
		i = 0
		for tempgpu in listgpu:
			if not defaultOnly:
				self.tabGpu[i].freqGpu = int(tempgpu[1])
				self.tabGpu[i].freqShader = int(tempgpu[2])
				self.tabGpu[i].freqMem = int(tempgpu[3])
				self.ui.lcdGPU.display(self.tabGpu[self.numGpu].freqGpu)
				self.ui.lcdMem.display(self.tabGpu[self.numGpu].freqMem)
				self.ui.lcdShader.display(self.tabGpu[self.numGpu].freqShader)
				self.ui.SliderGpu.setSliderPosition(self.tabGpu[self.numGpu].freqGpu)
				self.ui.SliderShader.setSliderPosition(self.tabGpu[self.numGpu].freqShader)
				self.ui.SliderMem.setSliderPosition(self.tabGpu[self.numGpu].freqMem)
				self.applyNewClock()
			else:
				self.tabGpu[i].defaultFreqGpu = int(tempgpu[1])
				self.tabGpu[i].defaultFreqShader = int(tempgpu[2])
				self.tabGpu[i].defaultFreqMem = int(tempgpu[3])
		return 0
		
	def overclock(self,mode):
		success = False
		i = 0
		for gpu in self.tabGpu:
			offsetGpu = int(self.tabGpu[i].freqGpu) - int(self.tabGpu[i].defaultFreqGpu)
			offsetShader = int(self.tabGpu[i].freqShader) - int(self.tabGpu[i].defaultFreqShader)
			offsetMem = int(self.tabGpu[i].freqMem) - int(self.tabGpu[i].defaultFreqMem)
			cmd = "nvidia-settings -a \"[gpu:" + str(i) + "]/GPUGraphicsClockOffset[2]=" + str(offsetGpu) + "\" -a \"[gpu:" + str(i) + "]/GPUMemoryTransferRateOffset[2]=" + str(offsetMem) + "\" >> /dev/null 2>&1 ;echo $?"
			if not sub.call(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True):
				success = True
			else:
				success = False
				break						
		if success:
			if mode == "1":
				self.showError(0,"Effectué","Changement effectué",self.info)
				self.ui.Message.setText(_fromUtf8("Changement effectué"))
			else:
				self.showError(0,"Effectué","Reset effectué",self.info)
				self.ui.Message.setText(_fromUtf8("Reset effectué"))
			self.change = 0
			self.ui.label_Dfreq_Gpu.setText(str(self.tabGpu[self.numGpu].freqGpu) + _fromUtf8("Mhz →"))
			self.ui.label_Dfreq_Shader.setText(str(self.tabGpu[self.numGpu].freqShader) + _fromUtf8("Mhz →"))
			self.ui.label_Dfreq_Mem.setText(str(self.tabGpu[self.numGpu].freqMem) + _fromUtf8("Mhz →"))
		else:
			if mode == "1":
				return self.showError(8,"Echec","L'overclock à échoué",self.error)
			else:
				return self.showError(9,"Echec","Le reset à échoué",self.error)
				
	def quitapp(self):
		if self.change:
			reply = QtGui.QMessageBox.question(self, _fromUtf8("Message"),_fromUtf8("Etes vous sur de vouloir quitter sans appliquer les modifications ?"), QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)
			if reply == QtGui.QMessageBox.Yes:
				self.threadInfoGpu.stop()
				time.sleep(0.5)
				self.close()
			else:
				self.applyNewClock()
		else:
			self.threadInfoGpu.stop()
			time.sleep(0.5)
			self.close()
			
	def reset(self):
		for i in range(0, self.nbGpuNvidia):
			self.tabGpu[i].freqShader = self.tabGpu[i].defaultFreqShader 
			self.tabGpu[i].freqGpu = self.tabGpu[i].defaultFreqGpu
			self.tabGpu[i].freqMem = self.tabGpu[i].defaultFreqMem
			self.updateGpu(int(self.tabGpu[i].defaultFreqGpu))
			self.updateMem(int(self.tabGpu[i].defaultFreqMem))
			self.ui.SliderGpu.setSliderPosition(int(self.tabGpu[i].defaultFreqGpu))
			self.ui.SliderShader.setSliderPosition(int(self.tabGpu[i].defaultFreqShader))
			self.ui.SliderMem.setSliderPosition(int(self.tabGpu[i].defaultFreqMem))
			self.ui.label_Dfreq_Gpu.setText(str(self.tabGpu[i].defaultFreqGpu) + _fromUtf8("Mhz →"))
			self.ui.label_Dfreq_Shader.setText(str(self.tabGpu[i].defaultFreqShader) + _fromUtf8("Mhz →"))
			self.ui.label_Dfreq_Mem.setText(str(self.tabGpu[i].defaultFreqMem) + _fromUtf8("Mhz →"))
		self.overclock("0")
		self.change = 0
		self.ui.Message.setText(_fromUtf8("Reset effectué"))
		
	
	def resizeEvent(self, event):
		self.showNormal()
		
	def stateFan(self,value):
		if value:
			cmd = "nvidia-settings -a [gpu:" + str(self.numGpu) + "]/GPUFanControlState=1"
			if sub.call(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True):
				self.ui.SliderFan.setEnabled(False)
				self.ui.checkBoxFan.setChecked(False)
				self.showError(-1,"Impossible","Impossible de changer la configuration des ventillos",self.warning)
			else:
				cmd = "nvidia-settings --query [fan:" + str(self.numGpu) + "]/GPUCurrentFanSpeed"
				if not sub.call(cmd ,stdout=sub.PIPE,stderr=sub.PIPE,shell=True):
					out, err = sub.Popen(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True).communicate()
					self.tabGpu[self.numGpu].fanSpeed = out.split(': ')[1].split('.')[0]
				else:
					self.tabGpu[self.numGpu].fanSpeed = 30
				self.ui.SliderFan.setEnabled(True)
				self.ui.SliderFan.setSliderPosition(int(self.tabGpu[self.numGpu].fanSpeed))
				self.ui.labelFanVitesse.setText(str(self.tabGpu[self.numGpu].fanSpeed)+ "%")
	
		else:
			cmd = "nvidia-settings -a [gpu:" + str(self.numGpu) + "]/GPUFanControlState=0"
			if sub.call(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True):
				self.ui.SliderFan.setEnabled(True)
				self.ui.checkBoxFan.setChecked(True)
				self.showError(-1,"Impossible","Impossible de revenir a la configuration par defaut des ventillos",self.warning)
			else:
				self.ui.SliderFan.setEnabled(False)
				self.ui.labelFanVitesse.setText("Auto")
	def startMonitor(self):
		print "todo monitor interface"
		
	def stateVSync(self,value):
		if value:
			cmd = "nvidia-settings -a SyncToVBlank=1"
			if not sub.call(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True):
				self.ui.checkBoxVSync.setChecked(True)
				self.ui.Message.setText(_fromUtf8("Vsync Actif"))
			else:
				self.ui.checkBoxVSync.setChecked(False)
				self.showError(-1,"Impossible","Impossible d'activer la syncro vertical",self.warning)
		else:
			cmd = "nvidia-settings -a SyncToVBlank=0"
			if not sub.call(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True):
				self.ui.checkBoxVSync.setChecked(False)
				self.ui.Message.setText(_fromUtf8("Vsync Inactif"))
			else:
				self.ui.checkBoxVSync.setChecked(True)
				self.showError(-1,"Impossible","Impossible de desactiver la syncro vertical",self.warning)
	
	def saveProfile(self,path=""):
		if path == "":
			filename = QtGui.QFileDialog.getSaveFileName(self, "Save file", str(self.tabGpu[0].nameGpu) + "-" + str(self.tabGpu[0].freqGpu) + " Mhz.ndi", "*.ndi")
			if filename[-4:] != ".ndi":
				filename = filename + ".ndi"
		else:
			filename = path
		fileToSave = minidom.Document()
		racine = fileToSave.createElement("nvidiux")
		fileToSave.appendChild(racine)
		version = fileToSave.createElement('version')
		text = fileToSave.createTextNode(str(self.nvidiuxVersion))
		version.appendChild(text)
		racine.appendChild(version)
		for tempgpu in self.tabGpu:
			gpuNode = fileToSave.createElement('gpu')
			
			name = fileToSave.createElement('name')
			text = fileToSave.createTextNode(str(tempgpu.nameGpu))
			name.appendChild(text)
			
			freq = fileToSave.createElement('gpufreq')
			text = fileToSave.createTextNode(str(tempgpu.freqGpu))
			freq.appendChild(text)
			
			shader = fileToSave.createElement('shader')
			text = fileToSave.createTextNode(str(tempgpu.freqShader))
			shader.appendChild(text)
			
			mem = fileToSave.createElement('mem')
			text = fileToSave.createTextNode(str(tempgpu.freqMem))
			mem.appendChild(text)
			
			
			gpuNode.appendChild(name)
			gpuNode.appendChild(freq)
			gpuNode.appendChild(shader)
			gpuNode.appendChild(mem)
			racine.appendChild(gpuNode)
			
		try:	
			filexml = open(filename, "w")
			filexml.write(fileToSave.toprettyxml())
			filexml.close()
		except:
			return 1
		return 0

	def showError(self,errorCode,title,errorMsg,etype):
		if etype == self.error:
			errorMsg = errorMsg + "\nError Code:" + str(errorCode)
			QMessageBox.critical(self, _fromUtf8(title),_fromUtf8(errorMsg))
		elif etype == self.warning:
			QMessageBox.warning(self, _fromUtf8(title),_fromUtf8(errorMsg))	
		else:
			QMessageBox.information(self, _fromUtf8(title),_fromUtf8(errorMsg))
		return errorCode
		
	def setThread(self,thread):
		self.threadInfoGpu = thread
				
	def updateshader(self,value):
		return 0
		
	def updateMem(self,value):
		self.change = 1
		self.tabGpu[self.numGpu].freqMem = value
		self.ui.lcdMem.display(value)
		self.ui.SliderMem.setSliderPosition(value)

	def updateGpu(self,value):
		self.change = 1
		self.tabGpu[self.numGpu].freqGpu = value
		if self.isFermiArch[self.numGpu]:
			self.tabGpu[self.numGpu].freqShader = value * 2
		else:
			self.tabGpu[self.numGpu].freqShader = value
		self.ui.lcdGPU.display(self.tabGpu[self.numGpu].freqGpu)
		self.ui.lcdShader.display(self.tabGpu[self.numGpu].freqShader)
		self.ui.SliderShader.setSliderPosition(self.tabGpu[self.numGpu].freqShader)
		
	def verifyGpu(self,gpuName):#-1:unknow 0:ok 1:not ok
		verified = ["GeForce GT 420M","GeForce GTX 460M","GeForce GTX 460","GeForce GTX 560 Ti","GeForce GTX 570","GeForce GTX 580","GeForce GT 620","GeForce GTX 770"]
		notWork = ["GeForce GTX TITAN Z","GeForce GTX TITAN Black","GeForce GTX TITAN","GeForce GTX 690","GeForce GTX 590"]

		if gpuName in verified:
			return 0
		if gpuName in notWork:
			return 1
		return -1	
			
if __name__ == "__main__":
	app = QApplication(sys.argv)
	locale = QLocale.system().name()
	translator=QTranslator ()
	#~ translator.load(QString("qt_") + locale,LibraryInfo.location(QLibraryInfo.TranslationsPath))
	#~ app.installTranslator(translator)
	myapp = ShipHolderApplication(sys.argv)
	threadInfoGpu = Mythread(1, majGpu, [0], {"fen":myapp})
	threadInfoGpu.setDaemon(True)
	myapp.setThread(threadInfoGpu)
	threadInfoGpu.start()
	myapp.show()
	sys.exit(app.exec_())
