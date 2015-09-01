import os
import glob

from abstractboard import get_gameinfo_from_file, apply_gameinfo_to_sgfmodel
from sgfmodels import Collection, Sgf, CollectionSgf, db

default_cols = ['Pro10','IMeijin','Kisei','ITengen','Gosei','Honinbo','Shusaku','Meijin','CJSuperGo','Tengen','Judan','Oza','NihonKiin','Ing']

#collectionslist = CollectionsList()

if not Sgf.table_exists():
    Sgf.create_table()
if not Collection.table_exists():
    Collection.create_table()
if not CollectionSgf.table_exists():
    CollectionSgf.create_table()

for entry in default_cols:
    sgfs = glob.glob('./games/' + entry + '/*.sgf')
    sgfmodels = []
    collections = []
    colsgfmodels = []
    for sgf in sgfs:
        with open(sgf) as fileh:
            sgfstr = fileh.read()
        model = Sgf()
        model.filename = sgf
        model.sgf = sgfstr

        colmod = list(Collection.select().where(Collection.name == entry))
        if len(colmod) == 0:
            colmod = [Collection(name=entry)]
            colmod[0].save()
            print 'made new collection', colmod[0].name
        col = colmod[0]
        collections.append(col)

        info = get_gameinfo_from_file(sgf)
        apply_gameinfo_to_sgfmodel(model, info)

        sgfmodels.append(model)
    # with db.transaction():
    #     for model in sgfmodels:
    #         try:
    #             model.save()
    #         except UnicodeDecodeError:
    #             pass
    with db.transaction():
        for i in range(len(sgfmodels)):
            sgf = sgfmodels[i]
            collection = collections[i]
            print 'sgf is', sgf
            print 'collection is', collection
            try:
                sgf.save()
                colsgf = CollectionSgf(collection=collection,
                                        sgf=sgf)
                colsgf.save()
            except UnicodeDecodeError:
                pass
        
    
# print 'saving'
# with db.transaction():
#     for model in models:
#         try:
#             model.save()
#         except UnicodeDecodeError:
#             pass
#     for model in colsgfs:
#         model.save()
