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

from pygtk_chart.basics import *
from pygtk_chart.chart_object import ChartObject
from pygtk_chart import chart
from pygtk_chart import label

COLOR_AUTO = 0

COLORS = color_list_from_file(os.sep.join([os.path.dirname(__file__), "data", "tango.color"]))


class Bar(chart.Area):
    """
    A class that represents a bar on a bar chart,
    """
    
    def __init__(self, name, value, title=""):
        chart.Area.__init__(self, name, value, title)
        self._label_object = label.Label((0, 0), title)
        self._value_label_object = label.Label((0, 0), "")
        
    def _do_draw(self, context, rect, i, n, padding, height_factor, max_value, draw_labels, multi_bar=False, j=0, m=0, width=0, label_rotation=0):
        if not multi_bar:
            self._do_draw_single(context, rect, i, n, padding, height_factor, max_value, draw_labels)
        else:
            return self._do_draw_multi(context, rect, i, n, padding, height_factor, max_value, draw_labels, j, m, width, label_rotation)
            
    def _do_draw_multi(self, context, rect, i, n, padding, height_factor, max_value, draw_labels, j, m, complete_width, label_rotation):
        """
        This method is used for drawing if the bar is on a
        MultiBarChart.
        """
        width = complete_width / m
        height = self._value / max_value * height_factor * rect.height
        x = i * (complete_width + padding) + j * width + padding / 2
        y = rect.height * (1 - height_factor) / 2 + rect.height * height_factor - height
        
        context.set_source_rgb(*self._color)
        context.rectangle(x, y, width, height)
        context.fill()
        
        if self._highlighted:
            context.set_source_rgba(1, 1, 1, 0.1)
            context.rectangle(x, y, width, height)
            context.fill()
            
        if draw_labels:
            #draw label under bar
            self._label_object.set_text(self._label)
            if i == 0 and j == 0:
                self._label_object.set_wrap(False)
            self._label_object.set_color(color_cairo_to_gdk(*self._color))
            self._label_object.set_anchor(label.ANCHOR_TOP_RIGHT)
            self._label_object.set_fixed(True)
            self._label_object.set_rotation(label_rotation)
            self._label_object.set_position((x + 0.7 * width, y + height + 8))
            self._label_object.draw(context, rect)
            
            #draw value on top of bar
            self._value_label_object.set_text(str(self._value))
            self._value_label_object.set_color(color_cairo_to_gdk(*self._color))
            self._value_label_object.set_anchor(label.ANCHOR_BOTTOM_CENTER)
            self._value_label_object.set_position((x + width / 2, y - 3))
            self._value_label_object.set_max_width(width)
            self._value_label_object.draw(context, rect)
            
        return y + height + 8 + self._label_object.get_real_dimensions()[1]
        
            
    def _do_draw_single(self, context, rect, i, n, padding, height_factor, max_value, draw_labels):
        """
        This method is used for drawing if the bar is on a BarChart.
        """
        width = (rect.width - n * padding) / n
        height = self._value / max_value * height_factor * rect.height
        x = padding / 2 + i * (width + padding)
        y = rect.height * (1 - height_factor) / 2 + rect.height * height_factor - height
        
        context.set_source_rgb(*self._color)
        context.rectangle(x, y, width, height)
        context.fill()
        
        if self._highlighted:
            context.set_source_rgba(1, 1, 1, 0.1)
            context.rectangle(x, y, width, height)
            context.fill()
        
        if draw_labels:
            #draw label under bar
            self._label_object.set_text(self._label)
            self._label_object.set_color(color_cairo_to_gdk(*self._color))
            self._label_object.set_anchor(label.ANCHOR_TOP_CENTER)
            self._label_object.set_position((x + width / 2, y + height + 3))
            self._label_object.set_max_width(width)
            self._label_object.draw(context, rect)
            
            #draw value on top of bar
            self._value_label_object.set_text(str(self._value))
            self._value_label_object.set_color(color_cairo_to_gdk(*self._color))
            self._value_label_object.set_anchor(label.ANCHOR_BOTTOM_CENTER)
            self._value_label_object.set_position((x + width / 2, y - 3))
            self._value_label_object.set_max_width(width)
            self._value_label_object.draw(context, rect)


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
                                        True, gobject.PARAM_READWRITE)}
    
    __gsignals__ = {"bar-clicked": (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,))}
    
    def __init__(self):
        super(BarChart, self).__init__()
        self._bars = []
        self._enable_mouseover = True
        self._values = True
        self._labels = True
        
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
        else:
            raise AttributeError, "Property %s does not exist." % property.name
    
    def do_set_property(self, property, value):
        if property.name == "draw-labels":
            self._labels = value
        elif property.name == "show-values":
            self._values = value
        elif property.name == "enable-mouseover":
            self._enable_mouseover = value
        else:
            raise AttributeError, "Property %s does not exist." % property.name
    
    def _cb_appearance_changed(self, widget):
        self.queue_draw()
    
    def _cb_motion_notify(self, widget, event):
        if not self._enable_mouseover: return
        bar = self._get_bar_at_pos(event.x, event.y)
        for b in self._bars:
            b.set_property("highlighted", b == bar)
        self.queue_draw()
    
    def _cb_button_pressed(self, widget, event):
        bar = self._get_bar_at_pos(event.x, event.y)
        if bar:
            self.emit("bar-clicked", bar)
    
    def _get_bar_at_pos(self, x, y):
        if not self._bars: return None
        rect = self.get_allocation()
        
        number_of_bars = len(self._bars)
        max_value = max(x.get_value() for x in self._bars)
        bar_padding = 16 # pixels of padding to either side of each bar
        bar_height_factor = .8 # percentage of total height the bars will use
        bar_vertical_padding = (1.0 - bar_height_factor) / 2.0 # space above and below the bars
        total_height = int(rect.height * bar_height_factor) # maximum height for a bar
        bottom = rect.height # y-value of bottom of bar chart
        bar_bottom = bottom * (1.0 - bar_vertical_padding)
        bar_width = int((rect.width-(bar_padding*number_of_bars)) / number_of_bars)
        for i,info in enumerate(self._bars):
            bar_x = int(rect.width / float(number_of_bars) * i) + rect.x + (bar_padding // 2)
            percent = float(info.get_value()) / float(max_value)
            bar_height = int(total_height * percent)
            bar_top = int(rect.height*bar_vertical_padding) + total_height - bar_height
            
            if bar_x <= x <= bar_x+bar_width and bar_top <= y <= bar_bottom:
                return info
        
        return None
    
    def _do_draw_bars(self, context, rect):
        """
        Draw the chart.
        
        @type context: cairo.Context
        @param context: The context to draw on.
        @type rect: gtk.gdk.Rectangle
        @param rect: A rectangle representing the charts area.
        """
        if not self._bars: return
        n = len(self._bars)
        max_value = max(x.get_value() for x in self._bars)
        bar_padding = 16 # pixels of padding to either side of each bar
        bar_height_factor = 0.8 # percentage of total height the bars will use
        
        for i, bar in enumerate(self._bars):
            bar.draw(context, rect, i, n, bar_padding, bar_height_factor, max_value, self._labels)
    
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
            
    def _do_draw(self, context, rect, i, n, bar_padding, height_factor, max_value, draw_labels, label_rotation):
        width = (rect.width - n * bar_padding) / n
        x = i * (width + bar_padding) + bar_padding / 2
        
        m = len(self._bars)
        bottom = 0
        
        for j, bar in enumerate(self._bars):
            b = bar.draw(context, rect, i, n, bar_padding, height_factor, max_value, draw_labels, True, j, m, width, label_rotation)
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
    
    def _cb_appearance_changed(self, widget):
        self.emit("appearance_changed")


class MultiBarChart(BarChart):
    
    __gsignals__ = {"multibar-clicked": (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,gobject.TYPE_PYOBJECT,))}
    
    def __init__(self):
        super(MultiBarChart, self).__init__()
        self.name_map = {}
        self._label_rotation = 300 # amout of rotation in the sub bar labels
        self._bar_padding = 16
        self._height_factor = 0.7
    
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
    
    def _cb_motion_notify(self, widget, event):
        if not self._enable_mouseover: return
        multibar, subbar = self._get_bar_at_pos(event.x, event.y)
        for bar in self._bars:
            for sub_bar in bar.get_bars():
                sub_bar.set_property("highlighted", subbar == sub_bar)
        self.queue_draw()

    def _cb_button_pressed(self, widget, event):
        multibar, subbar = self._get_bar_at_pos(event.x, event.y)
        if subbar:
            self.emit("multibar-clicked", multibar, subbar)
            self.emit("bar-clicked", multibar)
            
    def _do_draw_bars(self, context, rect):
        if not self._bars: return
        
        n = len(self._bars)
        max_value = max(x.get_max_value() for x in self._bars)
        height_factor = self._height_factor
        bar_padding = self._bar_padding
        width = (rect.width - n * bar_padding) / n
        
        bottom = rect.height
        
        for i, bar in enumerate(self._bars):
            label_y = bar.draw(context, rect, i, n, bar_padding, height_factor, max_value, self._labels, self._label_rotation)
            bottom = min(bottom, label_y)
            
        for i, bar in enumerate(self._bars):
            label_x = i * (width + bar_padding) + bar_padding / 2 + width / 2
            bar.draw_label(context, rect, label_x, bottom, width)
    
    def _get_bar_at_pos(self, x, y):
        if not self._bars:
            return None,None
            
        rect = self.get_allocation()
        max_value = max(x.get_max_value() for x in self._bars)
        n = len(self._bars)
        padding = self._bar_padding
        height_factor = self._height_factor
        width = (rect.width - n * padding) / n
        
        for i, bar in enumerate(self._bars):
            px = padding / 2 + i * (width + padding)
            if px <= x <= px + width:
                m = len(bar.get_bars())
                sub_width = width / m
                for j, sub_bar in enumerate(bar.get_bars()):
                    spx = px + j * sub_width
                    if spx <= x <= spx + sub_width:
                        bottom = rect.height * (1 - height_factor) / 2 + rect.height * height_factor
                        height = sub_bar.get_value() / max_value * height_factor * rect.height
                        top = bottom - height
                        if top <= y <= bottom:
                            return bar, sub_bar

        return None,None
    

