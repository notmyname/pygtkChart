#!/usr/bin/env python
#
#       pie_chart.py
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
Contains the PieChart widget.
"""
__docformat__ = "epytext"
import cairo
import gtk
import math
import os

from pygtk_chart.basics import *
from pygtk_chart import chart

COLORS = color_list_from_file(os.path.dirname(__file__) + "/data/tango.color")


class PieArea(chart.ChartObject):
    
    __gproperties__ = {"value": (gobject.TYPE_FLOAT,
                                    "value",
                                    "The value.",
                                    0.0, 9999999999.0, 0.0, gobject.PARAM_READWRITE)}
    
    def __init__(self, value):
        chart.ChartObject.__init__(self)
        self._value = value
        
    def do_get_property(self, property):
        if property.name == "visible":
            return self._show
        elif property.name == "antialias":
            return self._antialias
        elif property.name == "value":
            return self._value
        else:
            raise AttributeError, "Property %s does not exist." % property.name

    def do_set_property(self, property, value):
        if property.name == "visible":
            self._show = value
        elif property.name == "antialias":
            self._antialias = value
        elif property.nmae == "value":
            self._value = value
        else:
            raise AttributeError, "Property %s does not exist." % property.name
            
    def set_value(self, value):
        """
        Set the value of the PieArea.
        
        @type value: float.
        """
        self.set_property("value", value)
        self.emit("appearance_changed")
        
    def get_value(self):
        """
        Returns the current value of the PieArea.
        
        @return: float.
        """
        return self.get_property("value")


class PieChart(chart.Chart):
    
    __gproperties__ = {"rotate": (gobject.TYPE_INT,
                                    "rotation",
                                    "The angle to rotate the chart in degrees.",
                                    0, 360, 0, gobject.PARAM_READWRITE)}
    
    def __init__(self):
        chart.Chart.__init__(self)
        self._rotate = 0
        
    def do_get_property(self, property):
        if property.name == "rotate":
            return self._rotate
        else:
            raise AttributeError, "Property %s does not exist." % property.name

    def do_set_property(self, property, value):
        if property.name == "rotate":
            self._rotate = value
        else:
            raise AttributeError, "Property %s does not exist." % property.name
            
    def set_rotate(self, angle):
        """
        Set the rotation angle of the PieChart in degrees.
        
        @param angle: angle in degrees 0 - 360
        @type angle: integer.
        """
        self.set_property("rotate", angle)
        self.queue_draw()
        
    def get_rotate(self):
        """
        Get the current rotation angle in degrees.
        
        @return integer.
        """
        return self.get_property("rotate")
