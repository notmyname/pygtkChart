#!/usr/bin/env python
#
#       area_options.py
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
import gobject
import gtk
import pygtk

def to_gdkColor(r, g, b):
    return gtk.gdk.Color(int(65535 * r), int(65535 * g), int(65535 * b))
    
def from_gdkColor(c):
    return (c.red / 65535.0, c.green / 65535.0, c.blue / 65535.0)

class AreaControl(gtk.Table):
    
    def __init__(self, areas):
        gtk.Table.__init__(self, 10, 2)
        self.areas = areas
        self.selected = None
        self.set_row_spacings(2)
        self.set_col_spacings(6)
        self._init_combo()
        self._init_draw_options()
        self._init_title()
        self._init_value()
        self._init_color()
        self._load_from_selected()
        
    def _init_combo(self):
        store = gtk.ListStore(gobject.TYPE_PYOBJECT, str)
        self.area_combo = gtk.ComboBox(store)
        cell = gtk.CellRendererText()
        self.area_combo.pack_start(cell, True)
        self.area_combo.add_attribute(cell, 'text', 1)
        
        for area in self.areas:
            store.set(store.append(None), 0, area, 1, area.get_label())
        self.area_combo.set_active(0)
        self.area_combo.connect("changed", self._cb_combo)
        label = gtk.Label("Select area:")
        label.set_alignment(0.0, 0.5)
        self.attach(label, 0, 1, 0, 1, xoptions=gtk.FILL, yoptions=gtk.SHRINK)
        self.attach(self.area_combo, 1, 2, 0, 1, xoptions=gtk.EXPAND|gtk.FILL, yoptions=gtk.SHRINK)
        self.attach(gtk.HSeparator(), 0, 2, 1, 2, xoptions=gtk.EXPAND|gtk.FILL, yoptions=gtk.SHRINK)
        self._cb_combo(self.area_combo)
        
    def _init_draw_options(self):
        self.checkbox_visible = gtk.CheckButton("Visible")
        self.checkbox_visible.connect("toggled", self._cb_visible_toggled)
        self.attach(self.checkbox_visible, 0, 2, 2, 3, xoptions=gtk.EXPAND|gtk.FILL, yoptions=gtk.SHRINK)
        
        self.checkbox_antialias = gtk.CheckButton("Antialias")
        self.checkbox_antialias.connect("toggled", self._cb_antialias_toggled)
        self.attach(self.checkbox_antialias, 0, 2, 3, 4, xoptions=gtk.EXPAND|gtk.FILL, yoptions=gtk.SHRINK)
        
    def _init_title(self):
        self.entry_area_title = gtk.Entry()
        self.entry_area_title.connect("changed", self._cb_area_title_changed)
        label = gtk.Label("Title:")
        label.set_alignment(0.0, 0.5)
        self.attach(label, 0, 1, 4, 5, xoptions = gtk.FILL, yoptions=gtk.SHRINK)
        self.attach(self.entry_area_title, 1, 2, 4, 5, xoptions=gtk.EXPAND|gtk.FILL, yoptions=gtk.SHRINK)
        
    def _init_value(self):
        self.spin_value = gtk.SpinButton()
        self.spin_value.set_increments(1, 1)
        self.spin_value.set_range(1, 999999)
        self.spin_value.connect("value-changed", self._cb_value_changed)
        label = gtk.Label("Value:")
        label.set_alignment(0.0, 0.5)
        self.attach(label, 0, 1, 5, 6, xoptions = gtk.FILL, yoptions=gtk.SHRINK)
        self.attach(self.spin_value, 1, 2, 5, 6, xoptions=gtk.EXPAND|gtk.FILL, yoptions=gtk.SHRINK)
        
    def _init_color(self):
        self.color_chooser = gtk.ColorButton()
        self.color_chooser.connect("color-set", self._cb_area_color_changed)
        label = gtk.Label("Area color:")
        label.set_alignment(0.0, 0.5)
        self.attach(label, 0, 1, 6, 7, xoptions=gtk.FILL, yoptions=gtk.SHRINK)
        self.attach(self.color_chooser, 1, 2, 6, 7, xoptions=gtk.EXPAND|gtk.FILL, yoptions=gtk.SHRINK)
        
    def _load_from_selected(self):
        try:
            self.checkbox_visible.set_active(self.selected.get_visible())
            self.checkbox_antialias.set_active(self.selected.get_antialias())
            self.entry_area_title.set_text(self.selected.get_label())
            self.spin_value.set_value(self.selected.get_value())
            self.color_chooser.set_color(to_gdkColor(*self.selected.get_color()))
        except:
            pass
        
    def _cb_combo(self, widget):
        iter = widget.get_active_iter()
        model = widget.get_model()
        area = model.get_value(iter, 0)
        self.selected = area 
        print "Selected", area.get_property("name")
        self._load_from_selected()
        
    def _cb_visible_toggled(self, button):
        self.selected.set_visible(button.get_active())
        
    def _cb_antialias_toggled(self, button):
        self.selected.set_antialias(button.get_active())
        
    def _cb_area_title_changed(self, entry):
        self.selected.set_label(entry.get_text())
        
    def _cb_value_changed(self, spin):
        self.selected.set_value(spin.get_value())
        
    def _cb_area_color_changed(self, chooser):
        self.selected.set_color(from_gdkColor(chooser.get_color()))
