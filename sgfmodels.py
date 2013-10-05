'''Peewee ORM models for storing sgf metadata.'''

from peewee import *
import datetime

db = SqliteDatabase('./collections.db')
db.connect()

class BaseModel(Model):
    class Meta(object):
        database = db

class Sgf(BaseModel):
    '''Peewee model for storing sgf metadata in a databsae'''

    filename = CharField(null=True)

    sgf = TextField(null=True)
    '''The entire sgf.'''

    other = TextField(null=True)
    '''Anything else I think of...'''

    collections = CharField(null=True)

    keywords = CharField(null=True)

    user_rating = IntegerField(null=True)

    user_created = BooleanProperty(null=True)

    date_created = DateTimeField(default=datetime.datetime.now)
    
    
    # Direct sgf properties
    ap = CharField(null=True)
    charset = ca = CharField(null=True)
    fileformat = ff = CharField(null=True)
    gametype = gm = CharField(null=True)
    # Should always be 1 (== Go) for us...
    varshow = st = CharField(null=True)
    # We ignore this, and I'm not sure anyone uses it anyway
    size = sz = IntegerField(null=True)
    annotater = an = CharField(null=True)
    brank = br = CharField(null=True)
    bteam = bt = CharField(null=True)
    copyright = cp = CharField(null=True)
    date = dt = CharField(null=True)
    event = ev = CharField(null=True)
    gname = gn = CharField(null=True)
    gamecomment = gc = CharField(null=True)
    opening = on = CharField(null=True)
    overtime = ot = CharField(null=True)
    bname = pb = CharField(null=True)
    place = pc = CharField(null=True)
    wname = pw = CharField(null=True)
    result = re = CharField(null=True)
    round = ro = CharField(null=True)
    rules = ru = CharField(null=True)
    source = so = CharField(null=True)
    timelim = tm = CharField(null=True)
    user = us = CharField(null=True)
    wrank = wr = CharField(null=True)
    wteam = wt = CharField(null=True)
    handicap = ha = CharField(null=True)
    komi = km = CharField(null=True)
    bterritory = tb = CharField(null=True)
    # Or area, depending on rules
    wterritory = tw = CharField(null=True)
    # Or area, depending on rules


