#!/usr/bin/python3
import sqlite3
import pandas as pd
import os.path
import os

# delete old file & create new
if os.path.isfile('articles.html') == True:
    os.remove('articles.html')
    open('articles.html', 'w')

# Connect, Retrieve and Create pandas dataframe
conn = sqlite3.connect('testdb.db')
df = pd.read_sql_query('select * from articles;', conn)
# Convert dataframe to html and store in file.
print(df.to_html(), file=open('articles.html', 'a'))
