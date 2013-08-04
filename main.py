#!/usr/bin/env python2

# Copyright 2013 Alexander Taylor

# This file is part of noGo.

# noGo is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

# noGo is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with noGo. If not, see http://www.gnu.org/licenses/gpl-3.0.txt

print 'DEBUG STUFF'
import os
print 'THIS DIR'
print os.listdir('.')

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
from os.path import abspath, exists
from os import mkdir, rename, environ, getenv, putenv
from shutil import copyfile
from json import dump as jsondump, load as jsonload, dump as jsondump
import json
from time import asctime, time, sleep

from gomill import sgf, boards
from abstractboard import *
from boardview import GuiBoard, BoardContainer, PhoneBoardView, GuessPopup, SaveQuery, MySpinnerOption
from boardwidgets import Stone, TextMarker, TriangleMarker, SquareMarker, CircleMarker, CrossMarker, VarStone
from miscwidgets import VDividerLine, DividerLine, WhiteStoneImage, BlackStoneImage, CarouselRightArrow, CarouselLeftArrow
from info import InfoPage
from homepage import HomeScreen, OpenSgfDialog
from sgfcollections import DeleteCollectionQuestion, CollectionNameChooser, StandaloneGameChooser, GameChooserInfo, get_collectioninfo_from_dir, OpenChooserButton, CollectionsIndex, CollectionChooserButton, GameChooserButton, DeleteSgfQuestion, CollectionsList, Collection, CollectionSgf, get_collectioninfo_from_collection
from widgetcache import WidgetCache

import sys

# from kivy.config import Config
# Config.set('graphics', 'width', '400')
# Config.set('graphics', 'height', '600')




# Keybindings
advancekeys = ['right','l']
retreatkeys = ['left','h']
nextvariationkeys = ['up','k']
prevvariationkeys = ['down','j']

trianglecodes = ['triangle','TR']
squarecodes = ['square','SQ']
circlecodes = ['circle','CR']
crosscodes = ['cross','MA']
textcodes = ['text','LB']
def boardname_to_filepath(name):
    if name == 'full board photo':
        return './media/boards/edphoto_full_small2.png'
    elif name == 'board section photo 1':
        return './media/boards/edphoto_section.png'
    elif name == 'lightened board photo 1':
        return './media/boards/edphoto_section_light.png'
    elif name == 'board section photo 2':
        return './media/boards/edphoto_section_2.png'
    elif name == 'plain dark':
        return './media/boards/plain_light.png'
    else:
        return './media/boards/none.png'

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

def set_board_height(boardcontainer):
    width = Window.width
    height = Window.height
    print 'window height,width',height,width
    if height > width:
        boardheight = width
        boardcontainer.height = boardheight
        boardcontainer.size_hint_y = None
        print 'boardcontainer size',boardcontainer.size,boardcontainer.size_hint
    
        

def get_game_chooser_info_from_boardname(sm,boardname):
    board = sm.get_screen(boardname).children[0].board
    gameinfo = board.collectionsgf.info_for_button()
    if 'wname' in gameinfo:
        wname = gameinfo['wname']
    else:
        wname = 'Unknown'
    if 'bname' in gameinfo:
        bname = gameinfo['bname']
    else:
        bname = 'Unknown'
    if 'filepath'  in gameinfo:
        filepath = gameinfo['filepath']
    else:
        filepath = 'Not yet saved'
    if 'date' in gameinfo:
        date = gameinfo['date']
    else:
        date = '---'
    return {'boardname': boardname, 'wname': wname, 'bname': bname, 'filepath': filepath, 'date': date}

def get_temp_filepath():
    tempdir = './games/unsaved'
    return tempdir + '/' + asctime().replace(' ','_') + '.sgf'


class BoardSizeButton(ToggleButton):
    gridsize = NumericProperty(19)
    def current_selected_size(self):
        ws = self.get_widgets('sizebuttons')
        for entry in ws:
            if entry.state == 'down':
                return entry.gridsize
        return 19

class NewBoardQuery(BoxLayout):
    collections_list = ObjectProperty(None,allownone=True)
    manager = ObjectProperty(None,allownone=True)
 


class BoardSizeButton(ToggleButton):
    gridsize = NumericProperty(19)
    def current_selected_size(self):
        ws = self.get_widgets('sizebuttons')
        for entry in ws:
            if entry.state == 'down':
                return entry.gridsize
        return 19

