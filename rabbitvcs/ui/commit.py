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

import pygtk
import gtk
from time import sleep

try:
	from gi.repository import GObject as gobject
except ImportError:
	import gobject

from rabbitvcs.ui import InterfaceView
from rabbitvcs.util.contextmenu import GtkFilesContextMenu, GtkContextMenuCaller
import rabbitvcs.ui.action
import rabbitvcs.ui.widget
import rabbitvcs.ui.dialog
import rabbitvcs.util
from rabbitvcs.util import helper
from rabbitvcs.util.log import Log
from rabbitvcs.util.decorators import gtk_unsafe
import rabbitvcs.vcs.status

log = Log("rabbitvcs.ui.commit")

from rabbitvcs import gettext
_ = gettext.gettext

from rabbitvcs.ui.wraplabel import set_markup, TextColor

helper.gobject_threads_init()

class Commit(InterfaceView, GtkContextMenuCaller):
	"""
	Provides a user interface for the user to commit working copy
	changes to a repository.  Pass it a list of local paths to commit.
	"""
	SETTINGS = rabbitvcs.util.settings.SettingsManager()
	TOGGLE_ALL = False
	SHOW_UNVERSIONED = SETTINGS.get("general", "show_unversioned_files")
	# This keeps track of any changes that the user has made to the row
	# selections
	changes = {}
	
	def __init__(self, paths, base_dir=None, message=None):
		"""
		@type  paths:   list of strings
		@param paths:   A list of local paths.
		"""
		InterfaceView.__init__(self, "commit", "Commit")
		commit_widget = self.get_widget("Commit")
		
		# esh: autosize log window by screen width
		screen_width = rabbitvcs.ui.widget.get_screen_width()
		if screen_width > 2500:
			rabbitvcs.ui.widget.set_widget_size(commit_widget, 1500, 1200)
		elif screen_width > 1900:
			rabbitvcs.ui.widget.set_widget_size(commit_widget, 1400, 1025)
		else:
			commit_widget.maximize()
		
		self.isInitDone = False
		self.base_dir = base_dir
		self.vcs = rabbitvcs.vcs.VCS()
		self.items = []
		
		self.files_table = rabbitvcs.ui.widget.Table(
			self.get_widget("files_table"),
			[gobject.TYPE_BOOLEAN, rabbitvcs.ui.widget.TYPE_PATH,
				gobject.TYPE_STRING, rabbitvcs.ui.widget.TYPE_STATUS,
				gobject.TYPE_STRING],
			[rabbitvcs.ui.widget.TOGGLE_BUTTON, _("Path"), _("Extension"),
				_("Text Status"), _("Property Status")],
			filters=[{
				"callback": rabbitvcs.ui.widget.path_filter,
				"user_data": {
					"base_dir": base_dir,
					"column": 1
				}
			}],
			callbacks={
				"row-activated": self.on_files_table_row_activated,
				"mouse-event":   self.on_files_table_mouse_event,
				"key-event":     self.on_files_table_key_event,
				"row-toggled":   self.on_files_table_toggle_event
			},
			flags={
				"sortable": True,
				"sort_on": 1
			}
		)
		self.files_table.allow_multiple()
		self.get_widget("toggle_show_unversioned").set_active(self.SHOW_UNVERSIONED)
		self.message = rabbitvcs.ui.widget.TextView(
			self.get_widget("message"),
			(message and message or "")
		)
		# esh: text_clipboard for set_text_clipboard func
		self.text_clipboard = gtk.Clipboard()
		
		self.paths = []
		for path in paths:
			if self.vcs.is_in_a_or_a_working_copy(path):
				self.paths.append(path)
		self.isInitDone = True
	
	#
	# Helper functions
	#
	def load(self):
		"""
		  - Gets a listing of file items that are valid for the commit window.
		  - Determines which items should be "activated" by default
		  - Populates the files table with the retrieved items
		  - Updates the status area
		"""
		self.get_widget("status").set_text(_("Loading..."))
		self.items = self.vcs.get_items(self.paths, self.vcs.statuses_for_commit(self.paths))
		self.populate_files_table()
	
	# Overrides the GtkContextMenuCaller method
	def on_context_menu_command_finished(self):
		self.initialize_items()
	
	def should_item_be_activated(self, item):
		"""
		Determines if a file should be activated or not
		"""
		if (item.path in self.paths
				or item.is_versioned()
				and item.simple_content_status() != rabbitvcs.vcs.status.status_missing):
			return True
		return False
	
	def should_item_be_visible(self, item):
		show_unversioned = self.SHOW_UNVERSIONED
		if not show_unversioned:
			if not item.is_versioned():
			   return False
		return True
	
	def initialize_items(self):
		"""
		Initializes the activated cache and loads the file items
		"""
		gobject.idle_add(self.load)
	
	def show_files_table_popup_menu(self, treeview, data):
		paths = self.files_table.get_selected_row_items(1)
		GtkFilesContextMenu(self, data, self.base_dir, paths).show()
	
	def delete_items(self, widget, data=None):
		paths = self.files_table.get_selected_row_items(1)
		if len(paths) > 0:
			proc = helper.launch_ui_window("delete", paths)
			self.rescan_after_process_exit(proc, paths)
	
	def revert_items(self, widget, data=None):
		paths = self.files_table.get_selected_row_items(1)
		if len(paths) > 0:
			proc = helper.launch_ui_window("revert", ["-q"] + paths)
			self.rescan_after_process_exit(proc, paths)
	
	def set_text_clipboard(self, filename):
		self.text_clipboard.set_text(filename)
	
	#
	# Event handlers
	#
	def on_refresh_clicked(self, widget):
		self.initialize_items()
	
	def on_key_pressed(self, widget, data):
		if InterfaceView.on_key_pressed(self, widget, data):
			return True
		elif (data.state & gtk.gdk.CONTROL_MASK and
				data.keyval == gtk.keysyms.Return):
			self.on_ok_clicked(widget)
			return True
		elif data.keyval == gtk.keysyms.F2:
			self.get_widget("message").grab_focus()
			return True
		elif data.keyval == gtk.keysyms.F4:
			if len(self.files_table.get_items()) > 0 and \
			   len(self.files_table.get_selected_rows()) == 0:
				self.files_table.focus(0, 0)
			else:
				self.get_widget("files_table").grab_focus()
			return True
	
	def on_toggle_show_all_toggled(self, widget, data=None):
		self.TOGGLE_ALL = not self.TOGGLE_ALL
		self.changes.clear()
		for row in self.files_table.get_items():
			row[0] = self.TOGGLE_ALL
			self.changes[row[1]] = self.TOGGLE_ALL
	
	def on_toggle_show_unversioned_toggled(self, widget, data=None):
		if self.isInitDone:
			self.SHOW_UNVERSIONED = not self.SHOW_UNVERSIONED
		self.populate_files_table()
		# Save this preference for future commits.
		if self.SETTINGS.get("general", "show_unversioned_files") != self.SHOW_UNVERSIONED:
			self.SETTINGS.set(
				"general", "show_unversioned_files",
				self.SHOW_UNVERSIONED
			)
			self.SETTINGS.write()
	
	def on_files_table_row_activated(self, treeview, event, col):
		paths = self.files_table.get_selected_row_items(1)
		pathrev1 = helper.create_path_revision_string(paths[0], "base")
		pathrev2 = helper.create_path_revision_string(paths[0], "working")
		proc = helper.launch_ui_window("diff", ["-s", pathrev1, pathrev2])
		self.rescan_after_process_exit(proc, paths)
	
	def on_files_table_toggle_event(self, row, col):
		# Adds path: True/False to the dict
		self.changes[row[1]] = row[col]
	
	def on_files_table_key_event(self, treeview, data=None):
		state = data.state & rabbitvcs.ui.widget.CTRL_SHIFT_MASK
		if (state in (gtk.gdk.CONTROL_MASK, rabbitvcs.ui.widget.CTRL_SHIFT_MASK) and
				gtk.gdk.keyval_name(data.keyval).lower() in ("c", "cyrillic_es")):
			text = self.files_table.get_selected_paths(state != gtk.gdk.CONTROL_MASK)
			if text: self.set_text_clipboard(text)
			return True
		elif data.keyval == gtk.keysyms.Delete:
			self.delete_items(treeview, data)
			return True
		elif data.keyval == gtk.keysyms.F8:
			self.revert_items(treeview, data)
			return True
		elif data.keyval == gtk.keysyms.Return:
			self.on_files_table_row_activated(treeview, None, None)
			return True
		elif data.keyval == gtk.keysyms.space:
			selected_rows = self.files_table.get_selected_rows()
			if len(selected_rows) > 0:
				row = self.files_table.get_row(selected_rows[0])
				row[0] = not row[0]
				self.changes[row[1]] = row[0]
			return True
	
	def on_files_table_mouse_event(self, treeview, data=None):
		if data is not None and data.button == 3:
			self.show_files_table_popup_menu(treeview, data)
	
	def on_previous_messages_clicked(self, widget, data=None):
		dialog = rabbitvcs.ui.dialog.PreviousMessages()
		message = dialog.run()
		if message is not None:
			self.message.set_text(message)
	
	def populate_files_table(self):
		"""
		First clears and then populates the files table based on the items
		retrieved in self.load()
		"""
		# esh: get selected rows
		selected_rows = self.files_table.get_selected_rows()
		
		self.files_table.clear()
		n = 0
		m = 0
		for item in self.items:
			if item.path in self.changes:
				checked = self.changes[item.path]
			else:
				checked = self.should_item_be_activated(item)
			
			if item.is_versioned():
				n += 1
			else:
				m += 1
			
			if not self.should_item_be_visible(item):
				continue
			
			self.files_table.append([
				checked,
				item.path,
				helper.get_file_extension(item.path),
				item.simple_content_status(),
				item.simple_metadata_status()
			])
		
		# esh: set selected rows
		self.files_table.set_selected_rows(selected_rows, focus=True, default=True)
		
		self.get_widget("status").set_text(_("Found %(changed)d changed and %(unversioned)d unversioned item(s)") % {
				"changed": n,
				"unversioned": m
			}
		)

