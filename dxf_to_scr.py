import argparse
import bezier
import os
import math
import sys

try:
    import dxfgrabber
except:
    sys.stderr.write("Unable to import required package dxfgrabber. Please install it before continuing.")
    sys.exit(1)

"""

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

Splines
"""""""

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

"""

def add_line(f, x1, y1, x2, y2):
    """
    Add a line to an EAGLE script. 
    
    :param f: A ``file`` object. 
    :param x1: The `x` component of the start. 
    :param y1: The `y` component of the start. 
    :param x2: The `x` component of the end. 
    :param y2: The `y` component of the end.
    
    :returns: ``None``.
    """
    
    f.write('wire ({0} {1}) ({2} {3})\n'.format(x1, y1, x2, y2))

def add_arc(f, x, y, r, start_angle, end_angle):
    """
    Add an arc to an EAGLE script. 
    
    :param f: A ``file`` object. 
    :param x: The `x` component of the center.
    :param y: The `y` component of the center.
    :param r: The radius. 
    :param start_angle: The start angle.
    :param end_angle: The end angle.
    
    """
    
    start_x = x + r * math.cos(start_angle * math.pi / 180)
    start_y = y + r * math.sin(start_angle * math.pi / 180)
    
    end_x = x + r * math.cos(end_angle * math.pi / 180.0)
    end_y = y + r * math.sin(end_angle * math.pi / 180.0)
    
    curve = end_angle - start_angle
    if curve <= -180:
        curve += 360
    elif curve > 180:
        curve -= 360

    sign_str = '-' if curve < 0 else '+'

    f.write('wire ({0} {1}) {2}{3} ({4} {5})\n'.format(start_x, start_y, sign_str, curve, end_x, end_y))
        
def add_circle(f, x, y, r):
    """
    Add a circle to an EAGLE script. 
    
    :param f: A ``file`` object.
    :param x: The `x` component of the center. 
    :param y: The `y` component of the center.
    :param r: The radius of the center.
    
    :returns: ``None``.
    """
    
    f.write('circle ({0} {1}) ({2} {3})\n'.format(x, y, x + r, y))

def add_text(f, x, y, r, t):
    """
    Add text to an EAGLE script. 
    
    :param f: A ``file`` object. 
    :param x: The `x` component of the center. 
    :param y: The `y` component of the center. 
    :param r: The amount of rotation, in degrees.
    :param t: The text. 
    
    :returns: ``None``.
    """
    
    f.write('text {0} r{1} ({2} {3})'.format(t, r, x, y))
    
def add_set(f, name, val):
    """
    Add a ``set`` command to an EAGLE script. 
    
    :param f: A ``file`` object. 
    :param name: The name of the variable to set. 
    :param val: The value of the variable to set.
    
    :returns: ``None``.
    """
    
    f.write('set {0} {1}\n'.format(name, val))

def create_script(dxf_file, script_file, layers, scale_factor=1, offset=(0,0), spline_point_scalar = 50):
    """
    Create an EAGLE script from a DXF file.
    
    :param dxf_file: The path to the input DXF file. 
    :param script_file: The path to the output EAGLE script. 
    :param layers: A ``dict`` of layers which should be converted, or ``None`` if all layers should be converted.
    :param scale_factor: The factor by which to scale the output. 
    :param offset: A two-element tuple specifying the amount by which to offset the output.
    :param spline_point_scalar: The factor by which to multiply the number of spline control points to yield the total number of spline approximation points.
    
    :returns: ``None``.
    """
    
    # Read the input DXF file
    dxf = dxfgrabber.readfile(dxf_file)
    
    # Open the output EAGLE script file
    f = open(script_file, 'w')
    
    # Initialize counters to hold the number of primitives by type.
    num_arcs = 0
    num_circles = 0
    num_lines = 0
    num_polylines = 0
    num_splines = 0
    num_text = 0
    
    last_text_size = None
    
    # Iterate through the entities
    for e in dxf.entities:
        
        if layers == None or layers.has_key(e.layer):
            if isinstance(e, dxfgrabber.entities.Arc):
                add_arc(f, e.center[0]*scale_factor + offset[0],
                        e.center[1]*scale_factor + offset[1],
                        e.radius*scale_factor,
                        e.startangle,
                        e.endangle)
                num_arcs += 1
            
            elif isinstance(e, dxfgrabber.entities.Circle):
                add_circle(f, e.center[0]*scale_factor + offset[0], e.center[1]*scale_factor + offset[1], e.radius * scale_factor)
                num_circles += 1
            
            elif isinstance(e, dxfgrabber.entities.Line):
                add_line(f, e.start[0] * scale_factor + offset[0], e.start[1] * scale_factor + offset[1], e.end[0] * scale_factor + offset[0], e.end[1] * scale_factor + offset[1])
                num_lines += 1
            
            elif isinstance(e, dxfgrabber.entities.Polyline):
                for i in range(1, len(e.vertices)):
                    add_line(f, e.vertices[i-1].location[0] * scale_factor + offset[0],
                             e.vertices[i-1].location[1] * scale_factor + offset[1],
                             e.vertices[i].location[0] * scale_factor + offset[0], 
                             e.vertices[i].location[1] * scale_factor + offset[1])
                num_polylines += 1
                
            elif isinstance(e, dxfgrabber.entities.Spline):
                p = e.degree
                P = e.controlpoints
                U = e.knots
                
                num_points = spline_point_scalar * len(P) 
                step = (U[-1] - U[0]) / float(num_points)
                
                points = []
            
                for i in range(num_points):
                    u = U[0] + step * i
                    xy = bezier.deboor(P, U, u, p)
                    points.append(xy)
                    
                xy = bezier.deboor(P, U, U[-1] - step*0.01, p)
                points.append(xy)
                
                for i in range(len(points)-1):
                    add_line(f, points[i][0] * scale_factor + offset[0], 
                             points[i][1] * scale_factor + offset[1], 
                             points[i+1][0] * scale_factor + offset[0], 
                             points[i+1][1] * scale_factor + offset[1])
                    
                num_splines += 1
               
            elif isinstance(e, dxfgrabber.entities.Text):
                h = e.height * scale_factor
                
                if h != last_text_size:
                    add_set(f, 'size', h)
                    last_text_size = h
                
                add_text(f, e.insert[0] * scale_factor + offset[0],
                         e.insert[1] * scale_factor + offset[1],
                         e.rotation,
                         e.text)
                
                num_text += 1
            
            elif isinstance(e, dxfgrabber.entities.MText):
