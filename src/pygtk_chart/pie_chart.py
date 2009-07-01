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
import gobject
import gtk
import math
import os

from pygtk_chart.basics import *
from pygtk_chart import chart

COLOR_AUTO = 0

#load default color palette
COLORS = color_list_from_file(os.path.dirname(__file__) + "/data/tango.color")


class PieArea(chart.ChartObject):
    
    __gproperties__ = {"name": (gobject.TYPE_STRING, "pie are name",
                                "A unique name for the pie area.",
                                "", gobject.PARAM_READABLE),
                        "value": (gobject.TYPE_FLOAT,
                                    "value",
                                    "The value.",
                                    0.0, 9999999999.0, 0.0, gobject.PARAM_READWRITE),
                        "color": (gobject.TYPE_PYOBJECT, "pie area color",
                                    "The color of the area.",
                                    gobject.PARAM_READWRITE),
                        "label": (gobject.TYPE_STRING, "area label",
                                    "The label for the area.", "",
                                    gobject.PARAM_READWRITE)}
    
    def __init__(self, name, value, label=""):
        chart.ChartObject.__init__(self)
        self._name = name
        self._value = value
        self._label = label
        self._color = COLOR_AUTO
        
    def do_get_property(self, property):
        if property.name == "visible":
            return self._show
        elif property.name == "antialias":
            return self._antialias
        elif property.name == "name":
            return self._name
        elif property.name == "value":
            return self._value
        elif property.name == "color":
            return self._color
        elif property.name == "label":
            return self._label
        else:
            raise AttributeError, "Property %s does not exist." % property.name

    def do_set_property(self, property, value):
        if property.name == "visible":
            self._show = value
        elif property.name == "antialias":
            self._antialias = value
        elif property.name == "value":
            self._value = value
        elif property.name == "color":
            self._color = value
        elif property.name == "label":
            self._label = value
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
        
    def set_color(self, color):
        """
        Set the color of the pie area. Color has to either COLOR_AUTO or
        a tuple (r, g, b) with r, g, b in [0, 1].
        
        @type color: a color.
        """
        self.set_property("color", color)
        self.emit("appearance_changed")
        
    def get_color(self):
        """
        Returns the current color of the pie area or COLOR_AUTO.
        
        @return: a color.
        """
        return self.get_property("color")
        
    def set_label(self, label):
        """
        Set the label for the pie chart area.
        
        @param label: the new label
        @type label: string.
        """
        self.set_property("label", label)
        self.emit("appearance:changed")
        
    def get_label(self):
        """
        Returns the current label of the area.
        
        @return: string.
        """
        return self.get_property("label")


