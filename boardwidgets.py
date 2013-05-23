from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty, ListProperty, AliasProperty, StringProperty, DictProperty, BooleanProperty, StringProperty, OptionProperty

class Stone(Widget):
    colourname = StringProperty('b')
    colour = ListProperty([1,1,1])
    imagepath = StringProperty('./black_stone.png')
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