#                 lines = e.lines()
#                 
#                 # The defualt spacing between two baselines is 5/3 the height of the text
#                 default_spacing = 5/3.0
#                 
#                 # Thus, the text height is 1,
#                 # the descender is 1/3.0
#                 # the ascender is 1/3.0
#                 
#                 # This can be overriden by the linespacing property
#                 spacing = e.linespacing * default_spacing * scale_factor
#                 
#                 # The total height is the total number of lines multiplied by the spacing
#                 total_height = len(lines) * spacing
#                 
#                 # The attachment points are:
#                 
                
                
                
                
                pass
#                 lines = e.lines()
#                 
#                 # The default spacing between two baselines is 5/3 the height of the text
#                 default_spacing = 5 / 3.0
#                 
#                 # This can be overriden by the linespacing property
#                 spacing = e.linespacing * default_spacing * scale_factor
#                 h = e.height * scale_factor
#                 
#                 total_height = h + (len(lines) - 1) * spacing
#                 
#                 x_base = e.insert[0] * scale_factor + offset[0]
#                 y_base = e.insert[1] * scale_factor + offset[1]
#                 
#                 if (e.attachmentpoint >= 1 and e.attachmentpoint <= 3):
#                     # Attachment point is top
#                     y = y_base
#                 elif (e.attachmentpoint >= 4 and e.attachmentpoint <= 6):
#                     # Attachment point is middle
#                     pass
#                 elif (e.attachmentpoint >= 7 and e.attachmentpoint <= 8):
#                     # Attachment point is bottom
#                     pass
#                 else:
#                     raise Exception("Invalid text attachment point {0}.".format(e.attachmentpoint))
                
            else:
                print('Got unknown element {0}'.format(e))
                
               
    f.close()
    
    print("Script written successfully.")
    print("{0} arcs".format(num_arcs))
    print("{0} circles".format(num_circles))
    print("{0} lines".format(num_lines))
    print("{0} polylines".format(num_polylines))
    print("{0} splines".format(num_splines))
    print("{0} text".format(num_text))
    

def main():
    
    parser = argparse.ArgumentParser(description='Generate EAGLE scripts from DXF files.')
    parser.add_argument('-t', nargs=2, type=float, default=[0, 0], help='The amount by which to offset the output.')
    parser.add_argument('-s', type=float, default=1, help='The factor by which to scale the output.')
    parser.add_argument('-a', type=int, default=50, help='The factor by which to multiply the number of spline control points to yield the total number of approximation points.')
    parser.add_argument('-o', nargs=1, help='The output EAGLE SCR file (default: a file with the same name as the DXF file, but with a .scr extension).')
    parser.add_argument('-l', nargs='*')
    parser.add_argument('-i', nargs=1, required=True, help='The DXF file to parse.')
    args = parser.parse_args()
    
    num_errors = 0
     
    # Make sure the scale factor is valid
    if args.s <= 0:
        sys.stderr.write('Invalid scale factor {0}. Scale factor must be greater than zero.\n'.format(args.s))
        num_errors += 1
        
    # Make sure the spline point scalar is valid
    if args.a <= 0:
        sys.stderr.write('Invalid spline point scalar {0}. Spline point scalar must be greater than zero.\n'.format(args.a))
        num_errors += 1
        
    input_file = args.i[0]
     
    # Determine the output file name
    if args.o != None:
        # User-specified outfile
        output_file = args.o
    else:
        # Separate the name and extension
        file_name, file_ext = os.path.splitext(input_file)
         
        # If the file has a .dxf extension, replace it with .scr.
        # Otherwise, just append .scr
        if file_ext.lower() == '.dxf':
            output_file = file_name + '.scr'
        else:
            output_file = input_file + '.scr'
             
    # Parse the layers
    if args.l == None:
        layers = None
    else:
        layers = {}
        for l in args.l:
            if layers.has_key(l) == True:
                sys.stderr.write('Duplicate layer {0} in list. A layer name may only appear once.\n'.format(l))
                num_errors += 1
                break
            
            layers[l] = None
             
    if num_errors > 0:
        sys.exit(1)
         
    create_script(input_file, output_file, layers, args.s, args.t, args.a)     
    sys.exit(0)
    
if __name__ == "__main__":
    main()
