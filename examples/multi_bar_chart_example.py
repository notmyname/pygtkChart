#!/usr/bin/env python

import gtk
import pygtk
import random

from pygtk_chart import multi_bar_chart

def rand():
    l = range(1000)
    while True:
        yield random.choice(l)

r = rand().next

barchart = multi_bar_chart.MultiBarChart()
barchart.title.set_text('Loaves of Bread Made per City')
barchart.set_mode(multi_bar_chart.MODE_HORIZONTAL)

for city in 'dallas austin houston waco beaumont'.split():
    city_label = city.capitalize()
    multibar = multi_bar_chart.BarGroup(city, city_label)
    for bread in 'wheat oat raisin sourdough white'.split():
        bread_label = bread.capitalize()
        sub_bar = multi_bar_chart.Bar(bread, r(), bread_label)
        multibar.add_bar(sub_bar)
    barchart.add_bar(multibar)

def cb_group_clicked(barchart, group, bar):
    print "Bar ('%s', '%s') clicked." % (group.get_label(), bar.get_label())
    barchart.set_rotate_group_labels(not barchart.get_rotate_group_labels())
barchart.connect("group-clicked", cb_group_clicked)

def cb_bar_clicked(barchart, bar):
    print bar.get_label()
barchart.connect("bar-clicked", cb_bar_clicked)

window = gtk.Window()
window.connect("destroy", gtk.main_quit)
window.add(barchart)
window.resize(800,400)

window.show_all()
gtk.main()

