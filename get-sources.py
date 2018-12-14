#!/usr/bin/python3
import sqlite3
import re
import time

class Sources():
    def __init__(self):
        self.conn = sqlite3.connect('testdb.db')
        self.cur = self.conn.cursor()
        self.sources = {'cbc.ca':'CBC','thestar.com':'Toronto Star'}
    def find(self):
        st = time.time()
        allrows = self.cur.execute('select id, link from articles').fetchall()
        #for key, value in self.sources.items():
            #search = key ; source = value
            #print(search, source)
        for row in allrows:
            # Define id : row variables
            id = row[0] ; link = row[1]
            for key, value in self.sources.items():
                search = key ; source = value
                if re.search(search, link):
                    print(link, source)
            #if re.search('cbc.ca', link):
                #source = 'CBC'
                #self.cur.execute('update articles set source = ? where id = ?', (source, id))

        self.conn.commit()
        self.conn.close()
        ft = time.time() - st
        print('Finished updating records in', round(ft, 2), 'seconds.')

if __name__ == '__main__':
    program = Sources()
    program.find()
