#!/usr/bin/python3
'''
    A small script to clean html tags from entry.description.

    Added regex substitue to main parser script. Archived in cleaner.
'''
import sqlite3
import re
from tqdm import tqdm
conn = sqlite3.connect('testdb.db')
cur = conn.cursor()
data = cur.execute('select id, desc from articles').fetchall()
for entry in tqdm(data):
    id = entry[0] ; desc = entry[1]
    desc = re.sub('<[^<]+?>', '', desc)
    cur.execute('update articles set desc = ? where id = ?', (desc, id))
conn.commit()
conn.close()
print('finished')
