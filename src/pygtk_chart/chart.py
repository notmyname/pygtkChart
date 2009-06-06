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
"""
__docformat__ = "epytext"
import cairo
import gtk
import os
import pygtk

from pygtk_chart.basics import *


class Chart(gtk.DrawingArea):
    """
    This is the base class for all chart widgets.
    """
    
    def __init__(self):
        gtk.DrawingArea.__init__(self)
        self.connect("expose_event", self.expose)
        #objects needed for every chart
        self.background = Background()
        self.title = Title()
        
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
        

class ChartObject:
    """
    This is the base class for all things that can be drawn in a chart,
    e.g. title, axes, graphs,...
    """
    def __init__(self):
        self._show = True
        self._antialias = True
        
    def _do_draw(self, context, rect):
        """
        A derived class should override this method. The drawing stuff
        should happen here.
        
        @type context: cairo.Context
        @param context: The context to draw on.
        @type rect: gtk.gdk.Rectangle
        @param rect: A rectangle representing the charts area.
        """
        pass
        
    def draw(self, context, rect):
        """
        This method is called by the parent Chart instance. It
        calls _do_draw.
        
        @type context: cairo.Context
        @param context: The context to draw on.
        @type rect: gtk.gdk.Rectangle
        @param rect: A rectangle representing the charts area.
        """
        if self._show:
            if not self._antialias:
                context.set_antialias(cairo.ANTIALIAS_NONE)
            self._do_draw(context, rect)
            context.set_antialias(cairo.ANTIALIAS_DEFAULT)
        
    def set_antialias(self, antialias):
        """
        This method sets the antialiasing mode of the ChartObject. Antialiasing
        is enabled by default.
        
        @type antialias: boolean
        @param antialias: If False, antialiasing is disabled for this 
        ChartObject.
        """
        self._antialias = antialias
        
    def set_visible(self, visible):
        """
        Use this method to set whether the ChartObject should be visible or
        not.
        
        @type visible: boolean
        @param visible: If False, the PlotObject won't be drawn.
        """
        self._show = visible
        
        
class Background(ChartObject):
    """
    The background of a chart.
    """    
    def __init__(self):
        ChartObject.__init__(self)
        self._color = (1, 1, 1) #the backgound is filled white by default
        self._gradient = None
        
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
        elif self._image != None:
            #set source image
            if os.path.exists(self._image):
                surface = cairo.ImageSurface.create_from_png(self._image)
                context.set_source_surface(surface, 0, 0)
            else:
                context.set_source_rgb(1, 1, 1) #white bg if image not found
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
        self._color = color
        self._gradient = None
        self._image = None
        
    def set_gradient(self, color_start, color_end):
        """
        Use set_gradient() to define a vertical gradient as the background.
        
        @type color_start: a color
        @param color_start: The starting (top) color of the gradient.
        @type color_end: a color
        @param color_end: The ending (bottom) color of the gradient.
        """
        self._gradient = (color_start, color_end)
        self._color = None
        self._image = None
        
    def set_image(self, filename):
        """
        The set_image() method sets the background to be filled with a png
        image.
        
        @type filename: string
        @param filename: Path to the png file you want to use as background
        image. If the file does not exists, the background is set to white.
        """
        self._image = filename
        self._color = None
        self._gradient = None
        
        
class Title(ChartObject):
    """
    The title of a chart. The title will be drawn centered at the top of the
    chart.
    """    
    def __init__(self, text=None):
        ChartObject.__init__(self)
        self._text = text
        self._color = (0, 0, 0)
        
    def _do_draw(self, context, rect):
        """
        Do all the drawing stuff.
        
        @type context: cairo.Context
        @param context: The context to draw on.
        @type rect: gtk.gdk.Rectangle
        @param rect: A rectangle representing the charts area.
        """
        if self._text != None:
            #prepare the font
            font = gtk.Label().style.font_desc.get_family()
            context.set_font_size(rect.height / 30)
            context.select_font_face(font,cairo.FONT_SLANT_NORMAL, \
                                        cairo.FONT_WEIGHT_BOLD)
            size = context.text_extents(self._text)
            #calculate position
            x = (rect.width - size[2]) / 2
            y = size[3] + rect.height / 80
            #draw
            c = self._color
            context.move_to(x, y)
            context.set_source_rgb(c[0], c[1], c[2])
            context.show_text(self._text)
            context.fill()
            
            #reset font
            context.select_font_face(font,cairo.FONT_SLANT_NORMAL, \
                                        cairo.FONT_WEIGHT_NORMAL)
        
    def set_color(self, color):
        """
        The set_color() method sets the color of the title text.
        
        @type color: a color
        @param color: The color of the title.
        """
        self._color = color
        
    def set_text(self, text):
        """
        Use the set_text() method to set the title of the chart.
        
        @type text: string
        @param text: The title of the chart.
        """
        self._text = text
