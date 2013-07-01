# Copyright 2013 Alexander Taylor

# This file is part of noGo.

# noGo is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

# noGo is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with noGo. If not, see http://www.gnu.org/licenses/gpl-3.0.txt

from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty, ListProperty, AliasProperty, StringProperty, DictProperty, BooleanProperty, StringProperty, OptionProperty

class Stone(Widget):
    colourname = StringProperty('b')
    colour = ListProperty([1,1,1])
    imagepath = StringProperty('./black_stone.png')
    innerel = ObjectProperty(None)
    outerel = ObjectProperty(None)
    # def __init__(self,*args,**kwargs):
    #     super(Stone,self).__init__(*args,**kwargs)
    #     self.innerel.texture.min_filter = 'linear_mipmap_linear'
    #     self.outerel.texture.min_filter = 'linear_mipmap_linear'
    def set_colour(self,colour):
        if colour == 'black':
            self.colour = [0,0,0]
            self.imagepath = './black_stone.png'
            self.colourname = 'b'
        elif colour == 'white':
            self.colour = [1,1,1]
            self.imagepath = './white_stone.png'
            self.colourname = 'w'
        else:
            print 'colour doesn\'t exist'
            # should raise exception
    # Image:
    #     x: self.parent.pos[0]
    #     y: self.parent.pos[1]
    #     width: self.parent.width
    #     height: self.parent.height
    #     source: self.parent.imagepath
    #     mipmap: True

class KoMarker(Widget):
    markercolour = ListProperty([0,0,0])
    pass

class TriangleMarker(Widget):
    markercolour = ListProperty([0,0,0])
    pass

class SquareMarker(Widget):
    markercolour = ListProperty([0,0,0])
    
class CircleMarker(Widget):
    markercolour = ListProperty([0,0,0])

class CrossMarker(Widget):
    markercolour = ListProperty([0,0,0])

class TextMarker(Widget):
    markercolour = ListProperty([0,0,0])
    text = StringProperty('')
    def printinfo(self):
        print '##############'
        print self.markercolour
        print self.text
        print self.pos
        print self.size
        return 0.7

class VarStone(Widget):
    colour = ListProperty([1,1,1,0.5])
    textcolour = ListProperty([0,0,0.5])
    text = StringProperty('')
    def set_colour(self,colour):
        if colour in ['black','b']:
            self.colour = [0,0,0,0.3]
            self.textcolour = [1,1,1,0.8]
        elif colour in ['white','w']:
            self.colour = [1,1,1,0.6]
            self.textcolour = [0,0,0,0.8]
        else:
            print 'colour doesn\'t exist:', colour
            # should raise exception

