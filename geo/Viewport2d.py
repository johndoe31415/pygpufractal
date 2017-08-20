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

from .Vector2d import Vector2d

class Viewport2d(object):
	def __init__(self, device_width, device_height, logical_origin_x = 0, logical_origin_y = 0, logical_width = 1, logical_height = 1, keep_aspect_ratio = False):
		assert(device_width > 0)
		assert(device_height > 0)
		assert(logical_width > 0)
		assert(logical_height > 0)
		self._device_size = Vector2d(device_width, device_height)
		self._logical_origin = Vector2d(logical_origin_x, logical_origin_y)
		self._logical_size = Vector2d(logical_width, logical_height)
		self._keep_aspect_ratio = keep_aspect_ratio

	def set_device_size(self, device_width, device_height):
		self._device_width = self._device_width


