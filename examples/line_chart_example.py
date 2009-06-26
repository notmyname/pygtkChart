#!/usr/bin/env python
import gtk
import pygtk
from pygtk_chart import line_chart

window = gtk.Window()
window.resize(800,400)
window.connect("destroy", gtk.main_quit)

linechart = line_chart.LineChart()
linechart.title.set_text("Example Chart")

data = [(-3, 12), (0, 3), (-2, 4), (1, 5), (3, -6), (9, 9.3)]
graph = line_chart.Graph("some_name", "Example", data)
linechart.add_graph(graph)

more_data = [(-4, 3), (0, 8.434), (7, -5), (-1, 0)]
another_graph = line_chart.Graph("another_name", "Test", more_data)
linechart.add_graph(another_graph)
another_graph.set_fill_xaxis(True)

window.add(linechart)

window.show_all()
gtk.main()

