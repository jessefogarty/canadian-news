#!/usr/bin/python3
import sqlite3
import re
import time

class Sources():
    def __init__(self):
        self.st = time.time()
        self.conn = sqlite3.connect('testdb.db')
        self.cur = self.conn.cursor()
        self.sources = {'cbc.ca':'CBC','thestar.com':'Toronto Star','macleans.ca':'Macleans Magazine',
                        'ottawacitizen.com':'Ottawa Citizen','montrealgazette.com':'Montreal Gazette',
                        'vancouversun.com':'Vancouver Sun','financialpost.com':'Financial Post',
                        'torontosun.com':'Toronto Sun','nationalpost.com':'National Post',
                        'globalnews.ca':'Global News','ctvnews.ca':'CTV News',
                        'edmontonjournal.com':'Edmonton Journal','vice.com':'VICE',
                        'torontoist.com':'Torontoist','nationalobserver.com':'National Observer'}
    def find(self):
        allrows = self.cur.execute('select id, link from articles where source is null').fetchall()
        for row in allrows:
            # Define id : row variables
            id = row[0] ; link = row[1]
            # use dict to find / add source dynamically
            for key, value in self.sources.items():
                search = key ; source = value
                if re.search(search, link):
                    self.cur.execute('update articles set source = ? where id = ?', (source, id))
        self.conn.commit()
        self.conn.close()
        ft = time.time() - self.st
        print('Finished updating records in', round(ft, 2), 'seconds.')

if __name__ == '__main__':
    program = Sources()
    program.find()
