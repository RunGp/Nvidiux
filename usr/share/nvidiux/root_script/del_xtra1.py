# -*- coding: utf-8 -*-
#!/usr/bin/python2

# Copyright 2016 Payet Guillaume
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

import sys
import fileinput
import os
import shutil
if os.path.isfile("/etc/X11/xorg.conf"):
	shutil.copy("/etc/X11/xorg.conf","/etc/X11/xorg.conf.bak.xtra1")
	for line in fileinput.input("/etc/X11/xorg.conf",inplace=True):
		if not "PerfLevelSrc=0x2222" in line :
			print line.replace("\n","")
	
os.chmod("/etc/X11/xorg.conf", 0664)

