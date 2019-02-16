#!/usr/bin/env python3
'''
    Browse article data from the database. Includes cleaning features.
'''
import sqlite3
from tqdm import tqdm
import time
from newspaper import Article
import spacy
import re

print('Loading Data Model: en_core_web_lg')
st = time.time()
#nlp = spacy.load('en_core_web_lg', disable=['tagger', 'parser'])

conn = sqlite3.connect('testdb.db')
cur = conn.cursor()

links = cur.execute('''select id,link from articles where
 author is null limit 5''').fetchall()
print('test', cur.execute('select id from articles order by id DESC limit 1').fetchall()[0][0])
total = len(links)
count = 0

for link in tqdm(links):
    id = link[0]
    url = link[1]
    # Create Article opbject w/ url & .download()
    article = Article(url)
    try:
        # catch article download errors (404 etc)
        article.download()
        # Parse article object
        article.parse()
        authors = article.authors
        authors_rev = []
        # Clean newspaper authors w/ spaCy NER
        for author in authors:
            doc = nlp(author)
            for ent in doc.ents:
                # print(ent.text, ent.label_)
                if ent.label_ == 'PERSON':
                    if ent.text not in authors_rev:
                        authors_rev.append(ent.text)
        # Only submit DB changes if revised author list contains 1+ name(s)
        if len(authors_rev) > 0:
            string = ", ".join(authors_rev)
            updata = (string, id)
            cur.execute('''UPDATE articles SET author = ? WHERE id = ? ''', (updata))
            count += 1
    except:
        #TODO: Add print to log file - error downloading row = id url = link
        pass
ft = time.time() - st
#TODO: ADD print to log file - to compare run time / errors
print(f'finished updating {count} / {total} rows in {ft} seconds.')
conn.commit()
conn.close()
