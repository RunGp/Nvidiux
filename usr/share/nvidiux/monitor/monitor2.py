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




from pyqtgraph.Qt import QtGui, QtCore
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *

import os
import collections
import sys
import random
import time
import math
import numpy as np
import subprocess as sub
import pyqtgraph as pg
from Monitor2ui import Ui_MainWindow

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
	xMem = None
	yMem = None
	percentGpu = 0
	percentFan = 0
	totalMem = 0
	temperature = 0
	memoryUse = 0
	driverVersion = 0
	gpuName = ""
	
class MonitorApp(QMainWindow):
	
	
	sampleInterval=1.0 #second
	timeWindow=240 #second
	error = -1
	warning = -2
	plotGpuCurve = None
	plotFanCurve = None
	monitorVersion = 0.8
	versionPilote = 331.31
	versionPiloteMaxTest = 364.19
	nbGpuNvidia = -1
	tabGpu = list()
    
	def __init__(self,argv,parent=None,):
		super (MonitorApp, self).__init__(parent)

		self.ui = Ui_MainWindow()
		self.ui.setupUi(self)
		print "Nvidiux Monitor Beta 1"
		cmd = "nvidia-settings --query [gpu:0]/NvidiaDriverVersion"
		if not sub.call(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True):
			out, err = sub.Popen(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True).communicate()
			self.versionPilote = float(out.split(':')[-1][1:])
		else:
			sys.exit(1)
		
		if self.versionPilote > self.versionPiloteMaxTest:
			print "Driver non testé"
			
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
					return self.showError(4,"Gpu Nvidia introuvable","Gpu Nvidia introuvable",self.error)
			except:
				return self.showError(4,"Gpu Nvidia introuvable","Gpu Nvidia introuvable",self.error)
		
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

		self.ui.plotGpu.setTitle("Use GPU")
		self.ui.plotGpu.showGrid(x=True, y=True)
		self.ui.plotGpu.setLabel('left', '%')
		self.ui.plotGpu.setLabel('bottom', 'Time', 'sec')
		self.ui.plotGpu.setRange(yRange=[0,100])
		self.plotGpuCurve = self.ui.plotGpu.plot(self.tabGpu[0].xGpu, self.tabGpu[0].yGpu, pen=(255,0,0))
		self.ui.plotFan.setTitle("Use Fan")
		self.ui.plotFan.showGrid(x=True, y=True)
		self.ui.plotFan.setLabel('left', '%')
		self.ui.plotFan.setLabel('bottom', 'Time', 'sec')
		self.ui.plotFan.setRange(yRange=[0,100])
		self.plotFanCurve = self.ui.plotFan.plot(self.tabGpu[0].xFan, self.tabGpu[0].yFan, pen=(255,0,0))
		self.ui.plotTemp.setTitle("Temperature")
		self.ui.plotTemp.showGrid(x=True, y=True)
		self.ui.plotTemp.setLabel('left', '°C')
		self.ui.plotTemp.setLabel('bottom', 'Time', 'sec')
		self.ui.plotTemp.setRange(yRange=[0,120])
		self.plotTempCurve = self.ui.plotTemp.plot(self.tabGpu[0].xTemp, self.tabGpu[0].yTemp, pen=(255,0,0))
		
		
		cmd = "nvidia-settings --query [gpu:0]/videoRam"
		if not sub.call(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True):
			out, err = sub.Popen(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True).communicate()
			self.tabGpu[0].totalMem = int(float(out.split(': ')[1].split('.')[0]) / 1024)
		else:
			sys.exit(1)
		
		self.ui.plotMem.setTitle("Use Memory")
		self.ui.plotMem.showGrid(x=True, y=True)
		self.ui.plotMem.setLabel('left', 'Mo')
		self.ui.plotMem.setLabel('bottom', 'Time', 'sec')
		self.ui.plotMem.setRange(yRange=[0,self.tabGpu[0].totalMem])
		self.plotMemCurve = self.ui.plotMem.plot(self.tabGpu[0].xMem, self.tabGpu[0].yMem, pen=(255,0,0))
		
		
		self.timer = QtCore.QTimer()
		self.timer.timeout.connect(self.updatePlot)
		self.timer.start(self.interval)


	def iscompatible(self):
		
		cmd = "ls -l /usr/lib | grep nvidia"
		if sub.call(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True):
			return self.showError(1,_translate("nvidiux","Non supporte",None),_translate("nvidiux","Driver introuvable \nVeuillez installer les pilotes proprietaires",None),self.error)
		if not os.path.isfile("/usr/bin/nvidia-settings"):
			return self.showError(2,_translate("nvidiux","Non supporte",None),_translate("nvidiux","Nvidia settings introuvable \nveuillez installer les pilotes proprietaires et nvidia settings",None),self.error)
		
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
					return self.showError(4,"Gpu Nvidia introuvable","Gpu Nvidia introuvable",self.error)
			except:
				return self.showError(4,"Gpu Nvidia introuvable","Gpu Nvidia introuvable",self.error)

		if self.nbGpu >= 2: #MultiGpu
			if ListeGpu.count('Intel') == 1 and self.nbGpuNvidia == 1 : #optimus
				if os.popen("prime-supported 2>> /dev/null", "r").read().replace('\n','') != "yes":
					return self.showError(3,_translate("nvidiux","Prime",None),_translate("nvidiux","Seul prime est supporte pour les configurations optimus",None),self.error)	
				if os.popen("prime-select query", "r").read().replace('\n','') != "nvidia":
					return self.showError(-1,_translate("nvidiux","Mode intel",None),_translate("nvidiux","Configuration Prime\nVeuillez passer en mode nvidia svp",None),self.info)
				self.optimus = 1
				self.ui.checkBoxOptimus.setChecked(1)
		
		
	def getDataGpu(self):
		cmd = "nvidia-settings --query [gpu:0]/GPUUtilization"
		if not sub.call(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True):
			out, err = sub.Popen(cmd + "| grep GPUUtilization | head -1",stdout=sub.PIPE,stderr=sub.PIPE,shell=True).communicate()
			self.tabGpu[0].percentGpu = int(out.split('=')[1].split(',')[0])
			return self.tabGpu[0].percentGpu 
		else:
			sys.exit(1)
			return None
			
	def getDataFan(self):
		cmd = "nvidia-settings --query [fan:0]/GPUCurrentFanSpeed"
		if not sub.call(cmd ,stdout=sub.PIPE,stderr=sub.PIPE,shell=True):
			out, err = sub.Popen(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True).communicate()
			self.tabGpu[0].percentFan = int(out.split(': ')[1].split('.')[0])
			return self.tabGpu[0].percentFan
		else:
			sys.exit(1)
			return None
			
	def getDataTemp(self):
		cmd = "nvidia-settings --query [gpu:0]/GPUCoreTemp"
		if not sub.call(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True):
			out, err = sub.Popen(cmd + " | grep GPUCore | head -1",stdout=sub.PIPE,stderr=sub.PIPE,shell=True).communicate()
			self.tabGpu[0].temperature = int(out.split(':')[-1].split('.')[0])
			return self.tabGpu[0].temperature
		else:
			sys.exit(1)
			return None
			
	def getDataMem(self):
		cmd = "nvidia-settings --query [gpu:0]/UsedDedicatedGPUMemory"
		if not sub.call(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True):
			out, err = sub.Popen(cmd + " | grep UsedDedicatedGPUMemory | head -1",stdout=sub.PIPE,stderr=sub.PIPE,shell=True).communicate()
			self.tabGpu[0].memoryUse = int(out.split(':')[-1].split('.')[0])
			return self.tabGpu[0].memoryUse
		else:
			sys.exit(1)
			return None
		
	def showError(self,errorCode,title,errorMsg,etype):
		if etype == self.error:
			errorMsg = errorMsg + "\nError Code:" + str(errorCode)
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
		

if __name__ == '__main__':

	app = QApplication(sys.argv)
	monitorApp = MonitorApp(sys.argv[1:])
	monitorApp.show()
	sys.exit(app.exec_())
    
