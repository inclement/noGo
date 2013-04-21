from kivy.app import App
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, Ellipse
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.screenmanager import *
from kivy.utils import platform
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty, ListProperty, AliasProperty, StringProperty, DictProperty, BooleanProperty, StringProperty, OptionProperty
from kivy.vector import Vector
from kivy.clock import Clock

from kivy.input.postproc import doubletap

from random import random as r
from random import choice
from math import sin
from functools import partial
from glob import glob
from os.path import abspath

from gomill import sgf, boards
from abstractboard import *

import sys

# from kivy.config import Config
# Config.set('graphics', 'width', '400')
# Config.set('graphics', 'height', '600')

navigate_text = '[b]Navigation mode[/b] selected. Tap on the right side of the board to advance the game, or the left to move back.'
edit_text = '[b]Edit mode[/b] selected. Use the edit tools below the board to add SGF markers and cut/paste variations.'
score_text = '[b]Score mode[/b] selected. Tap on groups to toggle them as dead/alive.'
record_text = '[b]Record mode[/b] selected. Press, move and release on the board to play stones. Pressing back and replaying a move will give the option of whether to replace the next move or to create a new variation.'

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

def alternate_colour(colour):
    if colour == 'b':
        return 'w'
    elif colour == 'w':
        return 'b'
    else:
        return 'b'

def get_move_marker_colour(col):
    if col == 'w':
        return [1,1,1,0.5]
    elif col == 'b':
        return [0,0,0,0.5]
    else:
        return [0.5,0.5,0.5,0.5]

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

class WhiteStoneImage(Widget):
    pass
class BlackStoneImage(Widget):
    pass

class StandaloneGameChooser(BoxLayout):
    managedby = ObjectProperty(None,allownone=True)
    gameslist = ObjectProperty()
    def populate_from_directory(self,dir):
        sgfs = glob(''.join((dir,'/*.sgf')))
        print 'sgfs found in directory: ',sgfs
        for sgfpath in sgfs:
            sgfpath = abspath(sgfpath)
            info = get_gameinfo_from_file(sgfpath)
            info['filepath'] = sgfpath
            print info
            pathwidget = GameChooserButton(owner=self)
            pathwidget.construct_from_sgfinfo(info)
            self.gameslist.add_widget(pathwidget)

class GameChooserButton(Button):
    info = ObjectProperty()
    owner = ObjectProperty(None)
    filepath = StringProperty('')
    def construct_from_sgfinfo(self,info):
        self.info.construct_from_sgfinfo(info)
    

class GameChooserInfo(BoxLayout):
    owner = ObjectProperty('')
    bname = StringProperty('')
    wname = StringProperty('')
    brank = StringProperty('')
    wrank = StringProperty('')
    result = StringProperty('')
    date = StringProperty('')
    filepath = StringProperty('')
    def construct_from_sgfinfo(self,info):
        if 'bname' in info:
            self.bname = info['bname']
        else:
            self.bname = 'Unknown'
        if 'wname' in info:
            self.wname = info['wname']
        else:
            self.wname = 'Unknown'
        if 'brank' in info:
            self.brank = '(' + info['brank'] + ')'
        if 'wrank' in info:
            self.wrank = '(' + info['wrank'] + ')'
        if 'result' in info:
            result = info['result']
            if result[0] in ['w','W']:
                self.wname = ''.join(('[b]',self.wname,'[/b]'))
            elif result[0] in ['b','B']:
                self.bname = ''.join(('[b]',self.bname,'[/b]'))
            self.result = info['result']
        else:
            self.result = '?'
        if 'date' in info:
            self.date = info['date']
        else:
            self.date = '---'
        if 'filepath' in info:
            self.filepath = info['filepath']
        return self

class NextButton(Button):
    pass

class PrevButton(Button):
    pass

class CommentInput(BoxLayout):
    board = ObjectProperty(None)
    popup = ObjectProperty(None)
    comment = StringProperty('')

