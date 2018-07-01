# pygpufractal
[![Build Status](https://travis-ci.org/johndoe31415/pygpufractal.svg?branch=master)](https://travis-ci.org/johndoe31415/pygpufractal)

This is a small example of how to calculate fractals on the GPU using OpenGL,
the OpenGL shader language (GLSL) and Python. It implements a Newton solver and
a Mandelbrot solver in GLSL.

# Usage
You can specify the type of fractal you want on the command line. Here's the help page:

```
$ ./fractal.py --help
usage: fractal.py [-h] [--palette-json filename] [--palette-samples count]
                  [-p name] [-f {newton,mandelbrot}] [-c x,y] [-v]
                  real[,imag] [real[,imag] ...]

positional arguments:
  real[,imag]           Polynomial coefficients. Can be either real floating
                        point values or complex values by specifying a pair of
                        real,complex separated by comma. Ordered from low to
                        high degree. Any value can be prefixed with 'r' which
                        multiplies the given value with a random value from 0
                        to 1 or 'R' which multiplies the given value with a
                        random complex number [0-1]+[0-1]j.

optional arguments:
  -h, --help            show this help message and exit
  --palette-json filename
                        JSON file that holds all palette definitions, defaults
                        to palettes.json.
  --palette-samples count
                        Number of samples to use for palette sampling.
                        Defaults to 256.
  -p name, --palette name
                        Palette to choose from palette definition file.
                        Defaults to custom.
  -f {newton,mandelbrot}, --fractal {newton,mandelbrot}
                        Determines the type of solver that is used. Can be any
                        of newton, mandelbrot, defaults to newton.
  -c x,y, --center x,y  Center image initially around these x,y
                        (real/imaginary) coordinates. Defaults to 0,0.
  -v, --verbose         Be more verbose.
```

Examples are:

```
$ ./fractal.py -v 3 0 0 1
Showing Newton fractal with polynomial: 1.0 x^3 + 3.0
Current viewport: (-1.500, -1.000) - (1.500, 1.000) onto device (640.000, 480.000)
```

Which produces:

![x^3 + 3](https://raw.githubusercontent.com/johndoe31415/pygpufractal/master/docs/newton1.png)

You can use the mouse to move around and the mousewheel to zoom in and out of
the area.

Alternatively, you can just type 'r' or 'R' for coefficients and see where it
takes you:

![Other Newton Fractal](https://raw.githubusercontent.com/johndoe31415/pygpufractal/master/docs/newton2.png)

![Other Newton Fractal](https://raw.githubusercontent.com/johndoe31415/pygpufractal/master/docs/newton3.png)

Mandelbrot is also supported, coefficients are not needed for that:

```
$ ./fractal.py -f mandelbrot --palette rainbow
```

Shows:

![Mandelbrot Fractal](https://raw.githubusercontent.com/johndoe31415/pygpufractal/master/docs/mandelbrot.png)

# Dependencies
Python3 and GLUT.

# License
GNU GPL-3.
