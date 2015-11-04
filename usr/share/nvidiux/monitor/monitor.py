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

from Tkinter import *
import tkMessageBox
import os, sys
import subprocess as sub
import threading
import time
from os.path import expanduser
from xml.dom import minidom


class GpuInfoMonitor():
	
	def __init__(self):
		self.color = None
	oldPointTemp = 0
	oldPointFan = 0
	oldPointGpu = 0
	oldPointMem = 0
	totalMem = 0
	ABS = 0
	time = 0
	driverVersion = 0
	gpuName = ""
	templabel = ""
	fanlabel = ""
	gpulabel = ""
	memlabel = ""
	memclklabel = ""
	coreclklabel = ""
	shaderclklabel = ""
	
class ElementConfGpu():
	idGpu = 0
	color = [0,0,0]
	show = False

	def __init__(self, idGpu,color, show):
		try:
			if int(idGpu) > 0:
				self.idGpu = int(idGpu)
			else:
				self.idGpu = 1
			if int(color.split(':')[0]) >= 0 and int(color.split(':')[0]) <= 255:
				self.color[0] = int(color.split(':')[0])
			else:
				self.color[0] = 255
			if int(color.split(':')[1]) >= 0 and int(color.split(':')[1]) <= 255:
				self.color[1] = int(color.split(':')[1])
			else:
				self.color[1] = 255
			if int(color.split(':')[2]) >= 0 and int(color.split(':')[2]) <= 255:
				self.color[2] = int(color.split(':')[2])
			else:
				self.color[2] = 255
		except:
			self.idGpu = 1
			self.color[0] = 255
			self.color[1] = 0
			self.color[2] = 0
			
		if show == "True":
			self.show = True
		else:
			self.show = False	
	def info():
		print "Gpu" + str(idGpu) +")\nColor red:" + str(self.color[0]) + "blue:" + str(self.color[1]) + "green:" + str(self.color[2]) + "\nShow:" + str(self.show)
		
	def getId(self):
		return self.idGpu
	def getColor(self):
		return "#%02x%02x%02x" % (self.color[0],self.color[1],self.color[2])
	def getColorStr(self):
		return str(self.color[0]) + ":" + str(self.color[1]) + ":" + str(self.color[2])
	def getShow(self):
		return self.show

def closeEvent():
	saveConf(confGpu,monitorVersion)
	tkRT.destroy()

def color(value):
	return confGpu[value].getColor()
		
def saveConf(listgpu,versionMonitor):
	fileToSave = minidom.Document()
	racine = fileToSave.createElement("nvidiux")
	fileToSave.appendChild(racine)
	version = fileToSave.createElement('version')
	text = fileToSave.createTextNode(str(versionMonitor))
	version.appendChild(text)
	racine.appendChild(version)
	for gpu in listgpu:
		gpuElem = fileToSave.createElement('gpu')
		idGpu = fileToSave.createElement('id')
		text = fileToSave.createTextNode(str(gpu.getId()))
		idGpu.appendChild(text)
		gpuElem.appendChild(idGpu)
		colorGpu = fileToSave.createElement('color')
		text = fileToSave.createTextNode(str(gpu.getColorStr()))
		colorGpu.appendChild(text)
		gpuElem.appendChild(colorGpu)
		showGpu = fileToSave.createElement('show')
		text = fileToSave.createTextNode(str(gpu.getShow()))
		showGpu.appendChild(text)
		gpuElem.appendChild(showGpu)
		racine.appendChild(gpuElem)
	try:	
		filexml = open(expanduser("~") + "/.nvidiux/monitor.xml", "w")
		filexml.write(fileToSave.toprettyxml())
		filexml.close()
	except:
		print "Fail save monitor conf!"
		return 1
	return 0
	
