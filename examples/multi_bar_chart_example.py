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

data = [('dallas', 'Dallas', 'Wheat', r()),
        ('dallas', 'Dallas', 'Oat', r()),
        ('dallas', 'Dallas', 'Raisin', r()),
        ('dallas', 'Dallas', 'Sourdough', r()),
        ('dallas', 'Dallas', 'Raisin', r()),

        ('austin', 'Austin', 'Oat', r()),
        ('austin', 'Austin', 'Wheat', r()),
        ('austin', 'Austin', 'Sourdough', r()),
        ('austin', 'Austin', 'Raisin', r()),

        ('sa', 'San Antonio', 'White', r()),
        ('sa', 'San Antonio', 'Wheat', r()),
        ('sa', 'San Antonio', 'Raisin', r()),
        ('sa', 'San Antonio', 'Oat', r()),

        ('houston', 'Houston', 'Wheat', r()),
        ('houston', 'Houston', 'Oat', r()),
        ('houston', 'Houston', 'White', r()),
        ('houston', 'Houston', 'Sourdough', r()),
        ('houston', 'Houston', 'Raisin', r()),

        ('fw', 'Ft. Worth', 'Raisin', r()),
        ('fw', 'Ft. Worth', 'Oat', r()),
        ('fw', 'Ft. Worth', 'Wheat', r()),
        ('fw', 'Ft. Worth', 'White', r()),
       ]

barchart = bar_chart.MultiBarChart()
barchart.set_data(data)
barchart.title.set_text('Loaves of Bread Made per City')

window = gtk.Window()
window.connect("destroy", gtk.main_quit)
window.add(barchart)
window.resize(800,400)

window.show_all()
gtk.main()

