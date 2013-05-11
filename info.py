from kivy.uix.tabbedpanel import TabbedPanel
from kivy.properties import StringProperty

nogo_infotext = 'noGo is a free, open-source SGF viewer/creator/player/editor. It is distributed'
class InfoPage(TabbedPanel):
    infotext = StringProperty(nogo_infotext)
    licensetext = StringProperty('')
