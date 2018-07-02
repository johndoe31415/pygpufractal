#!/usr/bin/python3
#       pygpufractal - Fractal computation on GPU using GLSL.
#       Copyright (C) 2017-2018 Johannes Bauer
#
#       This file is part of pygpufractal.
#
#       pygpufractal is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; this program is ONLY licensed under
#       version 3 of the License, later versions are explicitly excluded.
#
#       pygpufractal is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#
#       You should have received a copy of the GNU General Public License
#       along with pygpufractal; if not, write to the Free Software
#       Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#       Johannes Bauer <JohannesBauer@gmx.de>

import gi
gi.require_version("Gtk", "3.0")
gi.require_version("GtkSource", "3.0")

from gi.repository import Gtk, GtkSource
from GLHandler import GLHandler
from NewtonSolver import Polynomial
from AdvancedColorPalette import AdvancedColorPalette

class FractalGTKApplication(object):
	def __init__(self):
		self._builder = Gtk.Builder()
		self._builder.add_from_file("gpufractal.glade")
		self._builder.connect_signals(self)
		self._palette_filename = "palettes.json"
		self._populate_palette_combobox()
		self._gl_handler = GLHandler()

	def _populate_palette_combobox(self):
		schemata = AdvancedColorPalette.get_schema_from_json(self._palette_filename)
		liststore = self._builder.get_object("color_schemata_liststore")
		for schema in schemata:
			liststore.append((schema, ))
		self._builder.get_object("color_scheme_combobox").set_active(0)

	def on_main_window_delete_event(self, widget, event):
		Gtk.main_quit()

	def on_option_change_value(self, *args):
		self._builder.get_object("gl_area").queue_render()

	def on_gl_area_resize(self, widget, width, height):
		self._gl_handler.resize(width, height)

	def on_gl_area_realize(self, widget):
		error = widget.get_error()
		if error is not None:
			print("Error realizing GL window: %s" % (error))

	def on_gl_area_render(self, widget, glctx):
		liststore = self._builder.get_object("color_schemata_liststore")
		color_scheme = liststore[self._builder.get_object("color_scheme_combobox").get_active()][0]

		scene_params = {
			"color_scheme_filename":	self._palette_filename,
			"color_scheme":				color_scheme,
			"type":						{
				0:	"newton",
				1:	"mandelbrot",
			}[self._builder.get_object("fractal_type_combobox").get_active()],
			"properties": {
				"max_iterations":			round(self._builder.get_object("max_iterations_scale").get_value()),
				"cutoff":					10 ** self._builder.get_object("cutoff_scale").get_value(),
			}
		}

		if scene_params["type"] == "newton":
			scene_params["properties"].update({
				"poly":						Polynomial(3, 0, -3j, 3j),
				"darken_brighten_exp":		self._builder.get_object("darken_brighten_exp_scale").get_value(),
				"darken_brighten_shift":	self._builder.get_object("darken_brighten_shift_scale").get_value(),
				"darken_brighten_clamp":	self._builder.get_object("darken_brighten_clamp_scale").get_value(),
			})

		self._gl_handler.render(glctx, scene_params)

	def on_gl_area_drag_motion(self, widget, *args):
		print(args)

	def xxx(self, *args):
		print("EVENT", args)

	def on_options_window_menuitem_toggled(self, widget):
		options_window = self._builder.get_object("options_window")
		if widget.get_active():
			options_window.show_all()
		else:
			options_window.hide()

	def on_options_window_delete_event(self, widget, event):
		widget.hide()
		self._builder.get_object("options_window_menuitem").set_active(False)
		return True

	def on_cutoff_scale_format_value(self, widget, value):
		return "10 ^ %.2f" % (value)

	def run(self):
		main_window = self._builder.get_object("main_window")
		main_window.show_all()

if __name__ == "__main__":
	try:
		gui = FractalGTKApplication()
		gui.run()
		Gtk.main()
	except KeyboardInterrupt:
		pass
