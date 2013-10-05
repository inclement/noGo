'''Peewee ORM models for storing sgf metadata.'''

from peewee import *
import datetime
import json

from helpers import embolden

db = SqliteDatabase('./games/sgfs.db')
db.connect()

class BaseModel(Model):
    class Meta(object):
        database = db

class Collection(BaseModel):
    name = CharField()
    date_created = DateTimeField(default=datetime.datetime.now)

    other = TextField(null=True)
    '''Anything else I think of...'''

    def __str__(self, *args):
        return '<{} collection>'.format(self.name)
    def __repr__(self, *args):
        return str(self)
        
class Sgf(BaseModel):
    '''Peewee model for storing sgf metadata in a database.'''

    filename = CharField(null=True)

    sgf = TextField(null=True)
    '''The entire sgf.'''

    other = TextField(null=True)
    '''Anything else I think of...'''

    keywords = CharField(null=True)
    def get_keywords(self):
        return json.loads(self.keywords)
    def set_keywords(self, keywords):
        self.keywords = json.dumps(keywords)

    user_rating = IntegerField(null=True)

    user_created = BooleanField(null=True)

    date_created = DateTimeField(default=datetime.datetime.now)
    
    
    # Direct sgf properties
    ap = CharField(null=True)
    charset = CharField(null=True)
    fileformat = CharField(null=True)
    gametype = CharField(null=True)
    # Should always be 1 (== Go) for us...
    varshow = CharField(null=True)
    # We ignore this, and I'm not sure anyone uses it anyway
    gridsize = IntegerField(null=True)
    annotater = CharField(null=True)
    brank = CharField(null=True)
    bteam = CharField(null=True)
    copyright = CharField(null=True)
    date = CharField(null=True)
    event = CharField(null=True)

    gname = CharField(null=True)
    gamecomment = CharField(null=True)
    opening = CharField(null=True)
    overtime = CharField(null=True)
    bname = CharField(null=True)
    place = CharField(null=True)
    wname = CharField(null=True)
    result = CharField(null=True)
    round = CharField(null=True)
    rules = CharField(null=True)
    source = CharField(null=True)
    timelim = CharField(null=True)
    user = CharField(null=True)
    wrank = CharField(null=True)
    wteam = CharField(null=True)
    handicap = CharField(null=True)
    komi = CharField(null=True)
    bterritory = CharField(null=True)
    # Or area, depending on rules
    wterritory = CharField(null=True)
    # Or area, depending on rules

    # def __init__(self, *args, **kwargs):
    #     super(Sgf, self).__init__(*args, **kwargs)

class CollectionSgf(BaseModel):
    collection = ForeignKeyField(Collection)
    sgf = ForeignKeyField(Sgf)

    def __str__(self):
        return '<CollectionSgf {} in {}>'.format(self.sgf, self.collection)


def get_collections():
    return list(Collection.select())

def collections_args_converter(ri, col):
    games = list(Sgf.select().join(CollectionSgf).join(Collection).where(Collection.name == col.name))
    return {'colname': col.name,
            'numentries': len(games),
            'collection': col}

def get_games_in(collection):
    games = list(Sgf.select().join(CollectionSgf).join(Collection).where(Collection.name == collection.name))
    return games

def games_args_converter(ri, game):
    info = {}
    info['sgf'] = game

    collection_list = list(Collection.select().join(CollectionSgf).join(Sgf).where(Sgf.id == game.id))
    if len(collection_list) > 0:
        info['collection'] = collection_list[0]

    if game.filename:
        info['filepath'] = game.filename
    if game.result:
        info['result'] = game.result
        winner = game.result[0].lower()
    if game.wname:
        info['wname'] = game.wname
        if winner == 'w':
            info['wname'] = embolden(info['wname'])
    if game.bname:
        info['bname'] = game.bname
        if winner == 'b':
            info['bname'] = embolden(info['bname'])
    if game.date:
        info['date'] = game.date

    return info