class PieChart(chart.Chart):
    
    __gproperties__ = {"rotate": (gobject.TYPE_INT,
                                    "rotation",
                                    "The angle to rotate the chart in degrees.",
                                    0, 360, 0, gobject.PARAM_READWRITE),
                        "draw-shadow": (gobject.TYPE_BOOLEAN,
                                        "draw pie shadow",
                                        "Set whether to draw pie shadow.",
                                        True, gobject.PARAM_READWRITE),
                        "draw-labels": (gobject.TYPE_BOOLEAN,
                                        "draw area labels",
                                        "Set whether to draw area labels.",
                                        True, gobject.PARAM_READWRITE),
                        "show-percentage": (gobject.TYPE_BOOLEAN,
                                        "show percentage",
                                        "Set whether to show percentage in the areas' labels.",
                                        True, gobject.PARAM_READWRITE)}
                                        
    __gsignals__ = {"area-clicked": (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,))}
    
    def __init__(self):
        chart.Chart.__init__(self)
        self._areas = []
        self._rotate = 0
        self._shadow = True
        self._labels = True
        self._percentage = True
        
        self.add_events(gtk.gdk.BUTTON_PRESS_MASK|gtk.gdk.SCROLL_MASK)
        self.connect("button_press_event", self._cb_button_pressed)

        
    def do_get_property(self, property):
        if property.name == "rotate":
            return self._rotate
        elif property.name == "draw-shadow":
            return self._shadow
        elif property.name == "draw-labels":
            return self._labels
        elif property.name == "show-percentage":
            return self._percentage
        else:
            raise AttributeError, "Property %s does not exist." % property.name

    def do_set_property(self, property, value):
        if property.name == "rotate":
            self._rotate = value
        elif property.name == "draw-shadow":
            self._shadow = value
        elif property.name == "draw-labels":
            self._labels = value
        elif property.name == "show-percentage":
            self._percentage = value
        else:
            raise AttributeError, "Property %s does not exist." % property.name
            
    def _cb_appearance_changed(self, widget):
        self.queue_draw()
        
    def _cb_button_pressed(self, widget, event):
        rect = self.get_allocation()
        center = rect.width / 2, rect.height / 2
        x = event.x - center[0]
        y = event.y - center[1]

        #calculate angle        
        angle = math.atan2(x, -y)
        angle -= math.pi / 2
        angle -= 2 * math.pi * self.get_rotate() / 360.0
        while angle < 0:
            angle += 2 * math.pi
            
        #calculate radius
        radius_squared = math.pow(int(0.4 * min(rect.width, rect.height)), 2)
        clicked_radius_squared = x*x + y*y
        
        if clicked_radius_squared <= radius_squared:
            #find out area that was clicked
            sum = 0
            for area in self._areas:
                if area.get_visible():
                    sum += area.get_value()
                    
            current_angle_position = 0
            for area in self._areas:
                area_angle = 2 * math.pi * area.get_value() / sum
                
                if current_angle_position <= angle <= current_angle_position + area_angle:
                    self.emit("area-clicked", area)
                    break
                
                current_angle_position += area_angle
        
    def draw(self, context):
        """
        Draw the widget. This method is called automatically. Don't call it
        yourself. If you want to force a redrawing of the widget, call
        the queue_draw() method.

        @type context: cairo.Context
        @param context: The context to draw on.
        """
        rect = self.get_allocation()
        #initial context settings: line width & font
        context.set_line_width(1)
        font = gtk.Label().style.font_desc.get_family()
        context.select_font_face(font, cairo.FONT_SLANT_NORMAL, \
                                    cairo.FONT_WEIGHT_NORMAL)

        self.draw_basics(context, rect)
        self._do_draw_shadow(context, rect)
        self._do_draw_areas(context, rect)
        
    def _do_draw_areas(self, context, rect):
        center = rect.width / 2, rect.height / 2
        radius = int(0.4 * min(rect.width, rect.height))
        sum = 0
        
        for area in self._areas:
            if area.get_visible():
                sum += area.get_value()
        
        current_angle_position = 2 * math.pi * self.get_rotate() / 360.0
        for i, area in enumerate(self._areas):
            if not area.get_visible(): continue
            #set the color or automaticly select one:
            color = area.get_color()
            if color == COLOR_AUTO: color = COLORS[i % len(COLORS)]
            #draw the area:
            area_angle = 2 * math.pi * area.get_value() / sum
            context.set_source_rgb(*color)
            context.move_to(center[0], center[1])
            context.arc(center[0], center[1], radius, current_angle_position, current_angle_position + area_angle)
            context.close_path()
            context.fill()
        
            if self._labels:
                #draw the label:
                label = area.get_label()
                if self._percentage:
                    label = label + " (%s%%)" % round(100. * area.get_value() / sum, 2)
                angle = current_angle_position + area_angle / 2
                angle = angle % (2 * math.pi)
                x = center[0] + (radius + 10) * math.cos(angle)
                y = center[1] + (radius + 10) * math.sin(angle)
                text_size = context.text_extents(label)
                text_width = text_size[2]
                text_height = text_size[3]
                
                ref = (0, 0)
                if 0 <= angle <= math.pi / 2:
                    ref = (0, text_height)
                elif math.pi / 2 <= angle <= math.pi:
                    ref = (-text_width, text_height)
                elif math.pi <= angle <= 1.5 * math.pi:
                    ref = (-text_width, 0)
                x = x + ref[0]
                y = y + ref[1]

                context.move_to(x, y)
                context.show_text(label)
                context.fill()
            
            current_angle_position += area_angle
            
    def _do_draw_shadow(self, context, rect):
        if not self._shadow: return
        center = rect.width / 2, rect.height / 2
        radius = int(0.4 * min(rect.width, rect.height))
        
        gradient = cairo.RadialGradient(center[0], center[1], radius, center[0], center[1], radius + 10)
        gradient.add_color_stop_rgba(0, 0, 0, 0, 0.5)
        gradient.add_color_stop_rgba(0.5, 0, 0, 0, 0)

        context.set_source(gradient)
        context.arc(center[0], center[1], radius + 10, 0, 2 * math.pi)
        context.fill()
        
    def add_area(self, area):
        self._areas.append(area)
        area.connect("appearance_changed", self._cb_appearance_changed)
        
    def get_pie_area(self, name):
        """
        Returns the PieArea with the id 'name' if it exists, None
        otherwise.
        
        @type name: string
        @param name: the id of a PieArea
        
        @return a PieArea or None.
        """
        for area in self._areas:
            if area.get_name() == name:
                return area
        return None
            
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
        
    def set_draw_shadow(self, draw):
        """
        Set whether to draw the pie chart's shadow.
        
        @type draw: boolean.
        """
        self.set_property("draw-shadow", draw)
        self.queue_draw()
        
    def get_draw_shadow(self):
        """
        Returns True if pie chart currently has a shadow.
        
        @return: boolean.
        """
        return self.get_property("draw-shadow")
        
    def set_draw_labels(self, draw):
        """
        Set whether to draw the labels of the pie areas.
        
        @type draw: boolean.
        """
        self.set_property("draw-labels", draw)
        self.queue_draw()
        
    def get_draw_labels(self):
        """
        Returns True if area labels are shown.
        
        @return: boolean.
        """
        return self.get_property("draw-labels")
        
    def set_show_percentage(self, show):
        """
        Set whether to show the percentage an area has in its label.
        
        @type show: boolean.
        """
        self.set_property("show-percentage", show)
        self.queue_draw()
        
    def get_show_percentage(self):
        """
        Returns True if percentages are shown.
        
        @return: boolean.
        """
        return self.get_property("show-percentage")
