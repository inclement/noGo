from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty, ListProperty, AliasProperty, StringProperty, DictProperty, BooleanProperty, StringProperty, OptionProperty

class VDividerLine(Widget):
    vgap = NumericProperty(0.2)
    linewidth = NumericProperty(1)
    colour = ListProperty([0.195,0.641,0.805])

class DividerLine(Widget):
    hgap = NumericProperty(0.1) 
    linewidth = NumericProperty(2)
    colour = ListProperty([0.195,0.641,0.805])

class WhiteStoneImage(Widget):
    pass
class BlackStoneImage(Widget):
    pass
