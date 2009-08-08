"""
Contains the BarChart widget.

Author: John Dickinson (john@johnandkaren.com)
"""
__docformat__ = "epytext"
import cairo
import gtk
import gobject
import os
import collections # for defaultdict
import math # for pi

import pygtk_chart
from pygtk_chart.basics import *
from pygtk_chart.chart_object import ChartObject
from pygtk_chart import chart
from pygtk_chart import label

MODE_VERTICAL = 0
MODE_HORIZONTAL = 1

COLOR_AUTO = 0
COLORS = gdk_color_list_from_file(os.sep.join([os.path.dirname(__file__), "data", "tango.color"]))


def draw_rounded_rectangle(context, x, y, width, height, radius=0):
    if radius == 0:
        context.rectangle(x, y, width, height)
    else:
        context.move_to(x, y + radius)
        context.arc(x + radius, y + radius, radius, math.pi, 1.5 * math.pi)
        context.rel_line_to(width - 2 * radius, 0)
        context.arc(x + width - radius, y + radius, radius, 1.5 * math.pi, 2 * math.pi)
        context.rel_line_to(0, height - 2 * radius)
        context.arc(x + width - radius, y + height - radius, radius, 0, 0.5 * math.pi)
        context.rel_line_to(-(width - 2 * radius), 0)
        context.arc(x + radius, y + height - radius, radius, 0.5 * math.pi, math.pi)
        context.close_path()


class Grid(ChartObject):
    
    __gproperties__ = {"line-style": (gobject.TYPE_INT,
                                        "line style",
                                        "Line Style for the grid lines",
                                        0, 3, 0, gobject.PARAM_READWRITE)}
    
    def __init__(self):
        ChartObject.__init__(self)
        self._antialias = False
        self._color = gtk.gdk.color_parse("#DEDEDE")
        self._line_style = pygtk_chart.LINE_STYLE_SOLID
        
    def do_get_property(self, property):
        if property.name == "visible":
            return self._show
        elif property.name == "antialias":
            return self._antialias
        elif property.name == "line-style":
            return self._line_style
            raise AttributeError, "Property %s does not exist." % property.name

    def do_set_property(self, property, value):
        if property.name == "visible":
            self._show = value
        elif property.name == "antialias":
            self._antialias = value
        elif property.name == "line-style":
            self._line_style = value
        else:
            raise AttributeError, "Property %s does not exist." % property.name
        
    def _do_draw(self, context, rect, mode, max_value, height_factor, padding):
        set_context_line_style(context, self._line_style)
        context.set_source_rgb(*color_gdk_to_cairo(self._color))
        n = int(max_value / (10 ** int(math.log10(max_value))))
        
        if mode == MODE_VERTICAL:
            delta = (rect.height * height_factor) / max_value
            x = padding
            y = rect.height - rect.height * (1 - height_factor) / 2
            for i in range(0, n + 1):
                context.move_to(x, y)
                context.line_to(rect.width - padding, y)
                context.stroke()
                y -= 10 ** int(math.log10(max_value)) * delta
        else:
            delta = (rect.width - 8 * padding) / max_value
            x = 5 * padding
            y = rect.height * (1 - height_factor) / 2 + padding
            for i in range(0, n + 1):
                context.move_to(x, y)
                context.line_to(x, rect.height - rect.height * (1 - height_factor) / 2)
                context.stroke()
                x += 10 ** int(math.log10(max_value)) * delta
                
    def set_line_style(self, style):
        """
        Set the grid's line style.
        
        @param style: the new line style
        @type style: a line style constant.
        """
        self.set_property("line-style", style)
        self.emit("appearance_changed")
        
    def get_line_style(self):
        """
        Returns the grid's current line style.
        
        @return: a line style constant.
        """
        return self.get_property("line-style")
            


