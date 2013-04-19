from kivy.app import App
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, Ellipse
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty, ListProperty, AliasProperty, StringProperty, DictProperty, BooleanProperty, StringProperty, OptionProperty
from kivy.vector import Vector
from kivy.clock import Clock

from kivy.input.postproc import doubletap

from random import random as r
from random import choice
from math import sin
from functools import partial

from gomill import sgf, boards
from abstractboard import AbstractBoard

import sys

# from kivy.config import Config
# Config.set('graphics', 'width', '400')
# Config.set('graphics', 'height', '600')

navigate_text = '[b]Navigation mode[/b] selected. Tap on the right side of the board to advance the game, or the left to move back.'
edit_text = '[b]Edit mode[/b] selected.'
score_text = '[b]Score mode[/b] selected. Tap on groups to toggle them as dead/alive.'

# Keybindings
advancekeys = ['right','l']
retreatkeys = ['left','h']
nextvariationkeys = ['up','k']
prevvariationkeys = ['down','j']

blacknames = ['black','b','B','Black']
whitenames = ['white','w','W','White']
def colourname_to_colour(colourname):
    if colourname in blacknames:
        return 'black'
    elif colourname in whitenames:
        return 'white'
    else:
        return None

trianglecodes = ['triangle','TR']
squarecodes = ['square','SQ']
circlecodes = ['circle','CR']
crosscodes = ['cross','MA']
textcodes = ['text','LB']
def markercode_to_marker(markercode):
    if markercode in trianglecodes:
        return 'triangle'
    elif markercode in squarecodes:
        return 'square'
    elif markercode in circlecodes:
        return 'circle'
    elif markercode in crosscodes:
        return 'cross'
    elif markercode in textcodes:
        return 'text'
    return None

class PlayerDetails(BoxLayout):
    wtext = StringProperty('W player')
    wrank = StringProperty('')
    btext = StringProperty('B player')
    brank = StringProperty('')
    wtoplaycolour = ListProperty([0,1,0,1])
    btoplaycolour = ListProperty([0,1,0,1])
    def set_to_play(self,player):
        if player == 'w':
            self.wtoplaycolour = [0,0.8,0,1]
            self.btoplaycolour = [0,0.8,0,0]
        elif player == 'b':
            self.btoplaycolour = [0,0.8,0,1]
            self.wtoplaycolour = [0,0.8,0,0]
        else:
            self.wtoplaycolour = [0,0.8,0,0]
            self.btoplaycolour = [0,0.8,0,0]
        print 'marker sizes:',self.wtoplaycolour,self.btoplaycolour

class CommentBox(ScrollView):
    pre_text = StringProperty('')
    text = StringProperty('')
    pass

class StarPoint(Widget):
    pass

