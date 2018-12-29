#!/usr/bin/python3
from newspaper import Article
import re
import sqlite3
import time
# Use to only pull names from newpaper Article.author
from nltk import word_tokenize
from nltk.corpus import names
'''
['Cbc News']
['Rhiannon Johnson', 'Rhiannon Johnson Is An Anishinaabe Journalist Hiawatha First Nation Based In Toronto. She Has Been With The Ind
igenous Unit Since Focusing On Indigenous Life', 'Experiences Throughout Ontario. You Can Reach Her At Rhiannon.Johnson Cbc.Ca', 'On
Twitter']
['Erica Johnson', 'Sophia Harris']
'''
# set debug start timer
st = time.time()

names = ([(name, 'male') for name in names.words('male.txt')] +
	 [(name, 'female') for name in names.words('female.txt')])

conn = sqlite3.connect('testdb.db')
cur = conn.cursor()

db = cur.execute('select id, link from articles').fetchall()

for row in db:
    id = row[0] ; link = row[1]
    content = Article(link)
    content.download()
    try:
        content.parse()
        try:
            # use NLTK if not a proper noun skip
            authors = content.authors
            print(authors)
        except:
            authors = None
    except:
        pass
ft = time.time() - st ; print('finished in:', ft, 'seconds.')

#cur.execute('update articles set ')