class NewBoardQuery(BoxLayout):
    collections_list = ObjectProperty(None,allownone=True)
    manager = ObjectProperty(None,allownone=True)

    
class GameOptions(DropDown):
    board = ObjectProperty(None,allownone=True)

class GameOptionsButton(Button):
    ddn = ObjectProperty(None,allownone=True)
    board = ObjectProperty(None,allownone=True)
    def __init__(self,*args,**kwargs):
        super(GameOptionsButton,self).__init__()
        self.ddn = GameOptions(board=self.board)
    def on_touch_up(self,touch):
        self.ddn.board = self.board
        if touch.grab_current == self:
            self.ddn.open(self)
        return super(GameOptionsButton,self).on_touch_up(touch)
        

class NextButton(Button):
    board = ObjectProperty(None,allownone=True)
    def on_touch_down(self, touch):
        super(NextButton,self).on_touch_down(touch)
        if self.collide_point(*touch.pos):
            if self.board is not None:
                self.board.stop_autoplay()
                callback = self.board.start_autoplay
                Clock.schedule_once(callback,1.1)
                touch.ud['event'] = callback
    def on_touch_up(self,touch):
        super(NextButton,self).on_touch_up(touch)
        try: 
            Clock.unschedule(touch.ud['event'])
        except KeyError:
            pass

class PrevButton(Button):
    pass








starposs = {19:[(3,3),(3,9),(3,15),(9,3),(9,9),(9,15),(15,3),(15,9),(15,15)],
            13:[(3,3),(3,9),(9,3),(9,9),(6,6)],
            9:[(2,2),(6,2),(2,6),(6,6),(4,4)]}
            


