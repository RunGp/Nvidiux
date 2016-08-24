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


try:
	from pyqtgraph.Qt import QtGui, QtCore
	import pyqtgraph as pg
	import pyqtgraph.exporters
except:
	from PyQt4.QtCore import *
	from PyQt4.QtGui import *
	from PyQt4 import QtCore, QtGui
	import sys
	app = QApplication(None)
	QtGui.QMessageBox.critical(None, "pyqtgraph","You must install pyqtgraph Package")
	sys.exit(0)


from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from monitorSettings import Ui_Pref_Monitor
import os
import collections
import sys
import time
import numpy as np
import subprocess as sub
import platform
from monitor2ui import Ui_MainWindow

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

class GpuInfoMonitor():
	
	def __init__(self):
		self.color = None
	color = None	
	dataBufferGpu = None
	xGpu = None
	yGpu = None
	dataBufferFan = None
	xFan = None
	yFan = None
	dataBufferTemp = None
	xTemp = None
	yTemp = None
	dataBufferMem = None
	formSettings = None
	xMem = None
	yMem = None
	percentGpu = 0
	percentFan = 0
	totalMem = 0
	temperature = 0
	memoryUse = 0
	driverVersion = 0
	gpuName = ""
	freqGpu = 0
	
class MonitorApp(QMainWindow):
	
	
	sampleInterval = 1 #second
	timeWindow = 240 #second
	totalTime = 0
	error = -1
	warning = -2
	plotGpuCurve = None
	plotFanCurve = None
	anguage = None
	monitorVersion = 0.8
	monitorVersionStr = "0.8.1"
	versionPilote = 331.31
	versionPiloteMaxTest = 370.23
	nbGpuNvidia = -1
	tabGpu = list()
    
	def __init__(self,argv,parent=None,):
		super (MonitorApp, self).__init__(parent)

		self.ui = Ui_MainWindow()
		self.pref.language = QtCore.QLocale.system().name()
		self.ui.setupUi(self)
		textSystem = _translate("monitor","Nvidia driver version: ",None)
		cmd = "nvidia-settings --query [gpu:0]/NvidiaDriverVersion"
		if not sub.call(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True):
			out, err = sub.Popen(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True).communicate()
			self.pref.piloteVersion = float(out.split(':')[-1][1:])
			textSystem = textSystem + str(self.pref.piloteVersion) + "\n"
		else:
			sys.exit(1)
		
		if self.pref.piloteVersion > self.versionPiloteMaxTest:
			print _translate("monitor","Driver > MAX",None)
			
		self.iscompatible()
		self.interval = int(self.sampleInterval*1000)
		self.bufSize = int(self.timeWindow / self.sampleInterval)
		
		for i in range(0,self.nbGpuNvidia):
			self.tabGpu.append(GpuInfoMonitor())
			self.tabGpu[i].dataBufferGpu = collections.deque([0.0]*self.bufSize, self.bufSize)
			self.tabGpu[i].dataBufferFan = collections.deque([0.0]*self.bufSize, self.bufSize)
			self.tabGpu[i].dataBufferMem = collections.deque([0.0]*self.bufSize, self.bufSize)
			self.tabGpu[i].dataBufferTemp = collections.deque([0.0]*self.bufSize, self.bufSize)
			
			self.tabGpu[i].xGpu = np.linspace(self.timeWindow, 0.0, self.bufSize)
			self.tabGpu[i].xFan = np.linspace(self.timeWindow, 0.0, self.bufSize)
			self.tabGpu[i].xMem = np.linspace(self.timeWindow, 0.0, self.bufSize)
			self.tabGpu[i].xTemp = np.linspace(self.timeWindow, 0.0, self.bufSize)
			self.tabGpu[i].yGpu = np.zeros(self.bufSize, dtype=np.float)
			self.tabGpu[i].yFan = np.zeros(self.bufSize, dtype=np.float)
			self.tabGpu[i].yMem = np.zeros(self.bufSize, dtype=np.float)
			self.tabGpu[i].yTemp = np.zeros(self.bufSize, dtype=np.float)
			
		self.ui.labelGpu.setAlignment(QtCore.Qt.AlignCenter)
		self.ui.labelMemory.setAlignment(QtCore.Qt.AlignCenter)
		self.ui.labelTemp.setAlignment(QtCore.Qt.AlignCenter)
		self.ui.labelFan.setAlignment(QtCore.Qt.AlignCenter)
		self.ui.labelTime.setAlignment(QtCore.Qt.AlignCenter)
		self.ui.labelGpuName.setAlignment(QtCore.Qt.AlignCenter)
		self.ui.labelInfo.setAlignment(QtCore.Qt.AlignCenter)
		
		cmd = "nvidia-settings --query [gpu:0]/videoRam"
		if not sub.call(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True):
			out, err = sub.Popen(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True).communicate()
			self.tabGpu[0].totalMem = int(float(out.split(': ')[1].split('.')[0]) / 1024)
		else:
			sys.exit(1)

		self.ui.plotGpu.setTitle(_translate("monitor","Use GPU",None))
		self.ui.plotGpu.showGrid(x=True, y=True)
		self.ui.plotGpu.setLabel('left', '%')
		self.ui.plotGpu.setLabel('bottom', _translate("monitor","Time",None), 'sec')
		self.ui.plotGpu.setRange(yRange=[8,91],xRange=[20,220])
		self.ui.plotGpu.setMenuEnabled(enableMenu=False)
		self.ui.plotGpu.autoRange(padding=0)
		self.plotGpuCurve = self.ui.plotGpu.plot(self.tabGpu[0].xGpu, self.tabGpu[0].yGpu, pen=(255,0,0))
		
		self.ui.plotFan.setTitle(_translate("monitor","Use Fan",None))
		self.ui.plotFan.showGrid(x=True, y=True)
		self.ui.plotFan.setLabel('left', '%')
		self.ui.plotFan.setLabel('bottom', _translate("monitor","Time",None), 'sec')
		self.ui.plotFan.setRange(yRange=[9,91],xRange=[20,220])
		self.ui.plotFan.setMenuEnabled(enableMenu=False)
		self.ui.plotFan.autoRange(padding=0)
		self.plotFanCurve = self.ui.plotFan.plot(self.tabGpu[0].xFan, self.tabGpu[0].yFan, pen=(255,0,0))
		
		self.ui.plotTemp.setTitle(_translate("monitor","Temperature",None))
		self.ui.plotTemp.showGrid(x=True, y=True)
		self.ui.plotTemp.setLabel('left', '°C')
		self.ui.plotTemp.setLabel('bottom', _translate("monitor","Time",None), 'sec')
		self.ui.plotTemp.setRange(yRange=[9,91],xRange=[20,220])
		self.ui.plotTemp.setMenuEnabled(enableMenu=False)
		self.ui.plotTemp.autoRange(padding=0)
		self.plotTempCurve = self.ui.plotTemp.plot(self.tabGpu[0].xTemp, self.tabGpu[0].yTemp, pen=(255,0,0))
			
		self.ui.plotMem.setTitle(_translate("monitor","Use Memory",None))
		self.ui.plotMem.showGrid(x=True, y=True)
		self.ui.plotMem.setLabel('left', 'Mo')
		self.ui.plotMem.setLabel('bottom', _translate("monitor","Time",None), 'sec')
		self.ui.plotMem.setRange(yRange=[110,self.tabGpu[0].totalMem - 80],xRange=[20,220])
		self.ui.plotMem.autoRange(padding=0)
		self.ui.plotMem.setMenuEnabled(enableMenu=False)
		self.plotMemCurve = self.ui.plotMem.plot(self.tabGpu[0].xMem, self.tabGpu[0].yMem, pen=(255,0,0))
		
		textgpu = _translate("monitor","Gpu name : ",None)
		cmd = "lspci -vnn | grep NVIDIA | grep -v Audio | grep GeForce"
		out, err = sub.Popen(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True).communicate()			
		try:
			self.tabGpu[0].nameGpu = str("GeForce" + out.split('\n')[i].split("GeForce")[-1].split("]")[0])
			textgpu = textgpu + self.tabGpu[0].nameGpu + "\n" + _translate("monitor","Gpu Freq : ",None)
			 
		except:
			sys.exit(1)
		
		cmd = "nvidia-settings --query [gpu:" + str(i) + "]/GPUCurrentClockFreqsString"
		if not sub.call(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True):
			out, err = sub.Popen(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True).communicate()
			try:
				self.tabGpu[0].freqGpu = str(out.split('nvclockmax=')[1].split(',')[0])
				textgpu = textgpu + self.tabGpu[0].freqGpu + "Mhz\n" + _translate("monitor","Memory freq : ",None)
			except:
				sys.exit(1)
			try:
				self.tabGpu[i].freqMem = str(out.split('memTransferRatemax=')[1].split(',')[0])
				textgpu = textgpu + self.tabGpu[i].freqMem  + "Mhz"
			except:
				sys.exit(1)

		textSystem = textSystem + _translate("monitor","Os version : ",None)
		self.linuxDistrib = platform.linux_distribution()
		if self.linuxDistrib == ('', '', ''):
			if os.path.isfile("/etc/issue"):
				with open("/etc/issue") as f:
					textSystem = textSystem + f.read().split()[0] + " " + platform.architecture()[0]
			else:
				textSystem = textSystem + "Unknow distrib " + platform.architecture()[0]
		else:
			textSystem = textSystem + self.linuxDistrib[0] + " " + self.linuxDistrib[1]
		
		self.ui.labelTime.setText(str(self.totalTime + self.sampleInterval) + _translate("monitor"," second",None))
		self.ui.labelGpuName.setText(textgpu)
		self.ui.labelInfo.setText(textSystem)
		
		if self.nbGpuNvidia >=2:
			self.ui.bouttonGpu.setEnabled(True)
		
		self.ui.bouttonExport.connect(self.ui.bouttonExport,SIGNAL("released()"),self.exportGraph)
		self.ui.bouttonSettings.connect(self.ui.bouttonSettings,SIGNAL("released()"),self.settings)
		self.ui.bouttonAbout.connect(self.ui.bouttonAbout,SIGNAL("released()"),self.about)
		self.ui.bouttonGpu.connect(self.ui.bouttonGpu,SIGNAL("released()"),self.changeGpu)
		
		self.timer = QtCore.QTimer()
		self.timer.timeout.connect(self.updatePlot)
		self.timer.start(self.interval)
		
	def about(self):
		tabParam = list()
		tabParam.append(self.monitorVersion)
		tabParam.append(self.monitorVersionStr)
		tabParam.append(self.nbGpuNvidia)
		tabParam.append(self.tabGpu)
		tabParam.append(self.pref.language)
		tabParam.append(app)
		self.formSettings = Ui_Pref_Monitor(1,tabParam,self)
		self.formSettings.show()
	
	def changeGpu(self):
		sys.exit(0)
		
	def exportGraph(self):
		exporter = pg.exporters.ImageExporter(self.ui.plotGpu.plotItem)
		exporter2 = pg.exporters.ImageExporter(self.ui.plotFan.plotItem)
		exporter3 = pg.exporters.ImageExporter(self.ui.plotTemp.plotItem)
		exporter4 = pg.exporters.ImageExporter(self.ui.plotMem.plotItem)

		filename = QtGui.QFileDialog.getSaveFileName(self, "Save png", "Export.png", "*.png")
		if filename == '':
			return False
		if str(filename[-4:]) == ".png":
			filename = filename[:-4]
		exporter.export(filename + "Gpu" + ".png")
		exporter2.export(filename + "Fan" + ".png")
		exporter3.export(filename + "Temp" + ".png")
		exporter4.export(filename + "Mem" + ".png")
		return True
		
	def getDataGpu(self):
		cmd = "nvidia-settings --query [gpu:0]/GPUUtilization"
		if not sub.call(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True):
			out, err = sub.Popen(cmd + "| grep GPUUtilization",stdout=sub.PIPE,stderr=sub.PIPE,shell=True).communicate()
			self.tabGpu[0].percentGpu = int(out.split('=')[1].split(',')[0])
			self.ui.labelGpu.setText(str(self.tabGpu[0].percentGpu) + " %")
			return self.tabGpu[0].percentGpu 
		else:
			sys.exit(1)
			return None
			
	def getDataFan(self):
		cmd = "nvidia-settings --query [fan:0]/GPUCurrentFanSpeed"
		if not sub.call(cmd ,stdout=sub.PIPE,stderr=sub.PIPE,shell=True):
			out, err = sub.Popen(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True).communicate()
			self.tabGpu[0].percentFan = int(out.split(': ')[1].split('.')[0])
			self.ui.labelFan.setText(str(self.tabGpu[0].percentFan) + " %")
			return self.tabGpu[0].percentFan
		else:
			sys.exit(1)
			return None
			
	def getDataTemp(self):
		cmd = "nvidia-settings --query [gpu:0]/GPUCoreTemp"
		if not sub.call(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True):
			out, err = sub.Popen(cmd + " | grep GPUCore",stdout=sub.PIPE,stderr=sub.PIPE,shell=True).communicate()
			self.tabGpu[0].temperature = int(out.split('.')[0].split(': ')[1])
			self.ui.labelTemp.setText(str(self.tabGpu[0].temperature) + " C")
			return self.tabGpu[0].temperature
		else:
			sys.exit(1)
			return None
			
	def getDataMem(self):
		cmd = "nvidia-settings --query [gpu:0]/UsedDedicatedGPUMemory"
		if not sub.call(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True):
			out, err = sub.Popen(cmd + " | grep UsedDedicatedGPUMemory",stdout=sub.PIPE,stderr=sub.PIPE,shell=True).communicate()
			self.tabGpu[0].memoryUse = int(out.split('.')[0].split(': ')[1])
			self.ui.labelMemory.setText(str(self.tabGpu[0].memoryUse) + " Mo")
			return self.tabGpu[0].memoryUse
		else:
			sys.exit(1)
			return None
			
	def iscompatible(self):
		
		cmd = "ls -l /usr/lib | grep nvidia"
		if sub.call(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True):
			return self.showError(1,_translate("monitor","Unsupported",None),_translate("monitor","Driver not found \nPlease install nvidia proprietary drivers",None),self.error)
		if not os.path.isfile("/usr/bin/nvidia-settings"):
			return self.showError(2,_translate("monitor","Unsupported",None),_translate("monitor","Nvidia settings not found \nPlease install nvidia proprietary drivers",None),self.error)
		
		cmd = "lspci -vnn | grep -E 'VGA|3D'"
		ListeGpu, err = sub.Popen(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True).communicate()
		self.nbGpuNvidia = ListeGpu.count('GeForce')
		self.nbGpu = len(ListeGpu)
		if self.nbGpuNvidia == 0:
			try:
				cmd = "nvidia-smi -L"
				ListeGpuSmi, err = sub.Popen(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True).communicate()
				self.nbGpuNvidia = ListeGpu.count('GeForce')
				if self.nbGpuNvidia == 0:
					return self.showError(4,_translate("monitor","Nvidia gpu not found",None),_translate("monitor","Nvidia gpu not found",None),self.error)
			except:
				return self.showError(4,_translate("monitor","Nvidia gpu not found",None),_translate("monitor","Nvidia gpu not found",None),self.error)
		
		if self.nbGpu >= 2: #MultiGpu
			if ListeGpu.count('Intel') == 1 and self.nbGpuNvidia == 1 : #optimus
				if os.popen("prime-supported 2>> /dev/null", "r").read().replace('\n','') != "yes":
					return self.showError(3,_translate("monitor","Prime",None),_translate("monitor","Only prime is supported for optimus configuration",None),self.error)	
				if os.popen("prime-select query", "r").read().replace('\n','') != "nvidia":
					return self.showError(-1,_translate("monitor","Mode intel",None),_translate("monitor","Prime\nPlease switch to nvidia mode",None),self.info)
				self.optimus = 1
				self.ui.checkBoxOptimus.setChecked(1)
			
	def settings(self):
		tabParam = list()
		tabParam.append(self.monitorVersion)
		tabParam.append(self.monitorVersionStr)
		tabParam.append(self.nbGpuNvidia)
		tabParam.append(self.tabGpu)
		tabParam.append(self.pref.language)
		tabParam.append(app)
		self.formSettings = Ui_Pref_Monitor(0,tabParam,self)
		self.formSettings.show()
		
	def showError(self,errorCode,title,errorMsg,etype):
		if etype == self.error:
			errorMsg = errorMsg + "\n" + _translate("monitor","Error Code:",None) + str(errorCode)
			QMessageBox.critical(self, _fromUtf8(title),_fromUtf8(errorMsg))
		elif etype == self.warning:
			QMessageBox.warning(self, _fromUtf8(title),_fromUtf8(errorMsg))	
		else:
			QMessageBox.information(self, _fromUtf8(title),_fromUtf8(errorMsg))
		return errorCode

	def updatePlot(self):
		self.tabGpu[0].dataBufferGpu.append(self.getDataGpu())
		self.tabGpu[0].yGpu[:] = self.tabGpu[0].dataBufferGpu
		self.plotGpuCurve.setData(self.tabGpu[0].xGpu, self.tabGpu[0].yGpu)
		self.tabGpu[0].dataBufferFan.append(self.getDataFan())
		self.tabGpu[0].yFan[:] = self.tabGpu[0].dataBufferFan
		self.plotFanCurve.setData(self.tabGpu[0].xFan, self.tabGpu[0].yFan)
		self.tabGpu[0].dataBufferTemp.append(self.getDataTemp())
		self.tabGpu[0].yTemp[:] = self.tabGpu[0].dataBufferTemp
		self.plotTempCurve.setData(self.tabGpu[0].xTemp, self.tabGpu[0].yTemp)
		self.tabGpu[0].dataBufferMem.append(self.getDataMem())
		self.tabGpu[0].yMem[:] = self.tabGpu[0].dataBufferMem
		self.plotMemCurve.setData(self.tabGpu[0].xMem, self.tabGpu[0].yMem)
		self.totalTime += self.sampleInterval
		self.ui.labelTime.setText(str(self.totalTime) + _translate("monitor"," seconds",None))

if __name__ == '__main__':

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
	monitorTranslator = QtCore.QTranslator()
	if localeSystem != "en_EN":
		if not os.path.isfile("/usr/share/nvidiux/nvidiux_" + localeSystem + ".qm"):
			monitorTranslator.load("qt_" + localeSystem,QtCore.QLibraryInfo.location(QtCore.QLibraryInfo.TranslationsPath))
		else:
			monitorTranslator.load("/usr/share/nvidiux/nvidiux_" + localeSystem)
		app.installTranslator(monitorTranslator)

	monitorApp = MonitorApp(sys.argv[1:])
	monitorApp.show()
	sys.exit(app.exec_())
    
