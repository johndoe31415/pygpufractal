# pygpufractal
[![Build Status](https://travis-ci.org/johndoe31415/pygpufractal.svg?branch=master)](https://travis-ci.org/johndoe31415/pygpufractal)

This is a small example of how to calculate fractals on the GPU using OpenGL,
the OpenGL shader language (GLSL) and Python. It implements Newton fractals,
Mandelbrot and Julia sets. It has an (experimental) GTK UI.

## Usage
Currently, no command line options are supported, just run it from the command line:

```
$ ./gtkfractal.py
```

## Screenshots
Here's example images of how it looks like. Note that these are from the
previous, command-line GLUT version and thus are not up-to-date.

![x^3 + 3](https://raw.githubusercontent.com/johndoe31415/pygpufractal/master/docs/newton1.png)

![Other Newton Fractal](https://raw.githubusercontent.com/johndoe31415/pygpufractal/master/docs/newton2.png)

![Other Newton Fractal](https://raw.githubusercontent.com/johndoe31415/pygpufractal/master/docs/newton3.png)

![Mandelbrot Fractal](https://raw.githubusercontent.com/johndoe31415/pygpufractal/master/docs/mandelbrot.png)

## Dependencies
Python3, GTK+ and GL/GLUT.

## License
GNU GPL-3.
