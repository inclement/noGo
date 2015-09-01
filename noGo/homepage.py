# Copyright 2013 Alexander Taylor

# This file is part of noGo.

# noGo is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

# noGo is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with noGo. If not, see http://www.gnu.org/licenses/gpl-3.0.txt

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.listview import ListView
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ObjectProperty, ListProperty
from kivy.utils import platform

class TabletHomeScreen(BoxLayout):
    managedby = ObjectProperty(None,allownone=True)
    gamesview = ObjectProperty(None,allownone=True)
    opengames = ObjectProperty(None,allownone=True)
    pb = ObjectProperty(None, allownone=True)
class HomeScreen(BoxLayout):
    managedby = ObjectProperty(None,allownone=True)
    gamesview = ObjectProperty(None,allownone=True)
    opengames = ObjectProperty(None,allownone=True)
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
    def get_dir(self):
        if platform() == 'android':
            return '/sdcard'
        else:
            return '.'
        
