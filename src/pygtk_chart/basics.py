#!/usr/bin/env python
#
#       misc.py
#       
#       Copyright 2008 Sven Festersen <sven@sven-festersen.de>
#       
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.
"""
This module contains simple functions needed by all other modules.
"""
__docformat__ = "epytext"
import os


def is_in_range(x, (xmin, xmax)):
    """
    Use this method to test whether M{xmin <= x <= xmax}.
    
    @type x: number
    @type xmin: number
    @type xmax: number
    """
    return (xmin <= x and xmax >= x)
    
def get_center(rect):
    """
    Find the center point of a rectangle.
    
    @type rect: gtk.gdk.Rectangle
    @param rect: The rectangle.
    @return: A (x, y) tuple specifying the center point.
    """
    return rect.width / 2, rect.height / 2
    
def color_rgb_to_cairo(color):
    """
    Convert a 8 bit RGB value to cairo color.
    
    @type color: a triple of integers between 0 and 255
    @param color: The color to convert.
    @return: A color in cairo format.
    """
    return (color[0] / 255.0, color[1] / 255.0, color[2] / 255.0)

def color_html_to_cairo(color):
    """
    Convert a html (hex) RGB value to cairo color.
    
    @type color: html color string
    @param color: The color to convert.
    @return: A color in cairo format.
    """
    if color[0] == '#':
        color = color[1:]
    (r, g, b) = (int(color[:2], 16),
                    int(color[2:4], 16), 
                    int(color[4:], 16))
    return color_rgb_to_cairo((r, g, b))
    
def color_list_from_file(filename):
    """
    Read a file with one html hex color per line and return a list
    of cairo colors.
    """
    result = []
    if os.path.exists(filename):
        f = open(filename, "r")
        for line in f.readlines():
            line = line.strip()
            result.append(color_html_to_cairo(line))
    return result

