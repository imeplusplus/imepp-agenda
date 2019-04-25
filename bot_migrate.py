import os
import sqlite3
import dataset

db = dataset.connect("sqlite:///bot.db");

def f1():
    db.query('create table if not exists links (url text primary key, name text)')
    db.query('create table if not exists admins (id integer primary key, name text)')
    version = 1;
    db['config'].upsert(dict(id=0, version=1), ['id'])

def f2():
    db.query('alter table links add column isPermanent integer default 0')
    version = 2;
    db['config'].upsert(dict(id=0, version=2), ['id'])


def migrate():
    exists = os.path.isfile('bot.db')
    if not exists: sqlite3.connect('bot.db')

    db.query('create table if not exists config (id integer primary key, version integer)')
    db['config'].insert_ignore(dict(id=0, version=0), ['id'])

    aux = list(db['config'].all())
    version = aux[0]['version']

    funcs = [f1, f2]
    for i in range(len(funcs)):
        if version < i + 1 : funcs[i]()
