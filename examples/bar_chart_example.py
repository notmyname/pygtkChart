import gtk
import pygtk

from pygtk_chart import bar_chart


data = [('wheat', 276, 'Wheat'),
        ('oat', 52, 'Oat'),
        ('white', 652, 'White'),
        ('sour', 65, 'Sourdough'),
        ('raisin', 120, 'Raisin'),
       ]

barchart = bar_chart.BarChart()
barchart.title.set_text('Loaves of Bread Made')
barchart.grid.set_visible(True)
barchart.grid.set_line_style(bar_chart.LINE_STYLE_DOTTED)

for bar_info in data:
    bar = bar_chart.Bar(*bar_info)
    barchart.add_bar(bar)

def cb_bar_clicked(barchart, bar):
    print "Bar '%s' clicked." % bar.get_label()
barchart.connect("bar-clicked", cb_bar_clicked)

window = gtk.Window()
window.connect("destroy", gtk.main_quit)
window.add(barchart)
window.resize(800,400)

window.show_all()
gtk.main()

