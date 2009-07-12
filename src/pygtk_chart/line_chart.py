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

Author: Sven Festersen (sven@sven-festersen.de)
"""
__docformat__ = "epytext"
import gobject
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
POSITION_BOTTOM = 6
POSITION_TOP = 7

#load default color palette
COLORS = color_list_from_file(os.sep.join([os.path.dirname(__file__), "data", "tango.color"]))


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
        self._cached_xtics = []
        self._cached_ytics = []

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

    def prepare_tics(self, rect):
        self._cached_xtics = self._get_xtics(rect)
        self._cached_ytics = self._get_ytics(rect)

    def get_xtics(self, rect):
        return self._cached_xtics

    def get_ytics(self, rect):
        return self._cached_ytics

    def _get_xtics(self, rect):
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

    def _get_ytics(self, rect):
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

        self.xaxis.connect("appearance_changed", self._cb_appearance_changed)
        self.yaxis.connect("appearance_changed", self._cb_appearance_changed)
        self.grid.connect("appearance_changed", self._cb_appearance_changed)

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
        self._range_calc.prepare_tics(rect)
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

        graph.connect("appearance-changed", self._cb_appearance_changed)

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


class Axis(chart.ChartObject):

    __gproperties__ = {"label": (gobject.TYPE_STRING, "axis label",
                                    "The label of the axis.", "",
                                    gobject.PARAM_READWRITE),
                        "show-label": (gobject.TYPE_BOOLEAN, "show label",
                                    "Set whether to show the axis label.",
                                    True, gobject.PARAM_READWRITE),
                        "position": (gobject.TYPE_INT, "axis position",
                                    "Position of the axis.", 5, 7, 5,
                                    gobject.PARAM_READWRITE),
                        "show-tics": (gobject.TYPE_BOOLEAN, "show tics",
                                    "Set whether to draw tics.", True,
                                    gobject.PARAM_READWRITE),
                        "show-tic-labels": (gobject.TYPE_BOOLEAN,
                                            "show tic labels",
                                            "Set whether to draw tic labels",
                                            True,
                                            gobject.PARAM_READWRITE),
                        "tic-format-function": (gobject.TYPE_PYOBJECT,
                                            "tic format function",
                                            "This function is used to label the tics.",
                                            gobject.PARAM_READWRITE)}

    def __init__(self, range_calc, label):
        chart.ChartObject.__init__(self)
        self.set_property("antialias", False)

        self._label = label
        self._show_label = True
        self._position = POSITION_AUTO
        self._show_tics = True
        self._show_tic_labels = True
        self._tic_format_function = str

        self._range_calc = range_calc

    def do_get_property(self, property):
        if property.name == "visible":
            return self._show
        elif property.name == "antialias":
            return self._antialias
        elif property.name == "label":
            return self._label
        elif property.name == "show-label":
            return self._show_label
        elif property.name == "position":
            return self._position
        elif property.name == "show-tics":
            return self._show_tics
        elif property.name == "show-tic-labels":
            return self._show_tic_labels
        elif property.name == "tic-format-function":
            return self._tic_format_function
        else:
            raise AttributeError, "Property %s does not exist." % property.name

    def do_set_property(self, property, value):
        if property.name == "visible":
            self._show = value
        elif property.name == "antialias":
            self._antialias = value
        elif property.name == "label":
            self._label = value
        elif property.name == "show-label":
            self._show_label = value
        elif property.name == "position":
            self._position = value
        elif property.name == "show-tics":
            self._show_tics = value
        elif property.name == "show-tic-labels":
            self._show_tic_labels = value
        elif property.name == "tic-format-function":
            self._tic_format_function = value
        else:
            raise AttributeError, "Property %s does not exist." % property.name

    def set_label(self, label):
        """
        Set the label of the axis.

        @param label: new label
        @type label: string.
        """
        self.set_property("label", label)
        self.emit("appearance_changed")

    def get_label(self):
        """
        Returns the current label of the axis.

        @return: string.
        """
        return self.get_property("label")

    def set_show_label(self, show):
        """
        Set whether to show the axis' label.

        @type show: boolean.
        """
        self.set_property("show-label", show)
        self.emit("appearance_changed")

    def get_show_label(self):
        """
        Returns True if the axis' label is shown.

        @return: boolean.
        """
        return self.get_property("show-label")

    def set_position(self, pos):
        """
        Set the position of the axis. pos hast to be one these
        constants: POSITION_AUTO, POSITION_BOTTOM, POSITION_LEFT,
        POSITION_RIGHT, POSITION_TOP.
        """
        self.set_property("position", pos)
        self.emit("appearance_changed")

    def get_position(self):
        """
        Returns the position of the axis. (see set_position for
        details).
        """
        return self.get_property("position")

    def set_show_tics(self, show):
        """
        Set whether to draw tics at the axis.

        @type show: boolean.
        """
        self.set_property("show-tics", show)
        self.emit("appearance_changed")

    def get_show_tics(self):
        """
        Returns True if tics are drawn.

        @return: boolean.
        """
        return self.get_property("show-tics")

    def set_show_tic_labels(self, show):
        """
        Set whether to draw tic labels. Labels are only drawn if
        tics are drawn.

        @type show: boolean.
        """
        self.set_property("show-tic-labels", show)
        self.emit("appearance_changed")

    def get_show_tic_labels(self):
        """
        Returns True if tic labels are shown.

        @return: boolean.
        """
        return self.get_property("show-tic-labels")

    def set_tic_format_function(self, func):
        """
        Use this to set the function that should be used to label
        the tics. The function should take a number as the only
        argument and return a string. Default: str

        @type func: function.
        """
        self.set_property("tic-format-function", func)
        self.emit("appearance_changed")

    def get_tic_format_function(self):
        """
        Returns the function currently used for labeling the tics.
        """
        return self.get_property("tic-format-function")


class XAxis(Axis):
    """
    This class represents the xaxis. It is used by the LineChart
    widget internally, there is no need to create an instance yourself.
    """
    def __init__(self, range_calc):
        Axis.__init__(self, range_calc, "x")

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
                        label = self._tic_format_function(label)
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


class YAxis(Axis):
    """
    This class represents the yaxis. It is used by the LineChart
    widget internally, there is no need to create an instance yourself.
    """
    def __init__(self, range_calc):
        Axis.__init__(self, range_calc, "y")

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
                        label = self._tic_format_function(label)
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


class Grid(chart.ChartObject):
    """
    A class representing the grid of the chart. It is used by the LineChart
    widget internally, there is no need to create an instance yourself.
    """

    __gproperties__ = {"show-horizontal": (gobject.TYPE_BOOLEAN,
                                    "show horizontal lines",
                                    "Set whether to draw horizontal lines.",
                                    True, gobject.PARAM_READWRITE),
                        "show-vertical": (gobject.TYPE_BOOLEAN,
                                    "show vertical lines",
                                    "Set whether to draw vertical lines.",
                                    True, gobject.PARAM_READWRITE),
                        "color": (gobject.TYPE_PYOBJECT,
                                    "grid color",
                                    "The color of the grid in (r,g,b) format. r,g,b in [0,1]",
                                    gobject.PARAM_READWRITE)}

    def __init__(self, range_calc):
        chart.ChartObject.__init__(self)
        self.set_property("antialias", False)
        self._range_calc = range_calc
        self._color = (0.9, 0.9, 0.9)
        self._show_h = True
        self._show_v = True

    def do_get_property(self, property):
        if property.name == "visible":
            return self._show
        elif property.name == "antialias":
            return self._antialias
        elif property.name == "show-horizontal":
            return self._show_h
        elif property.name == "show-vertical":
            return self._show_v
        elif property.name == "color":
            return self._color
        else:
            raise AttributeError, "Property %s does not exist." % property.name

    def do_set_property(self, property, value):
        if property.name == "visible":
            self._show = value
        elif property.name == "antialias":
            self._antialias = value
        elif property.name == "show-horizontal":
            self._show_h = value
        elif property.name == "show-vertical":
            self._show_v = value
        elif property.name == "color":
            self._color = value
        else:
            raise AttributeError, "Property %s does not exist." % property.name

    def _do_draw(self, context, rect):
        c = self._color
        context.set_source_rgb(c[0], c[1], c[2])
        #draw horizontal lines
        if self._show_h:
            ytics = self._range_calc.get_ytics(rect)
            xa = rect.width * GRAPH_PADDING
            xb = rect.width * (1 - GRAPH_PADDING)
            for ((x, y), label) in ytics:
                context.move_to(xa, y)
                context.line_to(xb, y)
                context.stroke()

        #draw vertical lines
        if self._show_v:
            xtics = self._range_calc.get_xtics(rect)
            ya = rect.height * GRAPH_PADDING
            yb = rect.height * (1 - GRAPH_PADDING)
            for ((x, y), label) in xtics:
                context.move_to(x, ya)
                context.line_to(x, yb)
                context.stroke()

    def set_draw_horizontal_lines(self, draw):
        """
        Set whether to draw horizontal grid lines.

        @type draw: boolean.
        """
        self.set_property("show-horizontal", draw)
        self.emit("appearance_changed")

    def get_draw_horizontal_lines(self):
        """
        Returns True if horizontal grid lines are drawn.

        @return: boolean.
        """
        return self.get_property("show-horizontal")

    def set_draw_vertical_lines(self, draw):
        """
        Set whether to draw vertical grid lines.

        @type draw: boolean.
        """
        self.set_property("show-vertical", draw)
        self.emit("appearance_changed")

    def get_draw_vertical_lines(self):
        """
        Returns True if vertical grid lines are drawn.

        @return: boolean.
        """
        return self.get_property("show-vertical")

    def set_color(self, color):
        """
        Set the color of the grid.

        @type color: a color
        @param color: The new color of the grid.
        """
        self.set_property("color", color)
        self.emit("appearance_changed")

    def get_color(self):
        """
        Returns the color of the grid.

        @return: a color.
        """
        return self.get_property("color")


class Graph(chart.ChartObject):
    """
    This class represents a graph or the data you want to plot on your
    LineChart widget.
    """

    __gproperties__ = {"name": (gobject.TYPE_STRING, "graph id",
                                "The graph's unique name.",
                                "", gobject.PARAM_READABLE),
                        "title": (gobject.TYPE_STRING, "graph title",
                                    "The title of the graph.", "",
                                    gobject.PARAM_READWRITE),
                        "color": (gobject.TYPE_PYOBJECT,
                                    "graph color",
                                    "The color of the graph in (r,g,b) format. r,g,b in [0,1].",
                                    gobject.PARAM_READWRITE),
                        "type": (gobject.TYPE_INT, "graph type",
                                    "The type of the graph.", 1, 3, 3,
                                    gobject.PARAM_READWRITE),
                        "point-size": (gobject.TYPE_INT, "point size",
                                        "Radius of the data points.", 1,
                                        100, 2, gobject.PARAM_READWRITE),
                        "fill-to": (gobject.TYPE_PYOBJECT, "fill to",
                                    "Set how to fill space under the graph.",
                                    gobject.PARAM_READWRITE),
                        "fill-color": (gobject.TYPE_PYOBJECT, "fill color",
                                    "Set which color to use when filling space under the graph.",
                                    gobject.PARAM_READWRITE),
                        "fill-opacity": (gobject.TYPE_FLOAT, "fill opacity",
                                    "Set which opacity to use when filling space under the graph.",
                                    0.0, 1.0, 0.3, gobject.PARAM_READWRITE),
                        "show-values": (gobject.TYPE_BOOLEAN, "show values",
                                    "Sets whether to show the y values.",
                                    False, gobject.PARAM_READWRITE),
                        "show-title": (gobject.TYPE_BOOLEAN, "show title",
                                    "Sets whether to show the graph's title.",
                                    True, gobject.PARAM_READWRITE)}

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
        self._type = GRAPH_BOTH
        self._point_size = 2
        self._show_value = False
        self._show_title = True
        self._fill_to = None
        self._fill_color = COLOR_AUTO
        self._fill_opacity = 0.3

        self._range_calc = None

    def do_get_property(self, property):
        if property.name == "visible":
            return self._show
        elif property.name == "antialias":
            return self._antialias
        elif property.name == "name":
            return self._name
        elif property.name == "title":
            return self._title
        elif property.name == "color":
            return self._color
        elif property.name == "type":
            return self._type
        elif property.name == "point-size":
            return self._point_size
        elif property.name == "fill-to":
            return self._fill_to
        elif property.name == "fill-color":
            return self._fill_color
        elif property.name == "fill-opacity":
            return self._fill_opacity
        elif property.name == "show-values":
            return self._show_value
        elif property.name == "show-title":
            return self._show_title
        else:
            raise AttributeError, "Property %s does not exist." % property.name

    def do_set_property(self, property, value):
        if property.name == "visible":
            self._show = value
        elif property.name == "antialias":
            self._antialias = value
        elif property.name == "title":
            self._title = value
        elif property.name == "color":
            self._color = value
        elif property.name == "type":
            self._type = value
        elif property.name == "point-size":
            self._point_size = value
        elif property.name == "fill-to":
            self._fill_to = value
        elif property.name == "fill-color":
            self._fill_color = value
        elif property.name == "fill-opacity":
            self._fill_opacity = value
        elif property.name == "show-values":
            self._show_value = value
        elif property.name == "show-title":
            self._show_title = value
        else:
            raise AttributeError, "Property %s does not exist." % property.name

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
            
    def _do_draw_fill(self, context, rect, xrange):
        if type(self._fill_to) in (int, float):
            data = []
            for i, (x, y) in enumerate(self._data):
                if is_in_range(x, xrange) and not data:
                    data.append((x, self._fill_to))
                elif not is_in_range(x, xrange) and len(data) == 1:
                    data.append((prev, self._fill_to))
                    break
                elif i == len(self._data) - 1:
                    data.append((x, self._fill_to))
                prev = x
            graph = Graph("none", "", data)
        elif type(self._fill_to) == Graph:
            graph = self._fill_to
            d = graph.get_data()
            range_b = d[0][0], d[-1][0]
            xrange = intersect_ranges(xrange, range_b)
            
        if not graph.get_visible(): return
        
        c = self._fill_color
        if c == COLOR_AUTO: c = self._color
        context.set_source_rgba(c[0], c[1], c[2], self._fill_opacity)
        
        data_a = self._data
        data_b = graph.get_data()
        
        first = True
        start_point = (0, 0)
        for x, y in data_a:
            if is_in_range(x, xrange):
                xa, ya = self._range_calc.get_absolute_point(rect, x, y)
                if first:
                    context.move_to(xa, ya)
                    start_point = xa, ya
                    first = False
                else:
                    context.line_to(xa, ya)
                
        first = True
        for i in range(0, len(data_b)):
            j = len(data_b) - i - 1
            x, y = data_b[j]
            xa, ya = self._range_calc.get_absolute_point(rect, x, y)
            if is_in_range(x, xrange):
                context.line_to(xa, ya)
        context.line_to(*start_point)
        context.fill()

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
                    if self._show_value:
                        font_size = rect.height / 50
                        if font_size < 9: font_size = 9
                        context.set_font_size(font_size)
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

        if self._fill_to != None:
            self._do_draw_fill(context, rect, xrange)

        if self._show_title:
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
        return self.get_property("name")

    def get_title(self):
        """
        Returns the title of the graph.

        @return: string
        """
        return self.get_property("title")

    def set_title(self, title):
        """
        Set the title of the graph.

        @type title: string
        @param title: The graph's new title.
        """
        self.set_property("title", title)
        self.emit("appearance_changed")

    def set_range_calc(self, range_calc):
        self._range_calc = range_calc

    def get_color(self):
        """
        Returns the current color of the graph or COLOR_AUTO.

        @return: a color (see set_color() for details).
        """
        return self.get_property("color")

    def set_color(self, color):
        """
        Set the color of the graph. color has to be a (r, g, b) triple
        where r, g, b are between 0 and 1.
        If set to COLOR_AUTO, the color will be choosen dynamicly.

        @type color: a color
        @param color: The new color of the graph.
        """
        self.set_property("color", color)
        self.emit("appearance_changed")

    def get_type(self):
        """
        Returns the type of the graph.

        @return: a type constant (see set_type() for details)
        """
        return self.get_property("type")

    def set_type(self, type):
        """
        Set the type of the graph to one of these:
         - GRAPH_POINTS: only show points
         - GRAPH_LINES: only draw lines
         - GRAPH_BOTH: draw points and lines, i.e. connect points with lines

        @param type: One of the constants above.
        """
        self.set_property("type", type)
        self.emit("appearance_changed")

    def get_point_size(self):
        """
        Returns the radius of the data points.

        @return: a poisitive integer
        """
        return self.get_property("point_size")

    def set_point_size(self, size):
        """
        Set the radius of the drawn points.

        @type size: a positive integer in [1, 100]
        @param size: The new radius of the points.
        """
        self.set_property("point_size", size)
        self.emit("appearance_changed")

    def get_fill_to(self):
        """
        The return value of this method depends on the filling under
        the graph. See set_fill_to() for details.
        """
        return self.get_property("fill-to")

    def set_fill_to(self, fill_to):
        """
        Use this method to specify how the space under the graph should
        be filled. fill_to has to be one of these:
        
         - None: dont't fill the space under the graph.
         - int or float: fill the space to the value specified (setting
           fill_to=0 means filling the space between graph and xaxis).
         - a Graph object: fill the space between this graph and the
           graph given as the argument.
           
        The color of the filling is the graph's color with 30% opacity.
           
        @type fill_to: one of the possibilities listed above.
        """
        self.set_property("fill-to", fill_to)
        self.emit("appearance_changed")
        
    def get_fill_color(self):
        """
        Returns the color that is used to fill space under the graph
        or COLOR_AUTO.
        """
        return self.get_property("fill-color")
        
    def set_fill_color(self, color):
        """
        Set which color should be used when filling the space under a
        graph.
        If color is COLOR_AUTO, the graph's color will be used.
        
        @type color: a color or COLOR_AUTO.
        """
        self.set_property("fill-color", color)
        self.emit("appearance_changed")
        
    def get_fill_opacity(self):
        """
        Returns the opacity that is used to fill space under the graph.
        """
        return self.get_property("fill-opacity")
        
    def set_fill_opacity(self, opacity):
        """
        Set which opacity should be used when filling the space under a
        graph. The default is 0.3.
        
        @type opacity: float in [0, 1].
        """
        self.set_property("fill-opacity", opacity)
        self.emit("appearance_changed")

    def get_show_values(self):
        """
        Returns True if y values are shown.

        @return: boolean
        """
        return self.get_property("show-values")

    def set_show_values(self, show):
        """
        Set whether the y values should be shown (only if graph type
        is GRAPH_POINTS or GRAPH_BOTH).

        @type show: boolean
        """
        self.set_property("show-values", show)
        self.emit("appearance_changed")

    def get_show_title(self):
        """
        Returns True if the title of the graph is shown.

        @return: boolean.
        """
        return self.get_property("show-title")

    def set_show_title(self, show):
        """
        Set whether to show the graph's title or not.

        @type show: boolean.
        """
        self.set_property("show-title", show)
        self.emit("appearance_changed")

    def add_data(self, data_list):
        """
        Add data to the graph.

        @type data_list: a list of pairs of numbers
        """
        self._data += data_list
        self._range_calc.add_graph(self)
        
    def get_data(self):
        """
        Returns the data of the graph.
        
        @return: a list of x, y pairs.
        """
        return self._data
        
        
def graph_new_from_function(func, xmin, xmax, graph_name, samples=100, do_optimize_sampling=True):
    """
    Returns a line_chart.Graph with data created from the function
    y = func(x) with x in [xmin, xmax]. The id of the new graph is
    graph_name.
    The parameter samples gives the number of points that should be
    evaluated in [xmin, xmax] (default: 100).
    If do_optimize_sampling is True (default) additional points will be
    evaluated to smoothen the curve.
    
    @type func: a function
    @param func: the function to evaluate
    @type xmin: float
    @param xmin: the minimum x value to evaluate
    @type xmax: float
    @param xmax: the maximum x value to evaluate
    @type graph_name: string
    @param graph_name: a unique name for the new graph
    @type samples: int
    @param samples: number of samples
    @type do_optimize_sampling: boolean
    @param do_optimize_sampling: set whether to add additional points
    
    @return: line_chart.Graph    
    """
    delta = (xmax - xmin) / float(samples)
    data = []
    x = xmin
    while x <= xmax:
        data.append((x, func(x)))
        x += delta
        
    if do_optimize_sampling:
        data = optimize_sampling(func, data)
        
    return Graph(graph_name, "", data)
    
def optimize_sampling(func, data):
    new_data = []
    prev_point = None
    prev_slope = None
    for x, y in data:
        if prev_point != None:
            if (x - prev_point[0]) == 0: return data
            slope = (y - prev_point[1]) / (x - prev_point[0])
            if prev_slope != None:
                if abs(slope - prev_slope) >= 0.1:
                    nx = prev_point[0] + (x - prev_point[0]) / 2.0
                    ny = func(nx)
                    new_data.append((nx, ny))
                    #print abs(slope - prev_slope), prev_point[0], nx, x
            prev_slope = slope
        
        prev_point = x, y
    
    if new_data:
        data += new_data
        data.sort(lambda x, y: cmp(x[0], y[0]))
        return optimize_sampling(func, data)
    else:
        return data
        
def graph_new_from_file(filename, graph_name, x_col=0, y_col=1):
    """
    Returns a line_chart.Graph with point taken from data file
    filename.
    The id of the new graph is graph_name.    
    
    Data file format:
    The columns in the file have to be separated by tabs or one
    or more spaces. Everything after '#' is ignored (comment).
    
    Use the parameters x_col and y_col to control which columns to use
    for plotting. By default, the first column (x_col=0) is used for
    x values, the second (y_col=1) is used for y values.
    
    @type filename: string
    @param filename: path to the data file
    @type graph_name: string
    @param graph_name: a unique name for the graph
    @type x_col: int
    @param x_col: the number of the column to use for x values
    @type y_col: int
    @param y_col: the number of the column to use for y values
    
    @return: line_chart.Graph
    """
    points = []
    f = open(filename, "r")
    data = f.read()
    f.close()
    lines = data.split("\n")
    
    for line in lines:
        line = line.strip() #remove special characters at beginning and end
        
        #remove comments:
        a = line.split("#", 1)
        if a and a[0]:
            line = a[0]
            #get data from line:
            if line.find("\t") != -1:
                #col separator is tab
                d = line.split("\t")
            else:
                #col separator is one or more space
                #normalize to one space:
                while line.find("  ") != -1:
                    line = line.replace("  ", " ")
                d = line.split(" ")
            d = filter(lambda x: x, d)
            d = map(lambda x: float(x), d)
            
            points.append((d[x_col], d[y_col]))
    return Graph(graph_name, "", points)