class Bar(chart.Area):
    """
    A class that represents a bar on a bar chart,
    """
    
    __gproperties__ = {"corner-radius": (gobject.TYPE_INT, "bar corner radius",
                                "The radius of the bar's rounded corner.",
                                0, 100, 0, gobject.PARAM_READWRITE)}
    
    def __init__(self, name, value, title=""):
        chart.Area.__init__(self, name, value, title)
        self._label_object = label.Label((0, 0), title)
        self._value_label_object = label.Label((0, 0), "")
        
        self._corner_radius = 0
        
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
        elif property.name == "highlighted":
            return self._highlighted
        elif property.name == "corner-radius":
            return self._corner_radius
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
        elif property.name == "highlighted":
            self._highlighted = value
        elif property.name == "corner-radius":
            self._corner_radius = value
        else:
            raise AttributeError, "Property %s does not exist." % property.name
        
    def _do_draw(self, context, rect, mode, i, n, padding, height_factor_vertical, height_factor_horizontal, max_value, draw_labels, multi_bar=False, j=0, m=0, width=0, label_rotation=0, multi=None):
        if not multi_bar and mode == MODE_VERTICAL:
            self._do_draw_single_vertical(context, rect, i, n, padding, height_factor_vertical, max_value, draw_labels)
        elif not multi_bar and mode == MODE_HORIZONTAL:
            self._do_draw_single_horizontal(context, rect, i, n, padding, height_factor_horizontal, max_value, draw_labels)
        elif multi_bar and mode == MODE_VERTICAL:
            return self._do_draw_multi_vertical(context, rect, i, n, padding, height_factor_vertical, max_value, draw_labels, j, m, width, label_rotation, multi)
            
    def _do_draw_multi_vertical(self, context, rect, i, n, padding, height_factor, max_value, draw_labels, j, m, complete_width, label_rotation, multi_bar):
        """
        This method is used for drawing if the bar is on a
        MultiBarChart.
        """
        width = complete_width / m
        height = self._value / max_value * height_factor * rect.height
        x = i * (complete_width + padding) + j * width + padding / 2
        y = rect.height * (1 - height_factor) / 2 + rect.height * height_factor - height
        
        self._do_draw_rectangle(context, x, y, width, height)
        chart.add_sensitive_area(chart.AREA_RECTANGLE, (x, y, width, height), (multi_bar, self))
        
        if self._highlighted:
            self._do_draw_higlighted(context, x, y, width, height)
            
        if draw_labels:
            #draw label under bar
            self._label_object.set_text(self._label)
            if i == 0 and j == 0:
                self._label_object.set_wrap(False)
            self._label_object.set_color(self._color)
            self._label_object.set_anchor(label.ANCHOR_TOP_RIGHT)
            self._label_object.set_fixed(True)
            self._label_object.set_rotation(label_rotation)
            self._label_object.set_position((x + 0.7 * width, y + height + 8))
            self._label_object.draw(context, rect)
            
            #draw value on top of bar
            self._do_draw_value_label_vertical(context, rect, x, y, width)
            
        return y + height + 8 + self._label_object.get_real_dimensions()[1]
        
            
    def _do_draw_single_vertical(self, context, rect, i, n, padding, height_factor, max_value, draw_labels):
        """
        This method is used for drawing if the bar is on a BarChart.
        """
        width = (rect.width - n * padding) / n
        height = self._value / max_value * height_factor * rect.height
        x = padding / 2 + i * (width + padding)
        y = rect.height * (1 - height_factor) / 2 + rect.height * height_factor - height
        
        self._do_draw_rectangle(context, x, y, width, height)
        chart.add_sensitive_area(chart.AREA_RECTANGLE, (x, y, width, height), self)
        
        if self._highlighted:
            self._do_draw_higlighted(context, x, y, width, height)
        
        if draw_labels:
            #draw label under bar
            self._label_object.set_text(self._label)
            self._label_object.set_color(self._color)
            self._label_object.set_anchor(label.ANCHOR_TOP_CENTER)
            self._label_object.set_position((x + width / 2, y + height + 3))
            self._label_object.set_max_width(width)
            self._label_object.draw(context, rect)
            
            #draw value on top of bar
            self._do_draw_value_label_vertical(context, rect, x, y, width)
   
    def _do_draw_single_horizontal(self, context, rect, i, n, padding, height_factor, max_value, draw_labels):
        height = (rect.height * height_factor - n * padding) / n
        width = self._value / max_value * (rect.width - 8 * padding)
        x = 5 * padding
        y = padding + i * (height + padding) + rect.height * (1 - height_factor) / 2
        
        self._do_draw_rectangle(context, x, y, width, height)
        chart.add_sensitive_area(chart.AREA_RECTANGLE, (x, y, width, height), self)
        
        if self._highlighted:
            self._do_draw_higlighted(context, x, y, width, height)
        
        if draw_labels:
            #draw label left of bar
            self._label_object.set_text(self._label)
            self._label_object.set_color(self._color)
            self._label_object.set_anchor(label.ANCHOR_RIGHT_CENTER)
            self._label_object.set_position((x - 3, y + height / 2))
            self._label_object.set_max_width(4 * padding)
            self._label_object.draw(context, rect)
            
            #draw value right of bar
            self._do_draw_value_label_horizontal(context, rect, x, y, width, height)
            
    def _do_draw_rectangle(self, context, x, y, width, height):
        context.set_source_rgb(*color_gdk_to_cairo(self._color))
        radius = min((width / 2, height / 2, self._corner_radius))
        draw_rounded_rectangle(context, x, y, width, height, radius)
        context.fill()
            
    def _do_draw_higlighted(self, context, x, y, width, height):
        context.set_source_rgba(1, 1, 1, 0.1)
        draw_rounded_rectangle(context, x, y, width, height, self._corner_radius)
        context.fill()
            
    def _do_draw_value_label_vertical(self, context, rect, x, y, width):
        self._value_label_object.set_text(str(self._value))
        self._value_label_object.set_color(self._color)
        self._value_label_object.set_anchor(label.ANCHOR_BOTTOM_CENTER)
        self._value_label_object.set_position((x + width / 2, y - 3))
        self._value_label_object.set_max_width(width)
        self._value_label_object.draw(context, rect)
        
    def _do_draw_value_label_horizontal(self, context, rect, x, y, width, height):
        self._value_label_object.set_text(str(self._value))
        self._value_label_object.set_color(self._color)
        self._value_label_object.set_anchor(label.ANCHOR_LEFT_CENTER)
        self._value_label_object.set_position((x + width + 3, y + height / 2))
        self._value_label_object.draw(context, rect)
        
    def set_corner_radius(self, radius):
        """
        Set the radius of the bar's corners in px (default: 0).
        
        @param radius: radius of the corners
        @type radius: int in [0, 100].
        """
        self.set_property("corner-radius", radius)
        self.emit("appearance_changed")
        
    def get_corner_radius(self):
        """
        Returns the current radius of the bar's corners in px.
        
        @return: int in [0, 100]
        """
        return self.get_property("corner-radius")


