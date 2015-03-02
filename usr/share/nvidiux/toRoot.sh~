#!/bin/bash

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

if [ $XDG_CURRENT_DESKTOP = "Kde" ] || [ $XDG_CURRENT_DESKTOP = "KDE" ]
then
	kdesudo python /usr/share/nvidiux/add_coolbits.py
	exit $?
else
	gksudo python /usr/share/nvidiux/add_coolbits.py
	exit $?
fi
	
