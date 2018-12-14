#!/usr/bin/python3
import sqlite3
import re

conn = sqlite3.connect('../testdb.db')
cur = conn.cursor()

data = cur.execute('select id, desc, source from articles').fetchall()

for entry in data:
    id = entry[0] ; desc = entry[1] ; source = entry[2]
    # change to findall and strip in same line.... No need for search then findall
    if re.search('<img', desc) and source == 'CBC':
        print('cbc with img html tag')
