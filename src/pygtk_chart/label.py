#!/usr/bin/env python
#
#       text.py
#       
#       Copyright 2009 Sven Festersen <sven@sven-festersen.de>
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
import cairo
import gobject
import gtk
import math
import pango
import pygtk

from pygtk_chart import basics
from pygtk_chart.chart_object import ChartObject


ANCHOR_BOTTOM_LEFT = 0
ANCHOR_TOP_LEFT = 1
ANCHOR_TOP_RIGHT = 2
ANCHOR_BOTTOM_RIGHT = 4
ANCHOR_CENTER = 5
ANCHOR_TOP_CENTER = 6
ANCHOR_BOTTOM_CENTER = 7
ANCHOR_LEFT_CENTER = 8
ANCHOR_RIGHT_CENTER = 9


class Label(ChartObject):
    
    __gproperties__ = {"color": (gobject.TYPE_PYOBJECT,
                                "label color",
                                "The color of the label (a gtk.gdkColor)",
                                gobject.PARAM_READWRITE),
                        "text": (gobject.TYPE_STRING,
                                "label text",
                                "The text to show on the label.",
                                "", gobject.PARAM_READWRITE),
                        "position": (gobject.TYPE_PYOBJECT,
                                    "label position",
                                    "A pair of x,y coordinates.",
                                    gobject.PARAM_READWRITE),
                        "anchor": (gobject.TYPE_INT, "label anchor",
                                    "The anchor of the label.", 0, 9, 0,
                                    gobject.PARAM_READWRITE),
                        "underline": (gobject.TYPE_BOOLEAN,
                                    "underline text",
                                    "Set whether to underline the text.",
                                    False,
                                    gobject.PARAM_READWRITE),
                        "max-width": (gobject.TYPE_INT, "maximum width",
                                        "The maximum width of the label.",
                                        1, 99999, 99999,
                                        gobject.PARAM_READWRITE),
                        "rotation": (gobject.TYPE_INT, "rotation of the label",
                                    "The angle that the label should be rotated by in degrees.",
                                    0, 360, 0, gobject.PARAM_READWRITE)}
    
    def __init__(self, position, text, font=None, size=None, slant=pango.STYLE_NORMAL, weight=pango.WEIGHT_NORMAL, underline=pango.UNDERLINE_NONE, anchor=ANCHOR_BOTTOM_LEFT, max_width=99999):
        ChartObject.__init__(self)
        self._position = position
        self._text = text
        self._font = font
        self._size = size
        self._slant = slant
        self._weight = weight
        self._underline = underline
        self._anchor = anchor
        self._rotation = 0 #rotation angle in degrees
        self._color = gtk.gdk.Color()
        self._max_width = max_width
        
        self._real_dimension = (0, 0)
        
    def do_get_property(self, property):
        if property.name == "visible":
            return self._show
        elif property.name == "antialias":
            return self._antialias
        elif property.name == "text":
            return self._text
        elif property.name == "color":
            return self._color
        elif property.name == "position":
            return self._position
        elif property.name == "anchor":
            return self._anchor
        elif property.name == "underline":
            return self._underline
        elif property.name == "max-width":
            return self._max_width
        elif property.name == "rotation":
            return self._rotation
        else:
            raise AttributeError, "Property %s does not exist." % property.name

    def do_set_property(self, property, value):
        if property.name == "visible":
            self._show = value
        elif property.name == "antialias":
            self._antialias = value
        elif property.name == "text":
            self._text = value
        elif property.name == "color":
            self._color = value
        elif property.name == "position":
            self._position = value
        elif property.name == "anchor":
            self._anchor = value
        elif property.name == "underline":
            self._underline = value
        elif property.name == "max-width":
            self._max_width = value
        elif property.name == "rotation":
            self._rotation = value
        else:
            raise AttributeError, "Property %s does not exist." % property.name
        
    def _do_draw(self, context, rect):
        self._do_draw_label(context, rect)
        
    def _do_draw_label(self, context, rect):
        angle = 2 * math.pi * self._rotation / 360.0
        label = gtk.Label()
        pango_context = label.create_pango_context()
        #if self._font == None:
        #    font = label.style.font_desc.get_family()            
        
        attrs = pango.AttrList()
        attrs.insert(pango.AttrWeight(self._weight, 0, len(self._text)))
        attrs.insert(pango.AttrStyle(self._slant, 0, len(self._text)))
        attrs.insert(pango.AttrUnderline(self._underline, 0, len(self._text)))
        if self._size != None:
            attrs.insert(pango.AttrSize(1000 * self._size, 0, len(self._text)))
        
        layout = pango.Layout(pango_context)
        layout.set_text(self._text)
        layout.set_attributes(attrs)
        
        #find out where to draw the layout and calculate the maximum width
        width = rect.width
        if self._anchor in [ANCHOR_BOTTOM_LEFT, ANCHOR_TOP_LEFT, ANCHOR_LEFT_CENTER]:
            width = rect.width - self._position[0]
        elif self._anchor in [ANCHOR_BOTTOM_RIGHT, ANCHOR_TOP_RIGHT, ANCHOR_RIGHT_CENTER]:
            width = self._position[0]
        
        text_width, text_height = layout.get_pixel_size()
        width = width * math.cos(angle)
        width = min(width, self._max_width)
        
        layout.set_wrap(pango.WRAP_WORD_CHAR)
        layout.set_width(int(1000 * width))
        
        x, y = get_text_pos(layout, self._position, self._anchor)
        y -= text_width * math.sin(angle)
        
        #draw layout
        context.move_to(x, y)
        context.rotate(angle)
        context.set_source_rgb(*basics.color_gdk_to_cairo(self._color))
        context.show_layout(layout)
        context.rotate(-angle)
        context.stroke()
        
        #calculate the real dimensions
        text_width, text_height = layout.get_pixel_size()
        real_width = abs(text_width * math.cos(angle)) + abs(text_height * math.sin(angle))
        real_height = abs(text_height * math.cos(angle)) + abs(text_width * math.sin(angle))
        self._real_dimensions = real_width, real_height
        
    def set_text(self, text):
        self.set_property("text", text)
        self.emit("appearance_changed")
        
    def get_text(self):
        return self.get_property("text")
        
    def set_color(self, color):
        self.set_property("color", color)
        self.emit("appearance_changed")
        
    def get_color(self):
        return self.get_property("color")
        
    def set_position(self, pos):
        self.set_property("position", pos)
        self.emit("appearance_changed")
        
    def get_position(self):
        return self.get_property("position")
        
    def set_anchor(self, anchor):
        self.set_property("anchor", anchor)
        self.emit("appearance_changed")
        
    def get_anchor(self):
        return self.get_property("anchor")
        
    def set_underline(self, underline):
        self.set_property("underline", underline)
        self.emit("appearance_changed")
        
    def get_underline(self):
        return self.get_property("underline")
        
    def set_max_width(self, width):
        self.set_property("max-width", width)
        self.emit("appearance_changed")
        
    def get_max_width(self):
        return self.get_property("max-width")
        
    def set_rotation(self, angle):
        self.set_property("rotation", angle)
        self.emit("appearance_changed")
        
    def get_rotation(self):
        return self.get_property("rotation")
        
    def get_real_dimensions(self):
        return self._real_dimensions
        
def get_text_pos(layout, pos, anchor):
    text_width, text_height = layout.get_pixel_size()
    x, y = pos
    ref = (0, -text_height)
    if anchor == ANCHOR_TOP_LEFT:
        ref = (0, 0)
    elif anchor == ANCHOR_TOP_RIGHT:
        ref = (-text_width, 0)
    elif anchor == ANCHOR_BOTTOM_RIGHT:
        ref = (-text_width, -text_height)
    elif anchor == ANCHOR_CENTER:
        ref = (-text_width / 2, -text_height / 2)
    elif anchor == ANCHOR_TOP_CENTER:
        ref = (-text_width / 2, 0)
    elif anchor == ANCHOR_BOTTOM_CENTER:
        ref = (-text_width / 2, -text_height)
    elif anchor == ANCHOR_LEFT_CENTER:
        ref = (0, -text_height / 2)
    elif anchor == ANCHOR_RIGHT_CENTER:
        ref = (-text_width, -text_height / 2)
    x += ref[0]
    y += ref[1]
    return x, y