class HomeScreen(BoxLayout):
    managedby = ObjectProperty(None,allownone=True)

class PhoneBoardView(BoxLayout):
    manager = ObjectProperty(None)
    boardcontainer = ObjectProperty(None)
    board = ObjectProperty(None)

class MakeMoveMarker(Widget):
    coord = ListProperty((0,0))
    board = ObjectProperty(None)
    colour = ListProperty((1,1,1,0.5))
    def set_position_from_coord(self,coord):
        if self.board is not None:
            if not (0<=coord[0]<self.board.gridsize and 0<=coord[1]<self.board.gridsize):
                self.colour[3] = 0.0
            else:
                self.colour[3] = 0.75
            newpos = self.board.coord_to_pos(self.coord)
            return newpos
        else:
            return (0,0)

class PickNewVarType(FloatLayout):
    board = ObjectProperty(None)
    popup = ObjectProperty(None)
    coord = ListProperty((0,0))

class OpenSgfDialog(FloatLayout):
    board = ObjectProperty(None)
    popup = ObjectProperty(None)

class PlayerDetails(BoxLayout):
    wstone = ObjectProperty(None)
    bstone = ObjectProperty(None)
    board = ObjectProperty(None)
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
    def on_touch_down(self,touch):
        if self.wstone.collide_point(*touch.pos):
            self.board.next_to_play = 'w'
        elif self.bstone.collide_point(*touch.pos):
            self.board.next_to_play = 'b'

class CommentBox(ScrollView):
    pre_text = StringProperty('')
    text = StringProperty('')
    board = ObjectProperty(None,allownone=True)
    def on_touch_down(self,touch):
        super(CommentBox,self).on_touch_down(touch)
        if self.collide_point(*touch.pos):
            if self.board is not None:
                callback = self.board.get_new_comment
                Clock.schedule_once(callback,1.1)
                touch.ud['event'] = callback
    def on_touch_move(self,touch):
        super(CommentBox,self).on_touch_move(touch)
        if (touch.x - touch.ox)**2 + (touch.y - touch.oy)**2 > 25:
            try: 
                Clock.unschedule(touch.ud['event'])
            except KeyError:
                pass
    def on_touch_up(self,touch):
        super(CommentBox,self).on_touch_up(touch)
        try: 
            Clock.unschedule(touch.ud['event'])
        except KeyError:
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
            

starposs = {19:[(3,3),(3,9),(3,15),(9,3),(9,9),(9,15),(15,3),(15,9),(15,15)],
            9:[(2,2),(5,2),(2,5),(5,5),(4,4)]}
            
