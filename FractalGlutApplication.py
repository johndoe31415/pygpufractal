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

from GlutApplication import GlutApplication, MouseButton, MouseButtonAction
from GLFragmentShader import GLFragmentShaderProgram
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from ColorMixer import ColorMixer
from geo import Viewport2d
from NewtonSolver import Polynomial, NewtonSolver

class MandelbrotFragmentShaderProgram(GLFragmentShaderProgram):
	def __init__(self, max_iterations = 40, cutoff = 10.0):
		GLFragmentShaderProgram.__init__(self, """\
		#define cplx_mul(a, b)		vec2(a.x * b.x - a.y * b.y, a.x * b.y + a.y * b.x)

		uniform sampler1D tex;
		uniform vec2 center, size;
		uniform int max_iterations;
		uniform float cutoff;

		void main() {
			vec2 c;
			c.x = center.x + (size.x * (gl_TexCoord[0].x - 0.5));
			c.y = center.y + (size.y * (gl_TexCoord[0].y - 0.5));

			int iteration;
			vec2 cur = c;
			for (iteration = 0; iteration < max_iterations; iteration++) {
				cur = cplx_mul(cur, cur) + c;
				float abs_value = length(cur);
				if (abs_value > cutoff) {
					break;
				}
			}

			float flt_iteration = iteration / float(max_iterations - 1);
			gl_FragColor = texture1D(tex, flt_iteration);
		}
		""")
		self._max_iterations = max_iterations
		self._cutoff = cutoff

	def use(self):
		GLFragmentShaderProgram.use(self)
		self.set_uniform("max_iterations", self._max_iterations)
		self.set_uniform("cutoff", self._cutoff)

class NewtonFragmentShaderProgram(GLFragmentShaderProgram):
	def __init__(self, polynomial, max_iterations = 50, cutoff = 1e-4):
		GLFragmentShaderProgram.__init__(self, """\
		#define cplx_mul(a, b)		vec2(a.x * b.x - a.y * b.y, a.x * b.y + a.y * b.x)
		#define cplx_div(a, b)		vec2(((a.x * b.x + a.y * b.y) / (b.x * b.x + b.y * b.y)), ((a.y * b.x - a.x * b.y) / (b.x * b.x + b.y * b.y)))
		#define cplx_abs(x)			length(x)

		uniform sampler1D tex;
		uniform vec2 center, size;
		uniform vec2 poly_coeffs[16];
		uniform vec2 poly_dx_coeffs[15];
		uniform vec2 solutions[16];
		uniform int max_iterations;
		uniform float cutoff;
		uniform int poly_degree;

		/* Calculate complex exponentation base ^ exponent */
		vec2 cplx_pow(vec2 base, float exponent) {
			float absval = pow(cplx_abs(base), exponent);
			float arg = exponent * atan2(base.y, base.x);
			return vec2(absval * cos(arg), absval * sin(arg));
		}

		/* Evaluate the polynomial with the given coefficients "coeffs" at the
		position "x" */
		vec2 poly_eval(vec2 coeffs[], int coeff_cnt, vec2 x) {
			vec2 result = vec2(0, 0);
			for (int exponent = 0; exponent < coeff_cnt; exponent++) {
				result = result + cplx_mul(coeffs[exponent], cplx_pow(x, exponent));
			}
			return result;
		}

		void main() {
			vec2 c;
			c.x = center.x + (size.x * (gl_TexCoord[0].x - 0.5));
			c.y = center.y + (size.y * (gl_TexCoord[0].y - 0.5));

			/* First, find convergent value of Newton solver with the given
			starting point "c" */
			for (int i = 0; i < max_iterations; i++) {
				vec2 new_c = c - cplx_div(poly_eval(poly_coeffs, poly_degree + 1, c), poly_eval(poly_dx_coeffs, poly_degree, c));
				float err = length(new_c - c);
				c = new_c;
				if (err < cutoff) {
					break;
				}
			}

			/* Then, among the previously pre-computed solutions, pick the one
			that most closely matches */
			int closest_index = 0;
			float min_err = length(solutions[0] - c);
			for (int i = 1; i < poly_degree; i++) {
				float err = length(solutions[i] - c);
				if (err < min_err) {
					min_err = err;
					closest_index = i;
				}
			}

			/* Convert into a float and lookup color value */
			float flt_closest = closest_index / float(poly_degree - 1);
			gl_FragColor = texture1D(tex, flt_closest);
		}
		""")
		self._poly = polynomial
		self._max_iterations = max_iterations
		self._cutoff = cutoff
		self._solutions = [ (value.real, value.imag) for value in NewtonSolver(self._poly).find_all(5, 0.1) ]

	@property
	def poly(self):
		return self._poly

	def use(self):
		GLFragmentShaderProgram.use(self)
		self.set_uniform("max_iterations", self._max_iterations)
		self.set_uniform("cutoff", self._cutoff)
		self.set_uniform("poly_coeffs", self._poly.coeffs)
		self.set_uniform("poly_dx_coeffs", self._poly.dx().coeffs)
		self.set_uniform("poly_degree", self._poly.degree)
		self.set_uniform("solutions", self._solutions)


