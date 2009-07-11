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

Author: Sven Festersen (sven@sven-festersen.de)
"""
__docformat__ = "epytext"
import cairo
import os

REF_BOTTOM_LEFT = 0
REF_TOP_LEFT = 1
REF_TOP_RIGHT = 2
REF_BOTTOM_RIGHT = 4


def is_in_range(x, (xmin, xmax)):
    """
    Use this method to test whether M{xmin <= x <= xmax}.
    
    @type x: number
    @type xmin: number
    @type xmax: number
    """
    return (xmin <= x and xmax >= x)
    
def intersect_ranges(range_a, range_b):
    min_a, max_a = range_a
    min_b, max_b = range_b
    return max(min_a, min_b), min(max_a, max_b)
    
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
    
def show_text(context, rect, x, y, text, font, size, slant=cairo.FONT_SLANT_NORMAL, weight=cairo.FONT_WEIGHT_NORMAL, underline=False, reference_point=REF_BOTTOM_LEFT):
    context.set_font_size(max(size, 8))
    context.select_font_face(font, slant, weight)
    
    text_dimensions = context.text_extents(text)
    text_width = text_dimensions[2]
    text_height = text_dimensions[3]
    
    ref = (0, 0)
    if reference_point == REF_TOP_LEFT:
        ref = (0, text_height)
    elif reference_point == REF_TOP_RIGHT:
        ref = (-text_width, text_height)
    elif reference_point == REF_BOTTOM_RIGHT:
        ref = (-text_width, 0)
    x = x + ref[0]
    y = y + ref[1]
    
    context.move_to(x, y)
    context.show_text(text)

