# ==========================================================================================================
# Erl - A Sublime Text 3 Plugin for Erlang Integrated Testing & Code Completion
#
# Copyright (C) 2013, Roberto Ostinelli <roberto@ostinelli.net>.
# All rights reserved.
#
# BSD License
#
# Redistribution and use in source and binary forms, with or without modification, are permitted provided
# that the following conditions are met:
#
#  * Redistributions of source code must retain the above copyright notice, this list of conditions and the
#        following disclaimer.
#  * Redistributions in binary form must reproduce the above copyright notice, this list of conditions and
#        the following disclaimer in the documentation and/or other materials provided with the distribution.
#  * Neither the name of the authors nor the names of its contributors may be used to endorse or promote
#        products derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED
# WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
# PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
# TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
# ==========================================================================================================


# imports
import sublime, sublime_plugin
import os
import Erl.erl_core as GLOBALS
from .erl_core import ErlTextCommand, ErlGlobal

# update command (used to edit the view content)
class UpdateCommand(sublime_plugin.TextCommand):
	def run(self, edit, buffer=None):
		self.view.insert(edit, self.view.size(), buffer)

# show man
class ErlMan():

	def __init__(self, view):
		# init
		self.view = view
		self.window = view.window()
		self.module_names = []

		self.panel_name = 'erl_man'
		self.panel_buffer = ''
		# setup panel
		self.setup_panel()

	def setup_panel(self):
		self.panel = self.window.get_output_panel(self.panel_name)

	def update_panel(self):
		if len(self.panel_buffer):
			self.panel.run_command("update", {"buffer": self.panel_buffer})
			self.panel.show(self.panel.size())
			self.panel_buffer = ''
			self.window.run_command("show_panel", {"panel": "output.%s" % self.panel_name})

	def hide_panel(self):
		self.window.run_command("hide_panel")

	def log(self, text):
		if type(text) == bytes:
			text = text.decode('utf-8')
		self.panel_buffer += text
		sublime.set_timeout(self.update_panel, 0)

	def show(self):
		# set modules
		self.set_module_names()
		# open quick panel
		sublime.active_window().show_quick_panel(self.module_names, self.on_select)

	def set_module_names(self):
		# load file
		modules_filepath = os.path.join(GLOBALS.ERL.plugin_path, "completion", "Erlang-libs.sublime-completions")
		f = open(modules_filepath, 'r')
		contents = eval(f.read())
		f.close()
		# strip out just the module names to be displayed
		module_names = []
		for t in contents['completions']:
			module_names.append(t['trigger'])
		self.module_names = module_names

	def on_select(self, index):
		# get file and line
		module_name = self.module_names[index]
		# open man
		retcode, data = GLOBALS.ERL.execute_os_command("%s -man %s | col -b" % (GLOBALS.ERL.erl_path, module_name))
		if retcode == 0: self.log(data)


# man command
class ErlManCommand(ErlTextCommand):
	def run_command(self, edit):
		man = ErlMan(self.view)
		man.show()
