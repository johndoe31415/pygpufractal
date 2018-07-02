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

from GLFragmentShader import GLFragmentShaderProgram
from NewtonSolver import Polynomial, NewtonSolver

class NewtonFragmentShaderProgram(GLFragmentShaderProgram):
	def __init__(self):
		GLFragmentShaderProgram.__init__(self, """\
		#define MAX_POLY_DEGREE		16
		#define cplx_mul(a, b)		vec2(a.x * b.x - a.y * b.y, a.x * b.y + a.y * b.x)
		#define cplx_div(a, b)		vec2(((a.x * b.x + a.y * b.y) / (b.x * b.x + b.y * b.y)), ((a.y * b.x - a.x * b.y) / (b.x * b.x + b.y * b.y)))
		#define cplx_abs(x)			length(x)

		uniform sampler1D tex;
		uniform vec2 center, size;
		uniform vec2 poly_coeffs[MAX_POLY_DEGREE];
		uniform vec2 poly_dx_coeffs[MAX_POLY_DEGREE - 1];
		uniform vec2 solutions[MAX_POLY_DEGREE];
		uniform int max_iterations;
		uniform float cutoff;
		uniform int poly_degree;
		uniform float darken_brighten_shift, darken_brighten_clamp, darken_brighten_exp;

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
			int iterations;
			for (iterations = 0; iterations < max_iterations; iterations++) {
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
			vec4 base_color = texture1D(tex, flt_closest);

			/* Darken or brighten by iteration count; convert to value from -1 to 1 first */
			float flt_iterations = (float(iterations) / float(max_iterations) * 2.0) - 1.0;

			/* Then shift value according to shifting uniform */
			flt_iterations += darken_brighten_shift;

			/* Finally clamp to final value */
			flt_iterations = clamp(flt_iterations, -1, 1) * darken_brighten_clamp;

			/* Finally exponentiate it according to uniform darken/brighten exponent */
			if (flt_iterations >= 0) {
				flt_iterations = pow(flt_iterations, darken_brighten_exp);
			} else {
				flt_iterations = -pow(-flt_iterations, darken_brighten_exp);
			}

			vec4 add_color = vec4(1, 1, 1, 0) * flt_iterations;
			gl_FragColor = base_color + add_color;
		}
		""")
		self.set_property("max_iterations", 50)
		self.set_property("cutoff", 1e-4)
		self.set_property("darken_brighten_shift", 0.75)
		self.set_property("darken_brighten_clamp", 0.5)
		self.set_property("darken_brighten_exp", 0.6)
		self._solution = None
		self.set_property("poly", Polynomial(3, 0, 0, 1))

	@property
	def poly(self):
		return self._poly

	def set_property(self, key, value):
		if key == "poly":
			if (self._solution is None) or (self._solution.poly != value):
				self._solution = NewtonSolver(value)
				self.set_property("poly_degree", self._solution.poly.degree)
				self.set_property("poly_coeffs", self._solution.poly.coeffs)
				self.set_property("poly_dx_coeffs", self._solution.poly_dx.coeffs)
				self.set_property("solutions", sorted([ (value.real, value.imag) for value in self._solution.find_all(field_size = 5, step_size = 0.1) ]))
		else:
			GLFragmentShaderProgram.set_property(self, key, value)
