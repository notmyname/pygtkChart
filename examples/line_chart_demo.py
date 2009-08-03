#!/usr/bin/env python
#
#       new_line_chart_demo.py
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
import gtk.glade
import math
import pygtk

from pygtk_chart import line_chart


def to_gdkColor(r, g, b):
    return gtk.gdk.Color(int(65535 * r), int(65535 * g), int(65535 * b))
    
def from_gdkColor(c):
    return (c.red / 65535.0, c.green / 65535.0, c.blue / 65535.0)


class Gui:
    
    def __init__(self):
        self._widgets = gtk.glade.XML("line_chart_demo.glade", "main")
        
        self._graph = None
        
        self._init_chart()
        self._init_chart_data()
        self._init_graph_select()
        self._init_callbacks()
        
        self._w("main").show_all()
        
    def _w(self, name):
        return self._widgets.get_widget(name)
        
    def _init_chart(self):
        self._chart = line_chart.LineChart()
        self._chart.title.set_text("LineChart demo")
        self._chart.legend.set_visible(True)
        self._chart.legend.set_position(line_chart.POSITION_BOTTOM_RIGHT)
        self._w("hpaned1").add2(self._chart)
        
        normal_dist = line_chart.graph_new_from_function(lambda x: math.exp(-0.5 * (x - 3) ** 2), -1, 10, "normal_dist", 50)
        normal_dist.set_type(line_chart.GRAPH_LINES)
        normal_dist.set_title("Normal distribution")
        self._chart.add_graph(normal_dist)
        
        cubic_exp = line_chart.graph_new_from_function(lambda x: 0.8 * x ** 3 * math.exp(-x / 2.0), -1, 10, "cubic", 50)
        cubic_exp.set_type(line_chart.GRAPH_LINES)
        cubic_exp.set_line_style(line_chart.LINE_STYLE_DASHED_ASYMMETRIC)
        cubic_exp.set_title("Test")
        self._chart.add_graph(cubic_exp)
        
        filegrapha = line_chart.graph_new_from_file("line_chart_test_data", "filea", 0, 1, xerror_col=4, yerror_col=3)
        filegrapha.set_title("File data 0:1")
        self._chart.add_graph(filegrapha)
        
        filegraphb = line_chart.graph_new_from_file("line_chart_test_data", "fileb", 0, 2)
        filegraphb.set_title("File data 0:2")
        self._chart.add_graph(filegraphb)
        
    def _init_chart_data(self):
        chart = self._chart
        
        #chart title
        self._w("chart_title_show").set_active(chart.title.get_visible())
        self._w("chart_title_text").set_text(chart.title.get_text())
        self._w("chart_title_color").set_color(chart.title.get_color())
        
        #chart background
        self._bg_picture_chooser = gtk.FileChooserButton("Choose background image")
        self._w("table2").attach(self._bg_picture_chooser, 1, 3, 2, 3, yoptions=gtk.FILL)
        self._w("chart_background_gradient1").set_sensitive(False)
        self._w("chart_background_gradient2").set_sensitive(False)
        self._bg_picture_chooser.set_sensitive(False)
        
        #chart grid
        self._w("chart_grid_color").set_color(chart.grid.get_color())
        self._w("chart_grid_show_horizontal").set_active(chart.grid.get_draw_horizontal_lines())
        self._w("chart_grid_style_horizontal").set_active(chart.grid.get_line_style_horizontal())
        self._w("chart_grid_show_vertical").set_active(chart.grid.get_draw_vertical_lines())
        self._w("chart_grid_style_vertical").set_active(chart.grid.get_line_style_vertical())
        
        #chart xaxis
        self._w("chart_xaxis_show").set_active(chart.xaxis.get_visible())
        self._w("chart_xaxis_label").set_text(chart.xaxis.get_label())
        self._w("chart_xaxis_show_tics").set_active(chart.xaxis.get_show_tics())
        self._w("chart_xaxis_show_tic_labels").set_active(chart.xaxis.get_show_tic_labels())
        self._w("chart_xaxis_position").set_active(chart.xaxis.get_position() - 5)
        
        #chart yaxis
        self._w("chart_yaxis_show").set_active(chart.yaxis.get_visible())
        self._w("chart_yaxis_label").set_text(chart.yaxis.get_label())
        self._w("chart_yaxis_show_tics").set_active(chart.yaxis.get_show_tics())
        self._w("chart_yaxis_show_tic_labels").set_active(chart.yaxis.get_show_tic_labels())
        self._w("chart_yaxis_position").set_active(chart.yaxis.get_position() - 5)
        
        #chart ranges
        self._w("chart_xrange_min").set_value(self._chart.get_xrange()[0])
        self._w("chart_xrange_max").set_value(self._chart.get_xrange()[1])
        self._w("chart_yrange_min").set_value(self._chart.get_yrange()[0])
        self._w("chart_yrange_max").set_value(self._chart.get_yrange()[1])
        
        #chart legend
        self._w("chart_legend_show").set_active(chart.legend.get_visible())
        self._w("chart_legend_position").set_active(chart.legend.get_position() - 8)
        
    def _init_graph_select(self):
        #fill graph list
        store = gtk.ListStore(gobject.TYPE_PYOBJECT, str)
        cell = gtk.CellRendererText()
        self._w("graph_select").pack_start(cell, True)
        self._w("graph_select").add_attribute(cell, 'text', 1)
        self._w("graph_select").set_model(store)
        
        for graph in self._chart:
            store.set(store.append(None), 0, graph, 1, graph.get_title())
            
        self._w("graph_select").set_active(0)
        self._cb_graph_changed(self._w("graph_select"))
            
        self._datapoint_chooser = gtk.FileChooserButton("Choose datapoint graphic")
        self._datapoint_chooser.set_sensitive(False)
        self._w("table8").attach(self._datapoint_chooser, 1, 2, 3, 4, yoptions=gtk.FILL, xoptions=gtk.FILL|gtk.EXPAND)
        
        cell = gtk.CellRendererText()
        self._w("graph_fill_graph").pack_start(cell, True)
        self._w("graph_fill_graph").add_attribute(cell, 'text', 1)
            
    def _init_graph_data(self):
        if not self._graph: return
        
        #graph basics
        self._w("graph_show").set_active(self._graph.get_visible())        
        self._w("graph_antialias").set_active(self._graph.get_antialias())        
        self._w("graph_title").set_text(self._graph.get_title())
        self._w("graph_show_title").set_active(self._graph.get_show_title())
        self._w("graph_color").set_color(self._graph.get_color())
        
        #graph lines and points
        self._w("graph_type").set_active(self._graph.get_type() - 1)
        self._w("graph_line_style").set_active(self._graph.get_line_style())
        if type(self._graph.get_point_style()) == gtk.gdk.Pixbuf:
            self._w("graph_point_style").set_active(6)
        else:
            self._w("graph_point_style").set_active(self._graph.get_point_style())
        self._w("graph_point_size").set_value(self._graph.get_point_size())
        self._w("graph_clickable").set_active(self._graph.get_clickable())
        
        #graph errors
        self._w("graph_show_xerrors").set_active(self._graph.get_show_xerrors())
        self._w("graph_show_yerrors").set_active(self._graph.get_show_yerrors())
        
        #graph filling
        self._w("graph_fill_value").set_sensitive(False)
        self._w("graph_fill_graph").set_sensitive(False)
            
        i = 0
        n = 0
        store = gtk.ListStore(gobject.TYPE_PYOBJECT, str)        
        for graph in self._chart:
            if graph == self._graph: continue
            store.set(store.append(None), 0, graph, 1, graph.get_title())
            if graph == self._graph.get_fill_to(): n = i
            i += 1
        self._w("graph_fill_graph").set_model(store)
        self._w("graph_fill_graph").set_active(n)
        
        if self._graph.get_fill_to() == None:
            self._w("graph_fill_type_none").set_active(True)
        elif type(self._graph.get_fill_to()) in [int, float]:
            self._w("graph_fill_type_value").set_active(True)
            self._w("graph_fill_value").set_sensitive(True)
        elif type(self._graph.get_fill_to()) == line_chart.Graph:
            self._w("graph_fill_type_graph").set_active(True)
            self._w("graph_fill_graph").set_sensitive(True)
            
        if self._graph.get_fill_color() == line_chart.COLOR_AUTO:
            self._w("graph_fill_color").set_color(self._graph.get_color())
        else:
            self._w("graph_fill_color").set_color(self._graph.get_fill_color())
            
        self._w("graph_fill_opacity").set_value(self._graph.get_fill_opacity())
        
    def _init_callbacks(self):
        self._w("main").connect("destroy", self._cb_close)
        
        #chart title
        self._w("chart_title_show").connect("toggled", self._cb_chart_title_show_changed)
        self._w("chart_title_text").connect("changed", self._cb_chart_title_text_changed)
        self._w("chart_title_color").connect("color-set", self._cb_chart_title_color_changed)
        
        #chart background
        self._w("chart_background_type_color").connect("toggled", self._cb_chart_background_type_changed)
        self._w("chart_background_type_gradient").connect("toggled", self._cb_chart_background_type_changed)
        self._w("chart_background_type_image").connect("toggled", self._cb_chart_background_type_changed)
        self._w("chart_background_color").connect("color-set", self._cb_chart_background_color_changed)
        self._w("chart_background_gradient1").connect("color-set", self._cb_chart_background_gradient_changed)
        self._w("chart_background_gradient2").connect("color-set", self._cb_chart_background_gradient_changed)
        self._bg_picture_chooser.connect("selection-changed", self._cb_chart_background_image_changed)
        
        #chart grid
        self._w("chart_grid_color").connect("color-set", self._cb_chart_grid_color_changed)
        self._w("chart_grid_show_horizontal").connect("toggled", self._cb_chart_grid_show_horizontal_changed)
        self._w("chart_grid_style_horizontal").connect("changed", self._cb_chart_grid_style_horizontal_changed)
        self._w("chart_grid_show_vertical").connect("toggled", self._cb_chart_grid_show_vertical_changed)
        self._w("chart_grid_style_vertical").connect("changed", self._cb_chart_grid_style_vertical_changed)
        
        #chart xaxis
        self._w("chart_xaxis_show").connect("toggled", self._cb_chart_xaxis_show_changed)
        self._w("chart_xaxis_label").connect("changed", self._cb_chart_xaxis_label_changed)
        self._w("chart_xaxis_show_tics").connect("toggled", self._cb_chart_xaxis_show_tics_changed)
        self._w("chart_xaxis_show_tic_labels").connect("toggled", self._cb_chart_xaxis_show_tic_labels_changed)
        self._w("chart_xaxis_position").connect("changed", self._cb_chart_xaxis_position_changed)
        
        #chart yaxis
        self._w("chart_yaxis_show").connect("toggled", self._cb_chart_yaxis_show_changed)
        self._w("chart_yaxis_label").connect("changed", self._cb_chart_yaxis_label_changed)
        self._w("chart_yaxis_show_tics").connect("toggled", self._cb_chart_yaxis_show_tics_changed)
        self._w("chart_yaxis_show_tic_labels").connect("toggled", self._cb_chart_yaxis_show_tic_labels_changed)
        self._w("chart_yaxis_position").connect("changed", self._cb_chart_yaxis_position_changed)
        
        #chart ranges
        self._w("chart_xrange_min").connect("value-changed", self._cb_chart_xrange_changed)
        self._w("chart_xrange_max").connect("value-changed", self._cb_chart_xrange_changed)
        self._w("chart_yrange_min").connect("value-changed", self._cb_chart_yrange_changed)
        self._w("chart_yrange_max").connect("value-changed", self._cb_chart_yrange_changed)
        
        #chart legend
        self._w("chart_legend_show").connect("toggled", self._cb_chart_legend_show_changed)
        self._w("chart_legend_position").connect("changed", self._cb_chart_legend_position_changed)
        
        #graph select
        self._w("graph_select").connect("changed", self._cb_graph_changed)
        
        #graph basics
        self._w("graph_show").connect("toggled", self._cb_graph_show_changed)
        self._w("graph_antialias").connect("toggled", self._cb_graph_antialias_changed)
        self._w("graph_title").connect("changed", self._cb_graph_title_changed)
        self._w("graph_show_title").connect("toggled", self._cb_graph_show_title_changed)
        self._w("graph_color").connect("color-set", self._cb_graph_color_changed)
        
        #graph style
        self._w("graph_type").connect("changed", self._cb_graph_type_changed)
        self._w("graph_line_style").connect("changed", self._cb_graph_line_style_changed)
        self._w("graph_point_style").connect("changed", self._cb_graph_point_style_changed)
        self._datapoint_chooser.connect("selection-changed", self._cb_graph_point_pb_changed)
        self._w("graph_point_size").connect("value-changed", self._cb_graph_point_size_changed)
        self._w("graph_clickable").connect("toggled", self._cb_graph_clickable_changed)
        
        #graph errors
        self._w("graph_show_xerrors").connect("toggled", self._cb_graph_show_xerrors_changed)
        self._w("graph_show_yerrors").connect("toggled", self._cb_graph_show_yerrors_changed)
        
        #graph filling
        self._w("graph_fill_type_none").connect("toggled", self._cb_graph_fill_type_changed)
        self._w("graph_fill_type_value").connect("toggled", self._cb_graph_fill_type_changed)
        self._w("graph_fill_type_graph").connect("toggled", self._cb_graph_fill_type_changed)
        self._w("graph_fill_value").connect("value-changed", self._cb_graph_fill_value_changed)
        self._w("graph_fill_graph").connect("changed", self._cb_graph_fill_graph_changed)
        self._w("graph_fill_color").connect("color-set", self._cb_graph_fill_color_changed)
        self._w("graph_fill_opacity").connect("value-changed", self._cb_graph_fill_opacity_changed)
        
        #linechart
        self._chart.connect("datapoint-clicked", self._cb_datapoint_clicked)
        self._chart.connect("datapoint-hovered", self._cb_datapoint_hovered)
                
    def _cb_close(self, widget):
        gtk.main_quit()
        
    #chart title callbacks
    def _cb_chart_title_show_changed(self, button):
        self._chart.title.set_visible(button.get_active())
        
    def _cb_chart_title_text_changed(self, entry):
        self._chart.title.set_text(entry.get_text())
        
    def _cb_chart_title_color_changed(self, chooser):
        self._chart.title.set_color(chooser.get_color())
        
    #chart background_callbacks
    def _cb_chart_background_type_changed(self, button):
        self._w("chart_background_color").set_sensitive(False)
        self._w("chart_background_gradient1").set_sensitive(False)
        self._w("chart_background_gradient2").set_sensitive(False)
        self._bg_picture_chooser.set_sensitive(False)
        if self._w("chart_background_type_color").get_active():
            self._w("chart_background_color").set_sensitive(True)
            self._cb_chart_background_color_changed(self._w("chart_background_color"))
        elif self._w("chart_background_type_gradient").get_active():
            self._w("chart_background_gradient1").set_sensitive(True)
            self._w("chart_background_gradient2").set_sensitive(True)
            self._cb_chart_background_gradient_changed(None)
        elif self._w("chart_background_type_image"):
            self._bg_picture_chooser.set_sensitive(True)
            self._cb_chart_background_image_changed(self._bg_picture_chooser)
            
    def _cb_chart_background_color_changed(self, chooser):
        self._chart.background.set_color(from_gdkColor(chooser.get_color()))
        
    def _cb_chart_background_gradient_changed(self, chooser):
        ca = from_gdkColor(self._w("chart_background_gradient1").get_color())
        cb = from_gdkColor(self._w("chart_background_gradient2").get_color())
        self._chart.background.set_gradient(ca, cb)
        
    def _cb_chart_background_image_changed(self, filechooser):
        self._chart.background.set_image(filechooser.get_filename())
        
    #chart grid callbacks
    def _cb_chart_grid_color_changed(self, chooser):
        self._chart.grid.set_color(chooser.get_color())
        
    def _cb_chart_grid_show_horizontal_changed(self, button):
        self._chart.grid.set_draw_horizontal_lines(button.get_active())
        
    def _cb_chart_grid_style_horizontal_changed(self, combo):
        self._chart.grid.set_line_style_horizontal(combo.get_active())
        
    def _cb_chart_grid_show_vertical_changed(self, button):
        self._chart.grid.set_draw_vertical_lines(button.get_active())
        
    def _cb_chart_grid_style_vertical_changed(self, combo):
        self._chart.grid.set_line_style_vertical(combo.get_active())
        
    #chart xaxis callbacks
    def _cb_chart_xaxis_show_changed(self, button):
        self._chart.xaxis.set_visible(button.get_active())
    
    def _cb_chart_xaxis_label_changed(self, entry):
        self._chart.xaxis.set_label(entry.get_text())
        
    def _cb_chart_xaxis_show_tics_changed(self, button):
        self._chart.xaxis.set_show_tics(button.get_active())
        
    def _cb_chart_xaxis_show_tic_labels_changed(self, button):
        self._chart.xaxis.set_show_tic_labels(button.get_active())
        
    def _cb_chart_xaxis_position_changed(self, combo):
        self._chart.xaxis.set_position(combo.get_active() + 5)
        
    #chart yaxis callbacks
    def _cb_chart_yaxis_show_changed(self, button):
        self._chart.yaxis.set_visible(button.get_active())
    
    def _cb_chart_yaxis_label_changed(self, entry):
        self._chart.yaxis.set_label(entry.get_text())
        
    def _cb_chart_yaxis_show_tics_changed(self, button):
        self._chart.yaxis.set_show_tics(button.get_active())
        
    def _cb_chart_yaxis_show_tic_labels_changed(self, button):
        self._chart.yaxis.set_show_tic_labels(button.get_active())
        
    def _cb_chart_yaxis_position_changed(self, combo):
        self._chart.yaxis.set_position(combo.get_active() + 5)
        
    #chart ranges callbacks
    def _cb_chart_xrange_changed(self, spin):
        xmin = self._w("chart_xrange_min").get_value()
        xmax = self._w("chart_xrange_max").get_value()
        self._chart.set_xrange((xmin, xmax))
        
    def _cb_chart_yrange_changed(self, spin):
        ymin = self._w("chart_yrange_min").get_value()
        ymax = self._w("chart_yrange_max").get_value()
        self._chart.set_yrange((ymin, ymax))
    
    #chart legend callbacks
    def _cb_chart_legend_show_changed(self, button):
        self._chart.legend.set_visible(button.get_active())
        
    def _cb_chart_legend_position_changed(self, combo):
        self._chart.legend.set_position(combo.get_active() + 8)
        
    #graph selected callback
    def _cb_graph_changed(self, combo):
        iter = combo.get_active_iter()
        model = combo.get_model()
        self._graph = model.get_value(iter, 0)
        self._init_graph_data()
        
    #graph basic callbacks
    def _cb_graph_show_changed(self, button):
        self._graph.set_visible(button.get_active())
        
    def _cb_graph_antialias_changed(self, button):
        self._graph.set_antialias(button.get_active())
        
    def _cb_graph_title_changed(self, entry):
        self._graph.set_title(entry.get_text())
        
    def _cb_graph_show_title_changed(self, button):
        self._graph.set_show_title(button.get_active())
        
    def _cb_graph_color_changed(self, chooser):
        self._graph.set_color(chooser.get_color())
        
    #graph style callbacks
    def _cb_graph_type_changed(self, combo):
        self._graph.set_type(combo.get_active() + 1)
        
    def _cb_graph_line_style_changed(self, combo):
        self._graph.set_line_style(combo.get_active())
        
    def _cb_graph_point_style_changed(self, combo):
        if combo.get_active() != 6:
            self._datapoint_chooser.set_sensitive(False)
            self._graph.set_point_style(combo.get_active())
        else:
            self._datapoint_chooser.set_sensitive(True)
            
    def _cb_graph_point_pb_changed(self, filechooser):
        self._graph.set_point_style(gtk.gdk.pixbuf_new_from_file(filechooser.get_filename()))
        
    def _cb_graph_point_size_changed(self, spin):
        self._graph.set_point_size(spin.get_value())
        
    def _cb_graph_clickable_changed(self, button):
        self._graph.set_clickable(button.get_active())
        
    #graph error callbacks
    def _cb_graph_show_xerrors_changed(self, button):
        self._graph.set_show_xerrors(button.get_active())
        
    def _cb_graph_show_yerrors_changed(self, button):
        self._graph.set_show_yerrors(button.get_active())
    
    #graph filling callbacks
    def _cb_graph_fill_type_changed(self, button):
        self._w("graph_fill_value").set_sensitive(False)
        self._w("graph_fill_graph").set_sensitive(False)
        if self._w("graph_fill_type_value").get_active():
            self._w("graph_fill_value").set_sensitive(True)
            self._cb_graph_fill_value_changed(self._w("graph_fill_value"))
        elif self._w("graph_fill_type_graph").get_active():
            self._w("graph_fill_graph").set_sensitive(True)
            self._cb_graph_fill_graph_changed(self._w("graph_fill_graph"))
        else:
            self._graph.set_fill_to(None)
            
    def _cb_graph_fill_value_changed(self, spin):
        self._graph.set_fill_to(spin.get_value())
        
    def _cb_graph_fill_graph_changed(self, combo):
        if not combo.get_property("sensitive"): return
        iter = combo.get_active_iter()
        model = combo.get_model()
        graph = model.get_value(iter, 0)
        self._graph.set_fill_to(graph)
        
    def _cb_graph_fill_color_changed(self, chooser):
        self._graph.set_fill_color(chooser.get_color())
        
    def _cb_graph_fill_opacity_changed(self, spin):
        self._graph.set_fill_opacity(spin.get_value())
        
    #linechart callbacks
    def _cb_datapoint_clicked(self, chart, graph, (x, y)):
        print "Point (%s, %s) on '%s' clicked." % (x, y, graph.get_title())
        
    def _cb_datapoint_hovered(self, chart, graph, (x, y)):
        print "Point (%s, %s) on '%s' hovered." % (x, y, graph.get_title())
        
        
if __name__ == "__main__":
    app = Gui()
    gtk.main()
