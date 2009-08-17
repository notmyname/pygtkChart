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
    def _do_draw(self, context, rect, group, bar_count, n, i, m, j, mode, group_padding, bar_padding, maximum_value, group_end, value_label_size, label_size, label_rotation, draw_labels):
        if mode == MODE_VERTICAL:
            return self._do_draw_multi_vertical(context, rect, group, bar_count, n, i, m, j, mode, group_padding, bar_padding, maximum_value, group_end, value_label_size, label_size, label_rotation, draw_labels)
            
    def _do_draw_multi_vertical(self, context, rect, group, bar_count, n, i, m, j, mode, group_padding, bar_padding, maximum_value, group_end, value_label_size, label_size, label_rotation, draw_labels):
        bar_width = (rect.width - (bar_count - n) * bar_padding - (n - 1) * group_padding) / bar_count
        bar_height = (rect.height - value_label_size - label_size) * self._value / maximum_value
        bar_x = group_end + j * (bar_width + bar_padding)
        bar_y = rect.y + rect.height - bar_height - label_size
        context.set_source_rgb(*color_gdk_to_cairo(self._color))
        bar_chart.draw_rounded_rectangle(context, bar_x, bar_y, bar_width, bar_height, self._corner_radius)
        context.fill()
        
        chart.add_sensitive_area(chart.AREA_RECTANGLE, (bar_x, bar_y, bar_width, bar_height), (group, self))
        
        if self._highlighted:
            context.set_source_rgba(1, 1, 1, 0.1)
            bar_chart.draw_rounded_rectangle(context, bar_x, bar_y, bar_width, bar_height, self._corner_radius)
            context.fill()
            
        if draw_labels:
            #draw the value label
            self._value_label_object.set_max_width(bar_width)
            self._value_label_object.set_text(str(self._value))
            self._value_label_object.set_color(self._color)
            self._value_label_object.set_position((bar_x + bar_width / 2, bar_y - 3))
            self._value_label_object.set_anchor(label.ANCHOR_BOTTOM_CENTER)
            self._value_label_object.draw(context, rect)
            context.fill()
            
            #draw label
            self._label_object.set_rotation(label_rotation)
            self._label_object.set_wrap(False)
            self._label_object.set_color(self._color)
            self._label_object.set_fixed(True)
            self._label_object.set_max_width(3 * bar_width)
            self._label_object.set_text(self._label)
            self._label_object.set_position((bar_x + bar_width / 2 + 5, bar_y + bar_height + 8))
            self._label_object.set_anchor(label.ANCHOR_TOP_RIGHT)
            self._label_object.draw(context, rect)
            context.fill()
        
        return bar_x + bar_width
        
    def get_value_label_size(self, context, rect, mode, bar_count, n, group_padding, bar_padding):
        if mode == MODE_VERTICAL:
            bar_width = (rect.width - (bar_count - n) * bar_padding - (n - 1) * group_padding) / bar_count
            self._value_label_object.set_max_width(bar_width)
            self._value_label_object.set_text(str(self._value))
            return self._value_label_object.get_calculated_dimensions(context, rect)[1]   
            
    def get_label_size(self, context, rect, mode, bar_count, n, group_padding, bar_padding, label_rotation):
        if mode == MODE_VERTICAL:
            bar_width = (rect.width - (bar_count - n) * bar_padding - (n - 1) * group_padding) / bar_count
            self._label_object.set_rotation(label_rotation)
            self._label_object.set_wrap(False)
            self._label_object.set_fixed(True)
            self._label_object.set_max_width(3 * bar_width)
            self._label_object.set_text(self._label)
            return self._label_object.get_calculated_dimensions(context, rect)[1]   
        
        
        
