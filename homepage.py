from kivy.uix.boxlayout import BoxLayout
from kivy.uix.listview import ListView
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ObjectProperty, ListProperty

class HomeScreen(BoxLayout):
    managedby = ObjectProperty(None,allownone=True)
    gamesview = ObjectProperty(None,allownone=True)
    pb = ObjectProperty(None, allownone=True)

class MyListView(ListView):
    selection = ListProperty()

class PrintyButton(Button):
    def getselchan(self,*args,**kwargs):
        print args
        print kwargs
        self.text = str(args) + str(kwargs)
        print args[0][0].text

class OpenSgfDialog(FloatLayout):
    manager = ObjectProperty(None)
    popup = ObjectProperty(None)
