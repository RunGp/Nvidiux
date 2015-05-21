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

import sys,fileinput,os
if os.path.isfile("/etc/X11/xorg.conf"):
	os.popen("cp /etc/X11/xorg.conf /etc/X11/xorg.conf.bak").read()
	for line in fileinput.input("/etc/X11/xorg.conf",inplace=True): 
	    print line.replace("\n","").replace("Section \"Device\"", "Section \"Device\"\n    Option         \"Coolbits\" \"12\"")

else:
	print os.popen("nvidia-xconfig").read()
	os.popen("cp /etc/X11/xorg.conf /etc/X11/xorg.conf.bak").read()
	for line in fileinput.input("/etc/X11/xorg.conf",inplace=True): 
	    print line.replace("\n","").replace("Section \"Device\"", "Section \"Device\"\n    Option         \"Coolbits\" \"12\"")

os.chmod("/etc/X11/xorg.conf", 0664)
