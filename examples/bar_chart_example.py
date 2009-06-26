import gtk
import pygtk

from pygtk_chart import bar_chart


data = [('wheat', 'Wheat', 276),
        ('oat', 'Oat', 52),
        ('white', 'White', 652),
        ('sour', 'Sourdough', 65),
        ('raisin', 'Raisin', 120),
       ]

barchart = bar_chart.BarChart()
barchart.set_data(data)
barchart.title.set_text('Loaves of Bread Made')

window = gtk.Window()
window.connect("destroy", gtk.main_quit)
window.add(barchart)
window.resize(800,400)

window.show_all()
gtk.main()

