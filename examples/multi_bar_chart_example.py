#!/usr/bin/env python

import gtk
import pygtk
import random

from pygtk_chart import bar_chart

def rand():
    l = range(1000)
    while True:
        yield random.choice(l)

r = rand().next

barchart = bar_chart.MultiBarChart()
barchart.title.set_text('Loaves of Bread Made per City')

for city in 'dallas austin houston waco beaumont'.split():
    city_label = city.capitalize()
    multibar = bar_chart.MultiBar(city, city_label)
    for bread in 'wheat oat raisin sourdough white'.split():
        bread_label = bread.capitalize()
        sub_bar = bar_chart.Bar(bread, r(), bread_label)
        multibar.add_bar(sub_bar)
    barchart.add_bar(multibar)

def cb_multibar_clicked(barchart, multibar, subbar):
    print "Bar ('%s', '%s') clicked." % (multibar.get_label(), subbar.get_label())
barchart.connect("multibar-clicked", cb_multibar_clicked)

def cb_bar_clicked(barchart, multibar):
    print "Bar '%s' clicked." % multibar.get_label()
barchart.connect("bar-clicked", cb_bar_clicked)

window = gtk.Window()
window.connect("destroy", gtk.main_quit)
window.add(barchart)
window.resize(800,400)

window.show_all()
gtk.main()

