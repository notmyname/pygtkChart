#!/usr/bin/env python
import gtk
from pygtk_chart import line_chart
import random
import math
import graph_options
import line_chart_options

def cb_chart_title(entry, chart):
    chart.title.set_text(entry.get_text())

window = gtk.Window()
window.connect("destroy", gtk.main_quit)
window.set_default_size(1000, 400)

hbox = gtk.HBox()

chart = line_chart.LineChart()
chart.title.set_text("LineChart example")
hbox.pack_start(chart)

sine = line_chart.graph_new_from_function(math.sin, -10, 10, "sine", 50)
sine.set_title("Sine")
chart.add_graph(sine)

gauss = line_chart.graph_new_from_function(lambda x: math.exp(- (x / 2)**2), -10, 10, "gauss", 50)
gauss.set_title("Normal distribution")
chart.add_graph(gauss)

sqrt = line_chart.graph_new_from_function(math.sqrt, 0, 10, "sqrt", 50)
sqrt.set_title("Square root")
chart.add_graph(sqrt)

filegrapha = line_chart.graph_new_from_file("line_chart_test_data", "filea", 0, 1)
filegrapha.set_title("File data 0:1")
chart.add_graph(filegrapha)

filegraphb = line_chart.graph_new_from_file("line_chart_test_data", "fileb", 0, 2)
filegraphb.set_title("File data 0:2")
chart.add_graph(filegraphb)

graphs = [sine, gauss, sqrt, filegrapha, filegraphb]

vbox_chart = line_chart_options.ChartControl(chart)

vbox_graph = graph_options.GraphControl(graphs)

notebook = gtk.Notebook()
notebook.append_page(vbox_chart, gtk.Label("Chart options"))
notebook.append_page(vbox_graph, gtk.Label("Graph options"))
hbox.pack_start(notebook, False, False)

window.add(hbox)
window.show_all()
gtk.main()

