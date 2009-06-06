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


class PieChart(chart.Chart):
    """
    A widget that shows a pie chart. The following objects can be accessed:
     - PieChart.background (inherited from chart.Chart)
     - PieChart.title (inherited from chart.Chart)
     - PieChart.data
    """    
    def __init__(self):
        chart.Chart.__init__(self)
        self.data = {}
        self._sum = 0
        self._rotate = 0
        self._show_percentage = True
        self._show_labels = True
        self._show_shadow = True
        
    def _do_draw_shadow(self, context, rect):
        """
        Draw a shadow under the pie.
        
        @type context: cairo.Context
        @param context: The context to draw on.
        @type rect: gtk.gdk.Rectangle
        @param rect: A rectangle representing the charts area.
        """
        (cx, cy) = get_center(rect)
        r = min(cx, cy) * (1 - 1 / 5.0) + 5
        gradient = cairo.RadialGradient(cx, cy, r - 20, cx, cy, r)
        gradient.add_color_stop_rgba(0, 0, 0, 0, 1)
        gradient.add_color_stop_rgba(1, 0, 0, 0, 0)
        context.arc(cx, cy, r, 0, 2 * math.pi)
        context.set_source(gradient)
        context.fill()
        
    def _do_draw(self, context, rect):
        """
        Draw the chart.
        
        @type context: cairo.Context
        @param context: The context to draw on.
        @type rect: gtk.gdk.Rectangle
        @param rect: A rectangle representing the charts area.
        """
        (cx, cy) = get_center(rect)
        r = min(cx, cy) * (1 - 1 / 5.0)
        angle = self._rotate
        for (name, info) in self.data.iteritems():
            c = info["color"]                    
            #draw sector
            sector_angle = 2 * math.pi * info["n"] / self._sum
            context.move_to(cx, cy)
            context.arc(cx, cy, r, angle, angle + sector_angle)
            context.close_path()
            context.set_source_rgb(c[0], c[1], c[2])
            context.fill_preserve()
            context.set_source_rgb(1, 1, 1)
            context.stroke()
            
            #draw label
            if self._show_labels:
                title = info["label"]
                if self._show_percentage:
                    title += " (" + str(round(100 * info["n"] / self._sum, 2)) + "%)"
                half_angle = angle + sector_angle / 2
                size = context.text_extents(title)
                #print name, half_angle, math.pi/2.0
                #x = r * math.cos(half_angle) + cx + size[2] * math.cos(half_angle) - size[2] / 2
                x = r * math.cos(half_angle) + cx + size[2] * math.cos(half_angle) * 4/5 - size[2] / 2
                #y = r * math.sin(half_angle) + cy + size[3] / 2 + size[3] * math.sin(half_angle)
                y = r * math.sin(half_angle) + cy + size[3] / 2 + 1.5 * size[3] * math.sin(half_angle)
                context.move_to(x, y)
                context.set_source_rgb(c[0], c[1], c[2])
                context.show_text(title)
                context.stroke()
            
            angle += sector_angle
        
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
        context.select_font_face(font,cairo.FONT_SLANT_NORMAL, \
                                    cairo.FONT_WEIGHT_NORMAL)
                                    
        self.draw_basics(context, rect)
        if self.data:
            if self._show_shadow:
                self._do_draw_shadow(context, rect)
            self._do_draw(context, rect)
        
    def set_data(self, data):
        """
        Set the data to show in the pie chart. data has to be a list of
        (name, label, n) triples. The name value is an identifier, it should
        be unique. label is the text that will be shown next to the
        corresponding sector. n has to be a positive number.
        
        Example (the population of G8 members, source: wikipedia)::

            population = [("usa", "United States", 303346630),
                            ("d", "Germany", 82244000),
                            ("uk", "United Kingdom", 60587300),
                            ("jap", "Japan", 127417244),
                            ("fr", "France", 64473140),
                            ("i", "Italy", 59619290),
                            ("cdn", "Canada", 32976026),
                            ("rus", "Russia", 142400000)]
            set_data(population)        
        
        @type data: list
        @param data: The data list.
        """
        self.data = {}
        self._sum = 0
        for (name, label, n) in data:
            self.data[name] = {"label": label,
                                "n": float(n),
                                "color": COLORS[len(self.data) % len(COLORS)]}
            self._sum += n
            
    def set_rotate(self, angle):
        """
        By calling set_rotate with an angle as the argument, the pie chart
        will be rotated by this angle. The angle has to be in radians.
        
        @type angle: number
        @param angle: The angle to rotate the pie chart by.
        """
        self._rotate = angle
            
    def set_show_labels(self, show):
        """
        Use set_show_labels() to set whether labels should be shown at the
        edges of the sectors.
        
        @type show: boolean
        @param show: If False, labels won't be shown.
        """
        self._show_labels = show
        
    def set_show_percentage(self, show):
        """
        Use set_show_labels() to set whether percentage labels should be shown
        at the edges of the sectors. The percentage will only be visible
        if the data labels are set visble.
        
        @type show: boolean
        @param show: If False, percentage labels won't be shown.
        """
        self._show_percentage = show
        
    def set_show_shadow(self, show):
        """
        Use set_show_labels() to set whether shadow should be drawn under the
        pie.
        
        @type show: boolean
        @param show: If False, the shadow won't be shown.
        """
        self._show_shadow = show
