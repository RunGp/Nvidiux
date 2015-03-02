# -*- coding: utf-8 -*-

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
from PyQt4 import QtCore, QtGui
from windows import Ui_MainWindow
from confirm import ConfirmWindow
from about import Ui_About
import sys
import os
import threading
import time

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
	output=os.popen("nvidia-settings --query [gpu:" + str(numGpu) + "]/GPUCoreTemp | grep GPUCore | head -1", "r").read() 
	fen.ui.Temp.setText(_fromUtf8("Température\n" + str(output.split(':')[-1].split('.')[0]) + " °C"))
	output=os.popen("nvidia-settings --query [gpu:" + str(numGpu) + "]/GPUUtilization | grep GPUUtilization | head -1", "r").read()
	fen.ui.UPCIE.setText(_fromUtf8("Utilisation Bus PCIE\n" + str(output.split('=')[-1].replace('\n','').replace(',','')) + " %"))
	fen.ui.UGPU.setText(_fromUtf8("Utilisation Gpu\n" + str(output.split('=')[1].split(',')[0]) + "%"))
	output=os.popen("nvidia-settings --query [gpu:" + str(numGpu) + "]/UsedDedicatedGPUMemory | grep UsedDedicatedGPUMemory | head -1", "r").read()
	fen.ui.UMem.setText(_fromUtf8("Utilisation Memoire\n" + str(output.split(':')[-1].split('.')[0]) + " Mo"))	