class PlayMarker(Widget):
    markercolour = ListProperty([0,0,0])
    pass

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
    navmode = StringProperty('Navigate') # How to scale the board
    abstractboard = ObjectProperty(None,allownone=True) # Object to query for where to play moves
    uielements = DictProperty({})

    variations_exist = BooleanProperty(False)

    # Board flipping
    flip_horiz = BooleanProperty(False)
    flip_vert = BooleanProperty(False)
    flip_forwardslash = BooleanProperty(True)
    flip_backslash = BooleanProperty(False)

    # Transient widgets
    playmarker = ObjectProperty(None,allownone=True) # Circle marking last played move
    boardmarkers = DictProperty({})

    stones = DictProperty({})
    starpoints = DictProperty()
    starpoint_positions = DictProperty(starposs)

    gobansize = ListProperty((100,100))
    boardindent = ListProperty((100,100))
    stonesize = ListProperty((100,100))
    gridspacing = NumericProperty(10)
    gridlines = ListProperty([])

    gobanpos = ListProperty((100,100))


    def set_navmode(self,spinner,mode):
        self.navmode = mode
        if self.uielements.has_key('commentbox'):
            for cb in self.uielements['commentbox']:
                if mode == 'Navigate':
                    cb.pre_text = navigate_text + '\n-----\n'
                    cb.scroll_y = 1
                elif mode == 'Edit':
                    cb.pre_text = edit_text + '\n-----\n'
                    cb.scroll_y = 1
                elif mode == 'Score':
                    cb.pre_text = score_text + '\n-----\n'
                    cb.scroll_y = 1


    def clear_transient_widgets(self):
        self.remove_playmarker()
        # self.remove_komarker()
        self.clear_markers()

    ## Board markers
    def add_marker(self,coord,mtype,other=[]):
        print 'adding marker:', coord, mtype
        if self.boardmarkers.has_key(coord):
            existingmarker = self.boardmarkers.pop(coord)
            self.remove_widget(existingmarker)
            
        if mtype == 'triangle':
            newmarker = TriangleMarker(size=self.stonesize, pos=self.coord_to_pos(coord))
        elif mtype == 'square':
            newmarker = SquareMarker(size=self.stonesize, pos=self.coord_to_pos(coord))
        elif mtype == 'circle':
            newmarker = CircleMarker(size=self.stonesize, pos=self.coord_to_pos(coord))
        elif mtype == 'cross':
            newmarker = CrossMarker(size=self.stonesize, pos=self.coord_to_pos(coord))
        elif mtype == 'text':
            newmarker = TextMarker(size=self.stonesize, pos=self.coord_to_pos(coord))
            newmarker.text = other[0]
        else:
            return None
            
        self.colour_marker_for_contrast(coord,newmarker)
        self.add_widget(newmarker)
        self.boardmarkers[coord] = newmarker

    def remove_marker(self,coord):
        if self.boardmarkers.has_key(coord):
            marker = self.boardmarkers.pop(coord)
            self.remove_widget(marker)            

    def clear_markers(self):
        for coord in self.boardmarkers.keys():
            marker = self.boardmarkers.pop(coord)
            self.remove_widget(marker)

    def update_markers(self):
        for coord in self.boardmarkers.keys():
            marker = self.boardmarkers[coord]
            marker.size = self.stonesize
            marker.pos = self.coord_to_pos(coord)
            self.remove_widget(marker)
            self.add_widget(marker)
            
            

    def marker_colour(self, coord):
        if self.stones.has_key(coord):
            stone_colour = self.stones[coord].colour
            return [1-stone_colour[0],1-stone_colour[1],1-stone_colour[2]]
        else:
            return [0,0,0]

    def colour_marker_for_contrast(self, coord, marker):
        markercolour = self.marker_colour(coord)
        marker.markercolour = markercolour
                

    ## Playmarker
    def set_playmarker(self,coord):
        self.remove_widget(self.playmarker)
        marker = PlayMarker(size=self.stonesize, pos=self.coord_to_pos(coord))
        self.colour_marker_for_contrast(coord,marker)
        marker.coord = coord
        self.add_widget(marker)
        self.playmarker = marker

    def remove_playmarker(self):
        self.remove_widget(self.playmarker)
        self.playmarker = None

    def update_playmarker(self):
        if self.playmarker is not None:
            self.set_playmarker(self.playmarker.coord)
        self.set_playmarker

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
        self.update_playmarker()
        self.update_markers()

    def on_pos(self,*args,**kwargs):
        self.on_size()


    def coord_to_pos(self, coord):
        gridspacing = self.gridspacing
        realcoord = [coord[0],coord[1]]
        if self.flip_horiz:
            realcoord[0] = self.game.size - 1 - realcoord[0]
        if self.flip_vert:
            realcoord[1] = self.game.size - 1 - realcoord[1]
        if self.flip_forwardslash:
            realcoord = realcoord[::-1]
        if self.flip_backslash:
            realcoord = realcoord[self.game.size - 1 - realcoord[0],self.game.size - 1 - realcoord[1]][::-1]

        coord = realcoord
        
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

        self.clear_transient_widgets()
        self.reset_uielements()
        
        if 'remove' in instructions:
            remove_stones = instructions['remove']
            for stone in remove_stones:
                self.remove_stone(coord=stone[0],colour=colourname_to_colour(stone[1]))
        if 'add' in instructions:
            add_stones = instructions['add']
            for stone in add_stones:
                self.add_stone(coord=stone[0],colour=colourname_to_colour(stone[1]))
        if 'empty' in instructions:
            empty_stones = instructions['empty']
            for stone in empty_stones:
                self.empty_stone(coord=stone[0])

        if 'playmarker' in instructions:
            pm = instructions['playmarker']
            print 'Asked to draw pm at', pm
            if pm is not None:
                self.set_playmarker(pm)
        if 'markers' in instructions:
            markers = instructions['markers']
            print 'received markers:', markers
            for marker in markers:
                if marker[1] == 'TR':
                    self.add_marker(marker[0],'triangle')
                elif marker[1] == 'SQ':
                    self.add_marker(marker[0],'square')
                elif marker[1] == 'CR':
                    self.add_marker(marker[0],'circle')
                elif marker[1] == 'MA':
                    self.add_marker(marker[0],'cross')
                elif marker[1] == 'LB':
                    self.add_marker(marker[0],'text',marker[2:])
        if 'variations' in instructions:
            curvar, varnum = instructions['variations']
            if varnum > 1:
                if self.uielements.has_key('varbutton'):
                    for button in self.uielements['varbutton']:
                        button.background_color = [0,1,0,1]
                        button.text = 'Next var\n  (%d / %d)' % (curvar, varnum)
        if 'comment' in instructions:
            commenttext = instructions['comment']
            if self.uielements.has_key('commentbox'):
                for cb in self.uielements['commentbox']:
                    cb.text = commenttext
                    cb.scroll_y = 1
                    cb.scroll_timeout = 0
                    cb.scroll_timeout = 55
        else:
            if self.uielements.has_key('commentbox'):
                for cb in self.uielements['commentbox']:
                    cb.text = '[color=444444]Long press to add comment.[/color]'

        if 'nextplayer' in instructions:
            player = instructions['nextplayer']
            if self.uielements.has_key('playerdetails'):
                for pd in self.uielements['playerdetails']:
                    pd.set_to_play(player)

    def get_player_details(self,*args,**kwargs):
        wname, bname = self.abstractboard.get_player_names()
        wrank, brank = self.abstractboard.get_player_ranks()
        if self.uielements.has_key('playerdetails'):
            pds = self.uielements['playerdetails']
            for pd in pds:
                pd.wtext = wname
                pd.wrank = wrank
                pd.btext = bname
                pd.brank = brank
        

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
        
    def reset_uielements(self,*args,**kwargs):
        for elementtype in self.uielements:
            elements = self.uielements[elementtype]
            for element in elements:
                if elementtype == 'varbutton':
                    element.background_color = [1,0,0,1]
                    element.text = 'Next var\n  (1 / 1)'
                elif elementtype == 'commentbox':
                    element.pre_text = ''
                    element.text = ''
                elif elementtype == 'playerdetails':
                    element.set_to_play(None)

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

    # Variation handling
    def next_variation(self,*args,**kwargs):
        instructions = self.abstractboard.increment_variation()
        self.follow_instructions(instructions)

    def prev_variation(self,*args,**kwargs):
        instructions = self.abstractboard.decrement_variation()
        self.follow_instructions(instructions)

    # Syncing
    def reset_abstractboard(self):
        self.clear_transient_widgets()
        self.reset_uielements()
        self.clear_stones()
        instructions = self.abstractboard.reset_position()
        self.follow_instructions(instructions)
        


