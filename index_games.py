import os
import glob

from sgfcollections import Collection, CollectionSgf, CollectionsList
from abstractboard import get_gameinfo_from_file

default_cols = ['Pro10','IMeijin','Kisei','ITengen','Gosei','Honinbo','Shusaku','Meijin','CJSuperGo','Tengen','Judan','Oza','NihonKiin','Ing']

collectionslist = CollectionsList()

for entry in default_cols:
    collection = Collection(name=entry,defaultdir='./games/' + entry)
    sgfs = glob.glob('./games/' + entry + '/*.sgf')
    for sgf in sgfs:
        info = get_gameinfo_from_file(sgf)
        game = collection.add_game(False)
        game.filen = sgf
        game.gameinfo = info
    collectionslist.collections.append(collection)
    collectionslist.save('indexed_collections.json')
