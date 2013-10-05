import os
import glob

from abstractboard import get_gameinfo_from_file, apply_gameinfo_to_sgfmodel
from sgfmodels import Sgf, db

default_cols = ['Pro10','IMeijin','Kisei','ITengen','Gosei','Honinbo','Shusaku','Meijin','CJSuperGo','Tengen','Judan','Oza','NihonKiin','Ing']

#collectionslist = CollectionsList()

if not Sgf.table_exists():
    Sgf.create_table()

models = []
for entry in default_cols:
    #collection = Collection(name=entry,defaultdir='./games/' + entry)
    # for sgf in sgfs:
    #     info = get_gameinfo_from_file(sgf)
    #     game = collection.add_game(False)
    #     game.filen = sgf
    #     game.gameinfo = info
    #     game.save()

    sgfs = glob.glob('./games/' + entry + '/*.sgf')
    for sgf in sgfs:
        with open(sgf) as fileh:
            sgfstr = fileh.read()
        model = Sgf()
        model.filename = sgf
        model.set_collections([entry])
        model.sgf = sgfstr

        info = get_gameinfo_from_file(sgf)
        apply_gameinfo_to_sgfmodel(model, info)

        models.append(model)

    
print 'saving'
print 'models are', models
with db.transaction():
    for model in models:
        print 'trying to save', model, model.collections, model.filename
        try:
            model.save()
        except UnicodeDecodeError:
            pass
        
