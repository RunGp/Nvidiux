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


from PyQt4.QtCore import *
from PyQt4.QtGui import *
from xml.dom import minidom
from PyQt4 import QtCore, QtGui
from Ui_Nvidiux import Ui_MainWindow
from confirm import ConfirmWindow
from preference import Ui_Pref
from preference import Settings
from os.path import expanduser
from donate import DonateWindow
import subprocess as sub
import sys
import os
import threading
import time
import psutil
import getopt
import platform
import re
import urllib

muttex = threading.RLock()

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

class Gpuinfo():
	defaultFreqShader = 0
	defaultFreqGpu = 0
	defaultFreqMem = 0
	resetFreqShader = 0
	resetFreqGpu = 0
	resetFreqMem = 0
	freqShader = 0
	freqGpu = 0
	freqMem = 0 
	fanSpeed = 0
	overvolt = 0
	maxOvervolt = 0
	nameGpu = ""
	videoRam = ""
	memInterface = ""
	cudaCores = ""
	openGlVersion = ""
	vulkanVersion = ""
	arch = ""
	uuid = ""
	isCompatible = False
	
class ThreadCheckMonitor(threading.Thread):
 
    def __init__(self,args=[], kwargs={}):
        threading.Thread.__init__(self)
        self.args = args
        self.kwargs = kwargs
        self.infinite = True 
        self.timer = None
 
    def run(self,args=0):
        while self.infinite:
            self.timer = threading.Timer(1, checkMonitor, self.args, self.kwargs)
            self.timer.setDaemon(True)
            self.timer.start()
            self.timer.join()
 
    def stop(self):
        self.infinite = False
        if self.timer != None:
		if self.timer.isAlive():
		    self.timer.cancel()

class Mythread(threading.Thread):
 
    def __init__(self, duree, fonction,args=[], kwargs={}):
        threading.Thread.__init__(self)
        self.args = args
        self.duree = duree
        self.fonction = fonction
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
		cmd = "nvidia-settings --query [gpu:" + str(numGpu) + "]/GPUCoreTemp"
		try:
			out, err = sub.Popen(cmd + " | grep GPUCore | head -1",stdout=sub.PIPE,stderr=sub.PIPE,shell=True).communicate()
			fen.ui.Temp.setText(_translate("nvidiux","Temperature",None) + "\n" + str(out.split(':')[-1].split('.')[0]) + _fromUtf8("°C"))
		except:
			fen.ui.Temp.setText(_fromUtf8("N/A"))
	
		cmd = "nvidia-settings --query [gpu:" + str(numGpu) + "]/GPUUtilization"
		try:
			out, err = sub.Popen(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True).communicate()
			if fen.showUseGpu:
				fen.ui.UGPU.setText(_translate("nvidiux","Utilisation Gpu",None) + "\n" + str(out.split('graphics=')[1].split(',')[0]) + "%")
			else:
				fen.ui.UGPU.setText(_translate("nvidiux","Util décodage video",None)+ "\n" + str(out.split('video=')[1].split(',')[0]) + "%")
			fen.ui.UPCIE.setText(_translate("nvidiux","Utilisation Bus PCIE",None) + "\n" + str(out.split('PCIe=')[-1].replace('\n','').replace(',','')) + " %")
		except:
			fen.ui.UPCIE.setText(_fromUtf8("N/A"))
			fen.ui.UGPU.setText(_fromUtf8("N/A"))
		
		cmd = "nvidia-settings --query [gpu:" + str(numGpu) + "]/UsedDedicatedGPUMemory"
		try:
			if fen.showValueMem:
				out, err = sub.Popen(cmd + " | grep UsedDedicatedGPUMemory | head -1",stdout=sub.PIPE,stderr=sub.PIPE,shell=True).communicate()
				fen.ui.UMem.setText(_translate("nvidiux","Utilisation Memoire",None) + "\n" + str(out.split(':')[-1].split('.')[0]) + " Mo")
			else:
				out, err = sub.Popen(cmd + " | grep UsedDedicatedGPUMemory | head -1",stdout=sub.PIPE,stderr=sub.PIPE,shell=True).communicate()
				memUse = float(out.split(':')[-1].split('.')[0])
				memTot = float(fen.tabGpu[numGpu].videoRam) * 1024 
				percent = round(float(memUse * 100 / memTot),1)
				fen.ui.UMem.setText(_translate("nvidiux","Utilisation Memoire (%)",None) + "\n" + str(percent) + " %")
		except:
			fen.ui.UMem.setText(_fromUtf8("N/A"))
		
		if fen.ui.labelFanVitesse.text()[0:4] == "Auto":
			cmd = "nvidia-settings --query [fan:" + str(numGpu) + "]/GPUCurrentFanSpeed"
			out, err = sub.Popen(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True).communicate()
			try:
				value = int(out.split('.')[0].split(':')[-1])
				fen.ui.labelFanVitesse.setText(_translate("nvidiux","Auto(",None) + str(value) + "%)")
				fen.ui.SliderFan.setSliderPosition(value)
			except:
				fen.ui.labelFanVitesse.setText(_fromUtf8("???%"))
			
def checkMonitor(pid,fen):
	if not psutil.pid_exists(pid):
		fen.ui.buttonStartMonitor.setText(_translate("nvidiux","Lancer",None))
		fen.ui.actionStartMonitor.setText(_translate("nvidiux","Lancer",None))
		fen.killTMonitor()
				