class BarChart(chart.Chart):
    __gproperties__ = {"draw-labels": (gobject.TYPE_BOOLEAN,
                                        "draw bar labels",
                                        "Set whether to draw bar labels.",
                                        True, gobject.PARAM_READWRITE),
                       "show-values": (gobject.TYPE_BOOLEAN,
                                        "show values",
                                        "Set whether to show values in the bars' labels.",
                                        True, gobject.PARAM_READWRITE),
                       "enable-mouseover": (gobject.TYPE_BOOLEAN,
                                        "enable mouseover",
                                        "Set whether a mouseover effect should be visible if moving the mouse over a bar.",
                                        True, gobject.PARAM_READWRITE),
                        "mode": (gobject.TYPE_INT, "mode",
                                "The BarChart's mode.", 0, 1, 0,
                                gobject.PARAM_READWRITE)}
    
    __gsignals__ = {"bar-clicked": (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,))}
    
    def __init__(self):
        super(BarChart, self).__init__()
        self.grid = Grid()
        self._bars = []
        self._enable_mouseover = True
        self._mode = MODE_VERTICAL
        self._values = True
        self._labels = True
        
        self._height_factor_vertical = 0.8
        self._height_factor_horizontal = 0.9
        self._bar_padding = 16
        
        self.add_events(gtk.gdk.BUTTON_PRESS_MASK|gtk.gdk.SCROLL_MASK|gtk.gdk.POINTER_MOTION_MASK)
        self.connect("button_press_event", self._cb_button_pressed)
        self.connect("motion-notify-event", self._cb_motion_notify)
    
    def do_get_property(self, property):
        if property.name == "draw-labels":
            return self._labels
        elif property.name == "show-values":
            return self._values
        elif property.name == "enable-mouseover":
            return self._enable_mouseover
        elif property.name == "mode":
            return self._mode
        else:
            raise AttributeError, "Property %s does not exist." % property.name
    
    def do_set_property(self, property, value):
        if property.name == "draw-labels":
            self._labels = value
        elif property.name == "show-values":
            self._values = value
        elif property.name == "enable-mouseover":
            self._enable_mouseover = value
        elif property.name == "mode":
            self._mode = value
        else:
            raise AttributeError, "Property %s does not exist." % property.name
    
    def _cb_appearance_changed(self, widget):
        self.queue_draw()
    
    def _cb_motion_notify(self, widget, event):
        if not self._enable_mouseover: return
        bars = chart.get_sensitive_areas(event.x, event.y)
        for bar in self._bars:
            bar.set_property("highlighted", bar in bars)
        self.queue_draw()
    
    def _cb_button_pressed(self, widget, event):
        bars = chart.get_sensitive_areas(event.x, event.y)
        for bar in bars:
            self.emit("bar-clicked", bar)     
            
    def _do_draw_grid(self, context, rect):
        max_value = max(x.get_value() for x in self._bars)
        if self._mode == MODE_VERTICAL:
            self.grid.draw(context, rect, self._mode, max_value, self._height_factor_vertical, self._bar_padding / 2)
        elif self._mode == MODE_HORIZONTAL:
            self.grid.draw(context, rect, self._mode, max_value, self._height_factor_horizontal, self._bar_padding)
    
    def _do_draw_bars(self, context, rect):
        """
        Draw the chart.
        
        @type context: cairo.Context
        @param context: The context to draw on.
        @type rect: gtk.gdk.Rectangle
        @param rect: A rectangle representing the charts area.
        """
        if not self._bars: return
        chart.init_sensitive_areas()
        n = len(self._bars)
        max_value = max(x.get_value() for x in self._bars)
        
        for i, bar in enumerate(self._bars):
            bar.draw(context, rect, self._mode, i, n, self._bar_padding, self._height_factor_vertical, self._height_factor_horizontal, max_value, self._labels)
    
    def draw(self, context):
        """
        Draw the widget. This method is called automatically. Don't call it
        yourself. If you want to force a redrawing of the widget, call
        the queue_draw() method.
        
        @type context: cairo.Context
        @param context: The context to draw on.
        """
        label.begin_drawing()
        
        rect = self.get_allocation()
        #initial context settings: line width & font
        context.set_line_width(1)
        font = gtk.Label().style.font_desc.get_family()
        context.select_font_face(font,cairo.FONT_SLANT_NORMAL, \
                                    cairo.FONT_WEIGHT_NORMAL)
                                    
        self.draw_basics(context, rect)
        self._do_draw_grid(context, rect)
        self._do_draw_bars(context, rect)
        
        label.finish_drawing()
    
    def add_bar(self, bar):
        """
        Add a bar_chart.Bar to the bar chart.
        
        @param bar: the bar to add
        @type bar: bar_chart.Bar.
        """
        color = bar.get_color()
        if color == COLOR_AUTO: bar.set_color(COLORS[len(self._bars) % len(COLORS)])
        self._bars.append(bar)
        bar.connect("appearance_changed", self._cb_appearance_changed)
    
    def get_bar(self, name):
        """
        Returns the Bar with the id 'name' if it exists, None
        otherwise.
        
        @type name: string
        @param name: the id of a Bar
        
        @return: Bar or None.
        """
        for bar in self._bars:
            if bar.get_name() == name:
                return bar
        return None
    
    def set_draw_labels(self, draw):
        """
        Set whether to draw the labels of the bars.
        
        @type draw: boolean.
        """
        self.set_property("draw-labels", draw)
        self.queue_draw()
    
    def get_draw_labels(self):
        """
        Returns True if bar labels are shown.
        
        @return: boolean.
        """
        return self.get_property("draw-labels")
    
    def set_enable_mouseover(self, mouseover):
        """
        Set whether a mouseover effect should be shown when the pointer
        enters a bar.
        
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
        Set whether the bar's value should be shown in its label.
        
        @type show: boolean.
        """
        self.set_property("show-values", show)
        self.queue_draw()
    
    def get_show_values(self):
        """
        Returns True if the value of a bar is shown in its label.
        
        @return: boolean.
        """
        return self.get_property("show-values")
        
    def set_bar_corner_radius(self, radius):
        """
        Set the corner radius of all bars.
        
        @type radius: int in [0,100]
        """
        for bar in self._bars:
            bar.set_property("corner-radius", radius)
        self.queue_draw()
        
    def set_mode(self, mode):
        """
        Set whether the bars should be displayed horizontal or
        vertical. The parameter mode has to be one of these constants:
        - bar_chart.MODE_VERTICAL (default)
        - bar_chart.MODE_HORIZONTAL
        
        @type mode: one of the constants above.
        """
        self.set_property("mode", mode)
        
    def get_mode(self):
        """
        Returns the BarChart's mode. (MODE_VERTICAL or MODE_HORIZONTAL).
        
        @return: a mode constant.
        """
        return self.get_property("mode")


