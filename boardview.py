from kivy.app import App
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, Ellipse
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.stencilview import StencilView
from kivy.uix.dropdown import DropDown
from kivy.uix.scatter import Scatter
from kivy.uix.spinner import Spinner, SpinnerOption
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.screenmanager import *
from kivy.adapters.listadapter import ListAdapter
#from kivy.uix.listview import ListView, ListItemButton
from mylistview import ListView, ListItemButton
from kivy.utils import platform
from kivy.animation import Animation
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
from os import mkdir
from json import dump as jsondump, load as jsonload, dump as jsondump
import json
from time import asctime, time


from gomill import sgf, boards
from abstractboard import *

import sys

navigate_text = '[b]Navigation mode[/b] selected. Tap on the right side of the board to advance the game, or the left to move back.'
edit_text = '[b]Edit mode[/b] selected. Use the edit tools below the board to add SGF markers and cut/paste variations.'
score_text = '[b]Score mode[/b] selected. Tap on groups to toggle them as dead/alive.'
play_text = '[b]Play mode[/b] selected. Press, move and release on the board to play stones. Pressing back and replaying a move will give the option of whether to replace the next move or to create a new variation.'
guess_text = '[b]Guess mode[/b] selected. Try to play stones that match the existing game. A marker indicates how good the guess was, and if correct the game advances.'
zoom_text = '[b]Zoom mode[/b] selected. Experimental.'

blacknames = ['black','b','B','Black']
whitenames = ['white','w','W','White']

def format_score(score):
    if score == 0:
        return '[color=#ff0000]j[/color][color=#00ff00]i[/color][color=#ff0000]g[/color][color=#00ff00]o[/color]'
    elif score > 0:
        return 'B+%.1f' % score
    else:
        return 'W+%.1f' % abs(score)

def alternate_colour(colour):
    if colour == 'b':
        return 'w'
    elif colour == 'w':
        return 'b'
    else:
        return 'b'

def colourname_to_colour(colourname):
    if colourname in blacknames:
        return 'black'
    elif colourname in whitenames:
        return 'white'
    else:
        return None

def get_move_marker_colour(col):
    if col == 'w':
        return [1,1,1,0.5]
    elif col == 'b':
        return [0,0,0,0.5]
    else:
        return [0.5,0.5,0.5,0.5]

class LDMarker(Widget):
    pass

class VarBranchButton(Button):
    pass

class GameInfo(BoxLayout):
    popup = ObjectProperty(None,allownone=True)
    board = ObjectProperty(None,allownone=True)
    bname = StringProperty('')
    wname = StringProperty('')
    brank = StringProperty('')
    wrank = StringProperty('')
    komi = StringProperty('')
    result = StringProperty('')
    event = StringProperty('')
    def populate_from_gameinfo(self,gi):
        if 'bname' in gi:
            self.bname = gi['bname']
        if 'wname' in gi:
            self.wname = gi['wname']
        if 'brank' in gi:
            self.brank = gi['brank']
        if 'wrank' in gi:
            self.wrank = gi['wrank']
        if 'komi' in gi:
            self.komi = str(gi['komi'])
        if 'result' in gi:
            self.result = gi['result']
        if 'event' in gi:
            self.event = gi['event']

class GuessPopup(Widget):
    alpha = NumericProperty(1)
    colour = ListProperty([1,0,0])
    pass

class PlayerDetails(BoxLayout):
    wstone = ObjectProperty(None)
    bstone = ObjectProperty(None)
    board = ObjectProperty(None)
    wtext = StringProperty('W player')
    wrank = StringProperty('')
    btext = StringProperty('B player')
    brank = StringProperty('')
    next_to_play = StringProperty('')
    wtoplaycolour = ListProperty([0,1,0,1])
    btoplaycolour = ListProperty([0,1,0,1])
    def set_to_play(self,player):
        print 'set_to_play called!',player
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

class TabletBoardView(BoxLayout):
    managedby = ObjectProperty(None,allownone=True)
    screenname = StringProperty('')
    boardcontainer = ObjectProperty(None,allownone=True)
    board = ObjectProperty(None,allownone=True)
    spinner = ObjectProperty(None,allownone=True)

