#!/usr/bin/env python
#
#       plot.py
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
Module Contents
===============
This is the main module. It contains the base classes for chart widgets.
 - class Chart: base class for all chart widgets.
 - class ChartObject: base class for all things that can be drawn on a chart.
 - class Background: background of a chart widget.
 - class Title: title of a chart.

Colors
------
All colors have to be C{(r, g, b)} tuples. The value of C{r, g} and C{b}
has to be between 0.0 and 1.0.
For example C{(0, 0, 0)} is black and C{(1, 1, 1)} is white.

Author: Sven Festersen (sven@sven-festersen.de)
"""
__docformat__ = "epytext"
import cairo
import gobject
import gtk
import os
import pango
import pygtk

from pygtk_chart.chart_object import ChartObject
from pygtk_chart.basics import *
from pygtk_chart import label


class Chart(gtk.DrawingArea):
    """
    This is the base class for all chart widgets.
    """
    
    def __init__(self):
        gtk.DrawingArea.__init__(self)
        self.connect("expose_event", self.expose)
        #objects needed for every chart
        self.background = Background()
        self.background.connect("appearance-changed", self._cb_appearance_changed)
        self.title = Title()
        self.title.connect("appearance-changed", self._cb_appearance_changed)
        
    def _cb_appearance_changed(self, object):
        """
        This method is called after the appearance of an object changed
        and forces a redraw.
        """
        self.queue_draw()
        
    def expose(self, widget, event):
        """
        This method is called when an instance of Chart receives
        the gtk expose_event.
        
        @type widget: gtk.Widget
        @param widget: The widget that received the event.
        @type event: gtk.Event
        @param event: The event.
        """
        self.context = widget.window.cairo_create()
        self.context.rectangle(event.area.x, event.area.y, \
                                event.area.width, event.area.height)
        self.context.clip()
        self.draw(self.context)
        return False
        
    def draw_basics(self, context, rect):
        """
        Draw basic things that every plot has (background, title, ...).
        
        @type context: cairo.Context
        @param context: The context to draw on.
        @type rect: gtk.gdk.Rectangle
        @param rect: A rectangle representing the charts area.
        """
        self.background.draw(context, rect)
        self.title.draw(context, rect)
        
    def draw(self, context):
        """
        Draw the widget. This method is called automatically. Don't call it
        yourself. If you want to force a redrawing of the widget, call
        the queue_draw() method.
        
        @type context: cairo.Context
        @param context: The context to draw on.
        """
        rect = self.get_allocation()
        context.set_line_width(1)
        self.draw_basics(context, rect)
        
    def export_svg(self, filename):
        """
        Saves the contents of the widget to svg file. The size of the image
        will be the size of the widget.
        
        @type filename: string
        @param filename: The path to the file where you want the chart to be saved.
        """
        rect = self.get_allocation()
        surface = cairo.SVGSurface(filename, rect.width, rect.height)
        context = cairo.Context(surface)
        self.draw(context)
        surface.finish()
        
    def export_png(self, filename):
        """
        Saves the contents of the widget to png file. The size of the image
        will be the size of the widget.
        
        @type filename: string
        @param filename: The path to the file where you want the chart to be saved.
        """
        rect = self.get_allocation()
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, rect.width,
                                        rect.height)
        context = cairo.Context(surface)
        self.draw(context)
        surface.write_to_png(filename)        
        
class Background(ChartObject):
    """
    The background of a chart.
    """    
    
    __gproperties__ = {"color": (gobject.TYPE_PYOBJECT,
                                    "background color",
                                    "The color of the backround in (r,g,b) format. r,g,b in [0,1]",
                                    gobject.PARAM_READWRITE),
                        "gradient": (gobject.TYPE_PYOBJECT,
                                    "background gradient",
                                    "A background gardient. (first_color, second_color)",
                                    gobject.PARAM_READWRITE),
                        "image": (gobject.TYPE_STRING,
                                    "background image file",
                                    "Path to the image file to use as background.",
                                    "", gobject.PARAM_READWRITE)}
    
    def __init__(self):
        ChartObject.__init__(self)
        self._color = (1, 1, 1) #the backgound is filled white by default
        self._gradient = None
        self._image = ""
        self._image_surface = None
        
    def do_get_property(self, property):
        if property.name == "visible":
            return self._show
        elif property.name == "antialias":
            return self._antialias
        elif property.name == "gradient":
            return self._gradient
        elif property.name == "color":
            return self._color
        elif property.name == "image":
            return self._image
        else:
            raise AttributeError, "Property %s does not exist." % property.name

    def do_set_property(self, property, value):
        if property.name == "visible":
            self._show = value
        elif property.name == "antialias":
            self._antialias = value
        elif property.name == "gradient":
            self._gradient = value
        elif property.name == "color":
            self._color = value
        elif property.name == "image":
            self._image = value
        else:
            raise AttributeError, "Property %s does not exist." % property.name
        
    def _do_draw(self, context, rect):
        """
        Do all the drawing stuff.
        
        @type context: cairo.Context
        @param context: The context to draw on.
        @type rect: gtk.gdk.Rectangle
        @param rect: A rectangle representing the charts area.
        """
        if self._color != None:
            #set source color
            c = self._color
            context.set_source_rgb(c[0], c[1], c[2])
        elif self._gradient != None:
            #set source gradient
            cs, ce = self._gradient
            gradient = cairo.LinearGradient(0, 0, 0, rect.height)
            gradient.add_color_stop_rgb(0, cs[0], cs[1], cs[2])
            gradient.add_color_stop_rgb(1, ce[0], ce[1], ce[2])
            context.set_source(gradient)
        elif self._image_surface:
            context.set_source_surface(self._image_surface, 0, 0)
        else:
            context.set_source_rgb(1, 1, 1) #fallback to white bg
        #create the background rectangle and fill it:
        context.rectangle(0, 0, rect.width, rect.height)
        context.fill()
        
    def set_color(self, color):
        """
        The set_color() method can be used to change the color of the
        background.
        
        @type color: a color
        @param color: Set the background to be filles with this color.
        """
        self.set_property("color", color)
        self.set_property("gradient", None)
        self.set_property("image", "")
        self.emit("appearance_changed")
        
    def get_color(self):
        return self.get_property("color")
        
    def set_gradient(self, color_start, color_end):
        """
        Use set_gradient() to define a vertical gradient as the background.
        
        @type color_start: a color
        @param color_start: The starting (top) color of the gradient.
        @type color_end: a color
        @param color_end: The ending (bottom) color of the gradient.
        """
        self.set_property("color", None)
        self.set_property("gradient", (color_start, color_end))
        self.set_property("image", "")
        self.emit("appearance_changed")
        
    def get_gradient(self):
        return self.get_property("gradient")
        
    def set_image(self, filename):
        """
        The set_image() method sets the background to be filled with a png
        image.
        
        @type filename: string
        @param filename: Path to the png file you want to use as background
        image. If the file does not exists, the background is set to white.
        """
        try:
            self._image_surface = cairo.ImageSurface.create_from_png(filename)
        except:
            self._image_surface = None
        
        self.set_property("color", None)
        self.set_property("gradient", None)
        self.set_property("image", filename)
        self.emit("appearance_changed")
        
    def get_image(self):
        return self.get_property("image")
        
        
class Title(label.Label):
    """
    The title of a chart. The title will be drawn centered at the top of the
    chart.
    """    
    
    def __init__(self, text=""):
        label.Label.__init__(self, (0, 0), text, weight=pango.WEIGHT_BOLD, anchor=label.ANCHOR_TOP_CENTER)
        
    def _do_draw(self, context, rect):
        self._size = int(rect.height / 50.0)
        self._position = rect.width / 2, rect.height / 80
        self._do_draw_label(context, rect)
