"""
Contains the BarChart widget.
Author: John Dickinson (john@johnandkaren.com)
"""
__docformat__ = "epytext"
import cairo
import gtk
import os
import collections # for defaultdict
import math # for pi

from pygtk_chart.basics import *
from pygtk_chart import chart

COLORS = color_list_from_file(os.path.dirname(__file__) + "/data/tango.color")

class BarChart(chart.Chart):
    """
    A widget that shows a bar chart. The following objects can be accessed:
     - BarChart.background (inherited from chart.Chart)
     - BarChart.title (inherited from chart.Chart)
     - BarChart.data
    """    
    def __init__(self):
        super(BarChart, self).__init__()
        self.data = {}
        self._show_labels = True
        self.bar_order = []
        
    def _do_draw(self, context, rect):
        """
        Draw the chart.
        
        @type context: cairo.Context
        @param context: The context to draw on.
        @type rect: gtk.gdk.Rectangle
        @param rect: A rectangle representing the charts area.
        """
        number_of_bars = len(self.data)
        max_value = max(x['n'] for x in self.data.values())
        bar_padding = 16 # pixels of padding to either side of each bar
        bar_height_factor = .8 # percentage of total height the bars will use
        bar_vertical_padding = (1.0 - bar_height_factor) / 2.0 # space above and below the bars
        total_height = int(rect.height * bar_height_factor) # maximum height for a bar
        bottom = rect.height # y-value of bottom of bar chart
        bar_bottom = bottom * (1.0 - bar_vertical_padding)
        bar_width = int((rect.width-(bar_padding*number_of_bars)) / number_of_bars)
        
        for i,name in enumerate(self.bar_order):
            info = self.data[name]
            x = int(rect.width / float(number_of_bars) * i) + rect.x + (bar_padding // 2)
            percent = float(info['n']) / float(max_value)
            bar_height = int(total_height * percent)
            bar_top = int(rect.height*bar_vertical_padding) + total_height - bar_height
            
            # draw the bar
            c = info['color']
            context.set_source_rgb(c[0], c[1], c[2])
            context.move_to(x, bar_bottom)
            context.line_to(x, bar_top)
            context.line_to(x+bar_width, bar_top)
            context.line_to(x+bar_width, bar_bottom)
            context.close_path()
            context.fill()
            context.stroke()
            
            if self._show_labels:
                # draw the label below the bar
                title = info['label']
                label_height, label_width = context.text_extents(title)[3:5]
                label_x = x + (bar_width // 2) - (label_width // 2)
                context.move_to(label_x, bottom * .95)
                context.show_text(title)
                context.stroke()
                
                # draw the count at the top of the bar
                count = '%d' % info['n']
                count_height, count_width = context.text_extents(count)[3:5]
                count_x = x + (bar_width // 2) - (count_width // 2)
                context.move_to(count_x, bar_top-1)
                context.show_text(count)
                context.stroke()
        
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
            self._do_draw(context, rect)
        
    def set_data(self, data):
        """
        Set the data to show in the bar chart. data has to be a list of
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
        self.bar_order = []
        for (name, label, n) in data:
            if name not in self.bar_order:
                self.bar_order.append(name)
            self.data[name] = {"label": label,
                                "n": int(n),
                                "color": COLORS[len(self.data) % len(COLORS)]}
            
    def set_show_labels(self, show):
        """
        Use set_show_labels() to set whether labels should be shown at the
        edges of the sectors.
        
        @type show: boolean
        @param show: If False, labels won't be shown.
        """
        self._show_labels = show

class MultiBarChart(BarChart):
    def __init__(self):
        super(MultiBarChart, self).__init__()
        self.sub_bar_order = []
        self.name_map = {}
        self.sub_label_rotation_deg = 15.0 # amout of rotation in the sub bar labels
    
    def _do_draw(self, context, rect):
        """
        Draw the chart.
        
        @type context: cairo.Context
        @param context: The context to draw on.
        @type rect: gtk.gdk.Rectangle
        @param rect: A rectangle representing the charts area.
        """
        number_of_bars = len(self.data)
        max_value = -9999999
        for name in self.data:
            for sub_label in self.data[name]:
                max_value = max(max_value, self.data[name][sub_label]['n'])
        bar_padding = 16 # pixels of padding to either side of each bar
        bar_height_factor = .75 # percentage of total height the bars will use
        bar_vertical_padding = (1.0 - bar_height_factor) / 2.0 # space above and below the bars
        total_height = int(rect.height * bar_height_factor) # maximum height for a bar
        bottom = rect.height # y-value of bottom of bar chart
        bar_bottom = bottom * (1.0 - bar_vertical_padding)
        bar_width = int((rect.width-(bar_padding*number_of_bars)) / number_of_bars)
        font_size = 12
        context.set_font_size(font_size)
        for bar_index, name in enumerate(self.bar_order):
            data_list = self.data[name]
            multibar_count = len(data_list)
            x = int(rect.width / float(number_of_bars) * bar_index) + rect.x + (bar_padding // 2)
            max_rotated_height = 0
            for sub_bar_index, sub_label in enumerate(self.sub_bar_order):
                info = self.data[name][sub_label]
                sub_bar_width = bar_width // multibar_count
                sub_bar_x = x + sub_bar_width * sub_bar_index
                percent = float(info['n']) / float(max_value)
                bar_height = max(1, int(total_height * percent))
                bar_top = int(rect.height*bar_vertical_padding) + total_height - bar_height
                
                # draw the bar
                c = info['color']
                context.set_source_rgb(c[0], c[1], c[2])
                context.move_to(sub_bar_x, bar_bottom)
                context.line_to(sub_bar_x, bar_top)
                context.line_to(sub_bar_x+sub_bar_width, bar_top)
                context.line_to(sub_bar_x+sub_bar_width, bar_bottom)
                context.close_path()
                context.fill()
                context.stroke()
                
                if self._show_labels:
                    # draw the count at the top of the bar
                    count = '%d' % info['n']
                    count_height, count_width = context.text_extents(count)[3:5]
                    count_x = sub_bar_x + (sub_bar_width // 2) - (count_width // 2)
                    context.move_to(count_x, bar_top-1)
                    context.show_text(count)
                    context.stroke()
                    # draw the label below the bar
                    #context.set_source_rgb(0, 0, 0)
                    title = sub_label
                    label_height, label_width = context.text_extents(title)[3:5]
                    rotation_rad = math.pi*self.sub_label_rotation_deg / 180.0
                    rotated_height = max(label_height, abs(math.sin(rotation_rad) * label_width))
                    rotated_width =  max(label_height, abs(math.cos(rotation_rad) * label_width))
                    max_rotated_height = max(max_rotated_height, int(rotated_height)+1)
                    label_x = sub_bar_x + (sub_bar_width // 3)
                    context.move_to(label_x, bar_bottom + 10)
                    context.rotate(rotation_rad)
                    context.show_text(title)
                    context.rotate(-rotation_rad)
                    context.stroke()
            
            if data_list and self._show_labels:
                # draw the label below the bar
                context.set_source_rgb(0, 0, 0)
                title = self.name_map[name]
                label_height, label_width = context.text_extents(title)[3:5]
                label_x = x + (bar_width // 2) - (label_width // 2)
                label_y = min(bottom, bar_bottom + max_rotated_height + 25)#(label_height + 3)*2
                context.move_to(label_x, label_y)
                context.show_text(title)
                context.stroke()
        
    def set_data(self, data):
        """
        Set the data to show in the bar chart. data has to be a list of
        (name, label, sublabel, n) tuples. The name value is an identifier, it should
        be unique. label is the text that will be shown next to the
        corresponding sector. n has to be a positive number.
        
        Example (the population of G8 members, source: wikipedia)::

            population = [("usa", "United States", "United States", 303346630),
                            ("d", "Germany", "Germany", 82244000),
                            ("uk", "United Kingdom", "United Kingdom", 60587300),
                            ("jap", "Japan", "Japan", 127417244),
                            ("fr", "France", "France", 64473140),
                            ("i", "Italy", "Italy", 59619290),
                            ("cdn", "Canada", "Canada", 32976026),
                            ("rus", "Russia", "Russia", 142400000)]
            set_data(population)        
        
        @type data: list
        @param data: The data list.
        """
        self.data = collections.defaultdict(dict)
        self.max_len = 0
        self.bar_order = []
        self.sub_bar_order = []
        self.name_map = {}
        color_map = dict.fromkeys(x[2] for x in data)
        for i, sub_label in enumerate(sorted(color_map)):
            color_map[sub_label] = COLORS[i % len(COLORS)]
        all_sub_labels = set()
        for name, main_label, sub_label, n in data:
            if name not in self.bar_order:
                self.bar_order.append(name)
            if sub_label not in self.sub_bar_order:
                self.sub_bar_order.append(sub_label)
            self.name_map[name] = main_label
            self.data[name][sub_label] = {'n': int(n),
                                          'color': color_map[sub_label]}
            self.max_len = max(self.max_len, len(self.data[name]))
            all_sub_labels.add(sub_label)
        
        # make sure all sub labels are represented for every main label
        for name in self.data:
            for sub_label in all_sub_labels:
                if sub_label not in self.data[name]:
                    self.data[name][sub_label] = {'n': 0,
                                                  'color': color_map[sub_label]}