class PhoneBoardView(BoxLayout):
    managedby = ObjectProperty(None,allownone=True)
    screenname = StringProperty('')
    boardcontainer = ObjectProperty(None,allownone=True)
    board = ObjectProperty(None,allownone=True)
    spinner = ObjectProperty(None,allownone=True)
    def rottest(self,num):
        Window.rotation = num

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
    imagepath = StringProperty('./black_stone.png')
    def set_colour(self,colour):
        if colour == 'black':
            self.colour = [0,0,0]
            self.imagepath = './black_stone.png'
        elif colour == 'white':
            self.colour = [1,1,1]
            self.imagepath = './white_stone.png'
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

starposs = {19:[(3,3),(3,9),(3,15),(9,3),(9,9),(9,15),(15,3),(15,9),(15,15)],
            13:[(3,3),(3,9),(9,3),(9,9),(6,6)],
            9:[(2,2),(6,2),(2,6),(6,6),(4,4)]}

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

class GuiBoard(Widget):
    gridsize = NumericProperty(19) # Board size
    navmode = StringProperty('Navigate') # How to scale the board
    abstractboard = ObjectProperty(None,allownone=True) # Object to query for where to play moves
    uielements = DictProperty({})
    makemovemarker = ObjectProperty(None,allownone=True)
    touchoffset = ListProperty([0,0])
    guesses = ListProperty([0,0])
    gameinfo = DictProperty({})

    # Save state
    user_saved = BooleanProperty(False)
    temporary_filepath = StringProperty('')
    permanent_filepath = StringProperty('')
    has_unsaved_data = BooleanProperty(False)

    # Score mode 
    ld_markers = DictProperty({})
    scoreboard = ObjectProperty(None,allownone=True)

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
    guesspopup = ObjectProperty(None,allownone=True)
    varstones = DictProperty({})

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

    def __init__(self,*args,**kwargs):
        super(GuiBoard,self).__init__(*args,**kwargs)
        print 'GuiBoard init, making abstractboard with gridsize', self.gridsize
        self.abstractboard = AbstractBoard(gridsize=self.gridsize)
        self.reset_abstractboard()

    def start_autoplay(self,*args,**kwargs):
        Clock.schedule_interval(self.advance_one_move,0.25)
        self.pre_text = '[b]Autoplay[/b] activated. Tap on the navigation buttons (or the board in navigation mode) to stop autoplaying.'
    def stop_autoplay(self,*args,**kwargs):
        try:
            Clock.unschedule(self.advance_one_move)
        except:
            pass

    def set_game_info(self,info):
        self.abstractboard.set_gameinfo(info)
        self.get_game_info()

    def get_game_info(self):
        self.gameinfo = self.abstractboard.get_gameinfo()
        if not self.user_saved:
            if self.gameinfo.has_key('filepath'):
                self.permanent_filepath = self.gameinfo['filepath']

    def view_game_info(self):
        gi = GameInfo(board=self)
        gi.populate_from_gameinfo(self.gameinfo)
        popup = Popup(content=gi,title='Game info.',size_hint=(0.85,0.85))
        popup.content.popup = popup
        popup.open()

    def save_sgf(self,saveas=False,autosave=False):
        if autosave:
            if self.permanent_filepath != '':
                self.abstractboard.save_sgf(self.permanent_filepath)
            else:
                if self.temporary_filepath == '':
                    self.temporary_filepath = get_temp_filepath()
                self.abstractboard.save_sgf(self.temporary_filepath)
        elif saveas:
            self.ask_where_to_save()
        else:
            if self.permanent_filepath != '':
                self.abstractboard.save_sgf(self.permanent_filepath)
            else:
                self.ask_where_to_save()

    def ask_where_to_save(self,force=True):
        sq = SaveQuery(board=self)
        popup = Popup(content=sq,title='Where to save?',size_hint=(0.85,0.85))
        popup.content.popup = popup
        fileh = open('game_collection_locations.json','r')
        collection_folders = jsonload(fileh)
        fileh.close()
        collections_args_converter = get_collectioninfo_from_dir
        list_adapter = ListAdapter(data=collection_folders,
                                   args_converter=collections_args_converter,
                                   selection_mode='single',
                                   allow_empty_selection=True,
                                   cls=CollectionChooserButton
                                   )
        sq.collections_list.adapter = list_adapter
        popup.open()

    def make_savefile_in_dir(self,dirn):
        filen = ''.join((dirn,'/',asctime().replace(' ','_')))
        if 'wname' in self.gameinfo:
            filen += '_' + self.gameinfo['wname']
        else:
            filen += '_' + 'wunknown'
        if 'bname' in self.gameinfo:
            filen += '_' + self.gameinfo['bname']
        else:
            filen += '_' + 'bunknown'
        if 'event' in self.gameinfo:
            filen += '_' + self.gameinfo['event']
        else:
            filen += '_' + 'eunknown'
        filen += '.sgf'
        self.permanent_filepath = filen
        self.user_saved = True
        self.save_sgf()

    def back_to_varbranch(self):
        instructions = self.abstractboard.jump_to_varbranch()
        self.follow_instructions(instructions)

    def take_stone_input(self,coords):
        if tuple(coords) not in self.stones:
            if self.navmode == 'Play':
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
            elif self.navmode == 'Guess':
                self.guesses[1] += 1
                nextcoords = self.abstractboard.get_next_coords()
                if nextcoords[0] is not None and nextcoords[1] is not None:
                    correct = False
                    if coords[0] == nextcoords[0] and coords[1] == nextcoords[1]:
                        self.guesses[0] += 1
                        correct = True
                        instructions = self.abstractboard.advance_position()
                        self.follow_instructions(instructions)
                    pre_text = '%.1f%% correct' % (100*float(self.guesses[0])/self.guesses[1])
                    if not correct:
                        off_by_x = abs(coords[0]-nextcoords[0])
                        off_by_y = abs(coords[1]-nextcoords[1])
                        self.set_guess_popup(coords,max(off_by_x,off_by_y))
                        pre_text = '[color=ff0000]Wrong[/color] - ' + pre_text
                    else:
                        pre_text = '[color=00ff00]Correct![/color] - ' + pre_text
                    pre_text += '\n-----\n'
                    self.comment_pre_text = pre_text
                    
    def set_guess_popup(self,centre, size):
        if self.guesspopup is not None:
            self.remove_widget(self.guesspopup)
            self.guesspopup = None
        centrecoords = self.coord_to_pos(centre)
        cx,cy = centrecoords
        lr = (cx - (size+0.25)*self.stonesize[0], cy - (size+0.25)*self.stonesize[1])
        tr = (cx + (size+1.25)*self.stonesize[0], cy + (size+1.25)*self.stonesize[1])
        markerpos = lr
        markersize = (tr[0]-lr[0],tr[1]-lr[1])
        markercolour = [0. + size/(0.5*self.gridsize), 1. - size/(0.5*self.gridsize), 0.]
        gp = GuessPopup(pos=markerpos, size=markersize, colour=markercolour,alpha=0.1)
        self.guesspopup = gp
        ani = Animation(alpha=1.0,t='in_out_quad',duration=0.2) + Animation(alpha=(0.15),t='in_out_quad', duration=0.5)
        #ani.bind(on_complete=self.remove_guess_popup)
        ani.start(gp)
        self.add_widget(gp)

    def remove_guess_popup(self,*args,**kwargs):
        if self.guesspopup is not None:
            self.remove_widget(self.guesspopup)
            self.guesspopup = None

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
        if newtype == 'insert':
            instructions = self.abstractboard.insert_before_next_node(coords,self.next_to_play)
            self.follow_instructions(instructions)
        print 'add_new_stone received instructions:',instructions

    def open_sgf_dialog(self,*args,**kwargs):
        popup = Popup(content=OpenSgfDialog(board=self),title='Open SGF',size_hint=(0.85,0.85))
        popup.content.popup = popup
        popup.open()

    def load_sgf_from_file(self,path,filen):
        print 'asked to load from',path,filen
        self.abstractboard.load_sgf_from_file(filen[0])
        self.permanent_filepath = self.abstractboard.filepath
        self.reset_abstractboard()

    def get_new_comment(self,*args,**kwargs):
        print 'get new comment called'
        if self.comment_text == '[color=444444]Long press to add comment.[/color]':
            popup = Popup(content=CommentInput(board=self,comment=''),title='Edit comment:',size_hint=(0.85,0.85))
        else:
            popup = Popup(content=CommentInput(board=self,comment=self.comment_text),title='Edit comment:',size_hint=(0.85,0.85))
        popup.content.popup = popup
        if platform() == 'android':
            android.vibrate(0.1)
        popup.open()

    def set_new_comment(self,comment):
        self.comment_text = comment
        self.abstractboard.curnode.set('C',comment)

    def clear_ld_markers(self):
        for coords in self.ld_markers:
            marker = self.ld_markers[coords]
            self.remove_widget(marker)
        self.ld_markers = {}
        print 'new self.ld_markers', self.ld_markers

    def make_scoreboard(self):
        if self.scoreboard is not None:
            self.scoreboard = None
        sb = ScoreBoard(self.gridsize)
        sb.board = self.abstractboard.get_current_boardpos()
        self.scoreboard = sb

    def set_navmode(self,spinner,mode):
        self.scoreboard = None
        self.clear_ld_markers()
        if mode != 'Guess':
            self.remove_guess_popup()
        self.navmode = mode
        if mode == 'Navigate':
            self.comment_pre_text = navigate_text + '\n-----\n'
        elif mode == 'Play':
            self.comment_pre_text = play_text + '\n-----\n'
        elif mode == 'Score':
            self.make_scoreboard()
            score = self.scoreboard.get_score()
            self.comment_pre_text = score_text + '\n-----\n'
        elif mode == 'Guess':
            self.comment_pre_text = guess_text + '\n-----\n'
        elif mode == 'Zoom':
            self.comment_pre_text = zoom_text + '\n-----\n'


    def clear_transient_widgets(self):
        self.remove_playmarker()
        # self.remove_komarker()
        self.clear_markers()
        self.clear_variation_stones()

    ## Board markers
    def toggle_ld_marker(self,coord):
        if self.ld_markers.has_key(coord):
            existingmarker = self.ld_markers.pop(coord)
            self.remove_widget(existingmarker)
        else:
            newmarker = LDMarker(size=self.stonesize, pos=self.coord_to_pos(coord))
            self.add_widget(newmarker)
            self.ld_markers[coord] = newmarker
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

    def on_gobanpos(self,*args,**kwargs):
        self.gridlines = self.get_gridlines()

        self.update_starpoints()
        self.update_stones()
        self.update_playmarker()
        self.update_markers()

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

        t1 = time()
        
        self.clear_transient_widgets()
        self.reset_uielements()
        self.remove_guess_popup()

        t2 = time()
        
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

        t3 = time()

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
        if 'varpositions' in instructions:
            vars = instructions['varpositions']
            for entry in vars:
                colour,coord,number = entry
                self.add_variation_stone(coord,colour,number)

        t4 = time()
                
        if 'comment' in instructions:
            commenttext = instructions['comment']
            self.comment_text = commenttext
        else:
            self.comment_text = '[color=444444]Long press to add comment.[/color]'

        if 'nextplayer' in instructions:
            player = instructions['nextplayer']
            if player in ['b','w']:
                print 'next_to_play from',self.next_to_play
                self.next_to_play = player
                print '-->',self.next_to_play
            elif player == 'a':
                self.next_to_play = alternate_colour(self.next_to_play)

        if 'pre_text' in instructions:
            text = instructions['pre_text']
            self.comment_pre_text = text

        if 'unsaved' in instructions:
            self.has_unsaved_data = True
        if 'saved' in instructions:
            self.has_unsaved_data = False

        t5 = time()

        tottime = t5-t1
        print '## Follow instruction times'
        print '## Total', t5-t1
        print '## Reset', t2-t1, (t2-t1)/tottime
        print '## Add remove empty', t3-t2, (t3-t2)/tottime
        print '## Playmarker, positions etc.', t4-t3, (t4-t3)/tottime
        print '## Comment and saved', t5-t4, (t5-t4)/tottime

    def get_player_details(self,*args,**kwargs):
        wname, bname = self.abstractboard.get_player_names()
        wrank, brank = self.abstractboard.get_player_ranks()
        self.wrank = wrank
        self.wname = wname
        self.brank = brank
        self.bname = bname
        

    def advance_one_move(self,*args,**kwargs):
        print '%% Advancing one move!', time()
        if self.navmode == 'Score':
            self.clear_ld_markers()
            self.make_scoreboard()
        t1 = time()
        children_exist = self.abstractboard.do_children_exist()
        t2 = time()
        if children_exist:
            instructions = self.abstractboard.advance_position()
            self.follow_instructions(instructions)
        else:
            if platform() == 'android':
                android.vibrate(0.1)
        t3 = time()
        print '%% Times taken:'
        print '%% Total', t3-t1
        print '%% Children exist', t2-t1
        print '%% Follow instructions', t3-t2
        print '%%'


    def retreat_one_move(self,*args,**kwargs):
        if self.navmode == 'Score':
            self.clear_ld_markers()
            self.make_scoreboard()
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

    def add_variation_stone(self,coord=(1,1),colour='black',num=1,*args,**kwargs):
        stonesize = self.stonesize
        stone = VarStone(size=stonesize, pos=self.coord_to_pos(coord), text=str(num))
        stone.set_colour(colour)
        if self.varstones.has_key(coord):
            self.remove_stone(coord)
        self.varstones[coord] = stone
        self.add_widget(stone)

    def clear_variation_stones(self):
        for coord in self.varstones.keys():
            stone = self.varstones.pop(coord)
            self.remove_widget(stone)

    def add_stone(self,coord=(1,1),colour='black',*args,**kwargs):
        stonesize = self.stonesize
        t1 = time()
        stone = Stone(size=stonesize, pos=self.coord_to_pos(coord))
        stone.set_colour(colour)
        t2 = time()
        if self.stones.has_key(coord):
            self.remove_stone(coord)
        self.stones[coord] = stone
        t3 = time()
        self.add_widget(stone)
        t4 = time()
        print '@@ total', t4-t1
        print '@@ make stone', t2-t1, (t2-t1)/(t4-t1)
        print '@@ add to dict', t3-t2, (t3-t2)/(t4-t1)
        print '@@ add widget', t4-t3, (t4-t3)/(t4-t1)

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
        self.gameinfo = self.abstractboard.get_gameinfo()

    def reset_gridsize(self,newsize):
        self.gridsize = newsize
        self.abstractboard = AbstractBoard(gridsize=newsize)
        print 'New gridsize is', self.gridsize
        print 'New abstractboard gridsize', self.abstractboard.game.size
        

