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
	def __init__(self, device_width, device_height, logical_center_x = 0, logical_center_y = 0, logical_width = 1, logical_height = 1, keep_aspect_ratio = False):
		assert(logical_width > 0)
		assert(logical_height > 0)
		self.set_device_size(device_width, device_height)
		self._logical_center = Vector2d(logical_center_x, logical_center_y)
		self._logical_size = Vector2d(logical_width, logical_height)
		self._keep_aspect_ratio = keep_aspect_ratio

	@property
	def device_size(self):
		return self._device_size

	@property
	def logical_center(self):
		return self._logical_center

	@property
	def logical_size(self):
		return self._logical_size

	@property
	def logical_lower(self):
		return self.logical_center - (self.logical_size / 2)

	@property
	def logical_upper(self):
		return self.logical_center + (self.logical_size / 2)

	def zoom_in(self, scalar):
		self._logical_size = self.logical_size / scalar

	def zoom_out(self, scalar):
		return self.zoom_in(1 / scalar)

	def device_to_logical(self, device_x, device_y):
		device = Vector2d(device_x, device_y)
		ratio = device.comp_div(self.device_size)
		return self.logical_lower + ratio.comp_mul(self.logical_size)

	def logical_to_device(self, logical_x, logical_y):
		logical = Vector2d(logical_x, logical_y)
		ratio = (logical - self.logical_lower).comp_div(self.logical_size)
		return ratio.comp_mul(self.device_size)

	def set_device_size(self, device_width, device_height):
		assert(device_width > 0)
		assert(device_height > 0)
		self._device_size = Vector2d(device_width, device_height)

	def __str__(self):
		return "%s - %s onto device %s" % (self.logical_lower, self.logical_upper, self.device_size)