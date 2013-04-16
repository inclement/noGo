from kivy.app import App
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, Ellipse
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty, ListProperty, AliasProperty, StringProperty, DictProperty
from kivy.vector import Vector
from kivy.clock import Clock

from random import random as r
from random import choice
from math import sin
from functools import partial

from gomill import sgf, boards
from abstractboard import AbstractBoard

# from kivy.config import Config
# Config.set('graphics', 'width', '400')
# Config.set('graphics', 'height', '600')

blacknames = ['black','b','B','Black']
whitenames = ['white','w','W','White']
def colourname_to_colour(colourname):
    if colourname in blacknames:
        return 'black'
    elif colourname in whitenames:
        return 'white'
    else:
        return None
    

        
class StarPoint(Widget):
    pass

class PlayMarker(Widget):
    markercolour = ListProperty([0,0,0])
    pass

class KoMarker(Widget):
    pass
    

class Stone(Widget):
    colour = ListProperty([1,1,1])
    def set_colour(self,colour):
        if colour == 'black':
            self.colour = [0,0,0]
        elif colour == 'white':
            self.colour = [1,1,1]
        else:
            print 'colour doesn\'t exist'
            # should raise exception
            

starposs = {19:[(3,3),(3,9),(3,15),(9,3),(9,9),(9,15),(15,3),(15,9),(15,15)]}
            