class ShipHolderApplication(QMainWindow):
	
	numGpu = 0
	tabGpu = list()
	nbGpu = -1
	nbGpuNvidia = -1
	optimus = 0
	#a = None
	change = 0
	form = ""
	
	def __init__(self,parent=None):
		super (ShipHolderApplication, self).__init__(parent)
		self.createWidgets()
		
	def resizeEvent(self, event):
		self.showNormal()
	
	def createWidgets(self):
		self.ui = Ui_MainWindow()
		self.ui.setupUi(self)
		self.initialisedata()
		self.ui.ButtonReset.connect(self.ui.ButtonReset,SIGNAL("released()"),self.reset)
		self.ui.ButtonApply.connect(self.ui.ButtonApply,SIGNAL("released()"),self.appliquer)
		self.ui.SliderShader.connect(self.ui.SliderShader, SIGNAL("sliderMoved(int)"),self.updateshader)
		self.ui.SliderMem.connect(self.ui.SliderMem, SIGNAL("sliderMoved(int)"),self.updatemem)
		self.ui.SliderGpu.connect(self.ui.SliderGpu, SIGNAL("sliderMoved(int)"),self.updategpu)
		self.ui.actionQuitter.connect(self.ui.actionQuitter, SIGNAL("triggered()"),self.quitapp)
		self.ui.actionAbout.connect(self.ui.actionAbout, SIGNAL("triggered()"),self.about)
		self.ui.listWidgetGpu.itemClicked.connect(self.changeGpu)

		if int(os.popen("vainfo | wc -l", "r").read().replace('\n','')) > 6:
			self.ui.checkBoxVaapi.setChecked(1)
		i = 0
		for gpu in self.tabGpu:
			self.ui.listWidgetGpu.addItem(str(i + 1) + ":" + gpu.nameGpu)
			i = i + 1
	
	def closeEvent(self, event):
		if self.change:
			reply = QtGui.QMessageBox.question(self, _fromUtf8("Message"),_fromUtf8("Etes vous sur de vouloir quitter sans appliquer les modifications ?"), QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)
			if reply == QtGui.QMessageBox.Yes:
				self.a.stop()
				time.sleep(0.5)
				event.accept()
			else:
				event.ignore()
		else:
			self.a.stop()
			time.sleep(0.5)
			event.accept()

	def verifyGpu(self,gpuName):#-1:unknow 0:ok 1:not ok
		verified = ["GeForce GT 420M","GeForce GTX 460M","GeForce GTX 460","GeForce GTX 570","GeForce GTX 560 Ti","GeForce GT 620"]
		notWork = ["GeForce GTX TITAN Z","GeForce GTX TITAN Black","GeForce GTX TITAN","GeForce GTX 690","GeForce GTX 590"]

		if gpuName in verified:
			return 0
		if gpuName in notWork:
			return 1
		return -1
	
	def overclock(self,mode):
		offsetGpu = int(self.tabGpu[self.numGpu].freqGpu) - int(self.tabGpu[self.numGpu].defaultFreqGpu)
		offsetShader = int(self.tabGpu[self.numGpu].freqShader) - int(self.tabGpu[self.numGpu].defaultFreqShader)
		offsetMem = int(self.tabGpu[self.numGpu].freqMem) - int(self.tabGpu[self.numGpu].defaultFreqMem)
		cmd = "nvidia-settings -a \"[gpu:" + str(self.numGpu) + "]/GPUGraphicsClockOffset[2]=" + str(offsetGpu) + "\" -a \"[gpu:" + str(self.numGpu) + "]/GPUMemoryTransferRateOffset[2]=" + str(offsetMem) + "\" >> /dev/null 2>&1 ;echo $?"
		result = os.popen(cmd, "r").read()
		if int(result) == 0:
			if mode == "1":
				QMessageBox.information(self, _fromUtf8("Effectué"),_fromUtf8("Changement effectué"))
			else:
				QMessageBox.information(self, _fromUtf8("Effectué"),_fromUtf8("Reset effectué"))
			self.change = 0
			self.ui.label_Dfreq_Gpu.setText(str(self.tabGpu[self.numGpu].freqGpu) + _fromUtf8("Mhz →"))
			self.ui.label_Dfreq_Shader.setText(str(self.tabGpu[self.numGpu].freqShader) + _fromUtf8("Mhz →"))
			self.ui.label_Dfreq_Mem.setText(str(self.tabGpu[self.numGpu].freqMem) + _fromUtf8("Mhz →"))
			self.ui.Message.setText(_fromUtf8("Changement effectué"))
		else:
			if mode == "1":
				QMessageBox.critical(self, _fromUtf8("Echec"),_fromUtf8("L'overclock à échoué"))
			else:
				QMessageBox.information(self, _fromUtf8("Echec"),_fromUtf8("Le reset à echoué"))
				
	def appliquer(self):
		self.form = ConfirmWindow(_fromUtf8("Confirmation( " + str(self.tabGpu[self.numGpu].nameGpu) + "," + str((self.numGpu+1)) + " )\nGpu : " + str(self.tabGpu[self.numGpu].freqGpu) + " Mhz\nShader : " + str(self.tabGpu[self.numGpu].freqShader) + " Mhz\nMémoire : " + str(self.tabGpu[self.numGpu].freqMem) + " Mhz"))
		self.connect(self.form, SIGNAL("accept(PyQt_PyObject)"), self.overclock)
		self.form.show()
	
	def reset(self):
		for i in range(0, self.nbGpuNvidia):
			self.tabGpu[i].freqShader = self.tabGpu[i].defaultFreqShader 
			self.tabGpu[i].freqGpu = self.tabGpu[i].defaultFreqGpu
			self.tabGpu[i].freqMem = self.tabGpu[i].defaultFreqMem
			print self.tabGpu[i].defaultFreqMem + self.tabGpu[i].defaultFreqMem + self.tabGpu[i].defaultFreqMem
			self.updateshader(int(self.tabGpu[i].defaultFreqShader))
			self.updatemem(int(self.tabGpu[i].defaultFreqMem))
			self.ui.SliderShader.setSliderPosition(int(self.tabGpu[i].defaultFreqShader))
			self.ui.SliderMem.setSliderPosition(int(self.tabGpu[i].defaultFreqMem))
			self.ui.label_Dfreq_Gpu.setText(str(self.tabGpu[i].defaultFreqGpu) + _fromUtf8("Mhz →"))
			self.ui.label_Dfreq_Shader.setText(str(self.tabGpu[i].defaultFreqShader) + _fromUtf8("Mhz →"))
			self.ui.label_Dfreq_Mem.setText(str(self.tabGpu[i].defaultFreqMem) + _fromUtf8("Mhz →"))
		self.overclock("0")
		self.change = 0
		self.ui.Message.setText(_fromUtf8("Reset effectué"))

	def quitapp(self):
		if self.change:
			reply = QtGui.QMessageBox.question(self, _fromUtf8("Message"),_fromUtf8("Etes vous sur de vouloir quitter sans appliquer les modifications ?"), QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)
			if reply == QtGui.QMessageBox.Yes:
				self.a.stop()
				time.sleep(0.5)
				self.close()
		else:
			self.a.stop()
			time.sleep(0.5)
			self.close()
			
	def about(self):
		self.form = Ui_About()
		self.form.show()
	
	def setThread(self,a):
		self.a = a
		
	def changeGpu(self,item):
		self.numGpu = int(item.text().split(':')[0]) - 1
		self.a.stop()
		self.a = Mythread(1, majGpu, [self.numGpu], {"fen":myapp})
		self.a.setDaemon(True)
		self.a.start()
		self.ui.lcdShader.display(self.tabGpu[self.numGpu].freqShader)
		self.ui.SliderShader.setSliderPosition(self.tabGpu[self.numGpu].freqShader)
		self.ui.SliderMem.setSliderPosition(int(self.tabGpu[self.numGpu].freqMem))
		self.ui.lcdMem.display(int(self.tabGpu[self.numGpu].freqMem))
		self.ui.SliderGpu.setSliderPosition(int(self.tabGpu[self.numGpu].freqGpu))
		self.ui.lcdGPU.display(int(self.tabGpu[self.numGpu].freqGpu))
		self.ui.NomGpu.setText(self.tabGpu[self.numGpu].nameGpu)
		self.ui.MemGpu.setText(_fromUtf8("Memoire video\n" + str(self.tabGpu[self.numGpu].videoRam) + " Go"))
		self.ui.CudaCore.setText(_fromUtf8("NB coeur cuda\n" + str(self.tabGpu[self.numGpu].cudaCores)))
		self.ui.PiloteVersion.setText(_fromUtf8("Version du Pilote\n" + str(self.tabGpu[self.numGpu].version)))
		self.ui.OpenGlSupport.setText(_fromUtf8("OpenGl Support\n"	+ str(self.tabGpu[self.numGpu].openGlVersion)))
		self.ui.label_Dfreq_Gpu.setText(str(self.tabGpu[self.numGpu].defaultFreqGpu) + _fromUtf8("Mhz →"))
		self.ui.label_Dfreq_Shader.setText(str(self.tabGpu[self.numGpu].defaultFreqShader) + _fromUtf8("Mhz →"))
		self.ui.label_Dfreq_Mem.setText(str(self.tabGpu[self.numGpu].defaultFreqMem) + _fromUtf8("Mhz →"))
			
	def updateshader(self,valeur):
		self.change = 1
		self.tabGpu[self.numGpu].freqShader = valeur
		self.tabGpu[self.numGpu].freqGpu = valeur / 2
		self.ui.lcdShader.display(self.tabGpu[self.numGpu].freqShader)
		self.ui.lcdGPU.display(self.tabGpu[self.numGpu].freqGpu)
		self.ui.SliderGpu.setSliderPosition(self.tabGpu[self.numGpu].freqGpu)
		
	def updatemem(self,valeur):
		self.change = 1
		self.tabGpu[self.numGpu].freqMem = valeur
		self.ui.lcdMem.display(valeur)
		
	def updategpu(self,valeur):
		self.change = 1
		self.tabGpu[self.numGpu].freqGpu = valeur
		self.tabGpu[self.numGpu].freqShader = valeur * 2
		self.ui.lcdGPU.display(self.tabGpu[self.numGpu].freqGpu)
		self.ui.lcdShader.display(self.tabGpu[self.numGpu].freqShader)
		self.ui.SliderShader.setSliderPosition(self.tabGpu[self.numGpu].freqShader)
		
	def iscompaptible(self):
		if os.popen("dpkg -l | grep nvidia-3", "r").read()[0:2] != "ii":
			QMessageBox.critical(self, _fromUtf8("Non supporté"),_fromUtf8("Drivers introuvable \nveuillez installer les pilotes proprietaires"))
			return 1
		if os.popen("file /usr/bin/nvidia-settings", "r").read().find('executable') == -1:
			QMessageBox.critical(self, _fromUtf8("Non supporté"),_fromUtf8("Nvidia settings introuvable \nveuillez installer les pilotes proprietaires et nvidia settings"))
			return 1
		ListeGpu = os.popen("lspci -vnn | egrep 'VGA|3D'", "r").read()
		self.nbGpuNvidia = ListeGpu.count('NVIDIA')
		self.nbGpu = len(ListeGpu)

		if self.nbGpu >= 2: #MultiGpu
			if ListeGpu.count('Intel') == 1 and self.nbGpuNvidia == 1 : #optimus
				if os.popen("prime-supported 2>> /dev/null", "r").read().replace('\n','') != "yes":
					QMessageBox.critical(self, _fromUtf8("Non supporté"),_fromUtf8("Seul prime est supporté pour les configurations optimus"))
					return 1
				if os.popen("prime-select query", "r").read().replace('\n','') != "nvidia":
					QMessageBox.information(self, _fromUtf8("Mode intel"),_fromUtf8("Configuration Prime\nVeuillez passer en mode nvidia svp"))
					return 1
				self.optimus = 1
				self.ui.checkBoxOptimus.setChecked(1)
			if self.nbGpuNvidia == 0:
				QMessageBox.critical(self, _fromUtf8("Non supporté"),_fromUtf8("Gpu nvidia introuvable !"))	
				return 1
		Xorg = 0
		if not os.path.isfile("/etc/X11/xorg.conf"):
			reply = QtGui.QMessageBox.question(self, _fromUtf8("Xorg.conf"),_fromUtf8("Pas de fichier xorg.conf en générer un ?"), QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)
			if reply == QtGui.QMessageBox.No:
				QMessageBox.critical(self, _fromUtf8("Erreur"),_fromUtf8("Vous n'avez pas de fichier xorg.conf"))
				return 1
			else:
				os.popen("bash /usr/share/nvidiux/toRoot.sh >> /dev/null 2>&1 ;echo $?", "r").read()
				if int(os.popen("touch /tmp/.reboot_nvidiux;echo $?", "r").read()) == 0:
					QMessageBox.information(self, _fromUtf8("Redémarrage Requis"),_fromUtf8("Configuration effectué\nVous devez redémarrer votre machine"))
					return 2
				else:
					QMessageBox.critical(self, _fromUtf8("Erreur"),_fromUtf8("Erreur 5 configuration !"))
					return 1

		if Xorg == 0 and int(os.popen("cat /etc/X11/xorg.conf | grep Coolbits | wc -l", "r").read()) == 0:
			QMessageBox.information(self, _fromUtf8("Configuration"),_fromUtf8("La configuration du fichier xorg n'est pas effectué !\nEntrer votre mot de passe administrateur pour effectuer la configuration"))
			if int(os.popen("bash /usr/share/nvidiux/toRoot.sh >> /dev/null 2>&1 ;echo $?", "r").read()) != 0:
				QMessageBox.critical(self, _fromUtf8("Erreur"),_fromUtf8("Votre mot de passe est incorrect"))
				return 1
			else:
				if int(os.popen("touch /tmp/.reboot_nvidiux;echo $?", "r").read()) == 0:
					QMessageBox.information(self, _fromUtf8("Redémarrage Requis"),_fromUtf8("Configuration effectué\nVous devez redémarrer votre machine"))
					return 2
				else:
					QMessageBox.critical(self, _fromUtf8("Erreur"),_fromUtf8("Erreur 5 configuration !"))
					return 1
		else:
			if os.path.isfile("/tmp/.reboot_nvidiux"):
				QMessageBox.information(self, _fromUtf8("Redémarrage Requis"),_fromUtf8("Configuration effectué\nVous devez redémarrer votre machine"))
				return 2
		return 0

	def initialisedata(self):
		compaptibility = self.iscompaptible()
		if compaptibility == 1:
			sys.exit(1)
		if compaptibility == 2:
			print "Please reboot"
			sys.exit(0)

		output=os.popen("nvidia-settings --query [gpu:0]/NvidiaDriverVersion", "r").read() #priorité verifier version driver
		versionPilote = float(output.split(':')[-1][1:])
		info = ""
		if versionPilote > 346.35:
			info = "Driver non testé\n"
		
		
		if versionPilote <= 337.12:
			self.ui.SliderMem.setEnabled(0)
			self.ui.SliderGpu.setEnabled(0)
			self.ui.SliderShader.setEnabled(0)
			self.ui.ButtonReset.setEnabled(0)
			self.ui.ButtonApply.setEnabled(0)
			self.ui.Message.setText(_fromUtf8("Driver non supporté (trop ancien)!\nOverclock desactivé"))
			QMessageBox.information(self, _fromUtf8("Driver"),_fromUtf8("Driver non supporté:trop ancien\nOverclock desactivé\nIl vous faut la version 337.19 ou plus recent pour overclocker"))
		for i in range(0, self.nbGpuNvidia):
			self.tabGpu.append(Gpuinfo())
			if i == 0:#si un seul pas de retour ligne
				output=os.popen("lspci -vnn | grep NVIDIA | head -n " + str(i + 1), "r").read()
			else:
				output=os.popen("lspci -vnn | grep NVIDIA | head -n " + str(i + 1), "r").read().split('\n')[-1]
			self.tabGpu[i].nameGpu = output.split(':')[-2].split('[')[-2].split(']')[0]		
			output=os.popen("nvidia-settings --query [gpu:" + str(i) + "]/videoRam", "r").read()
			self.tabGpu[i].videoRam=float(output.split(': ')[1].split('.')[0]) / 1048576
			output=os.popen("nvidia-settings --query [gpu:" + str(i) + "]/cudaCores", "r").read()
			self.tabGpu[i].cudaCores = output.split(': ')[1].split('.')[0]
			output=os.popen("nvidia-settings --query [gpu:" + str(i) + "]/GPUPerfModes | grep memTransferRatemax= | tail -1", "r").read()
			self.tabGpu[i].freqMem = output.split(',')[1].split('=')[1]
			output=os.popen("nvidia-settings --query [gpu:" + str(i) + "]/NvidiaDriverVersion", "r").read()
			self.tabGpu[i].version = float(output.split(':')[-1][1:])
			output=os.popen("nvidia-settings --query all | grep OpenGLVersion | head -1", "r").read()
			self.tabGpu[i].openGlVersion = output.split('NVIDIA')[0].split(':')[-1]
			if versionPilote <= 343.113:
				output=os.popen("nvidia-settings --query [gpu:" + str(i) + "]/GPU3DClockFreqs", "r").read()
			else:
				output=os.popen("nvidia-settings --query all | grep GPUCurrentClockFreqs | head -1", "r").read()
			self.tabGpu[i].freqGpu = output.split(': ')[1].split(',')[0]
			output=os.popen("nvidia-settings --query [gpu:" + str(i) + "]/GPUCurrentProcessorClockFreqs | head -2", "r").read()
			self.tabGpu[i].freqShader = output.split(': ')[1].split('.')[0]
	
			self.tabGpu[i].defaultFreqShader = self.tabGpu[i].freqShader
			self.tabGpu[i].defaultFreqGpu = self.tabGpu[i].freqGpu
			self.tabGpu[i].defaultFreqMem = self.tabGpu[i].freqMem
			
		self.ui.label_Img.setPixmap(QtGui.QPixmap("/usr/share/nvidiux/img/drivers_nvidia_linux.png"))	
		self.ui.SliderShader.setMinimum(int(self.tabGpu[self.numGpu].freqShader) * 0.9)
		self.ui.SliderShader.setMaximum(int(self.tabGpu[self.numGpu].freqShader) * 1.25)
		self.ui.SliderShader.setSliderPosition(int(self.tabGpu[self.numGpu].freqShader))
		self.ui.lcdShader.display(int(self.tabGpu[self.numGpu].freqShader))
		
		self.ui.SliderMem.setMinimum(int(self.tabGpu[self.numGpu].freqMem) * 0.9)
		self.ui.SliderMem.setMaximum(int(self.tabGpu[self.numGpu].freqMem) * 1.2)
		self.ui.SliderMem.setSliderPosition(int(self.tabGpu[self.numGpu].freqMem))
		self.ui.lcdMem.display(int(self.tabGpu[self.numGpu].freqMem))
		
		self.ui.SliderGpu.setMinimum(int(self.tabGpu[self.numGpu].freqGpu) * 0.9)
		self.ui.SliderGpu.setMaximum(int(self.tabGpu[self.numGpu].freqGpu) * 1.25)
		self.ui.SliderGpu.setSliderPosition(int(self.tabGpu[self.numGpu].freqGpu))
		self.ui.lcdGPU.display(int(self.tabGpu[self.numGpu].freqGpu))
		
		self.ui.label_Dfreq_Gpu.setText(str(self.tabGpu[self.numGpu].defaultFreqGpu) + _fromUtf8("Mhz →"))
		self.ui.label_Dfreq_Shader.setText(str(self.tabGpu[self.numGpu].defaultFreqShader) + _fromUtf8("Mhz →"))
		self.ui.label_Dfreq_Mem.setText(str(self.tabGpu[self.numGpu].defaultFreqMem) + _fromUtf8("Mhz →"))
		self.ui.NomGpu.setText(self.tabGpu[self.numGpu].nameGpu)

		self.ui.MemGpu.setText(_fromUtf8("Memoire video\n" + str(self.tabGpu[self.numGpu].videoRam) + " Go"))
		self.ui.CudaCore.setText(_fromUtf8("NB coeur cuda\n" + str(self.tabGpu[self.numGpu].cudaCores)))
		self.ui.PiloteVersion.setText(_fromUtf8("Version du Pilote\n" + str(versionPilote)))
		self.ui.OpenGlSupport.setText(_fromUtf8("OpenGl Support\n" + str(self.tabGpu[self.numGpu].openGlVersion)))
		self.ui.checkBoxSli.setChecked(0)
		if self.nbGpuNvidia >= 2:#detect sli 2 card with same name
			if len(list(set(self.tabGpu[i].nameGpu))) == 1:
				self.ui.checkBoxSli.setChecked(1)
		i = self.verifyGpu(self.tabGpu[0].nameGpu)
		if i == -1:
			info = info + "Ce gpu n'est pas dans la base des gpu compaptible"
		if i == 1:
			info = info + "Ce gpu n'est pas compaptible"
			self.ui.SliderMem.setEnabled(0)
			self.ui.SliderGpu.setEnabled(0)
			self.ui.SliderShader.setEnabled(0)
			self.ui.ButtonReset.setEnabled(0)
			self.ui.ButtonApply.setEnabled(0)
			self.ui.Message.setText(_fromUtf8("Gpu non supporté!\nOverclock desactivé"))
		if info != "":
			QMessageBox.warning(self, _fromUtf8("Warning"),_fromUtf8(info))	
		majGpu(0,self)
			
if __name__ == "__main__":
	app = QApplication(sys.argv)
	locale = QLocale.system().name()
	translator=QTranslator ()
	"""translator.load(QString("qt_") + locale,LibraryInfo.location(QLibraryInfo.TranslationsPath))
	app.installTranslator(translator)"""
	myapp = ShipHolderApplication()
	
	a = Mythread(1, majGpu, [0], {"fen":myapp})
	a.setDaemon(True)
	myapp.setThread(a)
	a.start()
	myapp.show()
	sys.exit(app.exec_())