class SVNCommit(Commit):
	def __init__(self, paths, base_dir=None, message=None):
		Commit.__init__(self, paths, base_dir, message)
		self.get_widget("commit_to_box").show()
		set_markup(self.get_widget("to"), self.vcs.svn().get_repo_url(self.base_dir),
				   TextColor.INFO)
		self.items = None
		if len(self.paths):
			self.initialize_items()
	
	def on_ok_clicked(self, widget, data=None):
		items = self.files_table.get_activated_rows(1)
		self.hide()
		if len(items) == 0:
			self.close()
			return
		added = 0
		recurse = False
		for item in items:
			status = self.vcs.status(item, summarize=False).simple_content_status()
			try:
				if status == rabbitvcs.vcs.status.status_unversioned:
					self.vcs.svn().add(item)
					added += 1
				elif status == rabbitvcs.vcs.status.status_deleted:
					recurse = True
				elif status == rabbitvcs.vcs.status.status_missing:
					self.vcs.svn().update(item)
					self.vcs.svn().remove(item)
			except Exception as e:
				log.exception(e)
		ticks = added + len(items)*2
		self.action = rabbitvcs.ui.action.SVNAction(
			self.vcs.svn(),
			register_gtk_quit=self.gtk_quit_is_set()
		)
		self.action.set_pbar_ticks(ticks)
		self.action.append(self.action.set_header, _("Commit"))
		self.action.append(self.action.set_status, _("Running Commit Command..."))
		self.action.append(
			helper.save_log_message,
			self.message.get_text()
		),
		self.action.append(self.do_commit, items, recurse)
		self.action.append(self.action.finish)
		self.action.schedule()
	
	def do_commit(self, items, recurse):
		# pysvn.Revision
		revision = self.vcs.svn().commit(items, self.message.get_text(), recurse=recurse)
		self.action.set_status(_("Completed Commit") + " at Revision: " + str(revision.number))