def loop():
	if gpu1.ABS >= 575:
		#~ tempchart.xview_moveto((gpu1.ABS - 575 ) / 5 * 0.00050)
		#~ for i in range (1,6):
			#~ tempchartText = tempchart.create_text(2, 381 - i * 76, anchor="nw",fill = "grey")
			#~ tempchart.itemconfig(tempchartText, text = str(int(i * 24)) + "°C")
			#~ tempchart.insert(tempchartText, 12, "")
			#~ tempchart.create_line(gpu1.ABS, i * 76,gpu1.ABS + 580, i * 76,fill = "grey")
		fanchart.delete("all")
		tempchart.delete("all")
		gpuchart.delete("all")
		memchart.delete("all")
		gpu1.ABS = 0

	if gpu1.ABS == 0: # draw line
		for i in range (1,6):
			fanchart.create_line(0, i * 76,580, i * 76,fill = "grey")
			fanchartText = fanchart.create_text(2, 381 - i * 76, anchor="nw",fill = "grey")
			fanchart.itemconfig(fanchartText, text = str(int(i * 20)) + "%")
			fanchart.insert(fanchartText, 12, "")
			gpuchartText = gpuchart.create_text(2, 381 - i * 76, anchor="nw",fill = "grey")
			gpuchart.itemconfig(gpuchartText, text = str(int(i * 20)) + "%")
			gpuchart.insert(gpuchartText, 12, "")
			gpuchart.create_line(0, i * 76,580, i * 76,fill = "grey")
			tempchartText = tempchart.create_text(2, 381 - i * 76, anchor="nw",fill = "grey")
			tempchart.itemconfig(tempchartText, text = str(int(i * 24)) + "°C")
			tempchart.insert(tempchartText, 12, "")
			tempchart.create_line(0, i * 76,580, i * 76,fill = "grey")
			memchartText = memchart.create_text(2, 381 - i * 76, anchor="nw",fill = "grey")
			memchart.itemconfig(memchartText, text = str(int(i * float(gpu1.totalMem / 5))) + "Mo")
			memchart.insert(memchartText, 12, "")
			memchart.create_line(0, i * 76,580, i * 76,fill = "grey")

	for i in range(0,nbGpuNvidia):
		cmd = "nvidia-settings --query [gpu:" + str(i) + "]/GPUCoreTemp"
		if not sub.call(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True):
			out, err = sub.Popen(cmd + " | grep GPUCore | head -1",stdout=sub.PIPE,stderr=sub.PIPE,shell=True).communicate()
			if nbGpuNvidia == 1:
				gpu1.templabel = "Temp : " + str(out.split(':')[-1].split('.')[0]) + "°C"
				templabel.set(gpu1.templabel)
			else:
				templabel.set("Multi GPU")
		else:
			sys.exit(0)
		newPointTemp = 380 - int(int(out.split(':')[-1].split('.')[0]) * 380 / 125)
		tempchart.create_line(gpu1.ABS,gpu1.oldPointTemp,gpu1.ABS + 5,newPointTemp,fill=color(i))
	
	gpu1.oldPointTemp = newPointTemp

	for i in range(0,nbGpuNvidia):
		cmd = "nvidia-settings --query [fan:" + str(i) + "]/GPUCurrentFanSpeed"
		if not sub.call(cmd ,stdout=sub.PIPE,stderr=sub.PIPE,shell=True):
			out, err = sub.Popen(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True).communicate()
			if nbGpuNvidia == 1:
				gpu1.fanlabel = "Fan : " + str(out.split(': ')[1].split('.')[0]) + "%"
				fanlabel.set(gpu1.fanlabel)
			else:
				fanlabel.set("Multi GPU")
		else:
			sys.exit(0)
		
		newPointFan = 380 - int(int(out.split(': ')[1].split('.')[0]) * 380 / 100)
		fanchart.create_line(gpu1.ABS,gpu1.oldPointFan,gpu1.ABS + 5,newPointFan,fill=color(i))
		
	gpu1.oldPointFan = newPointFan
	
	for i in range(0,nbGpuNvidia):
		cmd = "nvidia-settings --query [gpu:" + str(i) + "]/GPUUtilization"
		if not sub.call(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True):
			out, err = sub.Popen(cmd + "| grep GPUUtilization | head -1",stdout=sub.PIPE,stderr=sub.PIPE,shell=True).communicate()
			if nbGpuNvidia == 1:
				gpu1.gpulabel = "Core : " + str(out.split('=')[1].split(',')[0]) + "%"
				gpulabel.set(gpu1.gpulabel)
			else:
				gpulabel.set("Multi GPU")
		else:
			sys.exit(0)
		newPointGpu = int( 380 - int(out.split('=')[1].split(',')[0]) * 380 / 100)
		gpuchart.create_line(gpu1.ABS,gpu1.oldPointGpu,gpu1.ABS + 5,newPointGpu,fill=color(i))
	gpu1.oldPointGpu = newPointGpu	
	
	for i in range(0,nbGpuNvidia):
		cmd = "nvidia-settings --query [gpu:" + str(i) + "]/UsedDedicatedGPUMemory"
		if not sub.call(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True):
			out, err = sub.Popen(cmd + " | grep UsedDedicatedGPUMemory | head -1",stdout=sub.PIPE,stderr=sub.PIPE,shell=True).communicate()
			if nbGpuNvidia == 1:
				gpu1.memlabel = "Mem : " + str(out.split(':')[-1].split('.')[0]) + " Mo"
				memlabel.set(gpu1.memlabel)
			else:
				memlabel.set("Multi GPU")
		else:
			sys.exit(0)
		newPointMem = int(380 - int(out.split(':')[-1].split('.')[0]) * 380 / gpu1.totalMem)
		memchart.create_line(gpu1.ABS,gpu1.oldPointMem,gpu1.ABS + 5,newPointMem,fill=color(i))
	gpu1.oldPointMem = newPointMem
	
	if nbGpuNvidia == 1:
		cmd = "nvidia-settings --query [gpu:0]/GPUCurrentClockFreqsString"
		if not sub.call(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True):
			out, err = sub.Popen(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True).communicate()
			try:
				coreclklabel.set("Core :" + out.split('nvclockmax=')[1].split(',')[0] + "Mhz")
			except:
				sys.exit(1)
			try:
				memclklabel.set("Mem : " + str(out.split('memTransferRatemax=')[1].split(',')[0]) + "Mhz")
			except:
				sys.exit(1)
		else:
			self.showError(31,"Echec","Echec chargement des parametres Gpu",self.error)
	else:
		coreclklabel.set("Multi GPU")
		
			
	gpu1.ABS = gpu1.ABS + 5
	gpu1.time = gpu1.time + interval
	if int(gpu1.time / 1000) <= 1:
		timeLabel.set("Temps écoulé : " + str(int(gpu1.time / 1000)) + " seconde")
	else:
		timeLabel.set("Temps écoulé : " + str(int(gpu1.time / 1000)) + " secondes")
	tkRT.after(interval,loop)