class MultiBar(ChartObject):
    """
    This class represents a group of bars on a MultiBarChart.
    """
    
    __gproperties__ = {"name": (gobject.TYPE_STRING, "bar name",
                                "A unique name for the bar.",
                                "", gobject.PARAM_READABLE),
                        "max-value": (gobject.TYPE_FLOAT,
                                    "maximum value",
                                    "Maximum value of all bars in the group.",
                                    0.0, 9999999999.0, 0.0, gobject.PARAM_READABLE),
                        "label": (gobject.TYPE_STRING, "bar label",
                                    "The label for the bar.", "",
                                    gobject.PARAM_READWRITE)}
    
    def __init__(self, name, title=""):
        super(MultiBar, self).__init__()
        self._name = name
        self._label = title
        self._bars = []
        
        self._label_object = label.Label((0, 0), title, anchor=label.ANCHOR_BOTTOM_CENTER, fixed=True)
    
    def do_get_property(self, property):
        if property.name == "visible":
            return self._show
        elif property.name == "antialias":
            return self._antialias
        elif property.name == "name":
            return self._name
        elif property.name == "max-value":
            return max(x.get_value() for x in self._bars) if self._bars else 0.0
        elif property.name == "label":
            return self._label
        else:
            raise AttributeError, "Property %s does not exist." % property.name
    
    def do_set_property(self, property, value):
        if property.name == "visible":
            self._show = value
        elif property.name == "antialias":
            self._antialias = value
        elif property.name == "label":
            self._label = value
            self.label_object.set_text(value)
        else:
            raise AttributeError, "Property %s does not exist." % property.name
            
    def _do_draw(self, context, rect, i, n, bar_padding, height_factor_vertical, height_factor_horizontal, max_value, draw_labels, label_rotation, mode):
        width = (rect.width - n * bar_padding) / n
        x = i * (width + bar_padding) + bar_padding / 2
        
        m = len(self._bars)
        bottom = 0
        
        for j, bar in enumerate(self._bars):
            #self, context, rect, mode, i, n, padding, height_factor_vertical, height_factor_horizontal, max_value, draw_labels, multi_bar=False, j=0, m=0, width=0, label_rotation=0
            b = bar.draw(context, rect, mode, i, n, bar_padding, height_factor_vertical, height_factor_horizontal, max_value, draw_labels, True, j, m, width, label_rotation, self)
            if draw_labels:
                bottom = max(b, bottom)
            
        return min(rect.height - 20, bottom)
        
    def draw_label(self, context, rect, x, y, width):
        """
        Helper function to draw the group label. It's called by
        MultiBarChart objects.
        """
        self._label_object.set_position((x, y))
        self._label_object.set_anchor(label.ANCHOR_TOP_CENTER)
        self._label_object.set_max_width(width)
        self._label_object.set_text(self._label)
        self._label_object.draw(context, rect)
    
    def get_max_value(self):
        """
        Returns the maximum value of the MultiBar.
        
        @return: float.
        """
        return self.get_property("max-value")
    
    def set_label(self, label):
        """
        Set the label for the bar chart bar.
        
        @param label: the new label
        @type label: string.
        """
        self.set_property("label", label)
        self.emit("appearance_changed")
    
    def get_label(self):
        """
        Returns the current label of the bar.
        
        @return: string.
        """
        return self.get_property("label")
    
    def add_bar(self, bar):
        """
        Add a bar to the group of bars.
        
        @param bar: the bar to add
        @type bar: bar_chart.Bar.
        """
        color = bar.get_color()
        if color == COLOR_AUTO: bar.set_color(COLORS[len(self._bars) % len(COLORS)])
        self._bars.append(bar)
        bar.connect("appearance_changed", self._cb_appearance_changed)
    
    def get_bar(self, name):
        """
        Returns the Bar with the id 'name' if it exists, None
        otherwise.
        
        @type name: string
        @param name: the id of a Bar
        
        @return: Bar or None.
        """
        for bar in self._bars:
            if bar.get_name() == name:
                return bar
        return None
    
    def get_bars(self):
        """
        Get a list of bars in the group.
        
        @return: list of bar_chart.Bar.
        """
        return self._bars
        
    def set_bar_corner_radius(self, radius):
        """
        Set the the corner radius for all bars in the group.
        
        @type radius: int in [0,100].
        """
        for bar in self._bars:
            bar.set_property("corner-radius", radius)
    
    def _cb_appearance_changed(self, widget):
        self.emit("appearance_changed")


