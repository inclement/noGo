from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.listview import ListItemButton
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty, ListProperty, AliasProperty, StringProperty, DictProperty, BooleanProperty, StringProperty, OptionProperty, BoundedNumericProperty
from kivy.app import App
from kivy.event import EventDispatcher

from glob import glob
from os import mkdir
import json
import time


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
 
class CollectionChooserButton(ListItemButton):
    colname = StringProperty('')
    numentries = NumericProperty(0)

class OpenChooserButton(ListItemButton):
    wname = StringProperty('')
    bname = StringProperty('')
    date = StringProperty('')
    filepath = StringProperty('')
    boardname = StringProperty('')

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


class CollectionsList(EventDispatcher):
    collections = ListProperty([])
    def __str__(self):
        return 'CollectionsList with {0} collections'.format(len(self.collections))
    def __repr__(self):
        return self.__str__()
    def save(self,filen='default'):
        if filen == 'default':
            default_filen = App.get_running_app().user_data_dir + '/collections_list.json'
            filen = default_filen
        colstr = self.serialise()
        with open(filen,'w') as fileh:
            fileh.write(colstr)
    def serialise(self):
        coll_lists = map(lambda j: j.as_list(),self.collections)
        return json.dumps(coll_lists)
    def from_file(self,filen='default'):
        default_filen = App.get_running_app().user_data_dir + '/collections_list.json'
        if filen == 'default':
            filen = default_filen
        with open(filen,'r') as fileh:
            colstr = fileh.read()
        colpy = json.loads(colstr)
        for entry in colpy:
            col = Collection()
            col.name = entry[0]
            col.defaultdir = entry[1]
            for game in entry[2]:
                col.games.append(CollectionSgf().from_dict(game,col))
            self.collections.append(col)
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
    def delete_collection(self,name):
        matching_collections = filter(lambda j: j.name == name,self.collections)
        for col in matching_collections:
            self.collections.remove(col)

def get_collectioninfo_from_collection(row_index,col):
    return {'colname': col.name, 'numentries': len(col.games)}

class Collection(EventDispatcher):
    games = ListProperty([])
    name = StringProperty('Collection')
    defaultdir = StringProperty('./games/unsaved/')
    def __str__(self):
        return 'SGF collection {0} with {1} games'.format(self.name,len(self.games))
    def __repr__(self):
        return self.__str__()
    def get_default_dir(self):
        return App.get_running_app().user_data_dir + '/' + self.name
    def from_list(self,l):
        name,defaultdir,games = l
        self.name = name
        self.defaultdir = defaultdir
        self.games = map(lambda j: CollectionSgf().from_dict(j,self),games)
        return self
    def as_list(self):
        return [self.name, self.defaultdir, map(lambda j: j.to_dict(),self.games)]
    def add_game(self):
        pass



class CollectionSgf(object):
    def __init__(self,collection=None):
        self.gameinfo = {}
        self.collection = None
        self.filen = ''
    def get_default_filen(self):
        if self.collection is not None:
            return self.collection.defaultdir + time.asctime().replace(' ','_')
    def from_dict(self,info,collection=None):
        self.gameinfo = info
        self.collection = collection
        return self
    def to_dict(self):
        return self.gameinfo
    # def set_gameinfo(self,info):
    #     if 'bname' in info:
        
    