class BoardContainer(StencilView):
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
        self.board.stop_autoplay()
        if self.collide_point(*touch.pos):
            if self.board.navmode == 'Navigate':
                if touch.x > self.x + 0.5*self.width:
                    self.board.advance_one_move()
                else:
                    self.board.retreat_one_move()
            elif self.board.navmode in ['Play','Guess']:
                print 'Touch down at', self.board.pos_to_coord(touch.pos)
                print 'next to play is',self.board.next_to_play
                marker = MakeMoveMarker(coord=self.board.pos_to_coord(touch.pos),board=self.board,colour=get_move_marker_colour(self.board.next_to_play))
                if self.makemovemarker is not None:
                    self.remove_widget(self.makemovemarker)
                self.makemovemarker = marker
                self.add_widget(marker)
            elif self.board.navmode == 'Score':
                coord = self.board.pos_to_coord(touch.pos)
                changed, newscore = self.board.scoreboard.toggle_status_at(coord)
                print changed, newscore
                for coords in changed:
                    self.board.toggle_ld_marker(coords)
                if self.board.gameinfo.has_key('komi'):
                    komi = float(self.board.gameinfo['komi'])
                newscore -= komi
                self.board.comment_pre_text = 'Score: %s\n-----\n' % (format_score(newscore))
            elif self.board.navmode == 'Zoom':
                ani = Animation(gobanpos=(self.board.gobanpos[0]-100,self.board.gobanpos[1]-100),t='in_out_quad',duration=2) + Animation(gobanpos=self.board.gobanpos,t='in_out_quad',duration=2)
                ani.start(self.board)
                

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

class EditPanel(GridLayout):
    current_mode = OptionProperty('bwplay',options=['bwplay',
                                                    'wbplay',
                                                    'triangle',
                                                    'square',
                                                    'circle',
                                                    'cross',
                                                    'bstone',
                                                    'wstone',
                                                    'estone'])

class CommentInput(BoxLayout):
    board = ObjectProperty(None)
    popup = ObjectProperty(None)
    comment = StringProperty('')

class SaveQuery(BoxLayout):
    collections_list = ObjectProperty(None,allownone=True)
    board = ObjectProperty(None,allownone=True)

def get_collectioninfo_from_dir(row_index,dirn):
    sgfs = glob(dirn + '/*.sgf')
    colname = dirn.split('/')[-1]
    return {'colname': colname, 'coldir': dirn, 'numentries': len(sgfs)}