class GuiBoard(Widget):
    gridsize = NumericProperty(19) # Board size
    navmode = StringProperty('Navigate') # How to scale the board
    abstractboard = ObjectProperty(AbstractBoard()) # Object to query for where to play moves
    uielements = DictProperty({})
    makemovemarker = ObjectProperty(None,allownone=True)
    touchoffset = ListProperty((0,0))

    variations_exist = BooleanProperty(False)

    showcoords = BooleanProperty(False)

    wname = StringProperty('')
    wrank = StringProperty('')
    bname = StringProperty('')
    brank = StringProperty('')
    next_to_play = StringProperty('e')


    comment_pre_text = StringProperty('')
    comment_text = StringProperty('')
    

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
    numcells = NumericProperty(10)
    boardindent = ListProperty((100,100))
    stonesize = ListProperty((100,100))
    gridspacing = NumericProperty(10)
    gridlines = ListProperty([])

    gobanpos = ListProperty((100,100))

    def take_stone_input(self,coords):
        if tuple(coords) not in self.stones:
            existingvars = map(lambda j: j.get_move(),self.abstractboard.curnode)
            alreadyexists = False
            for entry in existingvars:
                if entry[0] == self.next_to_play and entry[1][0] == coords[0] and entry[1][1] == coords[1]:
                    instructions = self.abstractboard.jump_to_node(self.abstractboard.curnode[existingvars.index(entry)])
                    print 'entry already exists!'
                    self.follow_instructions(instructions)
                    return True
            children_exist = self.abstractboard.do_children_exist()
            if not children_exist:
                self.add_new_stone(coords)
            else:
                popup = Popup(content=PickNewVarType(board=self,coord=coords),title='Do you want to...',size_hint=(0.85,0.85))
                popup.content.popup = popup
                popup.open()

    def add_new_stone(self,coords,newtype='newvar'):
        print 'Called add_new_stone', coords, newtype
        colour = self.next_to_play
        if newtype == 'newvar':
            instructions = self.abstractboard.add_new_node(coords,self.next_to_play)
            self.follow_instructions(instructions)
        if newtype == 'newmain':
            instructions = self.abstractboard.add_new_node(coords,self.next_to_play,newmainline=True)
            self.follow_instructions(instructions)
        if newtype == 'replacenext':
            instructions = self.abstractboard.replace_next_node(coords,self.next_to_play)
            self.follow_instructions(instructions)
        print 'add_new_stone received instructions:',instructions

    def open_sgf_dialog(self,*args,**kwargs):
        popup = Popup(content=OpenSgfDialog(board=self),title='Open SGF',size_hint=(0.85,0.85))
        popup.content.popup = popup
        popup.open()

    def load_sgf_from_file(self,path,filen):
        print 'asked to load from',path,filen
        self.abstractboard.load_sgf_from_file(filen[0])
        self.reset_abstractboard()

    def get_new_comment(self,*args,**kwargs):
        print 'get new comment called'
        if self.comment_text == '[color=444444]Long press to add comment.[/color]':
            popup = Popup(content=CommentInput(board=self,comment=''),title='Edit comment:',size_hint=(0.85,0.85))
        else:
            popup = Popup(content=CommentInput(board=self,comment=self.comment_text),title='Edit comment:',size_hint=(0.85,0.85))
        popup.content.popup = popup
        popup.open()

    def set_new_comment(self,comment):
        self.comment_text = comment
        self.abstractboard.curnode.set('C',comment)

    def set_navmode(self,spinner,mode):
        self.navmode = mode
        if mode == 'Navigate':
            self.comment_pre_text = navigate_text + '\n-----\n'
        elif mode == 'Edit':
            self.comment_pre_text = edit_text + '\n-----\n'
        elif mode == 'Score':
            self.comment_pre_text = score_text + '\n-----\n'
        elif mode == 'Record':
            self.comment_pre_text = record_text + '\n-----\n'


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

    def on_size(self,*args,**kwargs):
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

    def pos_to_coord(self,pos):
        gridspacing = self.gridspacing
        relx = (pos[0] - (self.gobanpos[0] + self.boardindent[0])) / gridspacing
        rely = (pos[1] - (self.gobanpos[1] + self.boardindent[1])) / gridspacing
        relx += self.touchoffset[0]
        rely += self.touchoffset[1]
        realcoord = (int(round(relx)),int(round(rely)))
        if self.flip_horiz:
            realcoord[0] = self.game.size - 1 - realcoord[0]
        if self.flip_vert:
            realcoord[1] = self.game.size - 1 - realcoord[1]
        if self.flip_forwardslash:
            realcoord = realcoord[::-1]
        if self.flip_backslash:
            realcoord = realcoord[self.game.size - 1 - realcoord[0],self.game.size - 1 - realcoord[1]][::-1]
        return realcoord

    def get_gridlines(self):
        startx = self.boardindent[0] + self.gobanpos[0]
        starty = self.boardindent[1] + self.gobanpos[1]
        gridspacing = self.gridspacing
        length = self.boardlength
        gridnum = self.gridsize

        gridline = []

        curx = startx
        cury = starty

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
        print '### instructions are', instructions

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
            self.comment_text = commenttext
        else:
            self.comment_text = '[color=444444]Long press to add comment.[/color]'

        if 'nextplayer' in instructions:
            player = instructions['nextplayer']
            if player in ['b','w']:
                self.next_to_play = player
            elif player == 'a':
                self.next_to_play = alternate_colour(self.next_to_play)

    def get_player_details(self,*args,**kwargs):
        wname, bname = self.abstractboard.get_player_names()
        wrank, brank = self.abstractboard.get_player_ranks()
        self.wrank = wrank
        self.wname = wname
        self.brank = brank
        self.bname = bname
        

    def advance_one_move(self,*args,**kwargs):
        children_exist = self.abstractboard.do_children_exist()
        if children_exist:
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
        self.comment_pre_text = ''
        self.comment_text = ''

        #self.next_to_play = 'b'
        
        for elementtype in self.uielements:
            elements = self.uielements[elementtype]
            for element in elements:
                if elementtype == 'varbutton':
                    element.background_color = [1,0,0,1]
                    element.text = 'Next var\n  (1 / 1)'

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
        self.get_player_details()
        self.follow_instructions(instructions)
        


