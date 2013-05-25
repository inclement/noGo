#!/usr/bin/env python2

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
from os import mkdir, rename
from json import dump as jsondump, load as jsonload, dump as jsondump
import json
from time import asctime, time

from gomill import sgf, boards
from abstractboard import *
from boardview import GuiBoard, BoardContainer, PhoneBoardView, GuessPopup, SaveQuery, MySpinnerOption
from boardwidgets import Stone, TextMarker, TriangleMarker, SquareMarker, CircleMarker, CrossMarker, VarStone
from miscwidgets import VDividerLine, DividerLine, WhiteStoneImage, BlackStoneImage
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

def get_game_chooser_info_from_boardname(sm,boardname):
    board = sm.get_screen(boardname).children[0].board
    gameinfo = board.gameinfo
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


    def switch_and_set_back(self,newcurrent):
        print 'Asked to switch and set back',self.transition.is_active
        if not self.transition.is_active:
            self.back_screen_name = self.current
            self.current = newcurrent
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
            fileh = open('gpl.txt','r')
            gpl = fileh.read()
            fileh.close()
            fileh = open('README.rst','r')
            readme = fileh.read()
            fileh.close()
            infoscreen = Screen(name='Info Page')
            infoscreen.add_widget(InfoPage(infotext=readme,licensetext=gpl))
            self.add_widget(infoscreen)
            self.switch_and_set_back('Info Page')
    def view_or_open_collection(self,dirn,goto=True):
        if len(dirn) > 0:
            dirn = dirn[0].coldir
            if self.has_screen('Collection ' + dirn):
                self.current = 'Collection ' + dirn
            else:
                files = map(abspath,glob(dirn + '/*.sgf'))
                screenname = 'Collection ' + dirn
                args_converter = argsconverter_get_gameinfo_from_file
                list_adapter = ListAdapter(data=files,
                                           args_converter = args_converter,
                                           selection_mode='single',
                                           allow_empty_selection=True,
                                           cls=GameChooserButton
                                           )
                gc = StandaloneGameChooser(managedby=self,name=dirn.split('/')[-1],dirn=dirn)
                gc.gameslist.adapter = list_adapter
                s = Screen(name=screenname)
                s.add_widget(gc)
                self.add_widget(s)
                if goto:
                    self.switch_and_set_back(s.name)
    def open_sgf_dialog(self):
        popup = Popup(content=OpenSgfDialog(manager=self),title='Open SGF',size_hint=(0.85,0.85))
        popup.content.popup = popup
        popup.open()
    def board_from_gamechooser(self,filens):
        if len(filens) > 0:
            filen = filens[0].filepath
            self.new_board(filen,'Navigate')
    def close_board_from_selection(self,sel):
        print 'asked to close from sel',sel
        if len(sel) > 0:
            self.close_board(sel[0].boardname)
    def close_board(self,name):
        if self.has_screen(name):
            pbvs = self.get_screen(name)
            if pbvs.children[0].board.has_unsaved_data:
                print 'Should ask to save, but am not going to...'
            else:
                print 'removing board'
                print 'current boards',self.screens
                self.remove_widget(pbvs)
                self.boards.remove(name)
                print 'new boards',self.screens
    def new_board_dialog(self):
        dialog = NewBoardQuery(manager=self)
        popup = Popup(content=dialog,title='Create new board...',size_hint=(0.85,0.85))
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
        dialog.collections_list.adapter = list_adapter
        popup.open()
    def new_board_from_selection(self,sel,gridsize=19,handicap=0):
        if len(sel)>0:
            dirn = sel[0].coldir
        else:
            dirn = './games/unsaved'
        self.new_board(in_folder=dirn,gridsize=gridsize,handicap=handicap)
    def new_board(self,from_file='',mode='Play',in_folder='',gridsize=19,handicap=0):
        print 'from_file is',from_file
        print 'size is', gridsize
        print 'self.coordinates is', self.coordinates
        self.back_screen_name = self.current

        i = 1
        while True:
            if not self.has_screen('Board %d' % i):
                name = 'Board %d' % i
                break
            i += 1
        s = Screen(name=name)
        self.add_widget(s)
        self.current = name

        pbv = PhoneBoardView()
        if from_file != '':
            try:
                print 'loading from file'
                pbv.board.load_sgf_from_file('',[from_file])
                print 'done loading'
            except:
                popup = Popup(content=Label(text='Unable to open SGF. Please check the file exists and is a valid SGF.',title='Error opening file'),size_hint=(0.85,0.4),title='Error')
                popup.open()
                return False
        else:
            pbv.board.reset_gridsize(gridsize)
            pbv.board.add_handicap_stones(handicap)
        pbv.board.time_start()
        s.add_widget(pbv)
        pbv.screenname = name
        pbv.managedby = self
        pbv.spinner.text = mode
        pbv.board.touchoffset = self.touchoffset
        pbv.board.coordinates = self.coordinates
        self.boards.append(name)
        if in_folder != '':
            try:
                pbv.board.make_savefile_in_dir(in_folder)
                self.refresh_collections_index()
            except OSError:
                print 'Savefile in given folder could not be created.'
                print 'Should make error popup...'
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

    def refresh_collection(self,dirn):
        sname = 'Collection ' + dirn
        if self.has_screen(sname):
            scr = self.get_screen(sname)
            self.remove_widget(scr)
            self.view_or_open_collection(dirn,goto=False)
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
            Window.rotation = 90
        else:
            Window.rotation = 0

    def query_delete_sgf(self,sel):
        if len(sel)>0:
            popup = Popup(content=DeleteSgfQuestion(manager=self,selection=sel),height=(140,'sp'),size_hint=(0.85,None),title='Are you sure?')
            popup.content.popup = popup
            popup.open()
    def delete_sgf_from_selection(self,selection):
        if len(selection)>0:
            self.delete_sgf(selection[0].filepath)
    def delete_sgf(self,filen):
        name = filen.split('/')[-1]
        try:
            os.rename(filen,'./games/deleted'+name)
        except:
            print 'Couldn\'t delete sgf...should raise exception?'

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

    use_kivy_settings = False

    title = 'noGo'
    name = 'noGo'

    def build(self):
        # Load config
        print 'user data dir is', self.user_data_dir
        config = self.config
        print 'my config is',config

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

        self.bind(on_start=self.post_build_init)

        return sm


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
            {"type": "bool",
             "title": "Show coordinates",
             "desc": "Whether or not to display coordinates on the board.",
             "section": "Board",
             "key": "coordinates",
             "true": "auto"},
            {"type": "options",
             "title": "View mode",
             "desc": "Use compact phone view or expanded tablet view.",
             "section": "Board",
             "key": "view_mode",
             "options": ["phone","tablet"]},
            ])
        settings.add_json_panel('Board',
                                self.config,
                                data=jsondata)

    def build_config(self, config):
        config.setdefaults('Board',{'input_mode':'phone','coordinates':False,'view_mode':'phone'})

    def on_pause(self,*args,**kwargs):
        print 'App asked to pause'
        names = self.manager.screen_names
        for name in names:
            if name[:5] == 'Board':
                board = self.manager.get_screen(name)
                board.children[0].board.save_sgf(autosave=True)
        return True

    def on_stop(self,*args,**kwargs):
        print 'App asked to stop'
        names = self.manager.screen_names
        for name in names:
            if name[:5] == 'Board':
                board = self.manager.get_screen(name)
                board.children[0].board.save_sgf(autosave=True)
        return super(GobanApp,self).on_stop()

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
        else:
            super(GobanApp,self).on_config_change(config,section,key,value)

    def new_collection_query(self):
        popup = Popup(content=CollectionNameChooser(manager=self),title='Pick a collection name...',size_hint_x=0.85,size_hint_y=None,height=(130,'sp'))
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

            
if __name__ == '__main__':

    app = GobanApp()
    app.run()
