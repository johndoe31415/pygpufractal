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

class MandelbrotFragmentShaderProgram(GLFragmentShaderProgram):
	def __init__(self):
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
		self._uniforms["max_iterations"] = 40
		self._uniforms["cutoff"] = 10.0
