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

class Bar(ChartObject):
    __gproperties__ = {"name": (gobject.TYPE_STRING, "bar name",
                                "A unique name for the bar.",
                                "", gobject.PARAM_READABLE),
                        "value": (gobject.TYPE_FLOAT,
                                    "value",
                                    "The value.",
                                    0.0, 9999999999.0, 0.0, gobject.PARAM_READWRITE),
                        "color": (gobject.TYPE_PYOBJECT, "bar color",
                                    "The color of the bar.",
                                    gobject.PARAM_READWRITE),
                        "label": (gobject.TYPE_STRING, "bar label",
                                    "The label for the bar.", "",
                                    gobject.PARAM_READWRITE)}
    
    def __init__(self, name, value, title=""):
        super(Bar, self).__init__()
        self._name = name
        self._value = value
        self._label = title
        self._color = COLOR_AUTO
        
        self.label_object = label.Label((0, 0), title, anchor=label.ANCHOR_CENTER)
        self.value_label_object = label.Label((0, 0), "%d" % value, anchor=label.ANCHOR_BOTTOM_CENTER)
    
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
            self.value_label_object.set_text("%d" % value)
        elif property.name == "color":
            self._color = value
        elif property.name == "label":
            self._label = value
            self.label_object.set_text(value)
        else:
            raise AttributeError, "Property %s does not exist." % property.name
    
    def set_value(self, value):
        """
        Set the value of the Bar.
        
        @type value: float.
        """
        self.set_property("value", value)
        self.emit("appearance_changed")
    
    def get_value(self):
        """
        Returns the current value of the Bar.
        
        @return: float.
        """
        return self.get_property("value")
    
    def set_color(self, color):
        """
        Set the color of the bar. Color has to either COLOR_AUTO or
        a tuple (r, g, b) with r, g, b in [0, 1].
        
        @type color: a color.
        """
        self.set_property("color", color)
        self.emit("appearance_changed")
    
    def get_color(self):
        """
        Returns the current color of the bar or COLOR_AUTO.
        
        @return: a color.
        """
        return self.get_property("color")
    
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
        self._highlighted = None
        
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
        if bar != self._highlighted:
            self.queue_draw()
        self._highlighted = bar
    
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
            if not info.get_visible(): continue
            x = int(rect.width / float(number_of_bars) * i) + rect.x + (bar_padding // 2)
            percent = float(info.get_value()) / float(max_value)
            bar_height = int(total_height * percent)
            bar_top = int(rect.height*bar_vertical_padding) + total_height - bar_height
            
            # draw the bar
            context.set_source_rgb(*info.get_color())
            context.rectangle(x,  bar_bottom - bar_height, bar_width, bar_height)
            context.fill()
            
            if info == self._highlighted:
                context.set_source_rgba(1, 1, 1, 0.1)
                context.rectangle(x,  bar_bottom - bar_height, bar_width, bar_height)
                context.fill()
            
            if self._labels:
                horizontal_center = x + (bar_width // 2)
                
                # draw the label below the bar
                info.label_object.set_color(color_cairo_to_gdk(*info.get_color()))
                info.label_object.set_max_width(bar_width)
                info.label_object.set_position((horizontal_center, bottom * .95))
                info.label_object.draw(context, rect)
                
                # draw the count at the top of the bar
                info.value_label_object.set_color(color_cairo_to_gdk(*info.get_color()))
                info.value_label_object.set_max_width(bar_width)
                info.value_label_object.set_position((horizontal_center, bar_top))
                info.value_label_object.draw(context, rect)
    
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
        self._do_draw_bars(context, rect)
    
    def add_bar(self, bar):
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
    __gproperties__ = {"name": (gobject.TYPE_STRING, "bar name",
                                "A unique name for the bar.",
                                "", gobject.PARAM_READABLE),
                        "value": (gobject.TYPE_FLOAT,
                                    "value",
                                    "The value.",
                                    0.0, 9999999999.0, 0.0, gobject.PARAM_READABLE),
                        "label": (gobject.TYPE_STRING, "bar label",
                                    "The label for the bar.", "",
                                    gobject.PARAM_READWRITE)}
    
    def __init__(self, name, title=""):
        super(MultiBar, self).__init__()
        self._name = name
        self._label = title
        self.bars = []
        
        self.label_object = label.Label((0, 0), title, anchor=label.ANCHOR_BOTTOM_CENTER)
    
    def do_get_property(self, property):
        if property.name == "visible":
            return self._show
        elif property.name == "antialias":
            return self._antialias
        elif property.name == "name":
            return self._name
        elif property.name == "value":
            return max(x.get_value() for x in self.bars) if self.bars else 0.0
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
    
    def get_value(self):
        """
        Returns the maximum value of the MultiBar.
        
        @return: float.
        """
        return self.get_property("value")
    
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
        color = bar.get_color()
        if color == COLOR_AUTO: bar.set_color(COLORS[len(self.bars) % len(COLORS)])
        self.bars.append(bar)
        bar.connect("appearance_changed", self._cb_appearance_changed)
    
    def get_bar(self, name):
        """
        Returns the Bar with the id 'name' if it exists, None
        otherwise.
        
        @type name: string
        @param name: the id of a Bar
        
        @return: Bar or None.
        """
        for bar in self.bars:
            if bar.get_name() == name:
                return bar
        return None
    
    def _cb_appearance_changed(self, widget):
        self.emit("appearance_changed")

class MultiBarChart(BarChart):
    __gsignals__ = {"multibar-clicked": (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,gobject.TYPE_PYOBJECT,))}
    def __init__(self):
        super(MultiBarChart, self).__init__()
        self.name_map = {}
        self.sub_label_rotation_deg = 320 # amout of rotation in the sub bar labels
    
    def add_bar(self, bar):
        self._bars.append(bar)
        bar.connect("appearance_changed", self._cb_appearance_changed)
    
    def _cb_motion_notify(self, widget, event):
        if not self._enable_mouseover: return
        multibar, subbar = self._get_bar_at_pos(event.x, event.y)
        if subbar != self._highlighted:
            self.queue_draw()
        self._highlighted = subbar
    
    def _cb_button_pressed(self, widget, event):
        multibar, subbar = self._get_bar_at_pos(event.x, event.y)
        if subbar:
            self.emit("multibar-clicked", multibar, subbar)
            self.emit("bar-clicked", multibar)
    
    def _do_draw_bars(self, context, rect):
        """
        Draw the chart.
        
        @type context: cairo.Context
        @param context: The context to draw on.
        @type rect: gtk.gdk.Rectangle
        @param rect: A rectangle representing the charts area.
        """
        if not self._bars: return
        number_of_bars = len(self._bars)
        max_value = max(x.get_value() for x in self._bars)
        bar_padding = 16 # pixels of padding to either side of each bar
        bar_height_factor = .7 # percentage of total height the bars will use
        bar_vertical_padding = (1.0 - bar_height_factor) / 2.0 # space above and below the bars
        total_height = int(rect.height * bar_height_factor) # maximum height for a bar
        bottom = rect.height # y-value of bottom of bar chart
        bar_bottom = bottom * (1.0 - bar_vertical_padding)
        bar_width = int((rect.width-(bar_padding*number_of_bars)) / number_of_bars)
        
        font_size = 12
        context.set_font_size(font_size)
        
        for bar_index, multibar in enumerate(self._bars):
            if not multibar.get_visible(): continue
            multibar_count = len(multibar.bars)
            x = int(rect.width / float(number_of_bars) * bar_index) + rect.x + (bar_padding // 2)
            max_real_height = 0
            for sub_bar_index, sub_bar in enumerate(multibar.bars):
                sub_bar_width = bar_width // multibar_count
                sub_bar_x = x + sub_bar_width * sub_bar_index
                percent = float(sub_bar.get_value()) / float(max_value)
                bar_height = int(total_height * percent)
                bar_top = int(rect.height*bar_vertical_padding) + total_height - bar_height
                
                # draw the bar
                c = sub_bar.get_color()
                context.set_source_rgb(*sub_bar.get_color())
                context.rectangle(sub_bar_x,  bar_bottom - bar_height, sub_bar_width, bar_height)
                context.fill()
            
                if sub_bar == self._highlighted:
                    context.set_source_rgba(1, 1, 1, 0.1)
                    context.rectangle(sub_bar_x,  bar_bottom - bar_height, sub_bar_width, bar_height)
                    context.fill()
                
                if self._labels:
                    horizontal_center = sub_bar_x + (sub_bar_width // 2)
                    # draw the count at the top of the bar
                    sub_bar.value_label_object.set_position((horizontal_center, bar_top))
                    sub_bar.value_label_object.set_color(color_cairo_to_gdk(*sub_bar.get_color()))
                    sub_bar.value_label_object.set_max_width(sub_bar_width)
                    sub_bar.value_label_object.draw(context, rect)
                    # draw the label below the bar
                    sub_bar.label_object.set_position((sub_bar_x + 0.7 * sub_bar_width, bar_bottom))
                    sub_bar.label_object.set_color(color_cairo_to_gdk(*sub_bar.get_color()))
                    sub_bar.label_object.set_anchor(label.ANCHOR_TOP_RIGHT)
                    sub_bar.label_object.set_rotation(self.sub_label_rotation_deg)
                    sub_bar.label_object.draw(context, rect)
                    real_width, real_height = sub_bar.label_object.get_real_dimensions()
                    max_real_height = max(max_real_height, real_height)
            
            if self._labels:
                # draw the label below the bar
                horizontal_center = x + (bar_width // 2)
                vertical_pos = min(bottom, bar_bottom + max_real_height + 15)
                
                multibar.label_object.set_position((horizontal_center, vertical_pos))
                multibar.label_object.set_max_width(bar_width)
                multibar.label_object.draw(context, rect)
    
    def _get_bar_at_pos(self, x, y):
        if not self._bars:
            return None,None
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
        for bar_index, multibar in enumerate(self._bars):
            if not multibar.get_visible(): continue
            multibar_count = len(multibar.bars)
            multibar_x = int(rect.width / float(number_of_bars) * bar_index) + rect.x + (bar_padding // 2)
            max_rotated_height = 0
            for sub_bar_index, sub_bar in enumerate(multibar.bars):
                sub_bar_width = bar_width // multibar_count
                sub_bar_x = multibar_x + sub_bar_width * sub_bar_index
                percent = float(sub_bar.get_value()) / float(max_value)
                bar_height = int(total_height * percent)
                bar_top = int(rect.height*bar_vertical_padding) + total_height - bar_height
            
                if sub_bar_x <= x <= sub_bar_x+sub_bar_width and bar_top <= y <= bar_bottom:
                    return multibar, sub_bar
        
        return None,None
    

