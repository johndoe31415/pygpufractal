#!/usr/bin/python3
#       pygpufractal - Fractal computation on GPU using GLSL.
#       Copyright (C) 2017-2017 Johannes Bauer
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

from GlutApplication import GlutApplication
from GLFragmentShader import GLFragmentShaderProgram
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

class MandelbrotFragmentShaderProgram(GLFragmentShaderProgram):
	def __init__(self):
		GLFragmentShaderProgram.__init__(self, """\
		uniform sampler2D tex;
		uniform vec2 center, size;
		uniform int max_iterations;
		uniform float cutoff;

		void main() {
			vec2 c;
			c.x = center.x + (size.x * (gl_TexCoord[0].x - 0.5));
			c.y = center.y + (size.y * (gl_TexCoord[0].y - 0.5));

			int iteration;
			vec2 z = c;
			for (iteration = 0; iteration < max_iterations; iteration++) {
				float x = (z.x * z.x - z.y * z.y) + c.x;
				float y = (z.y * z.x + z.x * z.y) + c.y;

				float abs_value = x * x + y * y;
				if (abs_value > cutoff) {
					break;
				}
				z.x = x;
				z.y = y;
			}


			float flt_iteration = iteration / 19.0;
			gl_FragColor = vec4(flt_iteration, 0, 0, 1);
		}
		""")

class FractalGlutApplication(GlutApplication):
	def __init__(self):
		GlutApplication.__init__(self, window_title = "Python Fractals")
		self._lut_texture = self.load_texture_2d("texture.pnm")
		self._shader_pgm = MandelbrotFragmentShaderProgram()
		self._center = (-0.4, 0)
		self._size = (7 * 0.4, 7 * 0.3)
		self._max_iterations = 1000
		self._cutoff = 10.0;

	def _draw_gl_scene(self):
		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

		glViewport(0, 0, self.width, self.height)
		glClearDepth(1)
		glClearColor(0, 0, 0, 0)
		glClear(GL_COLOR_BUFFER_BIT)

		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		glOrtho(0, 1, 0, 1, -1, 1)

		glMatrixMode(GL_MODELVIEW);
		glLoadIdentity()

		glUseProgram(self._shader_pgm.program)
		self._shader_pgm.set_uniform("center", self._center)
		self._shader_pgm.set_uniform("size", self._size)
		self._shader_pgm.set_uniform("max_iterations", self._max_iterations)
		self._shader_pgm.set_uniform("cutoff", self._cutoff)
		glBindTexture(GL_TEXTURE_2D, self._lut_texture)
		glEnable(GL_TEXTURE_2D)
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

		glutSwapBuffers()