class GuiBoard(Widget):
    gridsize = NumericProperty(19) # Board size
    mode = StringProperty('fullscreen') # How to scale the board
    abstractboard = ObjectProperty(None,allownone=True) # Object to query for where to play moves

    playmarker = ObjectProperty(None,allownone=True) # Circle marking last played move

    stones = DictProperty({})
    starpoints = DictProperty()
    starpoint_positions = DictProperty(starposs)

    gobansize = ListProperty((100,100))
    boardindent = ListProperty((100,100))
    stonesize = ListProperty((100,100))
    gridspacing = NumericProperty(10)
    gridlines = ListProperty([])

    gobanpos = ListProperty((100,100))

    def set_playmarker(self,coord):
        self.remove_widget(self.playmarker)
        marker = PlayMarker(size=self.stonesize, pos=self.coord_to_pos(coord))
        if self.stones.has_key(coord):
            stone_colour = self.stones[coord].colour
            marker.markercolour = [1-stone_colour[0],1-stone_colour[1],1-stone_colour[2]]
        else:
            marker.markercolour = [0,0,0]
        self.add_widget(marker)
        self.playmarker = marker

    def remove_playmarker(self):
        self.remove_widget(self.playmarker)
        self.playmarker = None

    def on_gridsize(self):
        self.draw_starpoints()

    def on_size(self,*args,**kwargs):
        self.gobansize = self.size
        self.boardindent = self.get_boardindent()
        self.boardlength = self.get_boardlength()
        self.stonesize = self.current_stone_size()
        self.gridspacing = self.get_gridspacing()

        # pos
        self.gobanpos = self.pos
        self.gridlines = self.get_gridlines()

        self.update_starpoints()
        self.update_stones()

    def on_pos(self,*args,**kwargs):
        self.on_size()


    def coord_to_pos(self, coord):
        gridspacing = self.gridspacing
        coord = (coord[0]-0.5,coord[1]-0.5)
        return (self.gobanpos[0] + self.boardindent[0] + coord[0]*gridspacing, self.gobanpos[1] + self.boardindent[1] + coord[1]*gridspacing)

    def current_stone_size(self):
        newsize = float(self.gobansize[0]) / (self.gridsize + 2)
        return (newsize,newsize)

    def get_boardindent(self):
        indent = (1.5*float(self.width)/(self.gridsize + 2),1.5*float(self.height)/(self.gridsize + 2))
        return indent

    def get_boardlength(self):
        length = self.size[0] * float(self.gridsize-1) / (self.gridsize + 2)
        return length

    def get_gridspacing(self):
        return float(self.width)/(self.gridsize + 2)

    def get_gridlines(self):
        startx = self.boardindent[0] + self.gobanpos[0]
        starty = self.boardindent[1] + self.gobanpos[1]
        gridspacing = self.gridspacing
        length = self.boardlength
        gridnum = self.gridsize

        gridline = []

        curx = startx
        cury = starty

        # print 'size', self.size
        # print 'start', curx, cury
        # print 'length', length, self.size[1] - 3*gridspacing
        # print 'gobansize', self.gobansize

        dir = 1.0
        for y in range(self.gridsize - 1):
            curx += dir*length
            gridline.append([curx,cury])
            cury += gridspacing
            gridline.append([curx,cury])
            dir *= -1
        dir *= -1
        for x in range(self.gridsize - 1):
            cury += dir*length
            gridline.append([curx,cury])
            curx += gridspacing
            gridline.append([curx,cury])
            dir *= -1

        return reduce(lambda j,k: j+k, gridline)

        
    # Stone methods
    def follow_instructions(self,instructions,*args,**kwargs):
        print 'instructions are', instructions
        if 'add' in instructions:
            add_stones = instructions['add']
            for stone in add_stones:
                self.add_stone(coord=stone[0],colour=colourname_to_colour(stone[1]))
        if 'remove' in instructions:
            remove_stones = instructions['remove']
            for stone in remove_stones:
                self.remove_stone(coord=stone[0],colour=colourname_to_colour(stone[1]))
        if 'empty' in instructions:
            empty_stones = instructions['empty']
            for stone in empty_stones:
                self.empty_stone(coord=stone[0])
        if 'playmarker' in instructions:
            pm = instructions['playmarker']
            print 'Asked to draw pm at', pm
            if pm is not None:
                self.set_playmarker(pm)
            else:
                self.remove_playmarker()
        else:
            self.remove_playmarker()

    def advance_one_move(self,*args,**kwargs):
        instructions = self.abstractboard.advance_position()
        self.follow_instructions(instructions)


    def retreat_one_move(self,*args,**kwargs):
        instructions = self.abstractboard.retreat_position()
        self.follow_instructions(instructions)

    def jump_to_start(self,*args,**kwargs):
        instructions = self.abstractboard.jump_to_node(self.abstractboard.game.root)
        self.follow_instructions(instructions)

    def jump_to_end(self,*args,**kwargs):
        instructions = self.abstractboard.jump_to_node(self.abstractboard.game.get_last_node())
        self.follow_instructions(instructions)
        
        
    def add_stone(self,coord=(1,1),colour='black',*args,**kwargs):
        stonesize = self.stonesize
        stone = Stone(size=stonesize, pos=self.coord_to_pos(coord))
        stone.set_colour(colour)
        if self.stones.has_key(coord):
            self.remove_stone(coord)
        self.stones[coord] = stone
        self.add_widget(stone)

    def remove_stone(self,coord=(1,1),*args,**kwargs):
        if self.stones.has_key(coord):
            stone = self.stones.pop(coord)
            self.remove_widget(stone)
        else:
            print 'Tried to remove stone that doesn\'t exist'

    def empty_stone(self,coord=(1,1),*args,**kwargs):
        if self.stones.has_key(coord):
            stone = self.stones.pop(coord)
            self.remove_widget(stone)

    def update_stones(self):
        for coord in self.stones.keys():
            self.stones[coord].pos = self.coord_to_pos(coord)
            self.stones[coord].size = self.stonesize

    def redraw_stones(self):
        for coord in self.stones.keys():
            stone = self.stones[coord]
            self.remove_widget(stone)
            self.add_widget(stone)

    def clear_stones(self):
        for coord in self.stones.keys():
            stone = self.stones.pop(coord)
            self.remove_widget(stone)
            

    def add_random_stone(self,*args,**kwargs):
        self.add_stone((choice(range(19)),choice(range(19))),choice(['black','white']))

    def remove_random_stone(self,*args,**kwargs):
        coords = self.stones.keys()
        if len(coords) > 0:
            self.remove_stone(choice(coords))
        else:
            'Can\'t remove random stone, no coords'

    # Star point methods
    def draw_starpoints(self):
        self.remove_starpoints()
        if self.starpoint_positions.has_key(self.gridsize):
            coords = self.starpoint_positions[self.gridsize]
            for entry in coords:
                self.add_starpoint(entry)
    
    def add_starpoint(self,coord=(1,1),*args,**kwargs):
        stonesize = self.stonesize
        sp = StarPoint(size=stonesize, pos=self.coord_to_pos(coord))
        if self.starpoints.has_key(coord):
            self.remove_starpoint(coord)
        self.starpoints[coord] = sp
        self.add_widget(sp)
        self.redraw_stones()

    def remove_starpoint(self,coord=(1,1),*args,**kwargs):
        if self.starpoints.has_key(coord):
            sp = self.starpoints.pop(coord)
            self.remove_widget(ssp)
        else:
            print 'Tried to remove starpoint that doesn\'t exist'

    def remove_starpoints(self):
        for entry in self.starpoints:
            sp = self.starpoints[entry]
            self.remove_widget(sp)
        self.starpoints = {}

    def update_starpoints(self):
        self.remove_starpoints()
        self.draw_starpoints()

    def redraw_starpoints(self):
        for coord in self.starpoints.keys():
            sp = self.starpoints[coord]
            self.remove_widget(ssp)
            self.add_widget(sp)
        self.redraw_stones()