interval = 1000
tkRT=Tk()
tkRT.title("Moniteur Nvidiux")
tkRT.protocol('WM_DELETE_WINDOW', closeEvent)
gpuName = StringVar()
templabel = StringVar()
fanlabel = StringVar()
gpulabel = StringVar()
memlabel = StringVar()
memclklabel = StringVar()
coreclklabel = StringVar()
shaderclklabel = StringVar()
timeLabel = StringVar()
gpu1 = GpuInfoMonitor()
gpu1.time = 0
monitorVersion = 0.99
monitorVersionStr = "0.99"
listGpu = []
gpuInfo = [] #idGpu,color, show
confGpu = []
error = False
print "Monitor " + monitorVersionStr

cmd = "nvidia-settings --query [gpu:0]/NvidiaDriverVersion"
if not sub.call(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True):
	out, err = sub.Popen(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True).communicate()
	versionPilote = float(out.split(':')[-1][1:])
else:
	sys.exit(1)
if versionPilote > 349.00 and versionPilote < 349.53:
	tkMessageBox.showwarning("Erreur Version","Le moniteur n'est pas compatible avec cette version:(%s)" % versionPilote)
        sys.exit(1)

cmd = "lspci -vnn | egrep 'VGA|3D'"
ListeGpu, err = sub.Popen(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True).communicate()
nbGpuNvidia = ListeGpu.count('NVIDIA')
if nbGpuNvidia == 1:
	cmd = "lspci -vnn | grep NVIDIA | grep -v Audio | head -n 2"
	out, err = sub.Popen(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True).communicate()
	gpuName.set(out.split(':')[-2].split('[')[-2].split(']')[0])
else:
	gpuName.set("Multi Gpu")

try:
	profileFile = open(expanduser("~") + "/.nvidiux/monitor.xml", "r")
	ndiFile = minidom.parse(profileFile)
except:
	for i in range(1,nbGpuNvidia):
		confGpu.append(ElementConfGpu(i,"255:0:0","True"))
	saveConf(confGpu,monitorVersion)
	ndiFile = None

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
				listGpu.append(gpuInfo)
				gpuInfo = []

	for gpuInfo in listGpu:
		confGpu.append(ElementConfGpu(gpuInfo[0],gpuInfo[1],gpuInfo[2])) #3 inf for each gpu (idGpu,color, show)
	
