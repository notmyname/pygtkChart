#!/usr/bin/env python
#
#       graph_options.py
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
import gobject

def to_gdkColor(r, g, b):
    return gtk.gdk.Color(int(65535 * r), int(65535 * g), int(65535 * b))
    
def from_gdkColor(c):
    return (c.red / 65535.0, c.green / 65535.0, c.blue / 65535.0)

class GraphControl(gtk.Table):
    
    def __init__(self, graphs=[]):
        gtk.Table.__init__(self, 11, 2)
        self.set_row_spacings(2)
        self.set_col_spacings(6)
        self.graphs = graphs
        self.selected = None
        self._init_combo()
        self._init_draw_options()
        self._init_title()
        self._init_type()
        self._init_point_size()
        self._init_fill_xaxis()
        self._init_show_values()
        self._init_show_title()
        self._init_color()
        self._load_from_selected()
        
    def _init_combo(self):
        store = gtk.ListStore(gobject.TYPE_PYOBJECT, str)
        self.graph_combo = gtk.ComboBox(store)
        cell = gtk.CellRendererText()
        self.graph_combo.pack_start(cell, True)
        self.graph_combo.add_attribute(cell, 'text', 1)
        
        
        for graph in self.graphs:
            store.set(store.append(None), 0, graph, 1, graph.get_title())
        self.graph_combo.set_active(0)
        self.graph_combo.connect("changed", self._cb_combo)
        label = gtk.Label("Select graph:")
        label.set_alignment(0.0, 0.5)
        self.attach(label, 0, 1, 0, 1, xoptions=gtk.FILL, yoptions=gtk.SHRINK)
        self.attach(self.graph_combo, 1, 2, 0, 1, xoptions=gtk.EXPAND|gtk.FILL, yoptions=gtk.SHRINK)
        self.attach(gtk.HSeparator(), 0, 2, 1, 2, xoptions=gtk.EXPAND|gtk.FILL, yoptions=gtk.SHRINK)
        self._cb_combo(self.graph_combo)
        
    def _init_draw_options(self):
        self.checkbox_visible = gtk.CheckButton("Visible")
        self.checkbox_visible.connect("toggled", self._cb_visible_toggled)
        self.attach(self.checkbox_visible, 0, 2, 2, 3, xoptions=gtk.EXPAND|gtk.FILL, yoptions=gtk.SHRINK)
        
        self.checkbox_antialias = gtk.CheckButton("Antialias")
        self.checkbox_antialias.connect("toggled", self._cb_antialias_toggled)
        self.attach(self.checkbox_antialias, 0, 2, 3, 4, xoptions=gtk.EXPAND|gtk.FILL, yoptions=gtk.SHRINK)
        
    def _init_title(self):
        self.entry_graph_title = gtk.Entry()
        self.entry_graph_title.connect("changed", self._cb_graph_title_changed)
        label = gtk.Label("Title:")
        label.set_alignment(0.0, 0.5)
        self.attach(label, 0, 1, 4, 5, xoptions = gtk.FILL, yoptions=gtk.SHRINK)
        self.attach(self.entry_graph_title, 1, 2, 4, 5, xoptions=gtk.EXPAND|gtk.FILL, yoptions=gtk.SHRINK)
        
    def _init_type(self):
        self.combo_type = gtk.combo_box_new_text()
        self.combo_type.append_text("Points")
        self.combo_type.append_text("Lines")
        self.combo_type.append_text("Lines & Points")
        self.combo_type.connect("changed", self._cb_graph_type_changed)
        label = gtk.Label("Graph type:")
        label.set_alignment(0.0, 0.5)
        self.attach(label, 0, 1, 5, 6, xoptions=gtk.FILL, yoptions=gtk.SHRINK)
        self.attach(self.combo_type, 1, 2, 5, 6, xoptions=gtk.EXPAND|gtk.FILL, yoptions=gtk.SHRINK)
        
    def _init_point_size(self):
        self.spin_point_size = gtk.SpinButton()
        self.spin_point_size.set_increments(1, 1)
        self.spin_point_size.set_range(1, 100)
        self.spin_point_size.connect("value-changed", self._cb_graph_point_size)
        label = gtk.Label("Datapoint radius (px):")
        label.set_alignment(0.0, 0.5)
        self.attach(label, 0, 1, 6, 7, xoptions=gtk.FILL, yoptions=gtk.SHRINK)
        self.attach(self.spin_point_size, 1, 2, 6, 7, xoptions=gtk.EXPAND|gtk.FILL, yoptions=gtk.SHRINK)
        
    def _init_fill_xaxis(self):
        self.checkbox_fill_xaxis = gtk.CheckButton("Fill area between graph and xaxis")
        self.checkbox_fill_xaxis.connect("toggled", self._cb_fill_xaxis_toggled)
        self.attach(self.checkbox_fill_xaxis, 0, 2, 7, 8, xoptions=gtk.EXPAND|gtk.FILL, yoptions=gtk.SHRINK)
        
    def _init_show_values(self):
        self.checkbox_show_values = gtk.CheckButton("Show y values art datapoints.")
        self.checkbox_show_values.connect("toggled", self._cb_show_values_toggled)
        self.attach(self.checkbox_show_values, 0, 2, 8, 9, xoptions=gtk.FILL|gtk.EXPAND, yoptions=gtk.SHRINK)
        
    def _init_show_title(self):
        self.checkbox_show_title = gtk.CheckButton("Show graph title.")
        self.checkbox_show_title.connect("toggled", self._cb_show_title_toggled)
        self.attach(self.checkbox_show_title, 0, 2, 9, 10, xoptions=gtk.EXPAND|gtk.FILL, yoptions=gtk.SHRINK)
        
    def _init_color(self):
        self.color_chooser = gtk.ColorButton()
        self.color_chooser.connect("color-set", self._cb_graph_color_changed)
        label = gtk.Label("Graph color:")
        label.set_alignment(0.0, 0.5)
        self.attach(label, 0, 1, 10, 11, xoptions=gtk.FILL, yoptions=gtk.SHRINK)
        self.attach(self.color_chooser, 1, 2, 10, 11, xoptions=gtk.EXPAND|gtk.FILL, yoptions=gtk.SHRINK)
        
    def _load_from_selected(self):
        try:
            self.checkbox_visible.set_active(self.selected.get_visible())
            self.checkbox_antialias.set_active(self.selected.get_antialias())
            self.entry_graph_title.set_text(self.selected.get_title())
            self.combo_type.set_active(self.selected.get_type() - 1)
            self.spin_point_size.set_value(self.selected.get_point_size())
            self.checkbox_fill_xaxis.set_active(self.selected.get_fill_xaxis())
            self.checkbox_show_values.set_active(self.selected.get_show_values())
            self.checkbox_show_title.set_active(self.selected.get_show_title())
            self.color_chooser.set_color(to_gdkColor(*self.selected.get_color()))
        except:
            pass
        
    def _cb_combo(self, widget):
        iter = widget.get_active_iter()
        model = widget.get_model()
        graph = model.get_value(iter, 0)
        self.selected = graph 
        print "Selected", graph.get_property("name")
        self._load_from_selected()
        
    def _cb_visible_toggled(self, button):
        self.selected.set_visible(button.get_active())
        
    def _cb_antialias_toggled(self, button):
        self.selected.set_antialias(button.get_active())

    def _cb_graph_title_changed(self, entry):
        self.selected.set_title(entry.get_text())
        
    def _cb_graph_type_changed(self, combo):
        self.selected.set_type(combo.get_active() + 1)
        
    def _cb_graph_point_size(self, spin):
        self.selected.set_point_size(int(spin.get_value()))
        
    def _cb_fill_xaxis_toggled(self, button):
        self.selected.set_fill_xaxis(button.get_active())

    def _cb_show_values_toggled(self, button):
        self.selected.set_show_values(button.get_active())
        
    def _cb_show_title_toggled(self, button):
        self.selected.set_show_title(button.get_active())

    def _cb_graph_color_changed(self, chooser):
        self.selected.set_color(from_gdkColor(chooser.get_color()))
