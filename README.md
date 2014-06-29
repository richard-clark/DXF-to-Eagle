DXF-to-Eagle
============

This module provides functionality for creating EAGLE scripts from DXF files.

This module differs from other scripts for several reasons:

* It is entirely free and open source. 
* It is written in Python.
* It is platorm-independant--it works on OS X, Linux, and Windows. 
* It supports spline approximation.



Requirements
------------

The only non-standard module required is dxfgrabber:

    https://pypi.python.org/pypi/dxfgrabber/0.6.0

Usage
-----

When invoked from the console, the options are as follows:

* ``-t``: The two-element tuple specifying the offset (default: no offset).
* ``-s``: The factor by which to scale the output (default: 1). 
* ``-a``: The spline point scalar (default: 50, see Splines).
* ``-o``: The output file name (default: a file with the same name and location as the DXF file, but with a .scr extension).
* ``-l``: A list of layers from which to parse object (default: parse objects on all layers). 
* ``-i``: The input DXF file, required.

For typical behavior, before the script is run within EAGLE, the wire bend style should
be set to none. (That is, wires should extend from the start to the end with no intermediary points.)

Supported Primitives
--------------------

The following primitives are fully supported:

* Arcs
* Circles
* Lines
* Polylines
* Text

The following primtives may be approximated:

* Splines

### Splines

De Boor's algorithm may be used to divide a spline into a discrete number of points, which can then
be imported into EAGLE as a series of line segments.

The number of points is equal to the number of control points multipled by a scale factor 
(``spline_point_scalar``).

Layers
------

The contents of all layers can be parsed, or only the contents of desired layers.

To parse all layers, set the ``layers`` variable to ``None``; to only parse certain layers,
set the ``layers`` variable to a ``dict`` object, where the keys are the names of layers to parse.

Offset and Scale Factor
-----------------------

The output is offset and scaled with respect to the input in the following manner:

    output = input * scale_factor + offset
    
Thus, the ``output`` is in the scaled units.

Offset is specified in the form of a two element tuple, ``(x, y)``.
