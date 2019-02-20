#!/bin/bash

sqlite3 bot.db "create table links (url text primary key, name text)"
sqlite3 bot.db "create table admins (id integer primary key, name text)"
