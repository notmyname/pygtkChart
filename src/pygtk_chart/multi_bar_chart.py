"""
Contains the MultiBarChart widget.

Author: Sven Festersen (sven@sven-festersen.de)
"""
__docformat__ = "epytext"
import cairo
import gtk
import gobject
import os
import math

import pygtk_chart
from pygtk_chart.basics import *
from pygtk_chart import bar_chart
from pygtk_chart.chart_object import ChartObject
from pygtk_chart import chart
from pygtk_chart import label

MODE_VERTICAL = 0
MODE_HORIZONTAL = 1

COLOR_AUTO = 0
COLORS = gdk_color_list_from_file(os.sep.join([os.path.dirname(__file__), "data", "tango.color"]))


class Bar(bar_chart.Bar):
    
    def __init__(self, name, value, title=""):
        bar_chart.Bar.__init__(self, name, value, title)
    
    #drawing methods
    def _do_draw(self, context, rect, group, bar_count, n, i, m, j, mode, group_padding, bar_padding, maximum_value, group_end):
        if mode == MODE_VERTICAL:
            return self._do_draw_multi_vertical(context, rect, group, bar_count, n, i, m, j, mode, group_padding, bar_padding, maximum_value, group_end)
            
    def _do_draw_multi_vertical(self, context, rect, group, bar_count, n, i, m, j, mode, group_padding, bar_padding, maximum_value, group_end):
        bar_width = (rect.width - (bar_count - n) * bar_padding - (n - 1) * group_padding) / bar_count
        bar_height = rect.height * self._value / maximum_value
        bar_x = group_end + j * (bar_width + bar_padding)
        bar_y = rect.y + rect.height - bar_height
        context.set_source_rgb(*color_gdk_to_cairo(self._color))
        bar_chart.draw_rounded_rectangle(context, bar_x, bar_y, bar_width, bar_height, self._corner_radius)
        context.fill()
        
        chart.add_sensitive_area(chart.AREA_RECTANGLE, (bar_x, bar_y, bar_width, bar_height), (group, self))
        
        if self._highlighted:
            context.set_source_rgba(1, 1, 1, 0.1)
            bar_chart.draw_rounded_rectangle(context, bar_x, bar_y, bar_width, bar_height, self._corner_radius)
            context.fill()
        
        return bar_x + bar_width
        
        
        
class BarGroup(ChartObject):
    
    def __init__(self, name, title=""):
        ChartObject.__init__(self)
        #private properties:
        self._bars = []
        #gobject properties:
        self._name = name
        self._title = title
        self._bar_padding = 2
        
    #drawing methods
    def _do_draw(self, context, rect, bar_count, n, i, mode, group_padding, maximum_value, group_end):
        end = group_end
        for j, bar in enumerate(self._bars):
            end = bar.draw(context, rect, self, bar_count, n, i, len(self._bars), j, mode, group_padding, self._bar_padding, maximum_value, group_end)
        return end + group_padding
    
    #other methods        
    def add_bar(self, bar):
        """
        Add a bar to the group.
        
        @param bar: the bar to add
        @type bar: multi_bar_chart.Bar.
        """
        if bar.get_color() == COLOR_AUTO:
            bar.set_color(COLORS[len(self._bars) % len(COLORS)])
        self._bars.append(bar)
        self.emit("appearance_changed")
        
    def get_bar_count(self):
        return len(self._bars)
        
    def get_maximum_value(self):
        return max(bar.get_value() for bar in self._bars)
        
    def get_bars(self):
        return self._bars
        
    def get_label(self):
        return self._title
        
        
class MultiBarChart(bar_chart.BarChart):
    
    __gsignals__ = {"group-clicked": (gobject.SIGNAL_RUN_LAST, 
                                    gobject.TYPE_NONE, 
                                    (gobject.TYPE_PYOBJECT, gobject.TYPE_PYOBJECT))}
    
    def __init__(self):
        bar_chart.BarChart.__init__(self)
        #private properties:
        self._groups = []
        #gobject properties:
        self._group_padding = 16
        
    #callbacks
    def _cb_motion_notify(self, widget, event):
        if not self._mouseover: return
        active = chart.get_sensitive_areas(event.x, event.y)
        for group in self._groups:
            for bar in group.get_bars():
                bar.set_highlighted((group, bar) in active)
        self.queue_draw()
        
    def _cb_button_pressed(self, widget, event):
        active = chart.get_sensitive_areas(event.x, event.y)
        for group, bar in active:
            self.emit("group-clicked", group, bar)
        
    #drawing methods
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
        rect = gtk.gdk.Rectangle(0, 0, rect.width, rect.height) #transform rect to context coordinates
        context.set_line_width(1)
                                    
        rect = self.draw_basics(context, rect)
        """
        maximum_value = max(bar.get_value() for bar in self._bars)
        #find out the size of the value labels
        value_label_size = 0
        if self._draw_labels:
            for bar in self._bars:
                value_label_size = max(value_label_size, bar.get_value_label_size(context, rect, self._mode, len(self._bars), self._bar_padding))
            value_label_size += 3
            
        #find out the size of the labels:
        label_size = 0
        if self._draw_labels:
            for bar in self._bars:
                label_size = max(label_size, bar.get_label_size(context, rect, self._mode, len(self._bars), self._bar_padding))
            label_size += 3
        
        rect = self._do_draw_grid(context, rect, maximum_value, value_label_size, label_size)
        self._do_draw_bars(context, rect, maximum_value, value_label_size, label_size)
        """
        context.set_source_rgb(0, 0, 0)
        context.rectangle(rect.x, rect.y, rect.width, rect.height)
        context.stroke()
        
        chart.init_sensitive_areas()
        
        maximum_value = max(group.get_maximum_value() for group in self._groups)
        bar_count = 0
        for group in self._groups: bar_count += group.get_bar_count()
        if self._mode == MODE_VERTICAL:
            group_end = rect.x
        else:
            group_end = rect.y
        
        for i, group in enumerate(self._groups):
            group_end = group.draw(context, rect, bar_count, len(self._groups), i, self._mode, self._group_padding, maximum_value, group_end)
        
        label.finish_drawing()
    
    #other methods        
    def add_group(self, group):
        """
        Add a BarGroup to the chart.
        
        @type group: multi_bar_chart.BarGroup.
        """
        self._groups.append(group)
        self.queue_draw()
        
    def add_bar(self, bar):
        """
        Alias for add_group.
        This method is deprecated. Use add_group instead.
        """
        print "MultiBarChart.add_bar is deprecated. Use add_group instead."
        self.add_group(bar)