class NogoManager(ScreenManager):
    app = ObjectProperty(None,allownone=True)
    boards = ListProperty([])
    back_screen_name = StringProperty('')

    # Settings properties to keep an eye on
    touchoffset = ListProperty([0,0])
    coordinates = BooleanProperty(False)
    display_markers = BooleanProperty(True)
    boardtype = StringProperty('./media/boards/none.png')

    collectionindex_to_refresh = BooleanProperty(False)
    homescreen_to_refresh = BooleanProperty(False)
    collections_to_refresh = ListProperty([])

    def open_from_intentpath(self,path):
        print 'asked to open_from_intentpath',path
        names = self.screen_names
        for name in names:
            if name[:5] == 'Board':
                board = self.get_screen(name)
                try:
                    if board.children[0].board.collectionsgf.filen == path:
                        print 'filen is correct, name is',name
                        self.switch_and_set_back(name)
                        return
                except IndexError:
                    print 'Tried to go to board that doesn\'t exist, maybe didn\'t load properly'
        print 'path not already open, opening'
        self.new_board(from_file=path,mode='Navigate')

    def on_current(self,*args,**kwargs):
        super(NogoManager,self).on_current(*args,**kwargs)
        if self.current == 'Home' and self.homescreen_to_refresh:
            self.refresh_open_games()
            self.homescreen_to_refresh = False
        if self.current == 'Collections Index' and self.collectionindex_to_refresh:
            self.refresh_collections_index()
            self.collectionindex_to_refresh = False
    
    def add_collection_refresh_reminder(self, collection):
        print 'Asked to remind collection refresh',collection
        if collection not in self.collections_to_refresh:
            self.collections_to_refresh.append(collection)
    
    def switch_and_set_back(self,newcurrent):
        print 'Asked to switch and set back',self.transition.is_active
        if not self.transition.is_active:
            self.back_screen_name = self.current
            self.current = newcurrent
        print 'Finished switching'
    def go_home(self):
        if not self.transition.is_active:
            self.transition = SlideTransition(direction='right')
            self.current = 'Home'
            self.back_screen_name = 'Home'
            self.transition = SlideTransition(direction='left')
    def handle_android_back(self):
        if platform() == 'android':
            import android
            res = android.hide_keyboard()
        self.go_back()
    def go_back(self):
        if not self.transition.is_active:
            self.transition = SlideTransition(direction='right')
            if self.current == self.back_screen_name or self.current[:5] == 'Board':
                self.back_screen_name = 'Home'
            if self.has_screen(self.back_screen_name):
                self.current = self.back_screen_name
            else:
                self.current = 'Home'
            self.transition = SlideTransition(direction='left')
    def set_current_from_opengameslist(self,l):
        print 'open games list is',l
        if len(l)>0:
            screenname = l[0].boardname
            self.back_screen_name = self.current
            self.current = screenname
    def open_help(self):
        if self.has_screen('Info Page'):
            self.switch_and_set_back('Info Page')
        else:
            fileh = open('README.rst','r')
            readme = fileh.read()
            fileh.close()
            infoscreen = Screen(name='Info Page')
            infoscreen.add_widget(InfoPage(infotext=readme))
            self.add_widget(infoscreen)
            self.switch_and_set_back('Info Page')
    def view_or_open_collection(self,selection,goto=True):
        print 'asked to view_or_open',selection
        if len(selection) == 0:
            return False
        collection_name = selection[0].colname
        if self.has_screen('Collection ' + collection_name):
            print 'screen already exists',collection_name
            print 'supposed to refresh',self.collections_to_refresh
            matching_refresh = filter(lambda j: j.name == collection_name,self.collections_to_refresh)
            if len(matching_refresh) > 0:
                self.refresh_collection(matching_refresh[0])
                self.collections_to_refresh.remove(matching_refresh[0])
            self.current = 'Collection ' + collection_name
        else:
            collections = App.get_running_app().collections
            matching_collections = filter(lambda j: j.name == collection_name,collections.collections)
            if len(matching_collections) > 0:
                collection = matching_collections[0]
                print 'Established opening',collection
                screenname = 'Collection ' + collection.name
                games = collection.games
                args_converter = lambda k,j: j.info_for_button()
                print 'made args converter',games
                if len(games)>0:
                    print args_converter('yay',games[0])
                list_adapter = ListAdapter(data=games,
                                           args_converter = args_converter,
                                           selection_mode = 'single',
                                           allow_empty_selection=True,
                                           cls=GameChooserButton,
                                           )
                gc = StandaloneGameChooser(managedby=self,collection=collection)
                gc.gameslist.adapter = list_adapter
                print 'made gc and set adapter'
                print 'games are',games
                print 'gameinfos are', map(lambda j: j.gameinfo,games)
                s = Screen(name=screenname)
                s.add_widget(gc)
                self.add_widget(s)
                if goto:
                    self.switch_and_set_back(s.name)
    def refresh_open_games(self):
        homepage = self.get_screen('Home')
        args_converter = lambda c,j: get_game_chooser_info_from_boardname(self,j)
        list_adapter = ListAdapter(data=self.boards,
                                   args_converter=args_converter,
                                   selection_mode='single',
                                   allow_empty_selection=True,
                                   cls=OpenChooserButton,
                                   )
        homepage.children[0].opengames.adapter = list_adapter

    def refresh_collection(self,collection):
        print 'Asked to refresh collection',collection,collection.name
        matching_screens = filter(lambda j: j == ('Collection ' + collection.name),self.screen_names)
        if len(matching_screens) > 0:
            scr = self.get_screen(matching_screens[0])
            gc = scr.children[0]
            games = collection.games
            args_converter = lambda k,j: j.info_for_button()
            #args_converter = testconverter
            list_adapter = ListAdapter(data=games,
                                       args_converter = args_converter,
                                       selection_mode = 'single',
                                       allow_empty_selection=True,
                                       cls=GameChooserButton,
                                       )
            gc.gameslist.adapter = list_adapter
        self.refresh_collections_index()
    def open_sgf_dialog(self):
        popup = Popup(content=OpenSgfDialog(manager=self),title='Open SGF',size_hint=(0.85,0.85))
        popup.content.popup = popup
        popup.open()
    def board_from_gamechooser(self,selection):
        if len(selection) > 0:
            button = selection[0]
            collection = button.collection
            collectionsgf = button.collectionsgf
            self.new_board(with_collectionsgf=collectionsgf,mode='Navigate')
    def close_board_from_selection(self,sel):
        print 'asked to close from sel',sel
        if len(sel) > 0:
            self.close_board(sel[0].boardname)
    def close_board(self,name):
        if self.has_screen(name):
            pbvs = self.get_screen(name)
            try:
                pbvs.children[0].board.save_sgf()
            except IndexError:
                pass # Board not initialised
            self.remove_widget(pbvs)
            self.boards.remove(name)
            print 'new boards',self.screens
    def new_board_dialog(self):
        print 'Opening new_board_dialog'
        dialog = NewBoardQuery(manager=self)
        popup = Popup(content=dialog,title='Create new board...',size_hint=(0.85,0.9))
        popup.content.popup = popup
        collections_list = App.get_running_app().collections.collections
        collections_args_converter = get_collectioninfo_from_collection
        list_adapter = ListAdapter(data=collections_list,
                                   args_converter=collections_args_converter,
                                   selection_mode='single',
                                   allow_empty_selection=True,
                                   cls=CollectionChooserButton
                                   )
        dialog.collections_list.adapter = list_adapter
        popup.open()
    def new_board_from_selection(self,sel,gridsize=19,handicap=0):
        if len(sel)>0:
            collection = sel[0].collection
        else:
            collection = App.get_running_app().get_default_collection()
        self.new_board(in_collection=collection,gridsize=gridsize,handicap=handicap)
    def new_board(self,with_collectionsgf=None,in_collection=None,from_file='',mode='Play',gridsize=19,handicap=0):
        load_from_file = False

        print '%% NEW BOARD'
        print with_collectionsgf, in_collection, from_file
        print type(from_file)
        t1 = time()

        # Get a collection and collectionsgf to contain and represent the board 
        filen = from_file
        if with_collectionsgf is not None:
            collectionsgf = with_collectionsgf
            filen = collectionsgf.filen
            collection = collectionsgf.collection
            newboard = False
            load_from_file = True
        elif in_collection is not None:
            collection = in_collection
            collectionsgf = collection.add_game(can_change_name=True)
            load_from_file = False
            if from_file != '':
                load_from_file = True
                filen = from_file
                collectionsgf.filen = filen
                collectionsgf.can_change_name = False
        else:
            collection = App.get_running_app().get_default_collection()
            collectionsgf = collection.add_game()
            print 'Made new collectionsgf for the game',collectionsgf
            load_from_file = False
            if from_file != '':
                load_from_file = True
                filen = from_file
                collectionsgf.filen = filen
                collectionsgf.can_change_name = False

        t2 = time()

        if filen == '' and with_collectionsgf is None:
            collectionsgf.filen = collectionsgf.get_default_filen() + '.sgf'
            filen = collectionsgf.filen
            load_from_file = False

        t3 = time()

        # Work out what screen name is free to put it in
        i = 1
        while True:
            if not self.has_screen('Board %d' % i):
                name = 'Board %d' % i
                break
            i += 1

        s = Screen(name=name)
        self.add_widget(s)
        self.current = name

        t4 = time()


        pbv = PhoneBoardView(collectionsgf=collectionsgf)
        pbv.board.collectionsgf = collectionsgf

        if platform() == 'android':
            #set_board_height(pbv.boardcontainer)
            pbv.boardcontainer.set_board_height()

        gi = collectionsgf.gameinfo
        if 'gridsize' in gi:
            gridsize = gi['gridsize']
        pbv.board.gridsize = gridsize

        t5 = time()
        
        if load_from_file:
            print 'Trying to load from',filen
            try:
                pbv.board.load_sgf_from_file('',[filen])
            except:
                print 'Exception occurred, making popup'
                popup = Popup(content=Label(text='Unable to open SGF. Please check the file exists and is a valid SGF.',title='Error opening file'),size_hint=(0.85,0.4),title='Error')
                print 'popup made'
                popup.open()
                #self.close_board(name)
                return False
        else:
            pbv.board.reset_gridsize(gridsize)
            pbv.board.add_handicap_stones(handicap)

        t6 = time()

        ta = time()
        pbv.board.time_start()
        s.add_widget(pbv)
        pbv.screenname = name
        pbv.managedby = self
        pbv.spinner.text = mode
        pbv.board.touchoffset = self.touchoffset
        pbv.board.coordinates = self.coordinates
        pbv.board.board_path = boardname_to_filepath(self.boardtype)
        pbv.board.display_markers = self.display_markers
        pbv.board.cache = App.get_running_app().cache
        tb = time()
        pbv.board.get_game_info()
        tc = time()
        print 'Got to save...'
        pbv.board.save_sgf()
        td = time()
        self.boards.append(name)
        t65 = time()
        #App.get_running_app().collections.save()
        te = time()
        #self.refresh_collection(collection)
        tf = time()
        #self.refresh_open_games()
        tg = time()

        t7 = time()

        # if not pbv.board.gameinfo.has_key('date') and with_collectionsgf is None and from_file == '':
        #     pbv.board.set_game_date()

        t8 = time()

        print '%%%%',t8-t1,t2-t1,t3-t2,t4-t3,t5-t4,t6-t5,t65-t6,t7-t65,t8-t7
        print '%%%%',tg-ta,tb-ta,tc-tb,td-tc,te-td,tf-te,tg-tf
        # if platform() == 'android':
        #     Clock.schedule_once(pbv.boardcontainer.set_board_height,1)
        
    # def new_board(self,in_collection=None,mode='Play',from_file='',gridsize=19,handicap=0):
    #     if in_collection is None:
    #         in_collection = App.get_running_app().get_default_collection()
    #     print 'in_collection is',in_collection
    #     print 'size is', gridsize
    #     print 'self.coordinates is', self.coordinates
    #     self.back_screen_name = self.current

    #     i = 1
    #     while True:
    #         if not self.has_screen('Board %d' % i):
    #             name = 'Board %d' % i
    #             break
    #         i += 1
    #     s = Screen(name=name)
    #     self.add_widget(s)
    #     self.current = name

    #     collectionsgf = in_collection.add_game()
    #     pbv = PhoneBoardView(collectionsgf=collectionsgf)
    #     pbv.board.collectionsgf = collectionsgf
    #     if from_file != '':
    #         try:
    #             print 'loading from file'
    #             pbv.board.load_sgf_from_file('',[from_file])
    #             collectionsgf.from_file = True
    #             print 'done loading'
    #         except:
    #             popup = Popup(content=Label(text='Unable to open SGF. Please check the file exists and is a valid SGF.',title='Error opening file'),size_hint=(0.85,0.4),title='Error')
    #             popup.open()
    #             return False
    #     else:
    #         pbv.board.reset_gridsize(gridsize)
    #         pbv.board.add_handicap_stones(handicap)
    #         collectionsgf.from_file = False
    #     pbv.board.time_start()
    #     s.add_widget(pbv)
    #     pbv.screenname = name
    #     pbv.managedby = self
    #     pbv.spinner.text = mode
    #     pbv.board.touchoffset = self.touchoffset
    #     pbv.board.coordinates = self.coordinates
    #     self.boards.append(name)
    #     App.get_running_app().collections.save()
    def refresh_collections_index(self):
        if 'Collections Index' not in self.screen_names:
            self.create_collections_index()
            return False
        collections_index = self.get_screen('Collections Index').children[0]
        collections_list = App.get_running_app().collections.collections
        collections_args_converter = get_collectioninfo_from_collection
        list_adapter = ListAdapter(data=collections_list,
                                   args_converter = collections_args_converter,
                                   selection_mode = 'single',
                                   allow_empty_selection=True,
                                   cls=CollectionChooserButton,
                                   )
        collections_index.collections_list.adapter = list_adapter

    # def refresh_collection(self,dirn):
    #     sname = 'Collection ' + dirn
    #     if self.has_screen(sname):
    #         scr = self.get_screen(sname)
    #         self.remove_widget(scr)
    #         self.view_or_open_collection(dirn,goto=False)
    def create_collections_index(self):
        collections_list = App.get_running_app().collections.collections
        collections_index = CollectionsIndex(managedby=self)
        collections_args_converter = get_collectioninfo_from_collection
        list_adapter = ListAdapter(data=collections_list,
                                   args_converter = collections_args_converter,
                                   selection_mode = 'single',
                                   allow_empty_selection=True,
                                   cls=CollectionChooserButton,
                                   )
        collections_index.collections_list.adapter = list_adapter
        collections_screen = Screen(name='Collections Index')
        collections_screen.add_widget(collections_index)
        self.add_widget(collections_screen)
    def propagate_input_mode(self,val):
        if val == 'phone':
            newtouchoffset = [0,3]
        elif val == 'tablet/stylus':
            newtouchoffset = [0,0]
        else:
            newtouchoffset = [0,3]
            print 'An unrecognised input mode was chosen. Defaulting to [0,3] offset.'
        self.touchoffset = newtouchoffset
        for name in self.screen_names:
            if name[:5] == 'Board':
                curboard = self.get_screen(name)
                curboard.children[0].board.touchoffset = newtouchoffset
    def propagate_boardtype_mode(self,name):
        self.boardtype = name
        board_file = boardname_to_filepath(name)
        print 'propagating boardtype',name,board_file
        for name in self.screen_names:
            if name[:5] == 'Board':
                curboard = self.get_screen(name)
                curboard.children[0].board.board_path = board_file

    def propagate_stonegraphics_mode(self):
        for name in self.screen_names:
            if name[:5] == 'Board':
                curboard = self.get_screen(name)
                curboard.children[0].board.replace_stones()
    def propagate_markerdisplay_mode(self,val):
        if val == 'False':
            val = False
        elif val == 'True':
            val = True
        else:
            val = int(val)
        self.display_markers = bool(val)
        print 'propagating markerdisplay_mode',self.display_markers
        for name in self.screen_names:
            if name[:5] == 'Board':
                curboard = self.get_screen(name)
                curboard.children[0].board.display_markers = bool(val)
    def propagate_coordinates_mode(self,val):
        if val == 'False':
            val = False
        elif val == 'True':
            val = True
        else:
            val = int(val)
        self.coordinates = bool(val)
        for name in self.screen_names:
            if name[:5] == 'Board':
                curboard = self.get_screen(name)
                curboard.children[0].board.coordinates = bool(val)
            
    def propagate_view_mode(self,val):
        if val == 'phone':
            Window.rotation = 0
        elif val == 'tablet':
            Window.rotation = 270
        else:
            Window.rotation = 0

    def query_delete_sgf(self,sel):
        if len(sel)>0:
            popup = Popup(content=DeleteSgfQuestion(manager=self,selection=sel),height=(140,'sp'),size_hint=(0.85,None),title='Are you sure?')
            popup.content.popup = popup
            popup.open()
    def delete_sgf_from_selection(self,selection):
        print 'Asked to delete from selection',selection
        if len(selection)>0:
            button = selection[0]
            print 'collectionsgf is',button,button.collection,button.collectionsgf,button.filepath
            self.delete_sgf(selection[0].collectionsgf)
    def delete_sgf(self,collectionsgf):
        collectionsgf.delete()
        App.get_running_app().collections.save()
        self.refresh_collection(collectionsgf.collection)
        self.refresh_collections_index()
        self.refresh_open_games()
    def save_sgfs(self):
        for name in self.screen_names:
            if name[:6] == 'Board ':
                s = self.get_screen(name)
                s.children[0].board.save_sgf()