class BoardContainer(Widget):
    board = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(BoardContainer, self).__init__(**kwargs)
        self._keyboard = Window.request_keyboard(
            self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

    def _keyboard_closed(self):
        print 'My keyboard has been closed!'
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        # print 'The key', keycode, 'have been pressed'
        # print ' - text is %r' % text
        # print ' - modifiers are %r' % modifiers

        # Keycode is composed of an integer + a string
        # If we hit escape, release the keyboard
        if keycode[1] == 'escape':
            keyboard.release()
        elif keycode[1] == 'right':
            self.board.advance_one_move()
        elif keycode[1] == 'left':
            self.board.retreat_one_move()
        

        # Return True to accept the key. Otherwise, it will be used by
        # the system.
        return True

    def get_boardsize(self):
        mysize = self.size
        if mysize[1] < mysize[0]:
            boardsize = mysize[1]
        else:
            boardsize = mysize[0]
        print 'mysize =', mysize,'-> boardsize-20 = ', boardsize-20
        print 'mypos = ', self.pos
        print 'window size', Window.size
        print 'parent', self.parent

        return (boardsize-20, boardsize-20)

    def set_boardsize(self,value):
        self.boardsize = self.get_boardsize()

    def get_boardpos(self):
        size = self.get_boardsize()
        return (self.pos[0] + 10,self.pos[1] + 10)

    def set_boardpos(self, value):
        self.boardpos = self.get_boardpos()

    boardsize = AliasProperty(get_boardsize, set_boardsize, bind=('boardsize','size'))
    boardpos = AliasProperty(get_boardpos, set_boardpos, bind=('boardpos','pos'))


class GobanApp(App):

    def build(self):
        boardcontainer = BoardContainer(size_hint=(1.,0.9))

        abstractboard = AbstractBoard()
        abstractboard.load_sgf_from_file('/home/asandy/37tengent1.sgf')
        boardcontainer.board.abstractboard = abstractboard

        btn_start = Button(text='Start')
        btn_end = Button(text='End')
        btn_nextmove = Button(text='Next')
        btn_prevmove = Button(text='Prev')

        # btn_nextmove.bind(on_press=partial(boardcontainer.board.add_random_stone))
        # btn_prevmove.bind(on_press=partial(boardcontainer.board.remove_random_stone))
        btn_start.bind(on_press=partial(boardcontainer.board.jump_to_start))
        btn_end.bind(on_press=partial(boardcontainer.board.jump_to_end))
        btn_nextmove.bind(on_press=partial(boardcontainer.board.advance_one_move))
        btn_prevmove.bind(on_press=partial(boardcontainer.board.retreat_one_move))

        navigation_layout = BoxLayout(orientation='horizontal',size_hint=(1.,0.1))
        navigation_layout.add_widget(btn_start)
        navigation_layout.add_widget(btn_end)
        navigation_layout.add_widget(btn_prevmove)
        navigation_layout.add_widget(btn_nextmove)

        layout = BoxLayout(orientation='vertical')
        layout.add_widget(boardcontainer)
        layout.add_widget(navigation_layout)
        return layout
        #return boardcontainer


            
if __name__ == '__main__':
    GobanApp().run()
