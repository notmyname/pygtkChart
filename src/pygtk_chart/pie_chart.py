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

Author: Sven Festersen (sven@sven-festersen.de)
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
        self.emit("appearance_changed")
        
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
                                        False, gobject.PARAM_READWRITE),
                        "show-values": (gobject.TYPE_BOOLEAN,
                                        "show values",
                                        "Set whether to show values in the areas' labels.",
                                        True, gobject.PARAM_READWRITE),
                        "enable-scroll": (gobject.TYPE_BOOLEAN,
                                        "enable scroll",
                                        "If True, the pie can be rotated by scrolling with the mouse wheel.",
                                        True, gobject.PARAM_READWRITE),
                        "enable-mouseover": (gobject.TYPE_BOOLEAN,
                                        "enable mouseover",
                                        "Set whether a mouseover effect should be visible if moving the mouse over a pie area.",
                                        True, gobject.PARAM_READWRITE)}
                                        
    __gsignals__ = {"area-clicked": (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,))}
    
    def __init__(self):
        chart.Chart.__init__(self)
        self._areas = []
        self._rotate = 0
        self._shadow = True
        self._labels = True
        self._percentage = False
        self._values = True
        self._enable_scroll = True
        self._enable_mouseover = True
        
        self._highlighted = None
        
        self.add_events(gtk.gdk.BUTTON_PRESS_MASK|gtk.gdk.SCROLL_MASK|gtk.gdk.POINTER_MOTION_MASK)
        self.connect("button_press_event", self._cb_button_pressed)
        self.connect("scroll-event", self._cb_scroll_event)
        self.connect("motion-notify-event", self._cb_motion_notify)
        
    def do_get_property(self, property):
        if property.name == "rotate":
            return self._rotate
        elif property.name == "draw-shadow":
            return self._shadow
        elif property.name == "draw-labels":
            return self._labels
        elif property.name == "show-percentage":
            return self._percentage
        elif property.name == "show-values":
            return self._values
        elif property.name == "enable-scroll":
            return self._enable_scroll
        elif property.name == "enable-mouseover":
            return self._enable_mouseover
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
        elif property.name == "show-values":
            self._values = value
        elif property.name == "enable-scroll":
            self._enable_scroll = value
        elif property.name == "enable-mouseover":
            self._enable_mouseover = value
        else:
            raise AttributeError, "Property %s does not exist." % property.name
            
    def _cb_appearance_changed(self, widget):
        self.queue_draw()
        
    def _cb_motion_notify(self, widget, event):
        if not self._enable_mouseover: return
        area = self._get_area_at_pos(event.x, event.y)
        if area != self._highlighted:
            self.queue_draw()
        self._highlighted = area
        
    def _cb_button_pressed(self, widget, event):
        area = self._get_area_at_pos(event.x, event.y)
        if area:
            self.emit("area-clicked", area)
                
    def _get_area_at_pos(self, x, y):
        rect = self.get_allocation()
        center = rect.width / 2, rect.height / 2
        x = x - center[0]
        y = y - center[1]

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
                    return area
                
                current_angle_position += area_angle
        return None
                
    def _cb_scroll_event(self, widget, event):
        if not self._enable_scroll: return
        if event.direction in [gtk.gdk.SCROLL_UP, gtk.gdk.SCROLL_RIGHT]:
            delta = 360.0 / 32
        elif event.direction in [gtk.gdk.SCROLL_DOWN, gtk.gdk.SCROLL_LEFT]:
            delta = - 360.0 / 32
        else:
            delta = 0
        rotate = self.get_rotate() + delta
        rotate = rotate % 360.0
        if rotate < 0: rotate += 360
        self.set_rotate(rotate)
            
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
            #if color == COLOR_AUTO: color = COLORS[i % len(COLORS)]
            #draw the area:
            area_angle = 2 * math.pi * area.get_value() / sum
            context.set_source_rgb(*color)
            context.move_to(center[0], center[1])
            context.arc(center[0], center[1], radius, current_angle_position, current_angle_position + area_angle)
            context.close_path()
            context.fill()
            
            if area == self._highlighted:
                context.set_source_rgba(1, 1, 1, 0.1)
                context.move_to(center[0], center[1])
                context.arc(center[0], center[1], radius, current_angle_position, current_angle_position + area_angle)
                context.close_path()
                context.fill()
        
            if self._labels:
                font_name = gtk.Label().style.font_desc.get_family()
                font_slant = cairo.FONT_SLANT_NORMAL
                if area == self._highlighted:
                    font_slant = cairo.FONT_SLANT_ITALIC
                context.set_source_rgb(*color)
                
                label = area.get_label()
                label_extra = ""
                if self._percentage and not self._values:
                    label_extra = " (%s%%)" % round(100. * area.get_value() / sum, 2)
                elif not self._percentage and self._values:
                    label_extra = " (%s)" % area.get_value()
                elif self._percentage and self._values:
                    label_extra = " (%s, %s%%)" % (area.get_value(), round(100. * area.get_value() / sum, 2))
                label += label_extra
                angle = current_angle_position + area_angle / 2
                angle = angle % (2 * math.pi)
                x = center[0] + (radius + 10) * math.cos(angle)
                y = center[1] + (radius + 10) * math.sin(angle)
                
                ref = REF_BOTTOM_LEFT
                if 0 <= angle <= math.pi / 2:
                    ref = REF_TOP_LEFT
                elif math.pi / 2 <= angle <= math.pi:
                    ref = REF_TOP_RIGHT
                elif math.pi <= angle <= 1.5 * math.pi:
                    ref = REF_BOTTOM_RIGHT
                
                show_text(context, rect, x, y, label, font_name, rect.height / 30, slant=font_slant, reference_point=ref)
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
        color = area.get_color()
        if color == COLOR_AUTO: area.set_color(COLORS[len(self._areas) % len(COLORS)])
        self._areas.append(area)
        area.connect("appearance_changed", self._cb_appearance_changed)
        
    def get_pie_area(self, name):
        """
        Returns the PieArea with the id 'name' if it exists, None
        otherwise.
        
        @type name: string
        @param name: the id of a PieArea
        
        @return: a PieArea or None.
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
        
        @return: integer.
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
        
    def set_enable_scroll(self, scroll):
        """
        Set whether the pie chart can be rotated by scrolling with
        the mouse wheel.
        
        @type scroll: boolean.
        """
        self.set_property("enable-scroll", scroll)
        
    def get_enable_scroll(self):
        """
        Returns True if the user can rotate the pie chart by scrolling.
        
        @return: boolean.
        """
        return self.get_property("enable-scroll")
        
    def set_enable_mouseover(self, mouseover):
        """
        Set whether a mouseover effect should be shown when the pointer
        enters a pie area.
        
        @type mouseover: boolean.
        """
        self.set_property("enable-mouseover", mouseover)
        
    def get_enable_mouseover(self):
        """
        Returns True if the mouseover effect is enabled.
        
        @return: boolean.
        """
        return self.get_property("enable-mouseover")
        
    def set_show_values(self, show):
        """
        Set whether the area's value should be shown in its label.
        
        @type show: boolean.
        """
        self.set_property("show-values", show)
        self.queue_draw()
        
    def get_show_values(self):
        """
        Returns True if the value of a pie area is shown in its label.
        
        @return: boolean.
        """
        return self.get_property("show-values")
        