class DataItem(object):
    def __init__(self, text='', is_selected=False):
        self.text = text
        self.is_selected = is_selected

def printargs(*args,**kwargs):
    '###### printargs'
    print args
    print kwargs
    '######'

class GobanApp(App):
    manager = ObjectProperty(None,allownone=True)
    cache = ObjectProperty(WidgetCache())
    collections = ObjectProperty(CollectionsList())

    stone_type = StringProperty('default')
    board_type = StringProperty('./media/boards/none.png')

    use_kivy_settings = False

    title = 'noGo'
    name = 'noGo'

    prev_opened_file = StringProperty('')

    def build(self):
        # Load config
        print 'user data dir is', self.user_data_dir
        config = self.config
        print 'my config is',config

        # Get any json collection backups if on android
        if platform() == 'android':
            if not exists('/sdcard/noGo'):
                mkdir('/sdcard/noGo')
            if not exists('/sdcard/noGo/collections'):
                mkdir('/sdcard/noGo/collections')
            if not exists('/sdcard/noGo/collections/unsaved'):
                mkdir('/sdcard/noGo/collections/unsaved')
            json_backups = glob('/sdcard/noGo/*.json')
            for filen in json_backups:
                with open(filen,'r') as fileh:
                    filestr = fileh.read()
                if len(filestr) > 1:
                    name = filen.split('/')[-1]
                    copyfile(filen,'./'+name)
           

        # Load collections
        self.collections = CollectionsList().from_file()

        
        # Construct GUI
        sm = NogoManager(transition=SlideTransition(direction='left'))
        self.manager = sm
        sm.app = self

        hv = Screen(name="Home")
        hs = HomeScreen(managedby=sm)
        hv.add_widget(hs)
        sm.add_widget(hv)
        sm.create_collections_index()
        sm.current = 'Home'

        # Get initial settings from config panel
        config = self.config
        sm.propagate_input_mode(config.getdefault('Board','input_mode','phone'))
        sm.propagate_coordinates_mode(config.getdefault('Board','coordinates','1'))
        self.stone_type = config.getdefault('Board','stone_graphics','simple')
        self.boardtype = config.getdefault('Board','board_graphics','simple')
        sm.propagate_boardtype_mode(self.boardtype)

        self.bind(on_start=self.post_build_init)

        if platform() == 'android':
            from android import activity
            activity.bind(on_new_intent=self.on_intent)
            

        return sm

    def on_intent(self,intent):
        print 'INTENT'
        print 'INTENT'
        print 'INTENT'
        print 'INTENT'
        print 'INTENT'
        print '!!!!!'
        print 'on_intent called'
        action = intent.getAction()
        print 'action is',action
        if action == 'android.intent.action.VIEW':
            print 'Trying to act on intent'
            #sleep(5)
            print 'Slept briefly'
            path = intent.getData().getPath()
            print 'going for path',path
            #self.manager.go_home()
            Clock.schedule_once(lambda j: self.manager.open_from_intentpath(path),1.1)
            #self.manager.open_from_intentpath(path)
    # def on_resume(self,*args):
    #     print 'RESUMED'
    #     print 'RESUMED'
    #     print 'RESUMED'
    #     print 'RESUMED'
    #     print 'RESUMED'
        

    def on_start(self,*args,**kwargs):
        print '\nON_START',args,kwargs,'\n'
        print 'environment',environ.get('PYTHON_OPENFILE')
        open_file = getenv('PYTHON_OPENFILE','').replace('%20',' ')
        print 'open_file is',open_file
        if open_file != '':
            putenv('PYTHON_OPENFILE','')
            Clock.schedule_once(lambda j: self.manager.open_from_intentpath(open_file),1.1)
        super(GobanApp,self).on_start(*args,**kwargs)

    # def on_resume(self,*args,**kwargs):
    #     # print 'ON_RESUME',args,kwargs
    #     # print 'environment',environ.get('PYTHON_OPENFILE')
    #     # open_file = getenv('PYTHON_OPENFILE','').replace('%20',' ')
    #     # print 'open_file is',open_file
    #     # if open_file != '' and open_file != self.prev_opened_file:
    #     #     self.prev_opened_file = open_file
    #     #     self.manager.new_board(from_file=open_file,mode='Navigate')
    #     super(GobanApp,self).on_resume(*args,**kwargs)

    def get_application_config(self):
        if platform() == 'android':
            dirn = self.user_data_dir + '/nogo.ini'
            return dirn
        return super(GobanApp,self).get_application_config()

    def post_build_init(self,ev):
        if platform() == 'android':
            import android
            android.map_key(android.KEYCODE_BACK,1001)

        win = Window
        win.bind(on_keyboard=self.my_key_handler)

        Clock.schedule_interval(self.save_all_boards,60)

    def my_key_handler(self,window,keycode1,keycode2,text,modifiers):
        if keycode1 == 27 or keycode1 == 1001:
            self.manager.handle_android_back()
            return True
        return False

    def build_settings(self,settings):
        jsondata = json.dumps([
            {"type": "options",
             "title": "Input method",
             "desc": "Stone input method",
             "section": "Board",
             "key": "input_mode",
             "options": ["phone","tablet/stylus"]},
            {"type": "options",
             "title": "View mode",
             "desc": "Use compact phone view or expanded tablet view.",
             "section": "Board",
             "key": "view_mode",
             "options": ["phone","tablet"]},
            {"type": "bool",
             "title": "Show coordinates",
             "desc": "Whether or not to display coordinates on the board.",
             "section": "Board",
             "key": "coordinates",
             "true": "auto"},
            {"type": "bool",
             "title": "Show markers",
             "desc": "Whether to display board markers (square, triangle, letters, numbers etc.) when navigating games.",
             "section": "Board",
             "key": "markers",
             "true": "auto"},
            {"type": "options",
             "title": "Board graphics",
             "desc": "What kind of board graphics to use",
             "section": "Board",
             "key": "board_graphics",
             "options": ["plain light","plain dark","full board photo","board section photo 1","lightened board photo 1","board section photo 2"]},
            {"type": "options",
             "title": "Stone graphics",
             "desc": "What kind of stone graphics to use",
             "section": "Board",
             "key": "stone_graphics",
             "options": ["simple","slate and shell","bordered slate and shell","drawn by noGo"]},
            ])
        settings.add_json_panel('Board',
                                self.config,
                                data=jsondata)

    def build_config(self, config):
        config.setdefaults('Board',{'input_mode':'phone','view_mode':'phone','coordinates':False,'markers':True,'stone_graphics':'slate and shell','board_graphics':'board section photo 1'})

    def on_pause(self,*args,**kwargs):
        print 'App asked to pause'
        self.save_all_boards()
        return True

    def on_stop(self,*args,**kwargs):
        print 'App asked to stop'
        self.save_all_boards()
        return super(GobanApp,self).on_stop()

    def save_all_boards(self,*args):
        names = self.manager.screen_names
        for name in names:
            if name[:5] == 'Board':
                board = self.manager.get_screen(name)
                try:
                    board.children[0].board.save_sgf()
                except IndexError:
                    print 'Tried to save board that doesn\'t exist, maybe didn\'t load properly'

    def on_config_change(self, config, section, key, value):
        super(GobanApp,self).on_config_change(config,section,key,value)
        print '%%% config change',config,section,key,value
        if key == 'input_mode':
            self.manager.propagate_input_mode(value)
        elif key == 'view_mode':
            self.manager.propagate_view_mode(value)
        elif key == 'coordinates':
            print 'coordinates key pressed',config,section,key,value
            self.manager.propagate_coordinates_mode(int(value))
        elif key == 'markers':
            self.manager.propagate_markerdisplay_mode(int(value))
        elif key == 'stone_graphics':
            self.stone_type = value
            self.manager.propagate_stonegraphics_mode()
        elif key == 'board_graphics':
            self.board_type = value
            self.manager.propagate_boardtype_mode(value)
        else:
            super(GobanApp,self).on_config_change(config,section,key,value)

    def new_collection_query(self):
        popup = Popup(content=CollectionNameChooser(manager=self),title='Pick a collection name...',size_hint_x=0.95,size_hint_y=None,height=(130,'sp'),pos_hint={'top':0.85})
        popup.content.popup = popup
        popup.open()
    def new_collection(self,newname):
        self.collections.new_collection(newname)
        self.collections.save()
        self.manager.refresh_collections_index()
    def query_delete_collection(self,sel):
        if len(sel)>0:
            popup = Popup(content=DeleteCollectionQuestion(manager=self,selection=sel),height=(140,'sp'),size_hint=(0.85,None),title='Are you sure?')
            popup.content.popup = popup
            popup.open()
    def delete_collection(self,selection):
        print 'asked to delete collection using',selection,type(selection)
        self.collections.delete_collection(selection[0].colname)
        self.manager.refresh_collections_index()
    def get_default_collection(self):
        collections = self.collections.collections
        print 'current collections are',collections
        unsaved = filter(lambda j: j.name == 'unsaved',collections)
        print 'found name unsaved',unsaved
        if len(unsaved) > 0:
            unsaved = unsaved[0]
        else:
            unsaved = self.collections.new_collection('unsaved')
            self.manager.refresh_collections_index()
        if platform() == 'android':
            unsaved.defaultdir = '/sdcard/noGo/collections/unsaved/'
        return unsaved
    def move_collectionsgf(self,collectionsgf,selection,board=None):
        if len(selection) > 0:
            collection = selection[0].collection
        else:
            return False
        oldcollection = collectionsgf.collection
        collectionsgf.delete()
        collectionsgf.collection = collection
        collectionsgf.filen = collectionsgf.get_default_filen() + '.sgf'
        collection.games.append(collectionsgf)
        collection.save()
        self.manager.add_collection_refresh_reminder(collection)
        self.manager.add_collection_refresh_reminder(oldcollection)
        self.manager.collectionindex_to_refresh = True
        if board is not None:
            board.get_game_info()
            board.save_sgf()
            collectionsgf.save()
        
        
def testconverter(j,*args):
    print 'converter got j',j,args
    info = j.gameinfo
    print 'info is',info
    return info

if __name__ == '__main__':
    app = GobanApp()
    app.run()
