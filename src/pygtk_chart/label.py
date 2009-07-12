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
                                    gobject.PARAM_READWRITE)}
    
    def __init__(self, position, text, font=None, size=None, slant=pango.STYLE_NORMAL, weight=pango.WEIGHT_NORMAL, underline=pango.UNDERLINE_NONE, anchor=ANCHOR_BOTTOM_LEFT):
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
        else:
            raise AttributeError, "Property %s does not exist." % property.name
        
    def _do_draw(self, context, rect):
        self._do_draw_label(context, rect)
        
    def _do_draw_label(self, context, rect):
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
        
        text_width, text_height = layout.get_pixel_size()
        
        #find out where to draw the layout and calculate the maximum width
        x, y = get_text_pos(layout, self._position, self._anchor)
        if x < 0: x = 0
        width = rect.width - x
        layout.set_width(1000 * width)
        
        if text_width >= 0.9 * width:
            #text has to be wrapped => new position needed
            layout.set_wrap(pango.WRAP_WORD_CHAR)
            x, y = get_text_pos(layout, self._position, self._anchor)
            if x < 0: x = 0
        
        #draw layout
        context.move_to(x, y)
        context.set_source_rgb(*basics.color_gdk_to_cairo(self._color))
        context.show_layout(layout)
        context.stroke()
        
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
