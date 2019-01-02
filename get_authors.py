#!/usr/bin/python3
from newspaper import Article
import re
import sqlite3
import time
from tqdm import tqdm

conn = sqlite3.connect('testdb.db')
cur = conn.cursor()

db = cur.execute('select id, link from articles limit 300').fetchall()

for row in tqdm(db):
    id = row[0] ; link = row[1]
    content = Article(link)
    content.download()
    try:
        content.parse()
        try:
            authors = content.authors
            print(authors)
        except:
            authors = None
    except:
        pass
ft = time.time() - st ; print('finished in:', ft, 'seconds.')

#cur.execute('update articles set ')
