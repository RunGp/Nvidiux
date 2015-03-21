# -*- coding: utf-8 -*-
#!/usr/bin/python2

#This program was created by Peter Schmidt on January 21, 2011
#This depends on the the Nvidia driver 270.xx or higher and devilspie.

from Tkinter import *
import os, sys
import subprocess as sub
import threading
import time


class GpuInfoMonitor():
	
	def __init__(self,color):
		self.color = color
	oldPointTemp = 0
	oldPointFan = 0
	oldPointGpu = 0
	oldPointMem = 0
	totalMem = 0
	ABS = 0
	time = 0
	gpuName = ""
	templabel = ""
	fanlabel = ""
	gpulabel = ""
	memlabel = ""
	memclklabel = ""
	coreclklabel = ""
	shaderclklabel = ""
	
def loop():
	
	if gpu1.ABS >= 580:
		fanchart.delete("all")
		tempchart.delete("all")
		gpuchart.delete("all")
		memchart.delete("all")
		gpu1.ABS = 0

	if gpu1.ABS == 0:
		for i in range (1,5):
			fanchart.create_line(0, i * 76,580, i * 76,fill="grey")
			tempchart.create_line(0, i * 76,580, i * 76,fill="grey")
			gpuchart.create_line(0, i * 76,580, i * 76,fill="grey")
			memchart.create_line(0, i * 76,580, i * 76,fill="grey")
		
	cmd = "nvidia-settings --query [gpu:0]/GPUCoreTemp"
	if not sub.call(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True):
		out, err = sub.Popen(cmd + " | grep GPUCore | head -1",stdout=sub.PIPE,stderr=sub.PIPE,shell=True).communicate()
		gpu1.templabel = "Temp:" + str(out.split(':')[-1].split('.')[0]) + "°C"
		templabel.set(gpu1.templabel)
	else:
		sys.exit(0)
		
	newPointTemp = 380 - int(int(out.split(':')[-1].split('.')[0]) * 380 / 125)
	tempchart.create_line(gpu1.ABS,gpu1.oldPointTemp,gpu1.ABS + 5,newPointTemp,fill=gpu1.color)
	gpu1.oldPointTemp = newPointTemp

	cmd = "nvidia-settings --query [fan:0]/GPUCurrentFanSpeed"
	if not sub.call(cmd ,stdout=sub.PIPE,stderr=sub.PIPE,shell=True):
		out, err = sub.Popen(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True).communicate()
		gpu1.fanlabel = "Fan:" + str(out.split(': ')[1].split('.')[0]) + "%"
		fanlabel.set(gpu1.fanlabel)
	else:
		sys.exit(0)
	
	newPointFan = 380 - int(int(out.split(': ')[1].split('.')[0]) * 380 / 100)
	fanchart.create_line(gpu1.ABS,gpu1.oldPointFan,gpu1.ABS + 5,newPointFan,fill=gpu1.color)
	gpu1.oldPointFan = newPointFan
	
	cmd = "nvidia-settings --query [gpu:0]/GPUUtilization"
	if not sub.call(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True):
		out, err = sub.Popen(cmd + "| grep GPUUtilization | head -1",stdout=sub.PIPE,stderr=sub.PIPE,shell=True).communicate()
		gpu1.gpulabel = "Core:" + str(out.split('=')[1].split(',')[0]) + "%"
		gpulabel.set(gpu1.gpulabel)
	else:
		sys.exit(0)
	
	newPointGpu = int( 380 - int(out.split('=')[1].split(',')[0]) * 380 / 100)
	gpuchart.create_line(gpu1.ABS,gpu1.oldPointGpu,gpu1.ABS + 5,newPointGpu,fill=gpu1.color)
	gpu1.oldPointGpu = newPointGpu	
	
	
	cmd = "nvidia-settings --query [gpu:0]/UsedDedicatedGPUMemory"
	if not sub.call(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True):
		out, err = sub.Popen(cmd + " | grep UsedDedicatedGPUMemory | head -1",stdout=sub.PIPE,stderr=sub.PIPE,shell=True).communicate()
		gpu1.memlabel = "Mem:" + str(out.split(':')[-1].split('.')[0]) + " Mo"
		memlabel.set(gpu1.memlabel)
	else:
		sys.exit(0)
	newPointMem = int(380 - int(out.split(':')[-1].split('.')[0]) * 380 / gpu1.totalMem)
	memchart.create_line(gpu1.ABS,gpu1.oldPointMem,gpu1.ABS + 5,newPointMem,fill=gpu1.color)
	gpu1.oldPointMem = newPointMem
		
	gpu1.ABS = gpu1.ABS + 5
	gpu1.time = gpu1.time + interval
	timeLabel.set("Temps écoulé :" + str(int(gpu1.time / 1000)) + " secondes")
	
	tkRT.after(interval,loop)


interval = 1000

tkRT=Tk()
tkRT.title("Moniteur_Nvidiux")
gpuName = StringVar()
templabel = StringVar()
fanlabel = StringVar()
gpulabel = StringVar()
memlabel = StringVar()
memclklabel = StringVar()
coreclklabel = StringVar()
shaderclklabel = StringVar()
timeLabel = StringVar()
gpu1 = GpuInfoMonitor("red")
gpu1.totalMem = 1280
gpu1.time = 0

gpuName.set("GTX570")
coreclklabel.set("Core:732 MHz")
shaderclklabel.set("Shader:1048 MHz")
memclklabel.set("Memory:4000 MHz")
timeLabel.set("Temps écoulé:0 secondes")

cmd = "nvidia-settings --query [gpu:0]/GPUCoreTemp"
if not sub.call(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True):
	out, err = sub.Popen(cmd + " | grep GPUCore | head -1",stdout=sub.PIPE,stderr=sub.PIPE,shell=True).communicate()
	gpu1.oldPointTemp = int(380 - int(out.split(':')[-1].split('.')[0]) * 380 / 125)
else:
	sys.exit(0)

cmd = "nvidia-settings --query [fan:0]/GPUCurrentFanSpeed"
if not sub.call(cmd ,stdout=sub.PIPE,stderr=sub.PIPE,shell=True):
	out, err = sub.Popen(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True).communicate()
	gpu1.oldPointFan = int(380 - int(out.split(': ')[1].split('.')[0]) * 380 / 100)
else:
	sys.exit(0)

cmd = "nvidia-settings --query [gpu:0]/GPUUtilization"
if not sub.call(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True):
	out, err = sub.Popen(cmd + "| grep GPUUtilization | head -1",stdout=sub.PIPE,stderr=sub.PIPE,shell=True).communicate()
	gpu1.oldPointGpu = int( 380 - int(out.split('=')[1].split(',')[0]) * 380 / 100)
else:
	sys.exit(0)

cmd = "nvidia-settings --query [gpu:0]/UsedDedicatedGPUMemory"
if not sub.call(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True):
	out, err = sub.Popen(cmd + " | grep UsedDedicatedGPUMemory | head -1",stdout=sub.PIPE,stderr=sub.PIPE,shell=True).communicate()
	gpu1.oldPointMem = int(380 - int(out.split(':')[-1].split('.')[0]) * 380 / gpu1.totalMem)
else:
	sys.exit(0)

mainframe=Frame(tkRT)
mainframe.pack()

tempchart=Canvas(mainframe,width=580,height=380,bg="black")
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
Label(mainframe,textvariable = coreclklabel).grid(column=0,row=3,columnspan=3)
Label(mainframe,textvariable = shaderclklabel).grid(column=0,row=2,columnspan=3)

tkRT.geometry("1280x880+0+0")

tkRT.after(interval,loop)
tkRT.mainloop()