class BoardContainer(Widget):
    board = ObjectProperty(None,allownone=True)
    boardsize = ListProperty([10,10])
    boardpos = ListProperty([10,10])

    def __init__(self, **kwargs):
        super(BoardContainer, self).__init__(**kwargs)
        self._keyboard = Window.request_keyboard(
            self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

    def on_size(self,*args,**kwargs):
        self.set_boardsize()
        self.set_boardpos()

    def on_touch_down(self,touch):
        if self.board.navmode == 'Navigate':
            if self.x < touch.x < self.x + self.width and self.y < touch.y < self.y + self.height:
                if touch.x > self.x + 0.5*self.width:
                    self.board.advance_one_move()
                else:
                    self.board.retreat_one_move()

    def _keyboard_closed(self):
        print 'My keyboard has been closed!'
        # self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        # self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        # print 'The key', keycode, 'have been pressed'
        # print ' - text is %r' % text
        # print ' - modifiers are %r' % modifiers

        # Keycode is composed of an integer + a string
        # If we hit escape, release the keyboard
        if keycode[1] == 'escape':
            keyboard.release()
        elif keycode[1] in advancekeys:
            self.board.advance_one_move()
        elif keycode[1] in retreatkeys:
            self.board.retreat_one_move()
        elif keycode[1] in nextvariationkeys:
            self.board.next_variation()
        elif keycode[1] in prevvariationkeys:
            self.board.prev_variation()
        

        # Return True to accept the key. Otherwise, it will be used by
        # the system.
        return True

    def set_boardsize(self):
        mysize = self.size
        if mysize[1] < mysize[0]:
            boardsize = mysize[1]
        else:
            boardsize = mysize[0]
        print 'mysize =', mysize,'-> boardsize-20 = ', boardsize-20
        print 'mypos = ', self.pos
        print 'window size', Window.size
        print 'parent', self.parent

        self.boardsize = [boardsize-2, boardsize-2]

    def set_boardpos(self):
        boardsize = self.boardsize
        sparewidth = self.size[0] - boardsize[0]
        spareheight = self.size[1] - boardsize[1]
        self.boardpos = [self.pos[0] + 1 + 0.5*sparewidth,self.pos[1] + 1 + 0.5*spareheight]



class GobanApp(App):

    def build(self):
        boardcontainer = BoardContainer(size_hint=(1.,0.65))

        abstractboard = AbstractBoard()

        boardcontainer.board.abstractboard = abstractboard

        btn_opensgf = Button(text='Open SGF')
        btn_start = Button(text='Start')
        btn_end = Button(text='End')
        btn_nextvar = Button(text='Next var\n  (1 / 1)')
        btn_nextmove = Button(text='Next')
        btn_prevmove = Button(text='Prev')

        btn_nextvar.background_color = (1,0,0,1)
        boardcontainer.board.uielements['varbutton'] = [btn_nextvar]
        
        btn_start.bind(on_press=partial(boardcontainer.board.jump_to_start))
        btn_end.bind(on_press=partial(boardcontainer.board.jump_to_end))
        btn_nextvar.bind(on_press=partial(boardcontainer.board.next_variation))
        btn_nextmove.bind(on_press=partial(boardcontainer.board.advance_one_move))
        btn_prevmove.bind(on_press=partial(boardcontainer.board.retreat_one_move))

        navigation_layout = BoxLayout(orientation='horizontal',size_hint=(1.,0.09))
        # navigation_layout.add_widget(btn_start)
        navigation_layout.add_widget(btn_opensgf)
        navigation_layout.add_widget(btn_prevmove)
        navigation_layout.add_widget(btn_nextvar)
        navigation_layout.add_widget(btn_nextmove)
        navigation_layout.add_widget(btn_end)

        comment_box = CommentBox(text='',size_hint=(1.,0.18))
        boardcontainer.board.uielements['commentbox'] = [comment_box]

        player_details = PlayerDetails(size_hint=(0.75,1.0))
        boardcontainer.board.uielements['playerdetails'] = [player_details]
        mode_spinner = Spinner(text='Navigate',values=('Navigate', 'Edit', 'Score'),size_hint=(0.25,1.0))
        mode_spinner.bind(text=boardcontainer.board.set_navmode)

        top_layout = BoxLayout(orientation='horizontal',size_hint=(1.,0.08))
        top_layout.add_widget(player_details)
        top_layout.add_widget(mode_spinner)
        

        layout = BoxLayout(orientation='vertical')
        layout.add_widget(top_layout)
        layout.add_widget(boardcontainer)
        layout.add_widget(comment_box)
        layout.add_widget(navigation_layout)

        sgfn = sys.argv[-1]
        if sgfn[-3:] == 'sgf':
            abstractboard.load_sgf_from_file(sgfn)
        else:
            abstractboard.load_sgf_from_file('./67honinbot1.sgf')
        boardcontainer.board.reset_abstractboard()
        boardcontainer.board.get_player_details()

        return layout
        #return boardcontainer


            
if __name__ == '__main__':
    GobanApp().run()