class MultiBarChart(BarChart):
    
    __gsignals__ = {"multibar-clicked": (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,gobject.TYPE_PYOBJECT,))}
    
    def __init__(self):
        super(MultiBarChart, self).__init__()
        self.name_map = {}
        self._label_rotation = 300 # amout of rotation in the sub bar labels
        self._bar_padding = 16
        self._height_factor_vertical = 0.7
        self._height_factor_horizontal = 0.8
    
    def add_bar(self, bar):
        """
        B{Deprecated. Use L{add_multibar} instead.}
        
        Add a group of bars (bar_chart.MultiBar) to the MultiBarChart.
        
        @param bar: group of bars to add
        @type bar: bar_chart.MultiBar.
        """
        print "MultiBarChart.add_bar is deprecated. Use add_multibar instead."
        self.add_multibar(bar)
        
    def add_multibar(self, multibar):
        """
        Add a group of bars (bar_chart.MultiBar) to the MultiBarChart.
        
        @param multibar: group of bars to add
        @type multibar: bar_chart.MultiBar.
        """
        self._bars.append(multibar)
        multibar.connect("appearance_changed", self._cb_appearance_changed)
        
    def set_bar_corner_radius(self, radius):
        """
        Set the the corner radius for all bars in the group.
        
        @type radius: int in [0,100].
        """
        for bar in self._bars:
            bar.set_bar_corner_radius(radius)
        self.queue_draw()
    
    def _cb_motion_notify(self, widget, event):
        if not self._enable_mouseover: return
        bars = chart.get_sensitive_areas(event.x, event.y)
        for bar in self._bars:
            for sub_bar in bar.get_bars():
                sub_bar.set_property("highlighted", ((bar, sub_bar) in bars))
        self.queue_draw()

    def _cb_button_pressed(self, widget, event):
        bars = chart.get_sensitive_areas(event.x, event.y)
        for multibar, bar in bars:
            self.emit("multibar-clicked", multibar, bar)
            self.emit("bar-clicked", multibar)
            
    def _do_draw_grid(self, context, rect):
        max_value = max(x.get_max_value() for x in self._bars)
        if self._mode == MODE_VERTICAL:
            self.grid.draw(context, rect, self._mode, max_value, self._height_factor_vertical, self._bar_padding / 2)
            
    def _do_draw_bars(self, context, rect):
        if not self._bars: return
        chart.init_sensitive_areas()
        
        n = len(self._bars)
        max_value = max(x.get_max_value() for x in self._bars)
        bar_padding = self._bar_padding
        width = (rect.width - n * bar_padding) / n
        
        bottom = rect.height
        
        for i, bar in enumerate(self._bars):
            label_y = bar.draw(context, rect, i, n, bar_padding, self._height_factor_vertical, self._height_factor_horizontal, max_value, self._labels, self._label_rotation, self._mode)
            bottom = min(bottom, label_y)
            
        for i, bar in enumerate(self._bars):
            label_x = i * (width + bar_padding) + bar_padding / 2 + width / 2
            bar.draw_label(context, rect, label_x, bottom, width)
    


