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

import textwrap
import numpy
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

class GLFragmentShaderProgram(object):
	def __init__(self, shader_source):
		self._uniforms = { }
		shader_source = textwrap.dedent(shader_source)
		self._program = glCreateProgram()
		self._shader = self._compile_shader(shader_source, GL_FRAGMENT_SHADER)
		glAttachShader(self._program, self._shader)
		glLinkProgram(self._program)
		link_status = glGetProgramiv(self._program, GL_LINK_STATUS)
		if link_status == 0:
			raise Exception("Shader linking failed: %s" % (link_status, glGetProgramInfoLog(self._program)))
		glDeleteShader(self._shader)

	def set_property(self, key, value):
		self._uniforms[key] = value

	def set_uniform(self, uniform_name, value, error = "except"):
		uniform = glGetUniformLocation(self._program, uniform_name)
		if uniform < 0:
			msg = "No such uniform in shader program: %s" % (uniform_name)
			if error == "warn":
				print("Warning: %s" % (msg))
			elif error == "ignore":
				pass
			else:
				raise Exception(msg)
#		print("Setting uniform \"%s\" (%d) to %s" % (uniform_name, uniform, str(value)))
		if isinstance(value, tuple) and (len(value) == 2):
			glUniform2f(uniform, value[0], value[1])
		elif isinstance(value, list) and (len(value) > 0) and isinstance(value[0], tuple) and (len(value[0]) == 2):
			glUniform2fv(uniform, len(value), value)
		elif isinstance(value, int):
			glUniform1i(uniform, value)
		elif isinstance(value, float):
			glUniform1f(uniform, value)
		elif isinstance(value, complex):
			glUniform2f(uniform, value.real, value.imag)
		else:
			raise Exception("Do not know how to set uniform \"%s\" to value of unknown type: %s" % (uniform_name, str(value)))

	def _compile_shader(self, shader_source, shader_type):
		shader = glCreateShader(shader_type)
		glShaderSource(shader, shader_source)
		glCompileShader(shader)
		compile_status = glGetShaderiv(shader, GL_COMPILE_STATUS)
		if compile_status == 0:
			raise Exception("Shader compilation failed: %s" % (glGetShaderInfoLog(shader).decode("utf-8")))
		return shader

	@property
	def program(self):
		return self._program

	def use(self):
		glUseProgram(self.program)
		for (key, value) in self._uniforms.items():
			self.set_uniform(key, value)

class TrivialFragmentShaderProgram(GLFragmentShaderProgram):
	"""Shader that colors entire screen red."""
	def __init__(self):
		GLFragmentShaderProgram.__init__(self, """\
		void main(void) {
			gl_FragColor = vec4(1.0, 0.0, 0.0, 1.0);
		}
		""")

class SimpleFragmentShaderProgram(GLFragmentShaderProgram):
	"""Shader that colors entire screen in a color that depends on X and Y
	component of the pixel."""
	def __init__(self):
		GLFragmentShaderProgram.__init__(self, """\
		void main(void) {
			gl_FragColor = vec4(gl_TexCoord[0].x, gl_TexCoord[0].y, 0.0, 1.0);
		}
		""")

class InvertTextureFragmentShaderProgram(GLFragmentShaderProgram):
	"""Shader that takes a texture as input and inverts it."""
	def __init__(self):
		GLFragmentShaderProgram.__init__(self, """\
		uniform sampler2D texture;

		void main(void) {
			vec4 pixel_color = texture2D(texture, gl_TexCoord[0]);
			vec4 inverted_color = vec4(1 - pixel_color[0], 1 - pixel_color[1], 1 - pixel_color[2], 1.0);
			gl_FragColor = inverted_color;
		}
		""")


