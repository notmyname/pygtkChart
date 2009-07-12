#!/usr/bin/env python
#
#       pie_chart_options.py
#       
#       Copyright 2009 Sven Festersen <sven@sven-festersen.de>
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
#!/usr/bin/env python
#
#       line_chart_options.py
#       
#       Copyright 2009 Sven Festersen <sven@sven-laptop>
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
import gtk
import pygtk

def to_gdkColor(r, g, b):
    return gtk.gdk.Color(int(65535 * r), int(65535 * g), int(65535 * b))
    
def from_gdkColor(c):
    return (c.red / 65535.0, c.green / 65535.0, c.blue / 65535.0)

class ChartControl(gtk.Table):
    
    def __init__(self, chart):
        gtk.Table.__init__(self, 21, 3)
        self.set_row_spacings(2)
        self.set_col_spacings(6)
        self.set_border_width(6)
        self.chart = chart
        self._init_title()
        self._init_background()
        self._init_rotation()
        self._init_labels()
        self._init_mouseover()
        
    def _init_title(self):
        self.entry_chart_title = gtk.Entry()
        self.entry_chart_title.set_text(self.chart.title.get_text())
        self.entry_chart_title.connect("changed", self._cb_title_changed)
        label = gtk.Label("Title:")
        label.set_alignment(0.0, 0.5)
        self.attach(label, 0, 1, 0, 1, xoptions=gtk.FILL, yoptions=gtk.SHRINK)
        self.attach(self.entry_chart_title, 1, 3, 0, 1, xoptions=gtk.EXPAND|gtk.FILL, yoptions=gtk.SHRINK)
        
        self.color_title_chooser = gtk.ColorButton()
        self.color_title_chooser.set_color(self.chart.title.get_color())
        self.color_title_chooser.connect("color-set", self._cb_title_color_changed)
        label = gtk.Label("Title color:")
        label.set_alignment(0.0, 0.5)
        self.attach(label, 0, 1, 1, 2, xoptions=gtk.FILL, yoptions=gtk.SHRINK)
        self.attach(self.color_title_chooser, 1, 3, 1, 2, xoptions=gtk.EXPAND|gtk.FILL, yoptions=gtk.SHRINK)
        
        self.title_visible = gtk.CheckButton("Show title")
        self.title_visible.set_active(self.chart.title.get_visible())
        self.title_visible.connect("toggled", self._cb_title_visible_changed)
        self.attach(self.title_visible, 0, 3, 2, 3, xoptions=gtk.EXPAND|gtk.FILL, yoptions=gtk.SHRINK)
        
        self.title_antialias = gtk.CheckButton("Antialias title")
        self.title_antialias.set_active(self.chart.title.get_antialias())
        self.title_antialias.connect("toggled", self._cb_title_antialias_changed)
        self.attach(self.title_antialias, 0, 3, 3, 4, xoptions=gtk.EXPAND|gtk.FILL, yoptions=gtk.SHRINK)
        
        self.attach(gtk.HSeparator(), 0, 3, 4, 5, xoptions=gtk.EXPAND|gtk.FILL, yoptions=gtk.SHRINK)
        
    def _init_background(self):
        self.radio_bg_color = gtk.RadioButton(label="Background color:")
        self.radio_bg_color.connect("toggled", self._cb_bg_type_changed)
        self.color_bg_chooser = gtk.ColorButton()
        self.color_bg_chooser.set_color(to_gdkColor(*self.chart.background.get_color()))
        self.color_bg_chooser.connect("color-set", self._cb_bg_color_changed)
        self.attach(self.radio_bg_color, 0, 1, 5, 6, xoptions=gtk.FILL, yoptions=gtk.SHRINK)
        self.attach(self.color_bg_chooser, 1, 3, 5, 6, xoptions=gtk.EXPAND|gtk.FILL, yoptions=gtk.SHRINK)
        
        self.radio_bg_gradient = gtk.RadioButton(self.radio_bg_color, "Background gradient:")
        self.radio_bg_gradient.connect("toggled", self._cb_bg_type_changed)
        self.color_bg_grad1 = gtk.ColorButton()
        self.color_bg_grad1.set_color(to_gdkColor(1, 1, 1))
        self.color_bg_grad1.connect("color-set", self._cb_bg_gradient_changed)
        self.color_bg_grad2 = gtk.ColorButton()
        self.color_bg_grad2.set_color(to_gdkColor(1, 1, 1))
        self.color_bg_grad2.connect("color-set", self._cb_bg_gradient_changed)
        self.attach(self.radio_bg_gradient, 0, 1, 6, 7, xoptions=gtk.FILL, yoptions=gtk.SHRINK)
        self.attach(self.color_bg_grad1, 1, 2, 6, 7, xoptions=gtk.EXPAND|gtk.FILL, yoptions=gtk.SHRINK)
        self.attach(self.color_bg_grad2, 2, 3, 6, 7, xoptions=gtk.EXPAND|gtk.FILL, yoptions=gtk.SHRINK)
        
        self.radio_bg_image = gtk.RadioButton(self.radio_bg_color, "Background image (png file):")
        self.radio_bg_image.connect("toggled", self._cb_bg_type_changed)
        self.file_chooser_image = gtk.FileChooserButton("Select background image")
        self.file_chooser_image.set_action(gtk.FILE_CHOOSER_ACTION_OPEN)
        self.file_chooser_image.connect("selection-changed", self._cb_bg_image_changed)
        self.attach(self.radio_bg_image, 0, 1, 7, 8, xoptions=gtk.FILL, yoptions=gtk.SHRINK)
        self.attach(self.file_chooser_image, 1, 3, 7, 8, xoptions=gtk.EXPAND|gtk.FILL, yoptions=gtk.SHRINK)
        
        self.attach(gtk.HSeparator(), 0, 3, 8, 9, xoptions=gtk.EXPAND|gtk.FILL, yoptions=gtk.SHRINK)
        
        self._cb_bg_type_changed(None)
        
    def _init_rotation(self):
        self.checkbutton_scroll = gtk.CheckButton("Enable scrolling")
        self.checkbutton_scroll.set_active(self.chart.get_enable_scroll())
        self.checkbutton_scroll.connect("toggled", self._cb_scroll_changed)
        self.attach(self.checkbutton_scroll, 0, 3, 9, 10, xoptions=gtk.EXPAND|gtk.FILL, yoptions=gtk.SHRINK)
        
        self.scale_angle = gtk.HScale()
        self.scale_angle.set_range(0, 360)
        self.scale_angle.connect("change-value", self._cb_rotate_changed)
        label = gtk.Label("Rotation angle (degrees):")
        label.set_alignment(0.0, 0.5)
        self.attach(label, 0, 1, 10, 11, xoptions=gtk.FILL, yoptions=gtk.SHRINK)
        self.attach(self.scale_angle, 1, 3, 10, 11, xoptions=gtk.EXPAND|gtk.FILL, yoptions=gtk.SHRINK)
        self.chart.connect("notify", self._cb_chart_notify)
        
        self.attach(gtk.HSeparator(), 0, 3, 11, 12, xoptions=gtk.EXPAND|gtk.FILL, yoptions=gtk.SHRINK)
        
    def _init_labels(self):
        self.checkbutton_show_labels = gtk.CheckButton("Show labels")
        self.checkbutton_show_labels.set_active(self.chart.get_draw_labels())
        self.checkbutton_show_labels.connect("toggled", self._cb_labels_changed)
        self.attach(self.checkbutton_show_labels, 0, 3, 12, 13, xoptions=gtk.EXPAND|gtk.FILL, yoptions=gtk.SHRINK)
        
        self.checkbutton_show_percent = gtk.CheckButton("Show percentage in labels")
        self.checkbutton_show_percent.set_active(self.chart.get_show_percentage())
        self.checkbutton_show_percent.connect("toggled", self._cb_percentage_changed)
        self.attach(self.checkbutton_show_percent, 0, 3, 13, 14, xoptions=gtk.EXPAND|gtk.FILL, yoptions=gtk.SHRINK)
        
        self.checkbutton_show_values = gtk.CheckButton("Show values in labels")
        self.checkbutton_show_values.set_active(self.chart.get_show_values())
        self.checkbutton_show_values.connect("toggled", self._cb_values_changed)
        self.attach(self.checkbutton_show_values, 0, 3, 14, 15, xoptions=gtk.EXPAND|gtk.FILL, yoptions=gtk.SHRINK)
        
        self.attach(gtk.HSeparator(), 0, 3, 15, 16, xoptions=gtk.EXPAND|gtk.FILL, yoptions=gtk.SHRINK)
        
    def _init_mouseover(self):
        self.checkbutton_mouseover = gtk.CheckButton("Enable mouseover effect")
        self.checkbutton_mouseover.set_active(self.chart.get_enable_mouseover())
        self.checkbutton_mouseover.connect("toggled", self._cb_mouseover_changed)
        self.attach(self.checkbutton_mouseover, 0, 3, 16, 17, xoptions=gtk.EXPAND|gtk.FILL, yoptions=gtk.SHRINK)
        
    def _cb_title_changed(self, entry):
        self.chart.title.set_text(entry.get_text())
        
    def _cb_title_color_changed(self, chooser):
        self.chart.title.set_color(chooser.get_color())
        
    def _cb_title_visible_changed(self, button):
        self.chart.title.set_visible(button.get_active())
        
    def _cb_title_antialias_changed(self, button):
        self.chart.title.set_antialias(button.get_active())
        
    def _cb_bg_type_changed(self, button):
        self.color_bg_chooser.set_sensitive(self.radio_bg_color.get_active())
        self.color_bg_grad1.set_sensitive(self.radio_bg_gradient.get_active())
        self.color_bg_grad2.set_sensitive(self.radio_bg_gradient.get_active())
        self.file_chooser_image.set_sensitive(self.radio_bg_image.get_active())
        
        if self.radio_bg_color.get_active():
            self.chart.background.set_color(from_gdkColor(self.color_bg_chooser.get_color()))
        elif self.radio_bg_gradient.get_active():
            self.chart.background.set_gradient(from_gdkColor(self.color_bg_grad1.get_color()), from_gdkColor(self.color_bg_grad2.get_color()))
        elif self.radio_bg_image.get_active():
            self.chart.background.set_image(self.file_chooser_image.get_filename())      
        
    def _cb_bg_color_changed(self, chooser):
        self.chart.background.set_color(from_gdkColor(chooser.get_color()))
        
    def _cb_bg_gradient_changed(self, chooser):
        self.chart.background.set_gradient(from_gdkColor(self.color_bg_grad1.get_color()), from_gdkColor(self.color_bg_grad2.get_color()))
        
    def _cb_bg_image_changed(self, chooser):
        self.chart.background.set_image(chooser.get_filename())       

    def _cb_scroll_changed(self, button):
        self.chart.set_enable_scroll(button.get_active())
        
    def _cb_rotate_changed(self, range, scroll, value):
        self.chart.set_rotate(min(value, 360))
        
    def _cb_chart_notify(self, chart, property):
        if property.name == "rotate":
            self.scale_angle.set_value(chart.get_rotate())
            
    def _cb_labels_changed(self, button):
        self.chart.set_draw_labels(button.get_active())
        
    def _cb_percentage_changed(self, button):
        self.chart.set_show_percentage(button.get_active())
        
    def _cb_values_changed(self, button):
        self.chart.set_show_values(button.get_active())
        
    def _cb_mouseover_changed(self, button):
        self.chart.set_enable_mouseover(button.get_active())
