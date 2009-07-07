#!/usr/bin/env python
import gtk
from pygtk_chart import line_chart
import random
import math
import graph_options
import line_chart_options

def cb_chart_title(entry, chart):
    chart.title.set_text(entry.get_text())
    
def make_sin_data(factor=1, offset=0):
    data = []
    for x in range(0, 100):
        data.append((x / 10.0, math.sin(factor * x / 10.0) + offset))
    return data
    
def make_cos_data(offset=0):
    data = []
    for x in range(0, 100):
        data.append((x / 10.0, math.cos(x / 10.0) + offset))
    return data
    
def make_modulated_cos_data(offset=0):
    data = []
    for x in range(0, 100):
        data.append((x / 10.0, math.exp(-x / 50.0) * math.cos(x / 5.0) + offset))
    return data

window = gtk.Window()
window.connect("destroy", gtk.main_quit)
window.set_default_size(800, 400)

hbox = gtk.HBox()

chart = line_chart.LineChart()
chart.title.set_text("LineChart example")
hbox.pack_start(chart)

grapha = line_chart.Graph("sin", "Sine", make_sin_data(offset=4))
chart.add_graph(grapha)

graphb = line_chart.Graph("cos", "Cosine", make_cos_data(2))
chart.add_graph(graphb)

graphc = line_chart.Graph("modulated cos", "Modulated Cosine", make_modulated_cos_data())
chart.add_graph(graphc)

graphs = [grapha, graphb, graphc]

vbox_chart = line_chart_options.ChartControl(chart)

vbox_graph = graph_options.GraphControl(graphs)

notebook = gtk.Notebook()
notebook.append_page(vbox_chart, gtk.Label("Chart options"))
notebook.append_page(vbox_graph, gtk.Label("Graph options"))
hbox.pack_start(notebook, False, False)

window.add(hbox)
window.show_all()
gtk.main()