cmd = "nvidia-settings --query [gpu:0]/GPUCurrentClockFreqsString"
if not sub.call(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True):
	out, err = sub.Popen(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True).communicate()
	try:
		coreclklabel.set("Core :" + out.split('nvclockmax=')[1].split(',')[0] + "Mhz")
	except:
		sys.exit(1)
	try:
		memclklabel.set("Mem : " + str(out.split('memTransferRatemax=')[1].split(',')[0]) + "Mhz")
	except:
		sys.exit(1)
else:
	self.showError(31,"Echec","Echec chargement des parametres Gpu",self.error)

timeLabel.set("Temps écoulé : 0 seconde")

cmd = "nvidia-settings --query [gpu:0]/GPUCoreTemp"
if not sub.call(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True):
	out, err = sub.Popen(cmd + " | grep GPUCore | head -1",stdout=sub.PIPE,stderr=sub.PIPE,shell=True).communicate()
	gpu1.oldPointTemp = int(380 - int(out.split(':')[-1].split('.')[0]) * 380 / 125)
else:
	sys.exit(1)

cmd = "nvidia-settings --query [fan:0]/GPUCurrentFanSpeed"
if not sub.call(cmd ,stdout=sub.PIPE,stderr=sub.PIPE,shell=True):
	out, err = sub.Popen(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True).communicate()
	gpu1.oldPointFan = int(380 - int(out.split(': ')[1].split('.')[0]) * 380 / 100)
else:
	sys.exit(1)

cmd = "nvidia-settings --query [gpu:0]/GPUUtilization"
if not sub.call(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True):
	out, err = sub.Popen(cmd + "| grep GPUUtilization | head -1",stdout=sub.PIPE,stderr=sub.PIPE,shell=True).communicate()
	gpu1.oldPointGpu = int( 380 - int(out.split('=')[1].split(',')[0]) * 380 / 100)
else:
	sys.exit(1)

cmd = "nvidia-settings --query [gpu:0]/videoRam"
if not sub.call(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True):
	out, err = sub.Popen(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True).communicate()
	gpu1.totalMem = float(out.split(': ')[1].split('.')[0]) / 1024
else:
	sys.exit(1)

cmd = "nvidia-settings --query [gpu:0]/UsedDedicatedGPUMemory"
if not sub.call(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True):
	out, err = sub.Popen(cmd + " | grep UsedDedicatedGPUMemory | head -1",stdout=sub.PIPE,stderr=sub.PIPE,shell=True).communicate()
	gpu1.oldPointMem = int(380 - int(out.split(':')[-1].split('.')[0]) * 380 / gpu1.totalMem)
else:
	sys.exit(1)
	
mainframe=Frame(tkRT)
mainframe.pack()


tempchart=Canvas(mainframe,width=580,height=380,bg="black")
tempchart.config(scrollregion=[0,0,10000,380])
tempchart.grid(column=0,row=4)


Label(mainframe,textvariable = templabel).grid(column=0,row=3)

fanchart=Canvas(mainframe,width=580,height=380,bg="black")
fanchart.grid(column=2,row=4)
Label(mainframe,textvariable = fanlabel).grid(column=2,row=3)

Label(mainframe,textvariable = timeLabel).grid(column=0,row=5,columnspan=3)
Label(mainframe,text = "  ").grid(column=1,row=4)
Label(mainframe,text = "  ").grid(column=1,row=3)
Label(mainframe,text = "  ").grid(column=1,row=7)
Label(mainframe,text = "  ").grid(column=1,row=6)

gpuchart=Canvas(mainframe,width=580,height=380,bg="black")
gpuchart.grid(column=0,row=6)
Label(mainframe,textvariable = gpulabel).grid(column=0,row=7)

memchart=Canvas(mainframe,width=580,height=380,bg="black")
memchart.grid(column=2,row=6)
Label(mainframe,textvariable = memlabel).grid(column=2,row=7)

Label(mainframe,textvariable = gpuName).grid(column=0,row=0,columnspan=3)
Label(mainframe,textvariable = memclklabel).grid(column=0,row=1,columnspan=3)
Label(mainframe,textvariable = coreclklabel).grid(column=0,row=2,columnspan=3)
tkRT.geometry("1280x880+0+0")
tkRT.after(interval,loop)
tkRT.mainloop()
sys.exit(0)
