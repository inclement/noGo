# Copyright 2013 Alexander Taylor

# This file is part of noGo.

# noGo is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

# noGo is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with noGo. If not, see http://www.gnu.org/licenses/gpl-3.0.txt

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.listview import ListItemButton
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty, ListProperty, AliasProperty, StringProperty, DictProperty, BooleanProperty, StringProperty, OptionProperty, BoundedNumericProperty
from kivy.app import App
from kivy.event import EventDispatcher

from helpers import embolden

from glob import glob
from os import mkdir
import os
import json
import time
import shutil

SERIALISATION_VERSION = 2


def get_collectioninfo_from_dir(row_index,dirn):
    sgfs = glob(dirn + '/*.sgf')
    colname = dirn.split('/')[-1]
    return {'colname': colname, 'coldir': dirn, 'numentries': len(sgfs)}

class CollectionsIndex(BoxLayout):
    collections_list = ObjectProperty(None,allownone=True)
    managedby = ObjectProperty(None,allownone=True)

class DeleteSgfQuestion(BoxLayout):
    manager = ObjectProperty(None,allownone=True)
    selection = ObjectProperty(None,allownone=True)

class DeleteCollectionQuestion(BoxLayout):
    manager = ObjectProperty(None,allownone=True)
    selection = ObjectProperty(None,allownone=True)

class CollectionNameChooser(BoxLayout):
    popup = ObjectProperty(None,allownone=True)
    manager = ObjectProperty(None)

class StandaloneGameChooser(BoxLayout):
    managedby = ObjectProperty(None,allownone=True)
    gameslist = ObjectProperty()
    collection = ObjectProperty(None,allownone=True)
    # def populate_from_directory(self,dir):
    #     sgfs = glob(''.join((dir,'/*.sgf')))
    #     print 'sgfs found in directory: ',sgfs
    #     for sgfpath in sgfs:
    #         sgfpath = abspath(sgfpath)
    #         info = get_gameinfo_from_file(sgfpath)
    #         info['filepath'] = sgfpath
    #         print info
    #         pathwidget = GameChooserButton(owner=self)
    #         pathwidget.construct_from_sgfinfo(info)
    #         self.gameslist.add_widget(pathwidget)
 
class CollectionChooserButton(ListItemButton):
    colname = StringProperty('')
    numentries = NumericProperty(0)
    collection = ObjectProperty(None,allownone=True)

class OpenChooserButton(ListItemButton):
    wname = StringProperty('')
    bname = StringProperty('')
    date = StringProperty('')
    filepath = StringProperty('')
    boardname = StringProperty('')
    collection = ObjectProperty(None,allownone=True)
    collectionsgf = ObjectProperty(None,allownone=True)

class GameChooserButton(ListItemButton):
    info = ObjectProperty()
    owner = ObjectProperty(None,allownone=True)
    filepath = StringProperty('')
    bname = StringProperty('')
    wname = StringProperty('')
    brank = StringProperty('')
    wrank = StringProperty('')
    result = StringProperty('')
    date = StringProperty('')
    collection = ObjectProperty(None,allownone=True)
    collectionsgf = ObjectProperty(None,allownone=True)
    def construct_from_sgfinfo(self,info):
        self.info.construct_from_sgfinfo(info)

class GameChooserInfo(BoxLayout):
    owner = ObjectProperty('')
    filepath = StringProperty('')
    bname = StringProperty('')
    wname = StringProperty('')
    brank = StringProperty('')
    wrank = StringProperty('')
    result = StringProperty('')
    date = StringProperty('')
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
                self.wname = embolden(self.wname)
            elif result[0] in ['b','B']:
                self.bname = embolden(self.bname)
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


class CollectionsList(EventDispatcher):
    collections = ListProperty([])
    def __str__(self):
        return 'CollectionsList with {0} collections'.format(len(self.collections))
    def __repr__(self):
        return self.__str__()
    def save(self,filen='default'):
        if filen == 'default':
            default_filen = '.' + '/collections_list.json'
            filen = default_filen
        colstr = self.serialise()
        with open(filen,'w') as fileh:
            fileh.write(colstr)
    def save_collection(self,colname):
        cols = filter(lambda j: j.name == colname,self.collections)
        if len(cols) > 0:
            cols[0].save()
    def serialise(self):
        coll_lists = [SERIALISATION_VERSION,map(lambda j: j.get_filen(),self.collections)]
        return json.dumps(coll_lists)
    def from_file(self,filen='default'):
        #default_filen = App.get_running_app().user_data_dir + '/collections_list.json'
        default_filen = './collections_list.json'
        if filen == 'default':
            filen = default_filen
        with open(filen,'r') as fileh:
            colstr = fileh.read()
        version,colpy = json.loads(colstr)
        colpy = jsonconvert(colpy)
        if version == 1:
            for entry in colpy:
                col = Collection()
                col.name = entry[0]
                col.defaultdir = entry[1]
                for game in entry[2]:
                    col.games.append(CollectionSgf().from_dict(game,col))
                self.collections.append(col)
        elif version == 2:
            for entry in colpy:
                col = Collection().from_file(entry)
                self.collections.append(col)
        else:
            print 'Collection list version not recognised.'
        return self
    def new_collection(self,newname):
        dirn = './games/{0}'.format(newname)
        print 'Making dir for new collection:',dirn
        try:
            mkdir(dirn)
        except OSError:
            print 'File exists! Add an error popup.'
        col = Collection(name=newname,defaultdir=dirn)
        self.collections.append(col)
        self.save()
        return col
    def delete_collection(self,name):
        matching_collections = filter(lambda j: j.name == name,self.collections)
        for col in matching_collections:
            self.collections.remove(col)

