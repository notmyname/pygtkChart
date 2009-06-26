#!/usr/bin/env python

import gtk
import pygtk

from pygtk_chart import pie_chart


data = [('wheat', 'Wheat', 276),
        ('oat', 'Oat', 52),
        ('white', 'White', 652),
        ('sour', 'Sourdough', 65),
        ('raisin', 'Raisin', 120),
       ]

piechart = pie_chart.PieChart()
piechart.set_data(data)
piechart.title.set_text('Loaves of Bread Made')

window = gtk.Window()
window.connect("destroy", gtk.main_quit)
window.add(piechart)
window.resize(800,400)

window.show_all()
gtk.main()

