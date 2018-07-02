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

from geo import Viewport2d
from OpenGL.GL import *
from OpenGL.GLU import *
from NewtonFragmentShaderProgram import NewtonFragmentShaderProgram
from MandelbrotFragmentShaderProgram import MandelbrotFragmentShaderProgram
from NewtonSolver import Polynomial
from AdvancedColorPalette import AdvancedColorPalette

class GLHandler(object):
	def __init__(self):
		self._viewport = Viewport2d(device_width = 640, device_height = 480, keep_aspect_ratio = True)
		self._shader_pgm_input = None
		self._shader_pgm = None
		self._lut_texture_input = None
		self._lut_texture = None

	def _initialize_shader(self, scene_params):
		shader_pgm_input = (scene_params["type"], )

		if shader_pgm_input != self._shader_pgm_input:
			self._shader_pgm_input = shader_pgm_input
			shader_pgm_class = {
				"newton":		NewtonFragmentShaderProgram,
				"mandelbrot":	MandelbrotFragmentShaderProgram,
			}[scene_params["type"]]
			self._shader_pgm = shader_pgm_class()

	def _initialize_lookup_texture(self, scene_params):
		lut_texture_input = (scene_params["color_scheme_filename"], scene_params["color_scheme"])
		if lut_texture_input != self._lut_texture_input:
			self._lut_texture_input = lut_texture_input
			palette = AdvancedColorPalette.load_from_json(scene_params["color_scheme_filename"], scene_params["color_scheme"])
			self._lut_texture = self._create_gradient_texture(palette, 256)

	def _create_gradient_texture(self, palette, data_points):
		data = bytearray()
		for i in range(data_points):
			pixel = palette[i / (data_points - 1)]
			data += bytes(pixel)
		return self.create_texture_1d_rgb(data)

	def create_texture_1d_rgb(self, data):
		assert(isinstance(data, bytes) or isinstance(data, bytearray))
		assert((len(data) % 3) == 0)
		texture_id = glGenTextures(1)
		glBindTexture(GL_TEXTURE_1D, texture_id)
		glTexParameterf(GL_TEXTURE_1D, GL_TEXTURE_WRAP_S, GL_CLAMP)
		glTexParameterf(GL_TEXTURE_1D, GL_TEXTURE_WRAP_T, GL_CLAMP)
		glTexParameterf(GL_TEXTURE_1D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
		glTexParameterf(GL_TEXTURE_1D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
		glTexImage1D(GL_TEXTURE_1D, 0, GL_RGB, len(data) // 3, 0, GL_RGB, GL_UNSIGNED_BYTE, data)
		return texture_id

	def resize(self, width, height):
		self._viewport.set_device_size(width, height)

		glClearColor(0.0, 1.0, 1.0, 0.0)
		glClearDepth(1.0)
		glDepthFunc(GL_LESS)
		glEnable(GL_DEPTH_TEST)
		glShadeModel(GL_SMOOTH)
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		gluPerspective(45.0, self._viewport.device_size.x / self._viewport.device_size.y, 0.1, 100.0)
		glMatrixMode(GL_MODELVIEW)

	def render(self, glctx, scene_params):
		self._initialize_shader(scene_params)
		self._initialize_lookup_texture(scene_params)

		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

		glViewport(0, 0, self._viewport.device_size.x, self._viewport.device_size.y)
		glClearDepth(1)
		glClearColor(0, 0, 0, 0)
		glClear(GL_COLOR_BUFFER_BIT)

		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		glOrtho(0, 1, 0, 1, -1, 1)

		glMatrixMode(GL_MODELVIEW);
		glLoadIdentity()

		self._shader_pgm.set_property("center", tuple(self._viewport.logical_center))
		self._shader_pgm.set_property("size", tuple(self._viewport.logical_size))
		for (key, value) in scene_params["properties"].items():
			self._shader_pgm.set_property(key, value)
		self._shader_pgm.use()

		glBindTexture(GL_TEXTURE_1D, self._lut_texture)
		glEnable(GL_TEXTURE_1D)
		glBegin(GL_QUADS)
		glTexCoord2f(-1, -1)
		glVertex2f(-1, -1)
		glTexCoord2f(1, -1)
		glVertex2f(1, -1)
		glTexCoord2f(1, 1)
		glVertex2f(1, 1)
		glTexCoord2f(-1, 1)
		glVertex2f(-1, 1)
		glEnd()