class NvidiuxApp(QMainWindow):
	numGpu = 0
	tabGpu = []
	nbGpu = -1
	optimus = 0
	
	pref = Settings()
	pref.nvidiuxVersionStr = "2.0.5.46"
	pref.nvidiuxVersion = 2.0
	pref.nvidiuxVersionM = 2
	pref.updateTime = 1
	pref.startWithSystem = False
	pref.valueStart = "0:0"
	piloteVersion = "331.31"
	piloteVersionMaxTest = 396.51
	pathLibNvidia = "/usr/lib/"
	pref.language = "en_EN"
	pref.labelOs = ""
	pref.overclockEnabled = True
	pref.overvoltEnabled = False
	pref.sameParamGpu = True
	pref.monitorGen = 1
	pref.syncFan = False
	
	change = 0
	formSettings = None
	formConfirm = None
	monitor = False
	threadInfoGpu = None
	threadMonitor = None
	pidMonitor = 0
	isSli= False
	error = -1
	warning = -2
	acceptedEula = False
	info = 0
	autoUpdate = True
	showUseGpu = True
	showGraphicApi = False
	showValueMem = True
	showMemVid = True
	nvidiuxTranslator = None
	autoStartupSysOverclock = False
	autoStartupNvidiuxOverclock = False
	ndifile = None
	vaapi= False
	home = expanduser("~")
	resetAllGpu = False
	notUseNdi= False
	silent = False
	
	def __init__(self,argv,parent=None):
		super (NvidiuxApp, self).__init__(parent)
		try:                            
			opts, args = getopt.getopt(argv, "vhs:p:r", ["version","help", "silent=","pathlib=","reset","accept-eula","no-stat"])
		except getopt.GetoptError:
			if "-s" in argv:
				print "Missing ndiFile"
				print "Use nvidiux -s <ndiFile>"
			elif "--silent" in argv:
				print "Missing ndiFile"
				print "Use nvidiux --silent <ndiFile>" 
			elif "-p" in argv:
				print "Missing path"
				print "Use nvidiux -p <path to nvidia library>"
				print "ex : nvidiux -p /usr/lib/lib32/"
			elif "--pathlib" in argv:
				print "Missing path"
				print "Use nvidiux --pathlib <path to nvidia library>"
				print "ex : nvidiux --pathlib /usr/lib/lib32/"
			else:
				print "Unknown option"
				self.showHelp()
			sys.exit(2)
			
		for opt, arg in opts:
			if opt in ("-h", "--help"):
				self.showHelp()
				sys.exit(0)
				
			if opt in ("-p", "--pathlib"):
				if os.path.isdir(arg):
					self.pathLibNvidia = arg
					if os.path.isdir(self.home + "/.nvidiux/libNvidia"):
						os.unlink(self.home + "/.nvidiux/libNvidia")
				else:
					print "Unable to access this directory (please verify your path)"
					self.showHelp()
					sys.exit(3)
		
			elif opt in ("-v", "--version"):
				print "Nvidiux version : " + self.pref.nvidiuxVersionStr
				sys.exit(0)
				
			elif opt in ("-s", "--silent"):
				if os.path.isfile(arg):
					self.ndifile = arg
					self.silent = True
					print "here !"
				else:
					print "Unable to find profile file"
					self.showHelp()
					sys.exit(3)
			
			elif opt in ("--no-stat"):
				self.pref.sendStat = False
				self.notUseNdi = True
				print "NO STAT"
			
			elif opt in ("-r", "--reset"):
				self.resetAllGpu = True
				self.notUseNdi = True	 
			
			elif opt in ("--accept-eula"):
				if not os.path.isfile(self.home + "/.nvidiux/acceptedeula"):
					print "For use nvidiux you must accept this EULA :\nWarning this practice may void the warranty and remains of responsability of user software.\nThe author and community are not responsible of bad use and no liability for damages, direct or consequential, which may result from the use of Nvidiux.\nNvidiux is in no way affiliated to Nvidia"
					response = str(raw_input('Do you accept this terms (N/y):'))
					if response == "y" or response == "Y":
						self.acceptEula()
						sys.exit(0)
					else:
						self.denyEula()
				else:
					print "You already accept EULA\nnothing to do"
					sys.exit(0)
					
		if len(argv) == 1:
			if not self.notUseNdi:
				if os.path.isfile(argv[0]):
					self.ndifile = argv[0]
				else:
					print "Unable to find profile file"
					self.showHelp()
					sys.exit(3)
		self.createWidgets()
		
	def about(self):
		self.pref.gpu = self.tabGpu
		self.pref.app = app
		self.formSettings = Ui_Pref(2,self.pref,self)
		self.formSettings.show()
		
	def acceptEula(self):
		if not os.path.isfile(self.home + "/.nvidiux/acceptedeula"):
			 open(self.home + "/.nvidiux/acceptedeula", 'a').close()
		self.acceptedEula = True
	
	def applyNewClock(self):
		text = _translate("nvidiux","Confirmez vous les frequences suivante ?",None)
		i = 0
		for gpu in self.tabGpu:
			text = text + "\n" + str((i+1)) + ":" + str(self.tabGpu[i].nameGpu) + "\nGpu : " + str(self.tabGpu[i].freqGpu) + " Mhz\nMem : " + str(self.tabGpu[self.numGpu].freqMem) + " Mhz\n"
			i = i + 1
		tabLang = list()
		tabLang.append(self.pref.language)
		tabLang.append(app)	
		self.formConfirm = ConfirmWindow(text,tabLang,self.pref.nbGpuNvidia,False)
		self.formConfirm.setWindowModality(QtCore.Qt.ApplicationModal)
		self.connect(self.formConfirm, SIGNAL("accept(PyQt_PyObject)"), self.overclock)
		self.formConfirm.show()
		
	def changeGpuTo0(self):
		self.ui.buttongpu1.setEnabled(False)
		self.ui.buttongpu2.setEnabled(True)
		if self.pref.nbGpuNvidia >= 3:
			self.ui.buttongpu3.setEnabled(True)
		if self.pref.nbGpuNvidia >= 4:
			self.ui.buttongpu4.setEnabled(True)
		self.numGpu = 0
		self.changeGpu()
		
	def changeGpuTo1(self):
		self.ui.buttongpu1.setEnabled(True)
		self.ui.buttongpu2.setEnabled(False)
		if self.pref.nbGpuNvidia >= 3:
			self.ui.buttongpu3.setEnabled(True)
		if self.pref.nbGpuNvidia >= 4:
			self.ui.buttongpu4.setEnabled(True)
		self.numGpu = 1
		self.changeGpu()
		
	def changeGpuTo2(self):
		self.ui.buttongpu1.setEnabled(True)
		self.ui.buttongpu2.setEnabled(True)
		if self.pref.nbGpuNvidia >= 3:
			self.ui.buttongpu3.setEnabled(False)
		if self.pref.nbGpuNvidia >= 4:
			self.ui.buttongpu4.setEnabled(True)
		self.numGpu = 2
		self.changeGpu()
		
	def changeGpuTo3(self):
		self.ui.buttongpu1.setEnabled(True)
		self.ui.buttongpu2.setEnabled(True)
		if self.pref.nbGpuNvidia >= 3:
			self.ui.buttongpu3.setEnabled(True)
		if self.pref.nbGpuNvidia >= 4:
			self.ui.buttongpu4.setEnabled(False)
		self.numGpu = 3
		self.changeGpu()
	
	def changeGpu(self):
		self.ui.lcdShader.display(self.tabGpu[self.numGpu].freqShader)
		self.ui.SliderShader.setSliderPosition(int(self.tabGpu[self.numGpu].freqShader))
		self.ui.SliderMem.setSliderPosition(int(self.tabGpu[self.numGpu].freqMem))
		self.ui.lcdMem.display(int(self.tabGpu[self.numGpu].freqMem))
		self.ui.SliderGpu.setSliderPosition(int(self.tabGpu[self.numGpu].freqGpu))
		self.ui.lcdGPU.display(int(self.tabGpu[self.numGpu].freqGpu))
		self.ui.nomGpu.setText(self.tabGpu[self.numGpu].nameGpu)
		self.ui.MemGpu.setText(_translate("nvidiux","Memoire video",None) + "\n" + str(self.tabGpu[self.numGpu].videoRam) + " Go")
		self.ui.CudaCore.setText(_translate("nvidiux","NB coeur cuda",None) + "\n"  + str(self.tabGpu[self.numGpu].cudaCores))
		self.ui.PiloteVersion.setText(_translate("nvidiux","Version du Pilote",None) + "\n" + str(self.piloteVersion))
		self.ui.OpenGlSupport.setText(_translate("nvidiux","OpenGl Support",None) + "\n" + str(self.tabGpu[self.numGpu].openGlVersion))
		self.ui.MemGpu.setText(_translate("nvidiux","Memoire video",None) + "\n" + str(self.tabGpu[self.numGpu].videoRam) + " Go")
		self.ui.label_Dfreq_Gpu.setText(str(self.tabGpu[self.numGpu].defaultFreqGpu) + _fromUtf8(" Mhz →"))
		self.ui.label_Dfreq_Shader.setText(str(self.tabGpu[self.numGpu].defaultFreqShader) + _fromUtf8(" Mhz →"))
		self.ui.label_Dfreq_Mem.setText(str(self.tabGpu[self.numGpu].defaultFreqMem) + _fromUtf8(" Mhz →"))
		self.showGraphicApi = True
		self.valueMem = True
		self.memVid = True
		
		if self.ui.SliderFan.isEnabled():
			if self.tabGpu[self.numGpu].arch == "fermi":
				self.ui.SliderFan.setMinimum(30)
			else:
				self.ui.SliderFan.setMinimum(10)

		if not self.tabGpu[self.numGpu].isCompatible:
			self.ui.SliderMem.setEnabled(False)
			self.ui.SliderGpu.setEnabled(False)
			self.ui.SliderShader.setEnabled(False)
			self.ui.buttonReset.setEnabled(False)
			self.ui.buttonApply.setEnabled(False)
			self.ui.buttonLoadProfile.setEnabled(False)
			self.ui.buttonSaveProfile.setEnabled(False)
			self.ui.actionLoadProfile.setEnabled(False)
			self.ui.actionSaveProfile.setEnabled(False)
			self.printMessage(_translate("nvidiux","Gpu(" ,None) + str(gpu.nameGpu) + _translate("nvidiux",") non supporte",None))
			self.pref.overclockEnabled = False
		else:
			self.ui.SliderMem.setEnabled(True)
			self.ui.SliderGpu.setEnabled(True)
			self.ui.buttonLoadProfile.setEnabled(True)
			self.ui.buttonSaveProfile.setEnabled(True)
			self.ui.actionLoadProfile.setEnabled(True)
			self.ui.actionSaveProfile.setEnabled(True)
			self.printMessage(_translate("nvidiux","",None))
			self.pref.overclockEnabled = True
			if self.pref.overvoltEnabled and self.piloteVersion >= 346.16:
				self.ui.spinBoxOvervolt.setMaximum(self.tabGpu[self.numGpu].maxOvervolt)
				self.ui.labelValueOvervolt.setText(str(self.tabGpu[self.numGpu].overvolt) + _translate("nvidiux","μv",None))
				if self.tabGpu[self.numGpu].maxOvervolt == 0:
					self.ui.groupBoxOvervolt.setEnabled(False)
		if self.pref.autoUpdate:
			self.threadInfoGpu.stop()
			self.threadInfoGpu = Mythread(1, majGpu, [self.numGpu], {"fen":nvidiuxApp})
			self.threadInfoGpu.setDaemon(True)
			self.threadInfoGpu.start()
		
	def closeEvent(self, event):
		if self.change:
			reply = QtGui.QMessageBox.question(self,_translate("nvidiux","Message",None),_translate("nvidiux","Etes vous sur de vouloir quitter sans appliquer les modifications ?",None), QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)
			if reply == QtGui.QMessageBox.Yes:
				if self.threadMonitor != None:
					self.threadMonitor.stop()
				if self.pref.autoUpdate:
					self.threadInfoGpu.stop()
					time.sleep(0.5)
				self.saveNvidiuxConf()
				event.accept()
			else:
				event.ignore()
				self.applyNewClock()
		else:
			if self.threadMonitor != None:
				self.threadMonitor.stop()
			if self.pref.autoUpdate:
				self.threadInfoGpu.stop()
				time.sleep(0.5)
			self.saveNvidiuxConf()
			event.accept()
	
	def createWidgets(self):
		self.ui = Ui_MainWindow()
		self.ui.setupUi(self)
		if os.path.isdir(self.home + "/.nvidiux/libNvidia"):
			self.pathLibNvidia = os.path.realpath(self.home + "/.nvidiux/libNvidia")
		result = self.getVersionSupport()
		driver = float(result.split('|')[0])
		nvidiuxUpdate = result.split('|')[1]
		nvidiuxUpdateG = float(nvidiuxUpdate.split('.')[0] + "." + nvidiuxUpdate.split('.')[1])
		nvidiuxUpdateM =  int(nvidiuxUpdate.split('.')[2])
		
		if nvidiuxUpdateG > self.pref.nvidiuxVersion:
			self.ui.checkVersion.setText(_translate("MainWindow", "Une nouvelle version est dispo (", None) + nvidiuxUpdate.replace("\n","") + " )")
		if nvidiuxUpdateG == self.pref.nvidiuxVersion and nvidiuxUpdateM > self.pref.nvidiuxVersionM:
			self.ui.checkVersion.setText(_translate("MainWindow", "Une nouvelle version est dispo (", None) + nvidiuxUpdate.replace("\n","") + " )")
		
		if driver != 0:
			self.piloteVersionMaxTest = driver
		self.initialiseData()
		if self.ndifile != None:
			if os.path.isfile(self.home + "/.nvidiux/acceptedeula"):
				if not self.silent:
					print "Load:" + self.ndifile
				else:
					print "Silent load:"  + self.ndifile
				self.loadProfile(self.ndifile)
			else:
				print "Please accept EULA first\nYou can accept this with --accept-eula option"
				sys.exit(2)	
		if self.resetAllGpu:
			self.reset()
		linuxDistrib = platform.linux_distribution()
		if linuxDistrib == ('', '', ''):
			if os.path.isfile("/etc/issue"):
				with open("/etc/issue") as f:
					self.pref.labelOs = f.read().split()[0] + " " + platform.architecture()[0]
			else:
				self.pref.labelOs = "Unknown distrib" + platform.architecture()[0]
		else:
			self.pref.labelOs = linuxDistrib[0] + " " + linuxDistrib[1] + " " + linuxDistrib[2] + " " + platform.architecture()[0]
		self.setGpuStat(1,0,0)
		self.ui.buttonReset.connect(self.ui.buttonReset,SIGNAL("released()"),self.reset)
		self.ui.buttonAbout.connect(self.ui.buttonAbout,SIGNAL("released()"),self.about)
		self.ui.buttonLoadProfile.connect(self.ui.buttonLoadProfile,SIGNAL("released()"),self.loadProfile)
		self.ui.buttonSaveProfile.connect(self.ui.buttonSaveProfile,SIGNAL("released()"),self.saveProfile)
		self.ui.buttonStartMonitor.connect(self.ui.buttonStartMonitor,SIGNAL("released()"),self.startMonitor)
		self.ui.buttonConfigureMonitor.connect(self.ui.buttonConfigureMonitor,SIGNAL("released()"),self.configureMonitor)
		self.ui.buttonOvervolt.connect(self.ui.buttonOvervolt,SIGNAL("released()"),self.overvolt)
		self.ui.buttonConfigure.connect(self.ui.buttonConfigure,SIGNAL("released()"),self.loadPrefWindow)
		self.ui.buttonApply.connect(self.ui.buttonApply,SIGNAL("released()"),self.applyNewClock)
		self.ui.buttonSwitchApi.connect(self.ui.buttonSwitchApi,SIGNAL("released()"),self.switchApi)
		self.ui.buttonSwitchUseGpu.connect(self.ui.buttonSwitchUseGpu,SIGNAL("released()"),self.switchUseGpu)
		self.ui.buttonWeb.connect(self.ui.buttonWeb,SIGNAL("released()"),self.openRapport)
		self.ui.buttonDonate.connect(self.ui.buttonDonate,SIGNAL("released()"),self.showDonate)
		self.ui.buttonSwitchUseMem.connect(self.ui.buttonSwitchUseMem,SIGNAL("released()"),self.switchValueMem)
		self.ui.buttonSwitchTypeMem.connect(self.ui.buttonSwitchTypeMem,SIGNAL("released()"),self.switchMemVid)

		self.ui.SliderMem.connect(self.ui.SliderMem, SIGNAL("sliderMoved(int)"),self.updateMem)
		self.ui.SliderGpu.connect(self.ui.SliderGpu, SIGNAL("sliderMoved(int)"),self.updateGpu)
		self.ui.SliderFan.connect(self.ui.SliderFan, SIGNAL("sliderMoved(int)"),self.changeFanSpeed)
		
		self.ui.actionQuitter.connect(self.ui.actionQuitter, SIGNAL("triggered()"),self.quitapp)
		self.ui.actionLoadProfile.connect(self.ui.actionLoadProfile, SIGNAL("triggered()"),self.loadProfile)
		self.ui.actionSaveProfile.connect(self.ui.actionSaveProfile, SIGNAL("triggered()"),self.saveProfile)
		self.ui.actionStartMonitor.connect(self.ui.actionStartMonitor, SIGNAL("triggered()"),self.startMonitor)
		self.ui.actionConfigureMonitor.connect(self.ui.actionConfigureMonitor, SIGNAL("triggered()"),self.configureMonitor)
		self.ui.actionAbout.connect(self.ui.actionAbout, SIGNAL("triggered()"),self.about)
		
		self.ui.actionPref.connect(self.ui.actionPref, SIGNAL("triggered()"),self.loadPrefWindow)
		self.ui.checkBoxVaapi.connect(self.ui.checkBoxVaapi, SIGNAL("clicked(bool)"),self.setVaapi)
		self.ui.checkBoxFan.connect(self.ui.checkBoxFan,QtCore.SIGNAL("clicked(bool)"),self.stateFan)
		self.ui.checkBoxVSync.connect(self.ui.checkBoxVSync,QtCore.SIGNAL("clicked(bool)"),self.stateVSync)
		self.ui.checkBoxMPerf.connect(self.ui.checkBoxMPerf,QtCore.SIGNAL("clicked(bool)"),self.maxPerf)
	
		try:
			cmd = "vainfo | wc -l"
			if int(sub.Popen(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True).communicate()[0].replace('\n','')) > 6:
				cmd  = "vainfo"
				result = int(str(sub.Popen(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True).communicate()).split("returns")[1].split("libva")[0].replace(' ','').replace('\\n',''))
				if result == 0:
					self.ui.checkBoxVaapi.setChecked(True)
					self.vaapi = True
				else:
					self.ui.checkBoxVaapi.setChecked(False)
					self.vaapi = False
				self.ui.checkBoxVaapi.setEnabled(False)
		except:
			self.ui.checkBoxVaapi.setChecked(False)
			self.vaapi = False
			self.ui.checkBoxVaapi.setEnabled(False)
		
		if self.vaapi:
			self.ui.buttonSwitchUseGpu.setVisible(True)
		else:
			self.ui.buttonSwitchUseGpu.setVisible(False)
		i = 0
		for gpu in self.tabGpu:
			#self.ui.listWidgetGpu.addItem(str(i + 1) + ":" + gpu.nameGpu)
			i = i + 1
		if self.pathLibNvidia != "/usr/lib/" and not os.path.isdir(self.home + "/.nvidiux/libNvidia"):
			reply = QtGui.QMessageBox.question(self,_translate("nvidiux","Modifier chemin par defaut lib nvidia",None),_translate("nvidiux","Choisir le chemin:" + self.pathLibNvidia + " par defaut pour les prochaines utilisations ?",None), QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)
			if reply == QtGui.QMessageBox.Yes:
				os.symlink(self.pathLibNvidia,self.home + "/.nvidiux/libNvidia")
				
		self.ui.groupBoxOvervolt.setVisible(True)		
		self.printMessage(str(self.pref.nbGpuNvidia) + _translate("nvidiux"," gpu nvidia detecte",None))
		if not self.pref.sendStat:
			self.printMessage(_translate("nvidiux","Statistique desactivé",None))

	def configureMonitor(self):
		self.pref.gpu = self.tabGpu
		self.pref.app = app
		self.formSettings = Ui_Pref(1,self.pref,self)
		self.formSettings.show()
		
	def changeThemes(self):
		print "Version 2.1..."
	
	def changeFanSpeed(self,value):
		if self.pref.sameParamGpu and self.pref.nbGpuNvidia > 1:
			nomGpu = self.tabGpu[self.numGpu].gpuName
			i = 0
			for gpu in self.tabGpu:
				if gpu.gpuName == nomGpu:
					if self.piloteVersion < 346.99:
						cmd = "nvidia-settings -a [fan:" + str(self.numGpu) + "]/GPUCurrentFanSpeed="+ str(value)
					else:
						cmd = "nvidia-settings -a [fan:" + str(self.numGpu) + "]/GPUTargetFanSpeed="+ str(value)
					
					if not sub.call(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True):
						self.ui.labelFanVitesse.setText(str(value) + "%")
					else:
						self.printMessage(_translate("nvidiux","Echec changement vitesse ventillo",None) + " gpu " + str(i) + ":" + nomGpu)
				i = i + 1
		else:
			if self.piloteVersion < 346.99:
				cmd = "nvidia-settings -a [fan:" + str(self.numGpu) + "]/GPUCurrentFanSpeed="+ str(value)
			else:
				cmd = "nvidia-settings -a [fan:" + str(self.numGpu) + "]/GPUTargetFanSpeed="+ str(value)
		
			if not sub.call(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True):
				self.ui.labelFanVitesse.setText(str(value) + "%")
			else:
				self.printMessage(_translate("nvidiux","Echec changement vitesse ventillo",None))			
		
	def defineDefaultFreqGpu(self,gpuName):
		try:
			if not os.path.exists(self.home + "/.nvidiux/"):
				os.makedirs(self.home  + "/.nvidiux/")
			
			if os.path.isfile(self.home  + "/.nvidiux/" + gpuName + ".ndi"):
				self.loadProfile(self.home  + "/.nvidiux/" + gpuName + ".ndi",True)
			else:
				if self.saveProfile(self.home  + "/.nvidiux/" + gpuName + ".ndi") != 0:
					return self.showError(21,_translate("nvidiux","Droit insuffisant",None),_translate("nvidiux","Impossible d'ecrire le fichier !",None),self.error)
				self.loadProfile(self.home  + "/.nvidiux/" + gpuName + ".ndi",True)
			if self.ndifile == None:		
				if os.path.isfile(self.home  + "/.nvidiux/Startup.ndi"):
					self.loadProfile(self.home +"/.nvidiux/Startup.ndi",False,"3")	
		except:
			return self.showError(20,"Erreur","Erreur Chargement configuration",self.error)					
		
	def denyEula(self):
		print "User deny eula"
		sys.exit(-2)
	
	def getVersionSupport(self):
		try:
			page=urllib.urlopen('http://nvidiux.redirectme.net:2008/checkVersion.html?version=' + self.pref.nvidiuxVersionStr)#,timeout = 4
			return "356|2.1.6"
			#return str(page.read())
		except:
			return str(self.piloteVersionMaxTest) + "|" + str(self.pref.nvidiuxVersion) + ".0"
			
	def iscompatible(self):
		cmd = "ls -l " + self.pathLibNvidia +  " | grep nvidia"
		if sub.call(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True):
			return self.showError(1,_translate("nvidiux","Non supporte",None),_translate("nvidiux","Librairie nvidia introuvable \nVeuillez installer les pilotes proprietaires\nVous pouvez indiquer un chemin alternatif pour acceder aux librairie nvidia\navec l'option -p",None),self.error)
		if not os.path.isfile("/usr/bin/nvidia-settings"):
			return self.showError(2,_translate("nvidiux","Non supporte",None),_translate("nvidiux","Nvidia settings introuvable \nveuillez installer les pilotes proprietaires et nvidia settings",None),self.error)
		
		cmd = "lspci -vnn | grep -E 'VGA|3D'"
		ListeGpu, err = sub.Popen(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True).communicate()
		self.pref.nbGpuNvidia = ListeGpu.count('GeForce')
		self.nbGpu = len(ListeGpu)
		if self.pref.nbGpuNvidia == 0:
			try:
				cmd = "nvidia-smi -L"
				ListeGpuSmi, err = sub.Popen(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True).communicate()
				self.pref.nbGpuNvidia = ListeGpuSmi.count('GeForce')
				if self.pref.nbGpuNvidia == 0:
					return self.showError(4,"Gpu Nvidia introuvable","Gpu Nvidia introuvable",self.error)
				ListeGpu = ListeGpuSmi
			except:
				return self.showError(4,"Gpu Nvidia introuvable","Gpu Nvidia introuvable",self.error)

		if self.nbGpu >= 2: #MultiGpu
			if ListeGpu.count('Intel') == 1 and self.pref.nbGpuNvidia == 1 : #optimus
				if os.popen("prime-supported 2>> /dev/null", "r").read().replace('\n','') != "yes":
					return self.showError(3,_translate("nvidiux","Prime",None),_translate("nvidiux","Seul prime est supporte pour les configurations optimus",None),self.error)	
				if os.popen("prime-select query", "r").read().replace('\n','') != "nvidia":
					return self.showError(-1,_translate("nvidiux","Mode intel",None),_translate("nvidiux","Configuration Prime\nVeuillez passer en mode nvidia svp",None),self.info)
				self.optimus = 1
		
		if not os.path.isfile("/etc/X11/xorg.conf"):
			reply = QtGui.QMessageBox.question(self,_translate("nvidiux","Xorg.conf",None),_translate("nvidiux","Pas de fichier xorg.conf en generer un ?",None), QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)
			if reply == QtGui.QMessageBox.No:
				return self.showError(6,_translate("nvidiux","Erreur",None),_translate("nvidiux","Vous devez avoir un fichier xorg.conf",None),self.error)
			else:
				cmd = "bash /usr/share/nvidiux/toRoot.sh add_coolbits.py >> /dev/null 2>&1"
				if not sub.call(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True):
					try:
						tempFile = open('/tmp/.reboot_nvidiux','a')
						tempFile.write('Nvidiux temp file')
						tempFile.close()
						return self.showError(-1,_translate("nvidiux","Redemarrage Requis",None),_translate("nvidiux","Configuration effectue\nVous devez redemarrer votre machine",None),self.info)
					except:
						return self.showError(5,_translate("nvidiux","Erreur",None),_translate("nvidiux","Erreur configuration nvidiux",None),self.error)
				else:
					return self.showError(7,_translate("nvidiux","Erreur Credential",None),_translate("nvidiux","Votre mot de passe est incorrect",None),self.error)

		if int(os.popen("cat /etc/X11/xorg.conf | grep Coolbits | wc -l", "r").read()) == 0:
			self.showError(-1,_translate("nvidiux","Configuration",None),_translate("nvidiux","La configuration du fichier xorg n'est pas effectué!\nEntrer votre mot de passe administrateur pour effectuer la configuration",None),self.info)
			cmd = "bash /usr/share/nvidiux/toRoot.sh add_coolbits.py >> /dev/null 2>&1"
			if sub.call(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True):
				return self.showError(7,_translate("nvidiux","Erreur Credential",None),_translate("nvidiux","Votre mot de passe est incorrect",None),self.error)
			else:
				try:
					tempFile = open('/tmp/.reboot_nvidiux','a')
					tempFile.write('Nvidiux temp file')
					tempFile.close()
					return self.showError(-1,_translate("nvidiux","Redemarrage Requis",None),_translate("nvidiux","Configuration effectué\nVous devez redemarrer votre machine",None),self.info)
				except:
					return self.showError(5,_translate("nvidiux","Erreur",None),_translate("nvidiux","Erreur configuration nvidiux",None),self.error)
		else:
			if os.path.isfile("/tmp/.reboot_nvidiux"):
				return self.showError(-1,_translate("nvidiux","Redemarrage Requis",None),_translate("nvidiux","Configuration effectue\nVous devez redemarrer votre machine",None),self.info)
		return 0
					
	def initialiseData(self):
		info = ""
		err = ""
		out = ""
		openGlV = ""
		if os.path.isfile(self.home + "/.nvidiux/conf.xml"):
			self.loadNvidiuxConf()
		
		compatibility = self.iscompatible()
		if not os.path.isfile(self.home + "/.nvidiux/acceptedeula"):
			self.showeula()
		else:
			self.acceptEula = True
					
		if compatibility >= 1 and  compatibility <= 7:
			sys.exit(compatibility)
		if compatibility == -1:
			sys.exit(0)
		
		self.nvidiuxTranslator = QtCore.QTranslator()
		if self.pref.language != "fr_FR":
			if self.nvidiuxTranslator.load("/usr/share/nvidiux/nvidiux_" + self.pref.language):
				app.installTranslator(self.nvidiuxTranslator)
				self.ui.retranslateUi(self)
		
		cmd = "nvidia-settings --query [gpu:0]/NvidiaDriverVersion"
		if not sub.call(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True):
			out, err = sub.Popen(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True).communicate()
			out = out.split(':')[-1][1:]
			if out.count(".") > 1:
				out = str(out.split(".")[0] + "." + out.split(".")[1])
			self.piloteVersion = float(out)
			
		else:
			self.showError(29,_translate("nvidiux","Echec",None),_translate("nvidiux","Impossible de determiner la version des drivers",None),self.error)
		if self.piloteVersion > self.piloteVersionMaxTest:
			self.printMessage(_translate("nvidiux","Driver non supporté (trop recent ?)",None)) 
			if not os.path.isfile(self.home + "/.nvidiux/ntchkdriver"):
				reply = QtGui.QMessageBox.question(self,_translate("nvidiux","Xorg.conf",None),_translate("nvidiux","Driver non testé (support < " + str(self.piloteVersionMaxTest) +")!\nVoulez vous activer l'overcloking ?",None), QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)
				if reply == QtGui.QMessageBox.No:	
					self.ui.SliderMem.setEnabled(False)
					self.ui.SliderGpu.setEnabled(False)
					self.ui.buttonReset.setEnabled(False)
					self.ui.buttonApply.setEnabled(False)
					self.ui.SliderFan.setEnabled(False)
					self.ui.checkBoxFan.setEnabled(False)
					self.ui.buttonLoadProfile.setEnabled(False)
					self.ui.buttonSaveProfile.setEnabled(False)
					self.ui.actionLoadProfile.setEnabled(False)
					self.ui.actionSaveProfile.setEnabled(False)
					self.pref.overclockEnabled = False
					self.printMessage(_translate("nvidiux","Driver non supporté (trop recent ?) Overclock desactivé",None))
				
		if self.piloteVersion <= 337.18:
			self.ui.SliderMem.setEnabled(False)
			self.ui.SliderGpu.setEnabled(False)
			self.ui.buttonReset.setEnabled(False)
			self.ui.buttonApply.setEnabled(False)
			self.ui.SliderFan.setEnabled(False)
			self.ui.checkBoxFan.setEnabled(False)
			self.ui.buttonLoadProfile.setEnabled(False)
			self.ui.buttonSaveProfile.setEnabled(False)
			self.ui.actionLoadProfile.setEnabled(False)
			self.ui.actionSaveProfile.setEnabled(False)
			self.pref.overclockEnabled = False
			self.printMessage(_translate("nvidiux","Driver non supporté (trop ancien)! Overclock desactivé",None))
			QMessageBox.information(self,_translate("nvidiux","Driver",None),_translate("nvidiux","Driver non supporte:trop ancien\nOverclock desactive\nIl vous faut la version 337.19 ou plus recent pour overclocker",None))
		
		cmd = "glxinfo | grep \"OpenGL version string\""
		out, err = sub.Popen(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True).communicate()
		try:
			openGlV = out.split('NVIDIA')[0].split('string:')[-1]
			if openGlV == "":
				openGlV = "4.6.0"
		except: #Assuming  all card is in 4.6.0 found other method detect openGL version
			openGlV = "4.6.0"

		cmd = "lspci -vnn | grep NVIDIA | grep -v Audio | grep GeForce"
		out, err = sub.Popen(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True).communicate()		
		for i in range(0, self.pref.nbGpuNvidia):
			if out.count('GeForce') >= 1:
				try:
					self.tabGpu.append(Gpuinfo())
					self.tabGpu[i].nameGpu =  "GeForce" + out.split('\n')[i].split("GeForce")[-1].split("]")[0]
				except:
					print "Text to send:" + str(out)
					self.showError(34,_translate("nvidiux","Echec",None),_translate("nvidiux","Echec chargement des parametres Gpu",None),self.error)
					sys.exit(1)
			else:
				cmd = "nvidia-smi -L"
				out, err = sub.Popen(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True).communicate()
				if out.count('GeForce') >= 1:
					try:
						self.tabGpu.append(Gpuinfo())
						self.tabGpu[i].nameGpu =  "GeForce" + out.split('\n')[i].split("GeForce")[-1].split("(")[0][:-1]
					except:
						print "Text to send:" + str(out)
						self.showError(34,_translate("nvidiux","Echec",None),_translate("nvidiux","Echec chargement des parametres Gpu",None),self.error)
						sys.exit(1)
				else:
					print "Text to send:" + str(out)
					self.showError(-34,_translate("nvidiux","Echec",None),_translate("nvidiux","Echec chargement des parametres Gpu",None),self.error)
					sys.exit(1)
				
			cmd = "nvidia-settings -a [gpu:" + str(i) + "]/GPUPowerMizerMode=1"
			sub.call(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True)
				
			cmd = "nvidia-settings --query [gpu:" + str(i) + "]/videoRam"
			if not sub.call(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True):
				out, err = sub.Popen(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True).communicate()
				try:
					self.tabGpu[i].videoRam = float(out.split(': ')[1].split('.')[0]) / 1048576
				except:
					print "Text to send:" + str(out)
					self.showError(35,_translate("nvidiux","Echec",None),_translate("nvidiux","Echec chargement des parametres Gpu",None),self.error)
					sys.exit(1)
			else:
				self.tabGpu[i].videoRam = "N/A"
			
			cmd = "nvidia-settings --query [gpu:" + str(i) + "]/cudaCores"
			if not sub.call(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True):
				out, err = sub.Popen(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True).communicate()
				try:
					self.tabGpu[i].cudaCores = int(out.split(': ')[1].split('.')[0])
				except:
					print "Text to send:" + str(out)
					self.showError(35,_translate("nvidiux","Echec",None),_translate("nvidiux","Echec chargement des parametres Gpu",None),self.error)
					sys.exit(1)
			else:
				self.tabGpu[i].cudaCores = "N/A"

			cmd = "nvidia-settings --query [gpu:" + str(i) + "]/GPUCurrentClockFreqsString"
			if not sub.call(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True):
				out, err = sub.Popen(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True).communicate()
				try:
					self.tabGpu[i].freqGpu = int(out.split('nvclockmax=')[1].split(',')[0])
					self.tabGpu[i].defaultFreqGpu = int(out.split('nvclockmax=')[1].split(',')[0])
				except:
					print "Text to send:" + str(out)
					self.showError(39,_translate("nvidiux","Echec",None),_translate("nvidiux","Echec chargement des parametres Gpu",None),self.error)
					sys.exit(1)
				try:
					self.tabGpu[i].freqShader = int(out.split('processorclockmax=')[1].split(',')[0])
					self.tabGpu[i].defaultFreqShader = int(out.split('processorclockmax=')[1].split(',')[0])
				except: #Get an empty response sometimes on 6,7,8XX generation... => shadder = gpu clock
					self.tabGpu[i].freqShader = self.tabGpu[i].freqGpu
					self.tabGpu[i].defaultFreqShader = self.tabGpu[i].freqGpu  
				try:
					self.tabGpu[i].freqMem = int(out.split('memTransferRatemax=')[1].split(',')[0])
					self.tabGpu[i].defaultFreqMem = int(out.split('memTransferRatemax=')[1].split(',')[0])
				except:
					print "Text to send:" + str(out)
					self.showError(36,_translate("nvidiux","Echec",None),_translate("nvidiux","Echec chargement des parametres Gpu",None),self.error)
					sys.exit(1)
			else:
				self.showError(31,_translate("nvidiux","Echec",None),_translate("nvidiux","Echec chargement des parametres Gpu",None),self.error)
			
			tempNum = re.findall('\d+',self.tabGpu[i].nameGpu)
			try:
				if len(tempNum) > 0:
					nb_nvi = int(tempNum[0]) # A verifier
					if nb_nvi >= 400 and nb_nvi <= 799:
						if int(self.tabGpu[i].freqShader) == int(self.tabGpu[i].freqGpu) * 2 or int(self.tabGpu[i].freqShader) == int(self.tabGpu[i].freqGpu) * 2 + 1:
							self.tabGpu[i].arch = "fermi"
						else:
							self.tabGpu[i].arch = "kepler"	
					elif nb_nvi >= 900 and nb_nvi <= 999:
						self.tabGpu[i].arch = "maxwell"
					elif nb_nvi >= 1000 and nb_nvi <= 1099:
						self.tabGpu[i].arch = "pascal"
					elif nb_nvi >= 1100 and nb_nvi <= 1199 or nb_nvi >= 2000 and nb_nvi <= 2099:
						self.tabGpu[i].arch = "turing"
					else:
						self.tabGpu[i].arch = "ND"
				else:
					self.tabGpu[i].arch = "ND"
			except:
				self.tabGpu[i].arch = "ND"
				
			cmd = "nvidia-settings --query [gpu:" + str(i) + "]/GpuUUID"
			out, err = sub.Popen(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True).communicate()
			self.tabGpu[i].uuid = str(out.split("):")[-1].split("\n")[1].replace(" ", ""))
				
			cmd = "nvidia-settings --query all | grep SyncToVBlank"
			out, err = sub.Popen(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True).communicate()
			if out != "":
				if out.split(': ')[1].split('.')[0]:
					self.ui.checkBoxVSync.setChecked(True)
				else:
					self.checkBoxVSync.setChecked(False)
			else:
				self.ui.checkBoxVSync.setChecked(False)
			
			if self.piloteVersion < 349.0 or self.piloteVersion > 352.0:
				cmd = "nvidia-settings --query [fan:" + str(i) + "]/GPUCurrentFanSpeed" #GPUCurrentFanSpeedRPM for version 349 ...
				if not sub.call(cmd ,stdout=sub.PIPE,stderr=sub.PIPE,shell=True):
					try:
						out, err = sub.Popen(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True).communicate()
						self.tabGpu[i].fanSpeed = out.split(': ')[1].split('.')[0]
						if int(self.tabGpu[i].fanSpeed) == 0:
							self.ui.SliderFan.setEnabled(False)
							self.ui.checkBoxFan.setChecked(False)
							self.ui.checkBoxFan.setEnabled(False)
							self.ui.checkBoxFan.setVisible(False)
							self.ui.labelFanVitesse.setText(_translate("nvidiux","incompatible",None))
					except:
						self.tabGpu[i].fanSpeed = 0
						self.ui.SliderFan.setEnabled(False)
						self.ui.checkBoxFan.setChecked(False)
						self.ui.checkBoxFan.setEnabled(False)
						self.ui.checkBoxFan.setVisible(False)
						self.ui.labelFanVitesse.setText(_translate("nvidiux","incompatible",None))
				else:
					self.tabGpu[i].fanSpeed = 0
					self.ui.SliderFan.setEnabled(False)
					self.ui.checkBoxFan.setEnabled(False)
					self.ui.checkBoxFan.setChecked(False)
					self.ui.checkBoxFan.setVisible(False)
					self.ui.labelFanVitesse.setText(_translate("nvidiux","incompatible",None))
					
				try:
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
				except:
					self.ui.SliderFan.setEnabled(False)
					self.ui.checkBoxFan.setChecked(False)
					self.ui.checkBoxFan.setEnabled(False)
					self.tabGpu[i].fanSpeed = 0
					self.ui.labelFanVitesse.setText(_translate("nvidiux","incompatible",None))
			else:
				self.ui.SliderFan.setEnabled(False)
				self.ui.checkBoxFan.setChecked(False)
				self.ui.checkBoxFan.setEnabled(False)
				self.ui.labelFanVitesse.setText(_translate("nvidiux","incompatible",None))

			if self.piloteVersion >= 346.16:
				cmd = "nvidia-settings --query [gpu:" + str(i) + "]/GPUOverVoltageOffset"
				out, err = sub.Popen(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True).communicate()
				try:
					self.tabGpu[i].maxOvervolt = int(out.split('range')[1].split("(inclusive)")[0].split("-")[1])
					self.tabGpu[i].overvolt = int(out.split('range')[1].split("(inclusive)")[0].split("-")[0])
				except:
					self.tabGpu[i].maxOvervolt = 0
					self.tabGpu[i].overvolt = 0
					
			cmd = "nvidia-settings -a [gpu:" + str(i) + "]/GPUPowerMizerMode=0"
			sub.call(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True)
			
			if self.tabGpu[i].arch == "kepler" or self.tabGpu[i].arch == "pascal" or self.tabGpu[i].arch == "maxwell":
				if self.piloteVersion >= 355.0:
					self.tabGpu[i].vulkanVersion = "Oui"
				else:
					self.tabGpu[i].vulkanVersion = "Non"
			else:	
				self.tabGpu[i].vulkanVersion = "Non"
			self.tabGpu[i].openGlVersion = openGlV
			
			cmd = "nvidia-settings --query [gpu:" + str(self.numGpu) + "]/GPUMemoryInterface"
			out2, err = sub.Popen(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True).communicate()
			self.tabGpu[i].memInterface = int(out2.split("):")[1].split(".")[0])
		try:
			for gpu in self.tabGpu:
				returnCode = self.verifyGpu(gpu.nameGpu)
				if returnCode == -1:
					info = info + _translate("nvidiux","Ce gpu ",None) + str(gpu.nameGpu) + _translate("nvidiux"," n'est pas dans la liste blanche\nn'hesitez pas a confirmer son fonctionnement",None)
					self.tabGpu[i].isCompatible = True
				elif returnCode == 1:
					info = info + _translate("nvidiux","Ce gpu ",None) + str(gpu.nameGpu) + _translate("nvidiux"," n'est pas supporte \n(Overclock desactive !)",None)
					self.tabGpu[i].isCompatible = False
				else: #0 = white list
					self.tabGpu[i].isCompatible = True
				self.defineDefaultFreqGpu(gpu.nameGpu)
			if info != "":
				QMessageBox.information(self,_translate("nvidiux","Information",None),_fromUtf8(info))	
		except:
			self.showError(41,_translate("nvidiux","Echec",None),_translate("nvidiux","Echec chargement des parametres Gpu",None),self.error)
			sys.exit(1)
			
		if os.path.isfile("/usr/share/nvidiux/img/Gpu/" + self.tabGpu[i].nameGpu + ".png") and self.pref.nbGpuNvidia == 1:
			self.ui.label_Img.setPixmap(QtGui.QPixmap("/usr/share/nvidiux/img/Gpu/" + self.tabGpu[0].nameGpu + ".png"))
		else:	
			self.ui.label_Img.setPixmap(QtGui.QPixmap("/usr/share/nvidiux/img/drivers_nvidia_linux.png"))
		
		if self.pref.nbGpuNvidia <= 1:
			self.ui.label_Nvidiux.setPixmap(QtGui.QPixmap("/usr/share/nvidiux/img/drivers_nvidia_linux.png"))
		elif self.pref.nbGpuNvidia > 4:
			self.showError(52,_translate("nvidiux","Echec",None),_translate("nvidiux","Nvidiux ne supporte pas plus de 4 Gpu",None),self.error)
			sys.exit(1)
		else:
			self.ui.labelChangeGpu = QtGui.QLabel(self.ui.groupBoxTitleGpu)
			self.ui.labelChangeGpu.setGeometry(QtCore.QRect(70, 2, 150, 20))
			self.ui.labelChangeGpu.setObjectName(_fromUtf8("labelChangeGpu"))
			self.ui.labelChangeGpu.setText(_translate("nvidiux", "Changer de Gpu",None))
			if self.pref.nbGpuNvidia >= 2:
				self.ui.buttongpu1 = QtGui.QPushButton(self.ui.groupBoxTitleGpu)
				self.ui.buttongpu1.setGeometry(QtCore.QRect(45, 20, 160, 80))
				self.ui.buttongpu1.setAutoDefault(False)
				self.ui.buttongpu1.setDefault(False)
				self.ui.buttongpu1.setFlat(False)
				self.ui.buttongpu1.setEnabled(False)
				self.ui.buttongpu1.setObjectName(_fromUtf8("buttongpu1"))
				self.ui.buttongpu2 = QtGui.QPushButton(self.ui.groupBoxTitleGpu)
				self.ui.buttongpu2.setGeometry(QtCore.QRect(45, 100, 160, 80))
				self.ui.buttongpu2.setAutoDefault(False)
				self.ui.buttongpu2.setDefault(False)
				self.ui.buttongpu2.setFlat(False)
				self.ui.buttongpu2.setObjectName(_fromUtf8("buttongpu2"))
				self.ui.buttongpu1.connect(self.ui.buttongpu1,SIGNAL("released()"),self.changeGpuTo0)
				self.ui.buttongpu2.connect(self.ui.buttongpu2,SIGNAL("released()"),self.changeGpuTo1)
				self.ui.buttongpu1.setText(self.tabGpu[0].nameGpu)
				self.ui.buttongpu2.setText(self.tabGpu[1].nameGpu)	
				
			if self.pref.nbGpuNvidia >= 3:
				self.ui.buttongpu1.setGeometry(QtCore.QRect(45, 20, 160, 50))
				self.ui.buttongpu2.setGeometry(QtCore.QRect(45, 75, 160, 50))
				self.ui.buttongpu3 = QtGui.QPushButton(self.ui.groupBoxTitleGpu)
				self.ui.buttongpu3.setGeometry(QtCore.QRect(45, 130, 160, 50))
				self.ui.buttongpu3.setAutoDefault(False)
				self.ui.buttongpu3.setDefault(False)
				self.ui.buttongpu3.setFlat(False)
				self.ui.buttongpu3.connect(self.ui.buttongpu3,SIGNAL("released()"),self.changeGpuTo2)
				self.ui.buttongpu3.setText(self.tabGpu[2].nameGpu)
					
			if self.pref.nbGpuNvidia == 4:
				self.ui.buttongpu1.setGeometry(QtCore.QRect(45, 20, 160, 40))
				self.ui.buttongpu2.setGeometry(QtCore.QRect(45, 62, 160, 40))
				self.ui.buttongpu3.setGeometry(QtCore.QRect(45, 104, 160, 40))
				self.ui.buttongpu4 = QtGui.QPushButton(self.ui.groupBoxTitleGpu)
				self.ui.buttongpu4.setGeometry(QtCore.QRect(45, 146, 160, 40))
				self.ui.buttongpu4.setAutoDefault(False)
				self.ui.buttongpu4.setDefault(False)
				self.ui.buttongpu4.setFlat(False)
				self.ui.buttongpu4.connect(self.ui.buttongpu4,SIGNAL("released()"),self.changeGpuTo3)
				self.ui.buttongpu4.setText(self.tabGpu[3].nameGpu)
				
		self.ui.SliderShader.setMinimum(int(self.tabGpu[self.numGpu].resetFreqShader) * 0.80)
		self.ui.SliderShader.setMaximum(int(self.tabGpu[self.numGpu].resetFreqShader) * 1.3)
		self.ui.SliderShader.setSliderPosition(int(self.tabGpu[self.numGpu].freqShader))
		self.ui.lcdShader.display(int(self.tabGpu[self.numGpu].freqShader))
		if self.tabGpu[self.numGpu].arch == "fermi":
			self.ui.SliderFan.setMinimum(30)
		else:
			self.ui.SliderFan.setMinimum(15)
			
		if not self.tabGpu[0].isCompatible:
			self.ui.SliderMem.setEnabled(False)
			self.ui.SliderGpu.setEnabled(False)
			self.ui.SliderShader.setEnabled(False)
			self.ui.buttonReset.setEnabled(False)
			self.ui.buttonApply.setEnabled(False)
			self.ui.buttonLoadProfile.setEnabled(False)
			self.ui.buttonSaveProfile.setEnabled(False)
			self.ui.actionLoadProfile.setEnabled(False)
			self.ui.actionSaveProfile.setEnabled(False)
			self.printMessage(_translate("nvidiux","Gpu(" ,None) + str(self.tabGpu[0].nameGpu) + _translate("nvidiux",") non supporte",None))
			self.pref.overclockEnabled = False	
			
		if self.tabGpu[i].arch == "pascal" and self.pref.piloteVersion < 370.01:
			self.ui.SliderMem.setEnabled(False)
			self.ui.SliderGpu.setEnabled(False)
			self.ui.buttonReset.setEnabled(False)
			self.ui.buttonApply.setEnabled(False)
			self.ui.SliderFan.setEnabled(False)
			self.ui.checkBoxFan.setEnabled(False)
			self.ui.buttonLoadProfile.setEnabled(False)
			self.ui.buttonSaveProfile.setEnabled(False)
			self.ui.actionLoadProfile.setEnabled(False)
			self.ui.actionSaveProfile.setEnabled(False)
			self.pref.overclockEnabled = False
			
		self.ui.SliderFan.setMaximum(100)
		self.ui.SliderMem.setMinimum(int(self.tabGpu[self.numGpu].resetFreqMem) * 0.80)
		self.ui.SliderMem.setMaximum(int(self.tabGpu[self.numGpu].resetFreqMem) * 1.3)
		self.ui.SliderMem.setSliderPosition(int(self.tabGpu[self.numGpu].freqMem))
		self.ui.lcdMem.display(int(self.tabGpu[self.numGpu].freqMem))
		self.ui.SliderGpu.setMinimum(int(self.tabGpu[self.numGpu].resetFreqGpu) * 0.80)
		self.ui.SliderGpu.setMaximum(int(self.tabGpu[self.numGpu].resetFreqGpu) * 1.3)
		self.ui.SliderGpu.setSliderPosition(int(self.tabGpu[self.numGpu].freqGpu))
		self.ui.lcdGPU.display(int(self.tabGpu[self.numGpu].freqGpu))
		if not self.autoStartupNvidiuxOverclock:
			self.ui.label_Dfreq_Gpu.setText(str(self.tabGpu[self.numGpu].defaultFreqGpu) + _fromUtf8(" Mhz →"))
			self.ui.label_Dfreq_Shader.setText(str(self.tabGpu[self.numGpu].defaultFreqShader) + _fromUtf8(" Mhz →"))
			self.ui.label_Dfreq_Mem.setText(str(self.tabGpu[self.numGpu].defaultFreqMem) + _fromUtf8(" Mhz →"))
			
		self.ui.nomGpu.setText(self.tabGpu[self.numGpu].nameGpu)
		self.ui.MemGpu.setText(_translate("nvidiux","Memoire video",None) + "\n" + str(self.tabGpu[self.numGpu].videoRam) + " Go")
		self.ui.CudaCore.setText(_translate("nvidiux","NB coeur cuda",None) + "\n" + str(self.tabGpu[self.numGpu].cudaCores))
		self.ui.PiloteVersion.setText(_translate("nvidiux","Version du Pilote",None) + "\n" + str(self.piloteVersion))
		self.ui.OpenGlSupport.setText(_translate("nvidiux","OpenGl Support",None) + "\n" + str(self.tabGpu[self.numGpu].openGlVersion))
		self.ui.checkBoxSli.setChecked(False)
		if self.pref.nbGpuNvidia >= 2: #detect sli 2 card with same name #find a better way
			if len(list(set(self.tabGpu[i].nameGpu))) == 1:
				self.ui.checkBoxSli.setChecked(True)
				self.isSli = True
		majGpu(0,self)
		self.ui.SliderShader.setEnabled(False)
		self.ui.spinBoxOvervolt.setMaximum(self.tabGpu[self.numGpu].maxOvervolt)
		self.ui.labelValueOvervolt.setText(str(self.tabGpu[self.numGpu].overvolt) + _translate("nvidiux","μv",None))
				
		if self.tabGpu[self.numGpu].maxOvervolt == 0:
			self.ui.groupBoxOvervolt.setEnabled(False)
		
		if self.piloteVersion < 346.16:
			self.ui.groupBoxOvervolt.setVisible(False)
		else:
			self.ui.groupBoxOvervolt.setVisible(self.pref.overvoltEnabled)
			
		self.ui.buttonApply.setEnabled(False)
		if self.tabGpu[0].freqMem != self.tabGpu[0].resetFreqMem or self.tabGpu[0].freqGpu != self.tabGpu[0].resetFreqGpu:
			self.ui.buttonReset.setEnabled(True)
		else:
			self.ui.buttonReset.setEnabled(False)

		self.ui.labelGpuArch.setText("Gen: " + str(self.tabGpu[0].arch))
		self.ui.versionLabel.setText(_translate("nvidiux","Version : ",None) + str(".".join(self.pref.nvidiuxVersionStr.split(".")[:-1])))
		
	def killTMonitor(self):
		if self.pidMonitor != 0:
			self.threadMonitor.stop()
			self.pidMonitor = 0
		
	def loadNvidiuxConf(self):
		try:
			profileFile = open(self.home + "/.nvidiux/conf.xml", "r")
			confFile = minidom.parse(profileFile)
			versionElement = confFile.getElementsByTagName("version")
			update = confFile.getElementsByTagName("update")
			time = confFile.getElementsByTagName("updateinterval")
			lang = confFile.getElementsByTagName("lang")
			start = confFile.getElementsByTagName("start-system")
			valueStart = confFile.getElementsByTagName("valuestart")
			sendStat = confFile.getElementsByTagName("send-stat")
			overvoltEnabled =  confFile.getElementsByTagName("overvoltenabled")
			sameGpuParam =  confFile.getElementsByTagName("samegpuparam")
			if float(versionElement[0].firstChild.nodeValue) > float(self.pref.nvidiuxVersion):
				reply = QtGui.QMessageBox.question(self, _translate("nvidiux","Version",None),_translate("nvidiux","Le fichier de configuration est pour une version plus recente de Nvidiux\nCharger tous de même ?",None), QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)
				if reply == QtGui.QMessageBox.No:
					return False
			
			if update[0].firstChild.nodeValue == "True":
				self.pref.autoUpdate = True
			elif update[0].firstChild.nodeValue == "False":
				self.pref.autoUpdate = False
			else:
				raise DataError("corrupt Data")
				
			if sameGpuParam[0].firstChild.nodeValue == "True":
				self.pref.sameParamGpu = True
			elif sameGpuParam[0].firstChild.nodeValue == "False":
				self.pref.sameParamGpu = False
			else:
				raise DataError("corrupt Data")
				
			if sendStat[0].firstChild.nodeValue == "True":
				self.pref.sendStat = True
			elif sendStat[0].firstChild.nodeValue == "False":
				self.pref.sendStat = False
			else:
				raise DataError("corrupt Data")
				
			if overvoltEnabled[0].firstChild.nodeValue == "True":
				self.pref.overvoltEnabled = True
			elif overvoltEnabled[0].firstChild.nodeValue == "False":
				self.pref.overvoltEnabled = False
			else:
				raise DataError("corrupt Data")
			
			if int(time[0].firstChild.nodeValue) >= 1 and int(time[0].firstChild.nodeValue) <= 60: 
				self.pref.updateTime = int(time[0].firstChild.nodeValue)
			else:
				self.pref.updateTime = 1
			if start[0].firstChild.nodeValue == "True":
				self.pref.startWithSystem = True
			elif start[0].firstChild.nodeValue == "False":
				self.pref.startWithSystem = False
			else:
				raise DataError("corrupt Data")
			self.pref.language = lang[0].firstChild.nodeValue
			self.pref.valueStart = str(valueStart[0].firstChild.nodeValue)
		except:
			print "Error load config file"
		return True

	def loadPrefWindow(self):
		self.pref.gpu = self.tabGpu
		self.pref.app = app
		self.formSettings = Ui_Pref(0,self.pref,self)
		self.formSettings.show()
	
	def loadProfile(self,path = "",defaultOnly = False,otherCode = 2):
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
			return self.showError(-1,_translate("nvidiux","Fichier endommage",None),_translate("nvidiux","Impossible de charger ce fichier de configuration",None),self.warning)
			
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
		if versionElement == []:
			error = True
			self.showError(errorCode ,_translate("nvidiux","Echec",None),_translate("nvidiux","Echec chargement du profil",None),19)
			return 1	
		if not error and not defaultOnly:
			if float(self.pref.nvidiuxVersion) < float(versionElement[0].firstChild.nodeValue):
				reply = QtGui.QMessageBox.question(self, _translate("nvidiux","Version",None),_translate("nvidiux","Le profil est pour une version plus recente de Nvidiux\nCharger tous de même ?",None), QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)
				if reply == QtGui.QMessageBox.No:
					errorCode = 11
					self.showError(errorCode ,_translate("nvidiux","Echec",None),_translate("nvidiux","Echec chargement du profil",None),self.error)
					return 1
			i = 0
			if self.pref.nbGpuNvidia == len(listgpu):
				try:
					for tempgpu in listgpu:
						if str(self.tabGpu[i].nameGpu) != str(tempgpu[0]):
							errorCode = 12
							break
						if int(tempgpu[1]) < int((self.tabGpu[i].defaultFreqGpu)) * 0.80 or int(tempgpu[1]) > int((self.tabGpu[i].defaultFreqGpu)) * 1.3:
							errorCode = 13
							break
						if int(tempgpu[2]) < int((self.tabGpu[i].defaultFreqShader)) * 0.80 or int(tempgpu[2]) > int((self.tabGpu[i].defaultFreqShader)) * 1.3:
							errorCode = 14
							break
						if int(tempgpu[3]) < int((self.tabGpu[i].defaultFreqMem)) * 0.80 or int(tempgpu[3]) > int((self.tabGpu[i].defaultFreqMem)) * 1.3:
							errorCode = 15
							break
						if int(tempgpu[4]) < 0 or int(tempgpu[4]) > int(self.tabGpu[i].maxOvervolt):
							errorCode = 15.1
							break
						i = i + 1
				except:
					self.showError(21,_translate("nvidiux","Echec",None),_translate("nvidiux","Echec chargement du profil",None),self.error)
			else:
				error = 16
		if errorCode != 0:
			self.showError(errorCode ,_translate("nvidiux","Echec",None),_translate("nvidiux","Echec chargement du profil",None),self.error)
			return 1
		i = 0
		for tempgpu in listgpu:
			if not defaultOnly:
				self.tabGpu[i].freqGpu = int(tempgpu[1])
				self.tabGpu[i].freqShader = int(tempgpu[2])
				self.tabGpu[i].freqMem = int(tempgpu[3])
				self.tabGpu[i].overvolt = int(tempgpu[4])
				self.ui.lcdGPU.display(self.tabGpu[self.numGpu].freqGpu)
				self.ui.lcdMem.display(self.tabGpu[self.numGpu].freqMem)
				self.ui.lcdShader.display(self.tabGpu[self.numGpu].freqShader)
				self.ui.SliderGpu.setSliderPosition(self.tabGpu[self.numGpu].freqGpu)
				self.ui.SliderShader.setSliderPosition(self.tabGpu[self.numGpu].freqShader)
				self.ui.SliderMem.setSliderPosition(self.tabGpu[self.numGpu].freqMem)
				self.autoStartupNvidiuxOverclock = True
				if self.piloteVersion >= 346.16 and self.tabGpu[i].overvolt > 0:
					self.ui.labelValueOvervolt.setText(str(self.tabGpu[self.numGpu].overvolt) + _translate("nvidiux","μv",None))
					self.ui.spinBoxOvervolt.setMaximum(self.tabGpu[self.numGpu].maxOvervolt)
					if self.pref.overvoltEnabled:
						self.overvolt()
					else:
						QMessageBox.warning(self,_translate("nvidiux","Overvolt désactivé",None),_translate("nvidiux","Vous devez activer la foncion d'overvolt \npour appliquer le parametre d'overvolt de ce profil",None))	
				self.overclock(str(otherCode))
			else:
				self.tabGpu[i].resetFreqGpu = int(tempgpu[1])
				self.tabGpu[i].resetFreqShader = int(tempgpu[2])
				self.tabGpu[i].resetFreqMem = int(tempgpu[3])
		if self.silent and not defaultOnly:
			sys.exit(0)
		return 0
	
	def maxPerf(self,value):
		if value:
			reply = QtGui.QMessageBox.question(self,_translate("nvidiux","Mode Performance",None),_translate("nvidiux","Passer en mode performance oblige votre gpu a fonctionner a sa frequence maximale\nCette fonction est deconseille si vous avez un portable sur batterie\nvoulez vous continuer ?",None), QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)
			if reply == QtGui.QMessageBox.Yes:
				for i in range(0, self.pref.nbGpuNvidia):
					cmd = "nvidia-settings -a [gpu:" + str(i) + "]/GPUPowerMizerMode=1"
					if sub.call(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True):
						self.showError(-1,_translate("nvidiux","Erreur",None),_translate("nvidiux","Impossible de passer en mode max perf",None),self.warning)
						self.ui.checkBoxMPerf.setChecked(False)
				self.printMessage(_translate("nvidiux","Mode Max perf : Actif",None))
			else:
				self.ui.checkBoxMPerf.setChecked(False)
		else:
			for i in range(0, self.pref.nbGpuNvidia):
				cmd = "nvidia-settings -a [gpu:" + str() + "]/GPUPowerMizerMode=0"
				if sub.call(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True):
					self.showError(-1,_translate("nvidiux","Erreur",None),_translate("nvidiux","Impossible de passer en mode adaptatif",None),self.warning)
					self.ui.checkBoxMPerf.setChecked(True)
				self.printMessage(_translate("nvidiux","Mode Max perf : Inactif",None))
	
	def openRapport(self):
		try:
			cmd = "nvidia-settings --query [gpu:" + str(self.numGpu) + "]/PCIEGen"
			out3, err = sub.Popen(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True).communicate()
			msg = "GPU INFO"
			# ~ msg += _translate("nvidiux","Nom gpu:",None) + self.tabGpu[self.numGpu].nameGpu + "\n"
			# ~ msg += _translate("nvidiux","Gpu UUid:",None) + self.tabGpu[self.numGpu].uuid + "\n"
			# ~ msg += _translate("nvidiux","Interface memoire gpu:",None) + str(self.tabGpu[self.numGpu].memInterface) + _translate("nvidiux","bits",None) + "\n"
			# ~ msg += _translate("nvidiux","PCIE Gen:",None) + out3.split("):")[1].split(".")[0] + "\n"
			# ~ msg += _translate("nvidiux","Famille Gpu:",None) + self.tabGpu[self.numGpu].arch + "\n" 
			QMessageBox.information(self,_translate("nvidiux","Rapport",None),msg)
		except:
			QMessageBox.information(self,_translate("nvidiux","Rapport",None),_translate("nvidiux","Erreur lors d'obtention des données",None))
			
	def overvolt(self):
		if self.ui.spinBoxOvervolt.value() != 0 and self.pref.overvoltEnabled:
			reply = QtGui.QMessageBox.question(self,_translate("nvidiux","Confirmation",None),_translate("nvidiux","Etes vous sur de vouloir appliquer cet overvolt  + ",None) + str(self.ui.spinBoxOvervolt.value()) + _translate("nvidiux","μv\nPour ce gpu: ",None) + self.tabGpu[self.numGpu].nameGpu + " id(" + str(self.numGpu + 1) +") ?", QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)
			if reply == QtGui.QMessageBox.Yes:
				cmd = "nvidia-settings -a [gpu:" + str(self.numGpu) + "]/GPUOVerVoltageOffset=" + str(self.ui.spinBoxOvervolt.value())
				if sub.call(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True):
					self.showError(-1,_translate("nvidiux","Erreur",None),_translate("nvidiux","Echec application overvoltage",None),self.warning)
					self.ui.checkBoxMPerf.setChecked(False)
				else:
					self.overvoltValue = self.ui.spinBoxOvervolt.value()
					self.ui.labelValueOvervolt.setText(str(self.overvoltValue) + _translate("nvidiux","μv",None))
					self.tabGpu[semf.numGpu].overvoltValue = self.overvoltValue
			
	def overclock(self,mode):
		if not os.path.isfile(self.home + "/.nvidiux/acceptedeula"):
			self.showError(-1,_translate("nvidiux","Accepter le contrat de licence",None),_translate("nvidiux","Vous devez accepter le contrat de licence d'abord",None),self.info)
			return False
		success = False
		overclock = False
		i = 0
		maxNivPerf = 2
		offsetMem = 0
		offsetGpu = 0
		cmd = "nvidia-settings --query [gpu:" + str(i) + "]/GPUPerfModes"
		if not sub.call(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True):
			out, err = sub.Popen(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True).communicate()
			try:
				maxNivPerf = int(out.split("perf=")[-1].split(",")[0])
				overclock = True
			except:
				self.showError(-1,_translate("nvidiux","Erreur",None),_translate("nvidiux","Erreur interne overclock/downclock impossible",None),self.warning)
		if overclock:
			for gpu in self.tabGpu:
				offsetGpu = int(self.tabGpu[i].freqGpu) - int(self.tabGpu[i].resetFreqGpu)
				offsetMem = int(self.tabGpu[i].freqMem) - int(self.tabGpu[i].resetFreqMem)
				try:
					cmd = "nvidia-settings -a \"[gpu:" + str(i) + "]/GPUGraphicsClockOffset[" + str(maxNivPerf) + "]=" + str(offsetGpu) + "\" -a \"[gpu:" + str(i) + "]/GPUMemoryTransferRateOffset[" + str(maxNivPerf) + "]=" + str(offsetMem) + "\" >> /dev/null 2>&1"
					if not sub.call(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True):
						success = True
					else:
						success = False
						break
				except:
					self.showError(-1,_translate("nvidiux","Erreur",None),_translate("nvidiux","Erreur interne overclock/downclock impossible",None),self.warning)						
		if success:
			if mode == "0": #Reset
				self.showError(0,_translate("nvidiux","Effectue",None),_translate("nvidiux","Reset effectue",None),self.info)
				self.printMessage(_translate("nvidiux","Reset effectué",None))
			elif mode == "1": #Normal
				self.showError(0,_translate("nvidiux","Effectue",None),_translate("nvidiux","Changement effectue",None),self.info)
				self.printMessage(_translate("nvidiux","Overclock effectué",None))
			elif mode == "2": #On Load Profile
				self.printMessage(_translate("nvidiux","Overclock effectué",None))
			elif mode == "3": #Auto Startup
				self.ui.SliderGpu.setSliderPosition(self.tabGpu[self.numGpu].freqGpu)
				self.ui.SliderShader.setSliderPosition(self.tabGpu[self.numGpu].freqShader)
				self.ui.SliderMem.setSliderPosition(self.tabGpu[self.numGpu].freqMem)
				self.printMessage(_translate("nvidiux","Auto overclock effectué",None))
			else:
				self.printMessage(_fromUtf8(""))
				
			self.change = False
			self.ui.buttonApply.setEnabled(False)
			self.ui.buttonReset.setEnabled(True)
			self.ui.label_Dfreq_Gpu.setText(str(self.tabGpu[self.numGpu].freqGpu) + _fromUtf8(" Mhz →"))
			self.ui.label_Dfreq_Shader.setText(str(self.tabGpu[self.numGpu].freqShader) + _fromUtf8(" Mhz →"))
			self.ui.label_Dfreq_Mem.setText(str(self.tabGpu[self.numGpu].freqMem) + _fromUtf8(" Mhz →"))
			self.setGpuStat(2,offsetGpu,offsetMem)
		else:
			if mode == "1":
				return self.showError(8,_translate("nvidiux","Echec",None),_translate("nvidiux","L'overclock à echoué",None),self.error)
			else:
				return self.showError(9,_translate("nvidiux","Echec",None),_translate("nvidiux","Le reset à echoué",None),self.error)
				
	def printMessage(self,textToPrint):
		if self.ui.Message.text() == "":
			self.ui.Message.setText(textToPrint)
		else:
			if self.ui.Message.text().count('\n') >= 2:
				self.ui.Message.setText(self.ui.Message.text().split('\n')[1] + "\n" + self.ui.Message.text().split('\n')[2])
			self.ui.Message.setText(self.ui.Message.text() + "\n" + textToPrint.replace("\n",""))
		
	def quitapp(self):
		if self.change:
			reply = QtGui.QMessageBox.question(self,_translate("nvidiux","Message",None),_translate("nvidiux","Etes vous sur de vouloir quitter sans appliquer les modifications ?",None), QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)
			if reply == QtGui.QMessageBox.Yes:
				if self.pref.autoUpdate:
					self.threadInfoGpu.stop()
					time.sleep(0.5)
				if self.threadMonitor != None:
					self.threadMonitor.stop()
				self.saveNvidiuxConf()
				self.close()
			else:
				self.applyNewClock()
		else:
			if self.pref.autoUpdate:
				self.threadInfoGpu.stop()
				time.sleep(0.5)
			if self.threadMonitor != None:
				self.threadMonitor.stop()
			self.saveNvidiuxConf()
			self.close()
			
	def reset(self):
		for i in range(0, self.pref.nbGpuNvidia):
			self.tabGpu[i].freqShader = self.tabGpu[i].resetFreqShader 
			self.tabGpu[i].freqGpu = self.tabGpu[i].resetFreqGpu
			self.tabGpu[i].freqMem = self.tabGpu[i].resetFreqMem
			self.updateGpu(int(self.tabGpu[i].resetFreqGpu))
			self.updateMem(int(self.tabGpu[i].resetFreqMem))
			self.ui.SliderGpu.setSliderPosition(int(self.tabGpu[i].resetFreqGpu))
			self.ui.SliderShader.setSliderPosition(int(self.tabGpu[i].resetFreqShader))
			self.ui.SliderMem.setSliderPosition(int(self.tabGpu[i].resetFreqMem))
			self.ui.label_Dfreq_Gpu.setText(str(self.tabGpu[i].resetFreqGpu) + _fromUtf8(" Mhz →"))
			self.ui.label_Dfreq_Shader.setText(str(self.tabGpu[i].resetFreqShader) + _fromUtf8(" Mhz →"))
			self.ui.label_Dfreq_Mem.setText(str(self.tabGpu[i].resetFreqMem) + _fromUtf8(" Mhz →"))
		self.overclock("0")
		self.change = False
		self.ui.buttonApply.setEnabled(False)
		self.ui.buttonReset.setEnabled(False)
		self.printMessage(_translate("nvidiux","Reset effectue",None))
	
	def resizeEvent(self, event):
		self.showNormal()
	
	def showeula(self):
		text = ""
		tabLang = list()
		tabLang.append(self.pref.language)
		tabLang.append(app)	
		self.eulaForm = ConfirmWindow(text,tabLang,4)
		self.eulaForm.setWindowModality(QtCore.Qt.ApplicationModal)
		self.connect(self.eulaForm, SIGNAL("accept(PyQt_PyObject)"), self.acceptEula)
		self.connect(self.eulaForm, SIGNAL("reject(PyQt_PyObject)"), self.denyEula)
		self.eulaForm.show()
	
	def showHelp(self):
		print '''Use:nvidiux <option> ndifile
		-h --help 		print this help
		-r --reset		reset over/down-clock of all nvidia card
		-s --silent <ndiFile>	apply profile and not show interface
		-v --version 		print nvidiux version
		--accept-eula		Read and accept eula
		--no-stat 		Disable All stat
		<ndiFile> 		apply profile and show nvidiux'''
	
	def setGpuStat(self,step,offsetGpu,offsetMem):
		if self.pref.sendStat:
			try:
				if step == 1:
					page=urllib.urlopen('http://nvidiux.redirectme.net:8883/gpuStat2.html?gpu=' + str(self.tabGpu[0].nameGpu).replace(" ","_") + "&uuid=" + str(self.tabGpu[0].uuid)  + '&os=' + str(self.pref.labelOs).replace(" ","_"))
					return 0
				elif step == 2:
					page=urllib.urlopen("http://nvidiux.redirectme.net:8883/gpuStatOverclock2.html?UUID=" + str(self.tabGpu[0].uuid) + "&gpu_new_freq=" + str(self.tabGpu[0].freqGpu) + "," + str(offsetGpu) + "&mem_new_freq=" + str(self.tabGpu[0].freqMem)+ "," + str(offsetMem) + "&shader_new_freq="+ str(self.tabGpu[0].freqShader))
					return 0
				else:
					return 11
			except:
				return 1
		else:
			return 10
			
	def setStartSystem(self,start,value):
		self.pref.startWithSystem = start
		self.pref.valueStart = value
		
	def setLanguage(self,language):
		self.pref.language = language
		nvidiuxTranslator = QtCore.QTranslator()
		if nvidiuxTranslator.load("/usr/share/nvidiux/nvidiux_" + language):
			app.installTranslator(nvidiuxTranslator)
		self.ui.retranslateUi(self)
	
	def setAutoUpdate(self):
		try:
			if self.pref.autoUpdate:
				self.pref.autoUpdate = False
				self.threadInfoGpu.stop()
			else:
				self.pref.autoUpdate = True
				self.threadInfoGpu = Mythread(self.pref.updateTime, majGpu, [0], {"fen":nvidiuxApp})
				self.threadInfoGpu.setDaemon(True)
				self.threadInfoGpu.start()
			return True
		except:
			return False
	
	def setShowOvervoltButton(self,value):
		if value:
			for i in range(0, self.pref.nbGpuNvidia):
				cmd = "nvidia-settings --query [gpu:" + str(i) + "]/GPUOverVoltageOffset"
				out, err = sub.Popen(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True).communicate()
				try:
					self.tabGpu[i].maxOvervolt = int(out.split('range')[1].split("(inclusive)")[0].split("-")[1])
					self.tabGpu[i].overvolt = int(out.split('range')[1].split("(inclusive)")[0].split("-")[0])
				except:
					self.tabGpu[i].maxOvervolt = 0
					self.tabGpu[i].overvolt = 0

		self.ui.spinBoxOvervolt.setMaximum(self.tabGpu[self.numGpu].maxOvervolt)
		self.ui.labelValueOvervolt.setText(str(self.tabGpu[self.numGpu].overvolt) + _translate("nvidiux","μv",None))
		self.pref.overvoltEnabled = value
		self.ui.groupBoxOvervolt.setEnabled(value)
		
		if self.tabGpu[self.numGpu].maxOvervolt == 0:
			self.ui.groupBoxOvervolt.setEnabled(False)
			
	def setSameParamGpu(self,value):
		self.pref.sameParamGpu = value
	
	def setTimeUpdate(self,value):
		self.pref.updateTime = int(value)
		self.threadInfoGpu.stop()
		self.threadInfoGpu = Mythread(self.pref.updateTime, majGpu, [0], {"fen":nvidiuxApp})
		self.threadInfoGpu.setDaemon(True)
		self.threadInfoGpu.start()
		
	def setVaapi(self,value):
		if not self.vaapi:
			msg = "Pour activer la vaapi (Vidéo Accélération api) vous devez installer les paquets neccesaire à la vaapi\n"
			if platform.linux_distribution()[0] == "Ubuntu" or platform.linux_distribution()[0] == "Debian":
				msg = msg + "Utiliser la commande suivante:apt install libvdpau1 vdpau-va-driver"
			QMessageBox.information(self,_translate("nvidiux","vaapi",None),_translate("nvidiux",msg,None))
			self.ui.checkBoxVaapi.setChecked(False)
		else:
			self.ui.checkBoxVaapi.setChecked(True)
		
	def stateFan(self,value):
		if value:
			cmd = "nvidia-settings -a [gpu:" + str(self.numGpu) + "]/GPUFanControlState=1"
			if sub.call(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True):
				self.ui.SliderFan.setEnabled(False)
				self.ui.checkBoxFan.setChecked(False)
				self.showError(-1,_translate("nvidiux","Impossible",None),_translate("nvidiux","Impossible de changer la configuration des ventillos",None),self.warning)
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
				self.showError(-1,_translate("nvidiux","Impossible",None),_translate("nvidiux","Impossible de revenir à la configuration par defaut des ventillos",None),self.warning)
			else:
				self.ui.SliderFan.setEnabled(False)
				self.ui.labelFanVitesse.setText("Auto")
				
	def showDonate(self):
		
		self.donateW = DonateWindow(self.pref.language,app)
		self.donateW.show()
	
	def startMonitor(self):
		if self.pidMonitor != 0:
			try:
				os.kill(self.pidMonitor,9)
			except OSError:
				self.showError(-1,_translate("nvidiux","Erreur communication",None),_translate("nvidiux","Impossible de communiquer avec le processus monitor",None),self.warning)
			self.ui.buttonStartMonitor.setText("Lancer")
			self.ui.actionStartMonitor.setText("Lancer")
			self.threadMonitor.stop()
			self.pidMonitor = 0
		else:
			if self.pref.monitorGen == 1:
				proc = sub.Popen(['python2', '/usr/share/nvidiux/monitor/monitor.py', "&"])
			else:
				proc = sub.Popen(['python2', '/usr/share/nvidiux/monitor/monitor2.py', "&"])
			self.pidMonitor = proc.pid
			
			self.threadMonitor = ThreadCheckMonitor([proc.pid], {"fen":nvidiuxApp})
			self.threadMonitor.start()
			self.ui.buttonStartMonitor.setText("Stop")
			self.ui.actionStartMonitor.setText("Stop")
		return True
		
	def stateVSync(self,value):
		if value:
			cmd = "nvidia-settings -a SyncToVBlank=1"
			if not sub.call(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True):
				self.ui.checkBoxVSync.setChecked(True)
				printMessage(_fromUtf8("Vsync Actif"))
			else:
				self.ui.checkBoxVSync.setChecked(False)
				self.showError(-1,_translate("nvidiux","Impossible",None),_translate("nvidiux","Impossible d'activer la syncro vertical",None),self.warning)
		else:
			cmd = "nvidia-settings -a SyncToVBlank=0"
			if not sub.call(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True):
				self.ui.checkBoxVSync.setChecked(False)
				self.printMessage(_fromUtf8("Vsync Inactif"))
			else:
				self.ui.checkBoxVSync.setChecked(True)
				self.showError(-1,_translate("nvidiux","Impossible",None),_translate("nvidiux","Impossible de desactiver la syncro vertical",None),self.warning)
		return True
	
	def saveNvidiuxConf(self):
		fileToSave = minidom.Document()
		racine = fileToSave.createElement("nvidiux")
		fileToSave.appendChild(racine)
		version = fileToSave.createElement('version')
		text = fileToSave.createTextNode(str(self.pref.nvidiuxVersion))
		version.appendChild(text)
		racine.appendChild(version)
		lang = fileToSave.createElement('lang')
		text = fileToSave.createTextNode(str(self.pref.language))
		lang.appendChild(text)
		racine.appendChild(lang)
		update = fileToSave.createElement('update')
		text = fileToSave.createTextNode(str(self.pref.autoUpdate))
		update.appendChild(text)
		racine.appendChild(update)
		overvoltEnabled = fileToSave.createElement('overvoltenabled')
		text = fileToSave.createTextNode(str(self.pref.overvoltEnabled))
		overvoltEnabled.appendChild(text)
		racine.appendChild(overvoltEnabled)
		updateinterval = fileToSave.createElement('updateinterval')
		text = fileToSave.createTextNode(str(self.pref.updateTime))
		updateinterval.appendChild(text)
		racine.appendChild(updateinterval)
		startSystem = fileToSave.createElement('start-system')
		if self.pref.startWithSystem:
			text = fileToSave.createTextNode("True")
		else:
			text = fileToSave.createTextNode("False")
		startSystem.appendChild(text)
		racine.appendChild(startSystem)
		sendStat = fileToSave.createElement('send-stat')
		if self.pref.sendStat:
			text = fileToSave.createTextNode("True")
		else:
			text = fileToSave.createTextNode("False")
		sendStat.appendChild(text)
		racine.appendChild(sendStat)
		valueStart = fileToSave.createElement('valuestart')
		text = fileToSave.createTextNode(str(self.pref.valueStart))
		valueStart.appendChild(text)
		racine.appendChild(valueStart)
		sameGpuParam = fileToSave.createElement('samegpuparam')
		text = fileToSave.createTextNode(str(self.pref.sameParamGpu))
		sameGpuParam.appendChild(text)
		racine.appendChild(sameGpuParam)
		try:	
			filexml = open(self.home + "/.nvidiux/conf.xml", "w")
			filexml.write(fileToSave.toprettyxml())
			filexml.close()
		except:
			return 1
		return 0
	
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
		text = fileToSave.createTextNode(str(self.pref.nvidiuxVersion))
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
			volt = fileToSave.createElement('volt')
			text = fileToSave.createTextNode(str(tempgpu.overvolt))
			volt.appendChild(text)
			
			gpuNode.appendChild(name)
			gpuNode.appendChild(freq)
			gpuNode.appendChild(shader)
			gpuNode.appendChild(mem)
			gpuNode.appendChild(volt)
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
		
	def setMonitorGen(self,gen):
		self.pref.monitorGen = gen
	
	def setThread(self,threadMonitor,threadInfoGpu):
		self.threadMonitor = threadMonitor
		self.threadInfoGpu = threadInfoGpu
		
	def switchMemVid(self):
		if self.showMemVid:
			self.showMemVid = False
			self.ui.MemGpu.setText(_translate("nvidiux","Interface Memoire",None) + "\n" + str(self.tabGpu[self.numGpu].memInterface) + " BITS")
		else:
			self.ui.MemGpu.setText(_translate("nvidiux","Memoire video",None) + "\n" + str(self.tabGpu[self.numGpu].videoRam) + " Go")
			self.showMemVid = True
	
	def switchValueMem(self):
		if self.showValueMem:
			self.showValueMem = False
		else:
			self.showValueMem = True
			
	def switchApi(self):
		if not self.showGraphicApi:
			self.showGraphicApi = True
			self.ui.OpenGlSupport.setText(_translate("nvidiux","Vulkan Support",None) + "\n" + str(self.tabGpu[self.numGpu].vulkanVersion))	
		else:	
			self.ui.OpenGlSupport.setText(_translate("nvidiux","OpenGl Support",None) + "\n" + str(self.tabGpu[self.numGpu].openGlVersion))
			self.showGraphicApi = False
			
	def switchUseGpu(self):
		cmd = "nvidia-settings --query [gpu:" + str(self.numGpu) + "]/GPUUtilization"
		out, err = sub.Popen(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True).communicate()
		if not self.showUseGpu:
			self.showUseGpu = True
			self.ui.UGPU.setText(_translate("nvidiux","Utilisation Gpu",None) + "\n" + str(out.split('graphics=')[1].split(',')[0]) + "%")
		else:
			self.showUseGpu = False
			self.ui.UGPU.setText(_translate("nvidiux","Util décodage video",None)+ "\n" + str(out.split('video=')[1].split(',')[0]) + "%")
					
	def updateMem(self,value):
		if self.pref.sameParamGpu and self.pref.nbGpuNvidia > 1:
			nomGpu = self.tabGpu[self.numGpu].gpuName
			for gpu in self.tabGpu:
				if gpu.gpuName == nomGpu:
					gpu.freqMem = value
		else:
			self.tabGpu[self.numGpu].freqMem = value
		self.ui.lcdMem.display(value)
		self.ui.SliderMem.setSliderPosition(value)
		if value != self.tabGpu[self.numGpu].defaultFreqMem and value != self.tabGpu[self.numGpu].defaultFreqGpu:	
			self.ui.buttonApply.setEnabled(True)
			self.change = True
		else:
			self.ui.buttonApply.setEnabled(False)
			self.change = False
		
	def updateGpu(self,value):
		if self.pref.sameParamGpu and self.pref.nbGpuNvidia > 1:
			nomGpu = self.tabGpu[self.numGpu].gpuName
			i = 0
			for gpu in self.tabGpu:
				if gpu.gpuName == nomGpu:
					gpu.freqGpu = value
					if self.tabGpu[i].arch == "fermi":
						gpu.freqShader = value * 2
					else:
						gpu.freqShader = value
				i = i + 1
		else:
			self.tabGpu[self.numGpu].freqGpu = value
			if self.tabGpu[self.numGpu].arch == "fermi":
				self.tabGpu[self.numGpu].freqShader = value * 2
			else:
				self.tabGpu[self.numGpu].freqShader = value
				
		self.ui.lcdGPU.display(self.tabGpu[self.numGpu].freqGpu)
		self.ui.lcdShader.display(self.tabGpu[self.numGpu].freqShader)
		self.ui.SliderShader.setSliderPosition(self.tabGpu[self.numGpu].freqShader)
		if value != self.tabGpu[self.numGpu].defaultFreqMem and value != self.tabGpu[self.numGpu].defaultFreqGpu:	
			self.ui.buttonApply.setEnabled(True)
			self.change = True
		else:
			self.ui.buttonApply.setEnabled(False)
			self.change = False
		
	def verifyGpu(self,gpuName):#-1:unknown 0:ok 1:not ok 
		verified = ["geforce gt 420m","geforce gtx 460m","geforce gt 430","geforce gt 440","geforce gtx 460","geforce gtx 460 se v2","geforce gtx 470","geforce gtx 480",
		"geforce gtx 550 ti","geforce gtx 560m","geforce gtx 560 ti","geforce gtx 570","geforce gtx 580",
		"geforce gt 620","geforce gt 630","geforce gtx 650","geforce gtx 660","geforce gtx 670","geforce gtx 680","geforce gtx 690",
		"geforce gt 730","geforce gt 740","geforce gtx 750","geforce gtx 750 ti","geforce gtx 760","geforce gtx 770","geforce gtx 780","geforce gtx 780 ti",
		"geforce gtx 960","geforce gtx 970","geforce gtx 980","geforce gtx 980 ti","geforce gtx 880m",
		"geforce gt 1030","geforce gtx 1050","geforce gtx 1050 ti","geforce gtx 1060","geforce gtx 1070","geforce gtx 1070 ti","geforce gtx 1080","geforce gtx 1080 ti",
		"geforce rtx 2070","geforce rtx 2080"]
		notWork = ["geforce gt 340", "geforce gt 330", "geforce gt 320", "geforce 315", "geforce 310","geforce gts 360m", "geforce gts 350m", "geforce gt 335m", "geforce gt 330m","geforce gt 325m", "geforce gt 320m", "geforce 320m", "geforce 315m", "geforce 310m", "geforce 305m",
		"geforce gtx 295", "geforce gtx 285","geforce gtx 280", "geforce gtx 275", "geforce gtx 260", "geforce gts 250", "geforce gts 240", "geforce gt 230", "geforce gt 240", "geforce gt 220", "geforce g210", "geforce 210", "geforce 205",
		"geforce gtx 285m", "geforce gtx 280m", "geforce gtx 260m", "geforce gts 260m", "geforce gts 250m", "geforce gt 240m", "geforce gt 230m", "geforce gt 220m", "geforce g210m", "geforce g205m",
		"geforce gt 140", "geforce gt 130", "geforce gt 120", "geforce g100","geforce gts 160m", "geforce gts 150m", "geforce gt 130m", "geforce gt 120m", "geforce g 110m", "geforce g 105m", "geforce g 103m"
		"geforce 9800 gx2", "geforce 9800 gtx/gtx+", "geforce 9800 gt", "geforce 9600 gt", "geforce 9600 gso", "geforce 9600 gso 512", "geforce 9600 gs", "geforce 9500 gt", "geforce 9500 gs", "geforce 9400 gt", "geforce 9400", "geforce 9300 gs", "geforce 9300 ge", "geforce 9300 se", "geforce 9300", "geforce 9200", "geforce 9100",
		"geforce 9800m gtx", "geforce 9800m gts", "geforce 9800m gt", "geforce 9800m gs", "geforce 9700m gts", "geforce 9700m gt", "geforce 9650m gt", "geforce 9650m gs", "geforce 9600m gt", "geforce 9600m gs", "geforce 9500m gs", "geforce 9500m g", "geforce 9400m g", "geforce 9400m", "geforce 9300m gs", "geforce 9300m g", "geforce 9200m gs", "geforce 9100m g",
		"geforce 8800 ultra", "geforce 8800 gtx", "geforce 8800 gts 512", "geforce 8800 gts", "geforce 8800 gt","geforce 8800 gs", "geforce 8600 gts", "geforce 8600 gt", "geforce 8600 gs", "geforce 8500 gt", "geforce 8400 gs", "geforce 8400 se", "geforce 8400", "geforce 8300 gs", "geforce 8300", "geforce 8200", "geforce 8100 /nforce 720a",
		"geforce 8800m gtx", "geforce 8800m gts", "geforce 8700m gt", "geforce 8600m gt", "geforce 8600m gs", "geforce 8400m gt", "geforce 8400m gs", "geforce 8400m g", "geforce 8200m g", "geforce 8200m"]
	
		if gpuName.lower() in verified:
			return 0
		if gpuName.lower() in notWork:
			return 1
		return -1
		
