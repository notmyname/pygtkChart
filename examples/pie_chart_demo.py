#!/usr/bin/env python
#
#       pie_chart_demo.py
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
import gtk
import pygtk

from pygtk_chart import pie_chart
import pie_chart_options
import area_options

def cb_area_clicked(chart, area):
    print "Area '%s' clicked." % area.get_label()

w = gtk.Window()
w.connect("destroy", gtk.main_quit)
w.set_default_size(900, 400)

hbox = gtk.HBox()

chart = pie_chart.PieChart()
chart.title.set_text("PieChart example")
hbox.pack_start(chart)

chart.connect("area-clicked", cb_area_clicked)

area1 = pie_chart.PieArea("wheat", 276, "Wheat")
chart.add_area(area1)
area2 = pie_chart.PieArea("oat", 52, "Oat")
chart.add_area(area2)
area3 = pie_chart.PieArea("white", 652, "White")
chart.add_area(area3)
area4 = pie_chart.PieArea("sour", 65, "Sourdough")
chart.add_area(area4)
area5 = pie_chart.PieArea("raisin", 120, "Raisin")
chart.add_area(area5)

vbox_chart = pie_chart_options.ChartControl(chart)
vbox_area = area_options.AreaControl([area1, area2, area3, area4, area5])

notebook = gtk.Notebook()
notebook.append_page(vbox_chart, gtk.Label("Chart options"))
notebook.append_page(vbox_area, gtk.Label("Area options"))
hbox.pack_start(notebook, False, False)

w.add(hbox)
w.show_all()
gtk.main()
