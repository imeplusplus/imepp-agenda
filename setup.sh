#!/bin/bash

sqlite3 bot.db "create table links (id integer primary key, name text, url text)"