class BarGroup(ChartObject):
    
    def __init__(self, name, title=""):
        ChartObject.__init__(self)
        #private properties:
        self._bars = []
        self._group_label_object = label.Label((0, 0), title)
        #gobject properties:
        self._name = name
        self._title = title
        self._bar_padding = 2
        
    #drawing methods
    def _do_draw(self, context, rect, bar_count, n, i, mode, group_padding, maximum_value, group_end, value_label_size, label_size, label_rotation, draw_labels):
        end = group_end
        for j, bar in enumerate(self._bars):
            end = bar.draw(context, rect, self, bar_count, n, i, len(self._bars), j, mode, group_padding, self._bar_padding, maximum_value, group_end, value_label_size, label_size, label_rotation, draw_labels)
        
        if draw_labels:
            context.set_source_rgb(0, 0, 0)
            group_width = end - group_end
            self._group_label_object.set_text(self._title)
            self._group_label_object.set_fixed(True)
            self._group_label_object.set_max_width(group_width)
            self._group_label_object.set_position((group_end + group_width / 2, rect.y + rect.height))
            self._group_label_object.set_anchor(label.ANCHOR_BOTTOM_CENTER)
            self._group_label_object.draw(context, rect)
            context.fill()
        
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
        
    def get_value_label_size(self, context, rect, mode, bar_count, n, group_padding, bar_padding):
        value_label_size = 0
        for bar in self._bars:
            value_label_size = max(value_label_size, bar.get_value_label_size(context, rect, mode, bar_count, n, group_padding, bar_padding))
        return value_label_size
        
    def get_label_size(self, context, rect, mode, bar_count, n, group_padding, bar_padding, label_rotation):
        label_size = 0
        for bar in self._bars:
            label_size = max(label_size, bar.get_label_size(context, rect, mode, bar_count, n, group_padding, bar_padding, label_rotation))
        return label_size
        
    def get_group_label_size(self, context, rect, mode):
        self._group_label_object.set_text(self._title)
        if mode == MODE_VERTICAL:
            return self._group_label_object.get_calculated_dimensions(context, rect)[1]
        
        
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
        self._label_rotation = 300
        
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
    def _do_draw_groups(self, context, rect, maximum_value, value_label_size, label_size, bar_count):
        if self._groups == []: return
        
        if self._mode == MODE_VERTICAL:
            group_end = rect.x
        else:
            group_end = rect.y
        
        for i, group in enumerate(self._groups):
            group_end = group.draw(context, rect, bar_count, len(self._groups), i, self._mode, self._group_padding, maximum_value, group_end, value_label_size, label_size, self._label_rotation, self._draw_labels)
        
    def draw(self, context):
        """
        Draw the widget. This method is called automatically. Don't call it
        yourself. If you want to force a redrawing of the widget, call
        the queue_draw() method.
        
        @type context: cairo.Context
        @param context: The context to draw on.
        """
        label.begin_drawing()
        chart.init_sensitive_areas()
        
        rect = self.get_allocation()
        rect = gtk.gdk.Rectangle(0, 0, rect.width, rect.height) #transform rect to context coordinates
        context.set_line_width(1)
                                    
        rect = self.draw_basics(context, rect)
        
        maximum_value = max(group.get_maximum_value() for group in self._groups)
        bar_count = 0
        for group in self._groups: bar_count += group.get_bar_count()
        
        value_label_size = 0
        if self._draw_labels:
            for group in self._groups:
                value_label_size = max(value_label_size, group.get_value_label_size(context, rect, self._mode, bar_count, len(self._groups), self._group_padding, self._bar_padding))
        
        label_size = 0
        if self._draw_labels:
            for group in self._groups:
                label_size = max(label_size, group.get_label_size(context, rect, self._mode, bar_count, len(self._groups), self._group_padding, self._bar_padding, self._label_rotation))
            label_size += 10
            label_size += group.get_group_label_size(context, rect, self._mode)
        
        rect = self._do_draw_grid(context, rect, maximum_value, value_label_size, label_size)
        self._do_draw_groups(context, rect, maximum_value, value_label_size, label_size, bar_count)
        
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