def get_collectioninfo_from_collection(row_index,col):
    return {'colname': col.name, 'numentries': len(col.games), 'collection': col}

class Collection(EventDispatcher):
    games = ListProperty([])
    name = StringProperty('Collection')
    defaultdir = StringProperty('./games/unsaved/')
    def __str__(self):
        return 'SGF collection {0} with {1} games'.format(self.name,len(self.games))
    def __repr__(self):
        return self.__str__()
    def remove_sgf(self,sgf):
        if sgf in self.games:
            self.games.remove(sgf)
    def get_default_dir(self):
        return '.' + '/' + self.name
    def from_list(self,l):
        name,defaultdir,games = l
        self.name = name
        self.defaultdir = defaultdir
        self.games = map(lambda j: CollectionSgf(collection=self).load(j),games)
        return self
    def as_list(self):
        return [self.name, self.defaultdir, map(lambda j: j.get_filen(),self.games)]
    def serialise(self):
        return json.dumps([SERIALISATION_VERSION,self.as_list()])
    def save(self):
        filen = '.' + '/' + self.name + '.json'
        with open(filen,'w') as fileh:
            fileh.write(self.serialise())
        return filen
    def get_filen(self):
        filen = '.' + '/' + self.name + '.json'
        return filen
    def from_file(self,filen):
        with open(filen,'r') as fileh:
            jsonstr = fileh.read()
        version,selflist = json.loads(jsonstr)
        selflist = jsonconvert(selflist)
        return self.from_list(selflist)
    def add_game(self,can_change_name=True):
        game = CollectionSgf(collection=self,can_change_name=can_change_name)
        game.filen = game.get_default_filen() + '.sgf'
        self.games.append(game)
        self.save()
        return game



class CollectionSgf(object):
    def __init__(self,collection=None, can_change_name=True, filen=''):
        self.gameinfo = {}
        self.collection = collection
        self.can_change_name = can_change_name # Indicates whether the filename should be changed when game info does
        self.filen = filen
    def delete(self):
        self.collection.remove_sgf(self)
    def get_default_filen(self):
        #print 'asked for default filen',self.collection
        if self.collection is not None:
            return self.collection.defaultdir + '/' + time.asctime().replace(' ','_')
    def from_dict(self,info,collection=None):
        filen,can_change_name,gameinfo = info
        self.filen = filen
        self.can_change_name = can_change_name
        self.gameinfo = gameinfo
        if collection is not None:
            self.collection = collection
        return self
    def to_dict(self):
        gi = self.gameinfo
        try:
            gi.pop('collection')
        except KeyError:
            pass
        try:
            gi.pop('collectionsgf')
        except KeyError:
            pass
        return [self.filen,self.can_change_name,gi]
    def serialise(self):
        return json.dumps([SERIALISATION_VERSION,self.to_dict()])
    def save(self):
        dict = self.to_dict()
        filen = self.filen + '.json'
        with open(filen,'w') as fileh:
            fileh.write(self.serialise())
        return filen
    def get_filen(self):
        filen = self.filen + '.json'
        return filen
    def load(self,filen):
        with open(filen,'r') as fileh:
            jsonstr = fileh.read()
        version, selfdict = json.loads(jsonstr)
        selfdict = jsonconvert(selfdict)
        self.from_dict(selfdict)
        return self
    def set_gameinfo(self,info,resave=True):
        self.gameinfo = info
        if self.can_change_name:
            oldn = self.filen
            gamestr = ''
            if 'bname' in info:
                gamestr += '_' + info['bname']
            if 'wname' in info:
                gamestr += '_' + info['wname']
            if 'event' in info:
                gamestr += '_' + info['event']
            if gamestr not in self.filen:
                newn = self.get_default_filen() + gamestr + '.sgf'
                self.filen = newn
                self.collection.save()
                #App.get_running_app().collections.save()
                try:
                    shutil.copyfile(oldn,newn)
                    os.remove(oldn)
                except IOError:
                    print 'Tried to copy file that doesn\'t exist',oldn,newn
        #App.get_running_app().collections.save()
    def set_filen(self,filen=''):
        if filen == '':
            info = self.gameinfo
            if not self.from_file:
                oldn = self.filen
                gamestr = ''
                if 'bname' in info:
                    gamestr += '_' + info['bname']
                if 'wname' in info:
                    gamestr += '_' + info['wname']
                if 'event' in info:
                    gamestr += '_' + info['event']
                if gamestr not in self.filen:
                    newn = self.get_default_filen() + gamestr + '.sgf'
                    self.filen = newn
                    self.collection.save()
        else:
            self.filen = filen
        return self.filen
    def info_for_button(self):
        info = self.gameinfo
        info['collection'] = self.collection
        info['filepath'] = self.filen
        info['collectionsgf'] = self

        try:
            result = info['result']
            winner = result[0]
            if winner in ['B','b']:
                info['bname'] = embolden(info['bname'])
            elif winner in ['W','w']:
                info['wname'] = embolden(info['wname'])
        except (KeyError, IndexError):
            pass # If one of these keys doesn't exist, just don't modify anything
        return info
        
def jsonconvert(input):
    if isinstance(input, dict):
        return {jsonconvert(key): jsonconvert(value) for key, value in input.iteritems()}
    elif isinstance(input, list):
        return [jsonconvert(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode('utf-8')
    else:
        return input