class GitCommit(Commit):
	def __init__(self, paths, base_dir=None, message=None):
		Commit.__init__(self, paths, base_dir, message)
		self.git = self.vcs.git(paths[0])
		self.get_widget("commit_to_box").show()
		active_branch = self.git.get_active_branch()
		if active_branch:
			set_markup(self.get_widget("to"), active_branch.name, TextColor.INFO)
		else:
			set_markup(self.get_widget("to"), _("No active branch"), TextColor.WARN)
		self.items = None
		if len(self.paths):
			self.initialize_items()
	
	def on_ok_clicked(self, widget, data=None):
		items = self.files_table.get_activated_rows(1)
		self.hide()
		if len(items) == 0:
			self.close()
			return
		staged = 0
		for item in items:
			try:
				status = self.vcs.status(item, summarize=False).simple_content_status()
				if status == rabbitvcs.vcs.status.status_missing:
					self.git.checkout([item])
					self.git.remove(item)
				else:
					self.git.stage(item)
					staged += 1
			except Exception as e:
				log.exception(e)
		ticks = staged + len(items)*2
		
		self.action = rabbitvcs.ui.action.GitAction(
			self.git,
			register_gtk_quit=self.gtk_quit_is_set()
		)
		self.action.set_pbar_ticks(ticks)
		self.action.append(self.action.set_header, _("Commit"))
		self.action.append(self.action.set_status, _("Running Commit Command..."))
		self.action.append(
			helper.save_log_message,
			self.message.get_text()
		)
		self.action.append(
			self.git.commit,
			self.message.get_text()
		)
		self.action.append(self.action.set_status, _("Completed Commit"))
		self.action.append(self.action.finish)
		self.action.schedule()