class BoardContainer(Widget):
    board = ObjectProperty(None,allownone=True)
    boardsize = ListProperty([10,10])
    boardpos = ListProperty([10,10])
    uielements = DictProperty({})
    makemovemarker = ObjectProperty(None,allownone=True)

    def __init__(self, **kwargs):
        super(BoardContainer, self).__init__(**kwargs)
        # self._keyboard = Window.request_keyboard(
        #     self._keyboard_closed, self)
        # self._keyboard.bind(on_key_down=self._on_keyboard_down)

    def on_size(self,*args,**kwargs):
        self.set_boardsize()
        self.set_boardpos()

    def on_touch_down(self,touch):
        if self.collide_point(*touch.pos):
            if self.board.navmode == 'Navigate':
                    if touch.x > self.x + 0.5*self.width:
                        self.board.advance_one_move()
                    else:
                        self.board.retreat_one_move()
            elif self.board.navmode in ['Edit','Record']:
                print 'Touch down at', self.board.pos_to_coord(touch.pos)
                print 'next to play is',self.board.next_to_play
                marker = MakeMoveMarker(coord=self.board.pos_to_coord(touch.pos),board=self.board,colour=get_move_marker_colour(self.board.next_to_play))
                if self.makemovemarker is not None:
                    self.remove_widget(self.makemovemarker)
                self.makemovemarker = marker
                self.add_widget(marker)
            elif self.board.navmode == 'Guess'

    def on_touch_move(self,touch):
        if self.makemovemarker is not None:
            self.makemovemarker.coord = self.board.pos_to_coord(touch.pos)

    def on_touch_up(self,touch):
        if self.makemovemarker is not None:
            marker = self.makemovemarker
            finalcoord = marker.coord
            self.makemovemarker = None
            self.remove_widget(marker)
            print 'Marker let go at', finalcoord
            if (0<=finalcoord[0]<self.board.gridsize) and (0<=finalcoord[1]<self.board.gridsize):
                self.board.take_stone_input(finalcoord)


            

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


class NogoManager(ScreenManager):
    pass

class GobanApp(App):

    def build(self):
        sm = NogoManager(transition=SlideTransition(direction='left'))

        pbv = PhoneBoardView()
        pbv.board.load_sgf_from_file('',['./67honinbot1.sgf'])

        gc = StandaloneGameChooser(managedby=sm)

        bv = Screen(name="Board")
        bv.add_widget(pbv)
        hv = Screen(name="Home")
        hv.add_widget(HomeScreen(managedby=sm))
        gv = Screen(name="Choose")
        gv.add_widget(gc)

        gc.populate_from_directory('.')

        pbv.managedby = sm

        sm.add_widget(hv)
        sm.add_widget(bv)
        sm.add_widget(gv)

        return sm
        # return pbv
        #return layout
        #return boardcontainer

    def on_pause(self,*args,**kwargs):
        return True


            
if __name__ == '__main__':
    GobanApp().run()

