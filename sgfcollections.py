from kivy.uix.boxlayout import BoxLayout
from kivy.uix.listview import ListItemButton
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty, ListProperty, AliasProperty, StringProperty, DictProperty, BooleanProperty, StringProperty, OptionProperty

from glob import glob


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
    name = StringProperty('')
    dirn = StringProperty('')
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
    coldir = StringProperty('')
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


class CollectionsList(object):
    collections = ListProperty([])
