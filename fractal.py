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

import sys
import random
from FractalGlutApplication import FractalGlutApplication
from FriendlyArgumentParser import FriendlyArgumentParser

def complex_number(text):
	if text[0] == "r":
		rnd = random.random()
		text = text[1:]
		if len(text) == 0:
			text = "1"
	elif text[0] == "R":
		rnd = (1j * random.random()) + random.random()
		text = text[1:]
		if len(text) == 0:
			text = "1"
	else:
		rnd = 1

	if not "," in text:
		real = float(text)
		imag = 0
	else:
		(real, imag) = (float(x) for x in text.split(","))
	return ((1j * imag) + real) * rnd

parser = FriendlyArgumentParser()
parser.add_argument("--palette-json", metavar = "filename", type = str, default = "palettes.json", help = "JSON file that holds all palette definitions, defaults to %(default)s.")
parser.add_argument("--palette-samples", metavar = "count", type = int, default = 256, help = "Number of samples to use for palette sampling. Defaults to %(default)d.")
parser.add_argument("-p", "--palette", metavar = "name", type = str, default = "flatui", help = "Palette to choose from palette definition file. Defaults to %(default)s.")
parser.add_argument("-f", "--fractal", choices = [ "newton", "mandelbrot" ], default = "newton", help = "Determines the type of solver that is used. Can be any of %(choices)s, defaults to %(default)s.")
parser.add_argument("-c", "--center", metavar = "x,y", type = complex_number, default = "0,0", help = "Center image initially around these x,y (real/imaginary) coordinates. Defaults to %(default)s.")
parser.add_argument("-v", "--verbose", action = "count", default = 0, help = "Be more verbose.")
parser.add_argument("coeffs", metavar = "real[,imag]", type = complex_number, nargs = "+", help = "Polynomial coefficients. Can be either real floating point values or complex values by specifying a pair of real,complex separated by comma. Ordered from low to high degree. Any value can be prefixed with 'r' which multiplies the given value with a random value from 0 to 1 or 'R' which multiplies the given value with a random complex number [0-1]+[0-1]j.")
args = parser.parse_args(sys.argv[1:])

app = FractalGlutApplication(args)
app.run()