class FractalGlutApplication(GlutApplication):
	def __init__(self):
		GlutApplication.__init__(self, window_title = "Python Fractals")
		self._lut_texture = self._create_gradient_texture("rainbow", 256)
		self._shader_pgm = MandelbrotFragmentShaderProgram()
		self._viewport = Viewport2d(device_width = self.width, device_height = self.height, logical_center_x = -0.4, logical_center_y = 0, logical_width = 3, logical_height = 2)
		#self._shader_pgm = NewtonFragmentShaderProgram(Polynomial(-2, complex(-0.1, 0.1), complex(0.5, 0.2), complex(-1, 0.4), complex(0.3, -0.1), complex(0.1, 0.1)))
		#self._viewport = Viewport2d(device_width = self.width, device_height = self.height, logical_center_x = 0, logical_center_y = 0, logical_width = 3, logical_height = 2)
		self._drag_viewport = None
		self._dirty = True

	def _create_gradient_texture(self, palette, data_points):
		data = bytearray()
		color_mixer = ColorMixer(palette)
		for i in range(data_points):
			pixel = color_mixer[i / (data_points - 1)]
			data += bytes(pixel)
		return self.create_texture_1d_rgb(data)

	def _gl_keyboard(self, key, pos_x, pos_y):
		if key == b"\x1b":
			sys.exit(0)

	def _drag_start(self, mouse_button, origin_x, origin_y):
		if mouse_button == MouseButton.LeftButton:
			self._drag_viewport = self._viewport.clone()

	def _drag_motion(self, mouse_button, origin_x, origin_y, pos_x, pos_y, finished):
		if mouse_button == MouseButton.LeftButton:
			self._viewport = self._drag_viewport.clone()
			self._viewport.move_relative_device(-(pos_x - origin_x), pos_y - origin_y)
			if finished:
				self._drag_viewport = None
			self._dirty = True

	def _gl_reshape(self):
		self._viewport.set_device_size(self.width, self.height)

	def _gl_mouse(self, mouse_button, mouse_button_action, device_x, device_y):
		device_y = self.height - device_y
		if mouse_button_action == MouseButtonAction.ButtonDown:
			if mouse_button == MouseButton.MiddleButton:
				# Change center
				logical = self._viewport.device_to_logical(device_x, device_y)
				self._viewport.set_logical_center(logical.x, logical.y)
			elif mouse_button == MouseButton.WheelUp:
				self._viewport.zoom_in_around_device(1.5, device_x, device_y)
			elif mouse_button == MouseButton.WheelDown:
				self._viewport.zoom_out_around_device(1.5, device_x, device_y)
			self._draw_gl_scene()

	def _gl_idle(self):
		if self._dirty:
			self._draw_gl_scene()

	def _draw_gl_scene(self):
		self._dirty = False
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

		self._shader_pgm.use()
		self._shader_pgm.set_uniform("center", tuple(self._viewport.logical_center))
		self._shader_pgm.set_uniform("size", tuple(self._viewport.logical_size))
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

		glutSwapBuffers()