if __name__ == "__main__":
	app = QApplication(sys.argv)
	localeSystem = QtCore.QLocale.system().name()
	if "en" in localeSystem:
		localeSystem  = "en_EN"
	elif "es" in localeSystem:
		localeSystem = "es_ES"
	elif "de" in localeSystem:
		localeSystem = "de_DE"
	elif "fr" in localeSystem:
		localeSystem = "fr_FR"
	else:
		localeSystem = "en_EN"
	nvidiuxTranslator = QtCore.QTranslator()
	if not os.path.isfile("/usr/share/nvidiux/nvidiux_" + localeSystem + ".qm") or localeSystem == "fr_FR":
		nvidiuxTranslator.load("qt_" + localeSystem,QtCore.QLibraryInfo.location(QtCore.QLibraryInfo.TranslationsPath))
		app.installTranslator(nvidiuxTranslator)
	else:
		nvidiuxTranslator.load("/usr/share/nvidiux/nvidiux_" + localeSystem)
		app.installTranslator(nvidiuxTranslator)
	
	nvidiuxApp = NvidiuxApp(sys.argv[1:])
	threadMonitor = ThreadCheckMonitor([0], {"fen":nvidiuxApp})
	threadInfoGpu = None
	if nvidiuxApp.autoUpdate:
		threadInfoGpu = Mythread(nvidiuxApp.pref.updateTime, majGpu, [0], {"fen":nvidiuxApp})
		threadInfoGpu.setDaemon(True)
		threadInfoGpu.start()
	nvidiuxApp.setThread(threadMonitor,threadInfoGpu)
	nvidiuxApp.show()
	sys.exit(app.exec_())
