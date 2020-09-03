from __future__ import absolute_import
#
# This is an extension to the Nautilus file manager to allow better
# integration with the Subversion source control system.
# 
# Copyright (C) 2006-2008 by Jason Field <jason@jasonfield.com>
# Copyright (C) 2007-2008 by Bruce van der Kooij <brucevdkooij@gmail.com>
# Copyright (C) 2008-2010 by Adam Plumb <adamplumb@gmail.com>
# 
# RabbitVCS is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# RabbitVCS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with RabbitVCS;  If not, see <http://www.gnu.org/licenses/>.
#

import os
import subprocess

import pygtk
import gtk

from rabbitvcs.ui.action import GitAction
import rabbitvcs.vcs

from rabbitvcs import gettext
_ = gettext.gettext

from rabbitvcs.util.log import Log
log = Log("rabbitvcs.ui.cherrypick")

class GitCherrypick:
	def __init__(self, path, commits):
		self.vcs = rabbitvcs.vcs.VCS()
		self.git = self.vcs.git(path)
		self.commits = commits
		
		self.action = GitAction(
			self.git,
			register_gtk_quit=True
		)
		self.action.hide_cancel_button()
		self.action.append(self.action.set_header, _("Cherry Pick"))
		self.action.append(self.action.set_status, _("Cherry Pick selected commits..."))
		self.action.append(self.git.cherrypick, commits)
		self.action.append(self.action.set_status, _("Completed Cherry Pick"))
		self.action.append(self.action.finish)
		self.action.schedule()

if __name__ == "__main__":
	from rabbitvcs.ui import main
	(options, args) = main(usage="Usage: rabbitvcs cherrypick path [commit]")
	
	log.debug("options = %s, args = %s" % (options, args))
	
	window = GitCherrypick(args[0], args[1::])
	gtk.main()
