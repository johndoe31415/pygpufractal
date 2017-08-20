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

class Polynomial(object):
	def __init__(self, *coefficients):
		assert(len(coefficients) >= 1)
		self._coeffs = tuple(complex(coeff) for coeff in coefficients)

	@property
	def degree(self):
		return len(self._coeffs) - 1

	def __repr__(self):
		terms = [ ]
		for (exponent, coeff) in reversed(list(enumerate(self._coeffs))):
			if coeff == 0:
				continue

			if exponent == 0:
				terms.append("%s" % (coeff))
			elif exponent == 1:
				terms.append("%s x" % (coeff))
			else:
				terms.append("%s x^%d" % (coeff, exponent))
		return " + ".join(terms)

	def dx(self):
		return Polynomial(*[ exp * coeff for (exp, coeff) in enumerate(self._coeffs[1:], 1) ])

	def __call__(self, value):
		result = 0
		for (exponent, coeff) in enumerate(self._coeffs):
			result += coeff * (value ** exponent)
		return result

	@property
	def coeffs(self):
		return [ (coeff.real, coeff.imag) for coeff in self._coeffs ]

class ApproxEqualComplex(object):
	def __init__(self, value):
		self._value = value
		self._key = (round(self._value.real * 10000), round(self._value.imag * 10000))

	def __lt__(self, other):
		return self._key < other._key

	def __eq__(self, other):
		return self._key == other._key

	def __hash__(self):
		return hash(self._key)

	@property
	def complex(self):
		return self._value

class NewtonSolver(object):
	_max_iterations = 1000

	def __init__(self, poly):
		self._poly = poly
		self._poly_dx = poly.dx()

	def find_all(self, field_size, step_size):
		values = set()
		(minx, maxx) = (-field_size / 2, field_size / 2)
		(miny, maxy) = (-field_size / 2, field_size / 2)
		(stepx, stepy) = (step_size, step_size)
		x = minx
		while x < maxx:
			y = miny
			while y < maxy:
				value = complex(x, y)
				zero = self(value)
				values.add(ApproxEqualComplex(zero))
				y += step_size
			x += step_size
		return [ value.complex for value in values ]

	def __call__(self, value):
		for i in range(self._max_iterations):
			new_value = value - (self._poly(value) / self._poly_dx(value))
			err = abs(new_value - value)
			value = new_value
			if err < 1e-5:
				break
		return value

if __name__ == "__main__":
	poly = Polynomial(-1, 0, 0, 1)
	solver = NewtonSolver(poly)
	print(solver(-99.4))
	print(solver.find_all(5, 0.1))