class MercurialCommit(Commit):
	def __init__(self, paths, base_dir=None, message=None):
		Commit.__init__(self, paths, base_dir, message)
		self.mercurial = self.vcs.mercurial(paths[0])
		options_box = self.get_widget("options_box")
		self.close_branch = gtk.CheckButton(_("Close Branch"))
		options_box.pack_start(self.close_branch, False, False, 0)
		self.close_branch.show()
		self.items = None
		if len(self.paths):
			self.initialize_items()
	
	def on_ok_clicked(self, widget, data=None):
		items = self.files_table.get_activated_rows(1)
		self.hide()
		if len(items) == 0:
			self.close()
			return
		staged = 0
		for item in items:
			try:
				status = self.vcs.status(item, summarize=False).simple_content_status()
				if status == rabbitvcs.vcs.status.status_missing:
					self.mercurial.revert([item])
					self.mercurial.remove(item)
				else:
					self.mercurial.add(item)
					staged += 1
			except Exception as e:
				log.exception(e)
		ticks = staged + len(items)*2
		self.action = rabbitvcs.ui.action.MercurialAction(
			self.mercurial,
			register_gtk_quit=self.gtk_quit_is_set()
		)
		self.action.set_pbar_ticks(ticks)
		self.action.append(self.action.set_header, _("Commit"))
		self.action.append(self.action.set_status, _("Running Commit Command..."))
		self.action.append(
			helper.save_log_message,
			self.message.get_text()
		)
		self.action.append(
			self.mercurial.commit,
			self.message.get_text()
		)
		self.action.append(self.action.set_status, _("Completed Commit"))
		self.action.append(self.action.finish)
		self.action.start()

classes_map = {
	rabbitvcs.vcs.VCS_SVN: SVNCommit,
	rabbitvcs.vcs.VCS_GIT: GitCommit,
	rabbitvcs.vcs.VCS_MERCURIAL: MercurialCommit
}

def commit_factory(paths, base_dir=None, message=None):
	guess = rabbitvcs.vcs.guess(paths[0])
	return classes_map[guess["vcs"]](paths, base_dir, message)

if __name__ == "__main__":
	from rabbitvcs.ui import main, BASEDIR_OPT
	(options, paths) = main(
		[BASEDIR_OPT, (["-m", "--message"], {"help":"add a commit log message"})],
		usage="Usage: rabbitvcs commit [path1] [path2] ..."
	)
	
	log.debug("options = %s, paths = %s" % (options, paths)) # esh: log
	
	window = commit_factory(paths, options.base_dir, message=options.message)
	window.register_gtk_quit()
	gtk.main()
