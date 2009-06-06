#!/usr/bin/env python
#
#       lineplot.py
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
Contains the LineChart widget.
"""
__docformat__ = "epytext"
import cairo
import gtk
import math

import os

from pygtk_chart.basics import *
from pygtk_chart import chart

RANGE_AUTO = 0
GRAPH_PADDING = 1 / 15.0 #a relative padding
GRAPH_POINTS = 1
GRAPH_LINES = 2
GRAPH_BOTH = 3
COLOR_AUTO = 4
POSITION_AUTO = 5
POSITION_LEFT = 6
POSITION_RIGHT = 7
POSITION_TOP = 8
POSITION_BOTTOM = 9

#load default color palette
COLORS = color_list_from_file(os.path.dirname(__file__) + "/data/tango.color")


class RangeCalculator:
    """
    This helper class calculates ranges. It is used by the LineChart
    widget internally, there is no need to create an instance yourself.
    """
    def __init__(self):
        self._data_xrange = None
        self._data_yrange = None
        self._xrange = RANGE_AUTO
        self._yrange = RANGE_AUTO
        
    def add_graph(self, graph):
        if self._data_xrange == None:
            self._data_yrange = graph.get_y_range()
            self._data_xrange = graph.get_x_range()
        else:
            yrange = graph.get_y_range()
            xrange = graph.get_x_range()
            
            if xrange and yrange:
                xmin = min(xrange[0], self._data_xrange[0])
                xmax = max(xrange[1], self._data_xrange[1])
                ymin = min(yrange[0], self._data_yrange[0])
                ymax = max(yrange[1], self._data_yrange[1])
                
                self._data_xrange = (xmin, xmax)
                self._data_yrange = (ymin, ymax)
            
    def get_ranges(self):
        xrange = self._xrange
        if xrange == RANGE_AUTO:
            xrange = self._data_xrange
            if xrange[0] == xrange[1]:
                xrange = (xrange[0], xrange[0] + 0.1)
            
        yrange = self._yrange
        if yrange == RANGE_AUTO:
            yrange = self._data_yrange
            if yrange[0] == yrange[1]:
                yrange = (yrange[0], yrange[0] + 0.1)
        
        return (xrange, yrange)
        
    def set_xrange(self, xrange):
        self._xrange = xrange
        
    def set_yrange(self, yrange):
        self._yrange = yrange
        
    def get_absolute_zero(self, rect):
        xrange, yrange = self.get_ranges()
            
        xfactor = float(rect.width * (1 - 2 * GRAPH_PADDING)) / (xrange[1] - xrange[0])
        yfactor = float(rect.height * (1 - 2 * GRAPH_PADDING)) / (yrange[1] - yrange[0])
        zx = (rect.width * GRAPH_PADDING) - xrange[0] * xfactor
        zy = rect.height - ((rect.height * GRAPH_PADDING) - yrange[0] * yfactor)
        
        return (zx,zy)
        
    def get_absolute_point(self, rect, x, y):
        (zx, zy) = self.get_absolute_zero(rect)
        xrange, yrange = self.get_ranges()
            
        xfactor = float(rect.width * (1 - 2 * GRAPH_PADDING)) / (xrange[1] - xrange[0])
        yfactor = float(rect.height * (1 - 2 * GRAPH_PADDING)) / (yrange[1] - yrange[0])
        
        ax = zx + x * xfactor
        ay = zy - y * yfactor
        return (ax, ay)
        
    def get_xtics(self, rect):
        tics = []
        (zx, zy) = self.get_absolute_zero(rect)
        (xrange, yrange) = self.get_ranges()
        delta = xrange[1] - xrange[0]
        exp = int(math.log10(delta)) - 1
        
        first_n = int(xrange[0] / (10 ** exp))
        last_n = int(xrange[1] / (10 ** exp))
        n = last_n - first_n
        N = rect.width / 50.0
        divide_by = int(n / N)
        if divide_by == 0: divide_by = 1

        left = rect.width * GRAPH_PADDING
        right = rect.width * (1 - GRAPH_PADDING)

        for i in range(first_n, last_n + 1):
            num = i * 10 ** exp
            (x, y) = self.get_absolute_point(rect, num, 0)
            if i % divide_by == 0 and is_in_range(x, (left, right)):
                tics.append(((x, y), num))
        
        return tics
        
    def get_ytics(self, rect):
        tics = []
        (zx, zy) = self.get_absolute_zero(rect)
        (xrange, yrange) = self.get_ranges()
        delta = yrange[1] - yrange[0]
        exp = int(math.log10(delta)) - 1
        
        first_n = int(yrange[0] / (10 ** exp))
        last_n = int(yrange[1] / (10 ** exp))
        n = last_n - first_n
        N = rect.height / 50.0
        divide_by = int(n / N)
        if divide_by == 0: divide_by = 1
        
        top = rect.height * GRAPH_PADDING
        bottom = rect.height * (1 - GRAPH_PADDING)

        for i in range(first_n, last_n + 1):
            num = i * 10 ** exp
            (x, y) = self.get_absolute_point(rect, 0, num)
            if i % divide_by == 0 and is_in_range(y, (top, bottom)):
                tics.append(((x, y), num))
        
        return tics
        

class LineChart(chart.Chart):
    """
    A widget that shows a line chart. The following objects can be accessed:
     - LineChart.background (inherited from chart.Chart)
     - LineChart.title (inherited from chart.Chart)
     - LineChart.graphs
     - LineChart.grid
     - LineChart.xaxis
     - LineChart.yaxis
    """
    def __init__(self):
        chart.Chart.__init__(self)
        self.graphs = {}
        self._range_calc = RangeCalculator()
        self.xaxis = XAxis(self._range_calc)
        self.yaxis = YAxis(self._range_calc)
        self.grid = Grid(self._range_calc)
        
    def _do_draw_graphs(self, context, rect):
        """
        Draw all the graphs.
        
        @type context: cairo.Context
        @param context: The context to draw on.
        @type rect: gtk.gdk.Rectangle
        @param rect: A rectangle representing the charts area.
        """
        for (name, graph) in self.graphs.iteritems():
            graph.draw(context, rect)
        
    def _do_draw_axes(self, context, rect):
        """
        Draw x and y axis.
        
        @type context: cairo.Context
        @param context: The context to draw on.
        @type rect: gtk.gdk.Rectangle
        @param rect: A rectangle representing the charts area.
        """
        self.xaxis.draw(context, rect, self.yaxis)
        self.yaxis.draw(context, rect, self.xaxis)
        
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
        data_available = False
        for (name, graph) in self.graphs.iteritems():
            if graph.has_something_to_draw():
                data_available = True
                break
                
        if self.graphs and data_available:
            self.grid.draw(context, rect)
            self._do_draw_graphs(context, rect)
            self._do_draw_axes(context, rect)
        
    def add_graph(self, graph):
        """
        Add a graph object to the plot.
        
        @type graph: line_chart.Graph
        @param graph: The graph to add.
        """
        if graph.get_color() == COLOR_AUTO:
            graph.set_color(COLORS[len(self.graphs) % len(COLORS)])
        graph.set_range_calc(self._range_calc)
        self.graphs[graph.get_name()] = graph
        self._range_calc.add_graph(graph)
        
    def remove_graph(self, name):
        """
        Remove a graph from the plot.
        
        @type name: string
        @param name: The name of the graph to remove.
        """
        del self.graphs[name]
        self.queue_draw()
        
    def set_xrange(self, xrange):
        """
        Set the visible xrange. xrange has to be a pair: (xmin, xmax) or
        RANGE_AUTO. If you set it to RANGE_AUTO, the visible range will
        be calculated.
        
        @type xrange: pair of numbers
        @param xrange: The new xrange.
        """
        self._range_calc.set_xrange(xrange)
        
    def set_yrange(self, yrange):
        """
        Set the visible yrange. yrange has to be a pair: (ymin, ymax) or
        RANGE_AUTO. If you set it to RANGE_AUTO, the visible range will
        be calculated.
        
        @type yrange: pair of numbers
        @param yrange: The new yrange.
        """
        self._range_calc.set_yrange(yrange)

        
class XAxis(chart.ChartObject):
    """
    This class represents the xaxis. It is used by the LineChart
    widget internally, there is no need to create an instance yourself.
    """
    def __init__(self, range_calc):
        chart.ChartObject.__init__(self)
        self._range_calc = range_calc
        self._antialias = False
        self._show_tics = True
        self._show_tic_labels = True
        self._show_label = True
        self._label = "x"
        self.tic_format_function = str
        self._position = POSITION_AUTO
        
    def draw(self, context, rect, yaxis):
        """
        This method is called by the parent Plot instance. It
        calls _do_draw.
        """
        if self._show:
            if not self._antialias:
                context.set_antialias(cairo.ANTIALIAS_NONE)
            self._do_draw(context, rect, yaxis)
            context.set_antialias(cairo.ANTIALIAS_DEFAULT)
        
    def _do_draw_tics(self, context, rect, yaxis):
        if self._show_tics:
            tics = self._range_calc.get_xtics(rect)
            
            #select font size
            font_size = rect.height / 50
            if font_size < 9: font_size = 9
            context.set_font_size(font_size)
                                        
            for ((x,y), label) in tics:
                if self._position == POSITION_TOP:
                    y = rect.height * GRAPH_PADDING
                elif self._position == POSITION_BOTTOM:
                    y = rect.height * (1 - GRAPH_PADDING)
                tic_height = rect.height / 80.0
                context.move_to(x, y + tic_height / 2)
                context.rel_line_to(0, - tic_height)
                context.stroke()
                
                if self._show_tic_labels:
                    if label == 0 and self._position == POSITION_AUTO and yaxis.get_position() == POSITION_AUTO:
                        label = " "
                    else:
                        label = self.tic_format_function(label)
                    size = context.text_extents(label)
                    x = x - size[2] / 2
                    y = y + size[3] + font_size / 2
                    if self._position == POSITION_TOP:
                        y = y - size[3] - font_size / 2 - tic_height
                    if label[0] == "-":
                        x = x - context.text_extents("-")[2]
                    context.move_to(x, y)
                    context.show_text(label)
                    context.stroke()
                    
    def _do_draw_label(self, context, rect, pos):
        (x, y) = pos
        font_size = rect.height / 50
        if font_size < 9: font_size = 9
        context.set_font_size(font_size)
        size = context.text_extents(self._label)
        x = x + size[2] / 2
        y = y + size[3]
        
        context.move_to(x, y)
        context.show_text(self._label)
        context.stroke()
        
    def _do_draw(self, context, rect, yaxis):
        """
        Draw the axis.
        """
        (zx, zy) = self._range_calc.get_absolute_zero(rect)
        if self._position == POSITION_BOTTOM:
            zy = rect.height * (1 - GRAPH_PADDING)
        elif self._position == POSITION_TOP:
            zy = rect.height * GRAPH_PADDING
        if rect.height * GRAPH_PADDING <= zy and rect.height * (1 - GRAPH_PADDING) >= zy:
            context.set_source_rgb(0, 0, 0)
            #draw the line:
            context.move_to(rect.width * GRAPH_PADDING, zy)
            context.line_to(rect.width * (1 - GRAPH_PADDING), zy)
            context.stroke()
            #draw arrow:
            context.move_to(rect.width * (1 - GRAPH_PADDING) + 3, zy)
            context.rel_line_to(-3, -3)
            context.rel_line_to(0, 6)
            context.close_path()
            context.fill()
            
            if self._show_label:
                self._do_draw_label(context, rect, (rect.width * (1 - GRAPH_PADDING) + 3, zy))
            self._do_draw_tics(context, rect, yaxis)
        
    def set_show_tics(self, show):
        """
        If show is True, xtics are drawn.
        """
        self._show_tics = show
        
    def set_show_tic_labels(self, show):
        """
        If show is True, labels are drawn at the xtics.
        """
        self._show_tic_labels = show
        
    def set_show_label(self, show):
        """
        If show is True, a label is drawn at the left end of the axis.
        """
        self._show_label = show
        
    def set_position(self, pos):
        """
        Set the position of the xaxis to pos. Possible values are:
        POSITION_AUTO, POSITION_TOP, POSITION_BOTTOM
        """
        self._position = pos
        
    def get_position(self):
        return self._position
        
        
class YAxis(chart.ChartObject):
    """
    This class represents the yaxis. It is used by the LineChart
    widget internally, there is no need to create an instance yourself.
    """
    def __init__(self, range_calc):
        chart.ChartObject.__init__(self)
        self._range_calc = range_calc
        self._antialias = False
        self._show_tics = True
        self._show_tic_labels = True
        self._show_label = True
        self._label = "y"
        self.tic_format_function = str
        self._position = POSITION_AUTO
        
    def draw(self, context, rect, xaxis):
        """
        This method is called by the parent Plot instance. It
        calls _do_draw.
        """
        if self._show:
            if not self._antialias:
                context.set_antialias(cairo.ANTIALIAS_NONE)
            self._do_draw(context, rect, xaxis)
            context.set_antialias(cairo.ANTIALIAS_DEFAULT)
        
    def _do_draw_tics(self, context, rect, xaxis):
        if self._show_tics:
            tics = self._range_calc.get_ytics(rect)
            
            #select font size
            font_size = rect.height / 50
            #if font_size < 9: font_size = 9
            context.set_font_size(font_size)
            
            for ((x,y), label) in tics:
                if self._position == POSITION_LEFT:
                    x = rect.width * GRAPH_PADDING
                elif self._position == POSITION_RIGHT:
                    x = rect.width * (1 - GRAPH_PADDING)
                tic_width = rect.height / 80.0
                context.move_to(x + tic_width / 2, y)
                context.rel_line_to(- tic_width, 0)
                context.stroke()
                
                if self._show_tic_labels:
                    if label == 0 and self._position == POSITION_AUTO and xaxis.get_position() == POSITION_AUTO:
                        label = " "
                    else:
                        label = self.tic_format_function(label)
                    size = context.text_extents(label)
                    x = x - size[2] - font_size / 2
                    if self._position == POSITION_RIGHT:
                        x = x + size[2] + font_size / 2 + tic_width
                    y = y + size[3] / 2
                    if label[0] == "-":
                        x = x - context.text_extents("-")[2]
                    context.move_to(x, y)
                    context.show_text(label)
                    context.stroke()
                    
    def _do_draw_label(self, context, rect, pos):
        (x, y) = pos
        font_size = rect.height / 50
        if font_size < 9: font_size = 9
        context.set_font_size(font_size)
        size = context.text_extents(self._label)
        x = x - size[2]
        y = y - size[3] / 2
        
        context.move_to(x, y)
        context.show_text(self._label)
        context.stroke()
        
    def _do_draw(self, context, rect, xaxis):
        (zx, zy) = self._range_calc.get_absolute_zero(rect)
        if self._position == POSITION_LEFT:
            zx = rect.width * GRAPH_PADDING
        elif self._position == POSITION_RIGHT:
            zx = rect.width * (1 - GRAPH_PADDING)
        if rect.width * GRAPH_PADDING <= zx and rect.width * (1 - GRAPH_PADDING) >= zx:
            context.set_source_rgb(0, 0, 0)
            #draw line:
            context.move_to(zx, rect.height * (1 - GRAPH_PADDING))
            context.line_to(zx, rect.height * GRAPH_PADDING)
            context.stroke()
            #draw arrow:
            context.move_to(zx, rect.height * GRAPH_PADDING - 3)
            context.rel_line_to(-3, 3)
            context.rel_line_to(6, 0)
            context.close_path()
            context.fill()
            
            if self._show_label:
                self._do_draw_label(context, rect, (zx, rect.height * GRAPH_PADDING - 3))
            self._do_draw_tics(context, rect, xaxis)
            
    def set_show_tics(self, show):
        """
        If show is True, ytics are drawn.
        """
        self._show_tics = show
        
    def set_show_tic_labels(self, show):
        """
        If show is True, labels are drawn at the ytics.
        """
        self._show_tic_labels = show
        
    def set_show_label(self, show):
        """
        If show is True, a label is drawn at the top end of the axis.
        """
        self._show_label = show
        
    def set_position(self, pos):
        """
        Set the position of the xaxis to pos. Possible values are:
        POSITION_AUTO, POSITION_LEFT, POSITION_RIGHT
        """
        self._position = pos
        
    def get_position(self):
        return self._position
        
        
class Grid(chart.ChartObject):
    """
    A class representing the grid of the chart. It is used by the LineChart
    widget internally, there is no need to create an instance yourself.
    """
    def __init__(self, range_calc):
        chart.ChartObject.__init__(self)
        self._range_calc = range_calc
        self._color = (0.9, 0.9, 0.9)
        self._show = (True, True)
        self._antialias = False
        
    def _do_draw(self, context, rect):
        c = self._color
        context.set_source_rgb(c[0], c[1], c[2])
        #draw horizontal lines
        if self._show[0]:
            ytics = self._range_calc.get_ytics(rect)
            xa = rect.width * GRAPH_PADDING
            xb = rect.width * (1 - GRAPH_PADDING)
            for ((x, y), label) in ytics:
                context.move_to(xa, y)
                context.line_to(xb, y)
                context.stroke()
                
        #draw vertical lines
        if self._show[1]:
            xtics = self._range_calc.get_xtics(rect)
            ya = rect.height * GRAPH_PADDING
            yb = rect.height * (1 - GRAPH_PADDING)
            for ((x, y), label) in xtics:
                context.move_to(x, ya)
                context.line_to(x, yb)
                context.stroke()
                
    def set_visible(self, h, v):
        """
        Set which grid lines to draw.
        
        @type h: boolean
        @param h: If this is True horizontal grid lines will be drawn.
        @type v: boolean
        @param v: If this is True vertical grid lines will be drawn.
        """
        self._show = (h, v)
        
    def set_color(self, color):
        """
        Set the color of the grid.
        
        @type color: a color
        @param color: The new color of the grid.
        """
        self._color = color
        
        
class Graph(chart.ChartObject):
    """
    This class represents a graph or the data you want to plot on your
    LineChart widget.
    """
    def __init__(self, name, title, data):
        """
        Create a new instance.
        
        @type name: string
        @param name: A unique name for the graph. This could be everything.
        It's just a name used internally for identification. You need to know
        this if you want to access or delete a graph from a chart.
        @type title: string
        @param title: The graphs title. This can be drawn on the chart.
        @type data: list of pairs of numbers
        @param data: This is the data you want to be visualized. data has to
        be a list of (x, y) pairs.
        """
        chart.ChartObject.__init__(self)
        self._name = name
        self._title = title
        self._data = data
        self._color = COLOR_AUTO
        self._range_calc = None
        self._type = GRAPH_BOTH
        self._point_size = 2
        self._fill_xaxis = False
        
    def has_something_to_draw(self):
        return self._data != []
        
    def _do_draw_title(self, context, rect, last_point):
        """
        Draws the title.
        
        @type context: cairo.Context
        @param context: The context to draw on.
        @type rect: gtk.gdk.Rectangle
        @param rect: A rectangle representing the charts area.
        @type last_point: pairs of numbers
        @param last_point: The absolute position of the last drawn data point.
        """
        c = self._color
        context.set_source_rgb(c[0], c[1], c[2])
        
        font_size = rect.height / 50
        if font_size < 9: font_size = 9
        context.set_font_size(font_size)
        size = context.text_extents(self._title)
        if last_point:
            context.move_to(last_point[0] + 5, last_point[1] + size[3] / 3)
            context.show_text(self._title)
            context.stroke()
        
    def _do_draw(self, context, rect):
        """
        Draw the graph.
        
        @type context: cairo.Context
        @param context: The context to draw on.
        @type rect: gtk.gdk.Rectangle
        @param rect: A rectangle representing the charts area.
        """
        #self._data.sort(lambda x, y: cmp(x[0], y[0]))
        (xrange, yrange) = self._range_calc.get_ranges()
        c = self._color
        context.set_source_rgb(c[0], c[1], c[2])
        previous = None #previous is set to None if a point is not in range
        last = None #last will not be set to None in this case
        for (x, y) in self._data:
            if is_in_range(x, xrange) and is_in_range(y, yrange):
                (ax, ay) = self._range_calc.get_absolute_point(rect, x, y)
                if self._type == GRAPH_POINTS or self._type == GRAPH_BOTH:
                    context.arc(ax, ay, self._point_size, 0, 2 * math.pi)
                    context.fill()
                    context.move_to(ax+2*self._point_size,ay)
                    context.show_text(str(y))
                if self._type == GRAPH_LINES or self._type == GRAPH_BOTH:
                    if previous != None:
                        context.move_to(previous[0], previous[1])
                        context.line_to(ax, ay)
                        context.stroke()
                previous = (ax, ay)
                last = (ax, ay)
            else:
                previous = None
                
        if self._fill_xaxis:
            #fill the space between the graph and the xaxis with the graph's
            #color (alpha = 0.3)
            context.set_source_rgba(c[0], c[1], c[2], 0.3)
            first = True
            (zx, zy) = self._range_calc.get_absolute_zero(rect)
            for (x, y) in self._data:
                if is_in_range(x, xrange) and is_in_range(y, yrange):
                    (ax, ay) = self._range_calc.get_absolute_point(rect, x, y)
                    if first:
                        context.move_to(ax, zy)
                        first = False
                    context.line_to(ax, ay)
            if not first:
                context.line_to(ax, zy)
                context.fill()
        self._do_draw_title(context, rect, last)
        
    def get_x_range(self):
        """
        Get the the endpoints of the x interval.
        
        @return: pair of numbers
        """
        try:
            self._data.sort(lambda x, y: cmp(x[0], y[0]))
            return (self._data[0][0], self._data[-1][0])
        except:
            return None
        
    def get_y_range(self):
        """
        Get the the endpoints of the y interval.
        
        @return: pair of numbers
        """
        try:
            self._data.sort(lambda x, y: cmp(x[1], y[1]))
            return (self._data[0][1], self._data[-1][1])
        except:
            return None
        
    def get_name(self):
        """
        Get the name of the graph.
        
        @return: string
        """
        return self._name
        
    def set_range_calc(self, range_calc):
        self._range_calc = range_calc
        
    def get_color(self):
        """
        Returns the current color of the graph or COLOR_AUTO.
        """
        return self._color
        
    def set_color(self, color):
        """
        Set the color of the graph. color has to be a (r, g, b) triple
        where r, g, b are between 0 and 1.
        If set to COLOR_AUTO, the color will be choosen dynamicly.
        
        @type color: a color
        @param color: The new color of the graph.
        """
        self._color = color
        
    def set_type(self, type):
        """
        Set the type of the graph to one of these:
         - GRAPH_POINTS: only show points
         - GRAPH_LINES: only draw lines
         - GRAPH_BOTH: draw points and lines, i.e. connect points with lines
        
        @param type: One of the constants above.
        """
        self._type = type
        
    def set_point_size(self, size):
        """
        Set the radius of the drawn points.
        
        @type size: a positive number
        @param size: The new radius of the points.
        """
        self._point_size = size
        
    def set_fill_xaxis(self, fill):
        """
        Use set_fill_xaxis() to set whether the area between the graph should
        be filled with the graphs color (30% opacity) or not.
        
        @type fill: boolean
        """
        self._fill_xaxis = fill
        
    def add_data(self, data_list):
        """
        Add data to the graph.
        
        @type data_list: a list of pairs of numbers
        """
        self._data += data_list
        self._range_calc.add_graph(self)
