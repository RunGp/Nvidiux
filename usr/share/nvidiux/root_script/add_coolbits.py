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

import sys,fileinput,os,shutil
if os.path.isfile("/etc/X11/xorg.conf"):
	shutil.copy("/etc/X11/xorg.conf","/etc/X11/xorg.conf.bak")
	if not os.path.isdir("/etc/X11/xorg.conf.d"):
		os.mkdir("/etc/X11/xorg.conf.d")
	if os.path.isfile("/etc/X11/xorg.conf.d/nvidiux.conf"):
		os.remove("/etc/X11/xorg.conf.d/nvidiux.conf")
	file = open("/etc/X11/xorg.conf.d/nvidiux.conf", "a")
	file.write(
"""Section "Device"
    Identifier     "Device0"
    Driver         "nvidia"
    VendorName     "NVIDIA Corporation"
    Option         "Coolbits" "28"
Endsection
""")
	file.close()

else:
	print os.popen("nvidia-xconfig").read()
	shutil.copy("/etc/X11/xorg.conf","/etc/X11/xorg.conf.bak")
	if not os.path.isdir("/etc/X11/xorg.conf.d"):
		os.mkdir("/etc/X11/xorg.conf.d")
	if os.path.isfile("/etc/X11/xorg.conf.d/nvidiux.conf"):
		os.remove("/etc/X11/xorg.conf.d/nvidiux.conf")
	file = open("/etc/X11/xorg.conf.d/nvidiux.conf", "a")
	file.write(
"""Section "Device"
    Identifier     "Device0"
    Driver         "nvidia"
    VendorName     "NVIDIA Corporation"
    Option         "Coolbits" "28"
Endsection
""")
if os.path.isfile("/etc/X11/xorg.conf.d/nvidiux.conf"):
	os.chmod("/etc/X11/xorg.conf.d/nvidiux.conf", 0664)
