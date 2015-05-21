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

import shutil
import os
import sys
if not os.path.isfile("/etc/rc.local") or not os.path.isfile("/tmp/nvidiuxOk.rcfile"):
	sys.exit(1)
if os.getuid() != 0:
	sys.exit(2)

shutil.move("/etc/rc.local","/etc/rc.local.bak")
shutil.copy("/tmp/nvidiuxOk.rcfile","/etc/rc.local")
sys.exit(0)

