#!/usr/bin/python3
import sqlite3
from newspaper import Article
from tqdm import tqdm
import time

class dMiner():
    '''
    A simple data mining algorithm for newpaper article parsing.
    '''
    def __init__(self):
        self.conn = sqlite3.connect('testdb.db')
        self.cur = self.conn.cursor()
        self.st = time.time()
    def getcontent(self):
        links = self.cur.execute('select id,link from articles where content is null').fetchall()
        total = len(links)
        count = 0
        for link in tqdm(links):
            id = link[0]
            url = link[1]
            count += 1
            # Create Article opbject w/ url & .download()
            article = Article(url)
            try:
                article.download()
                # Parse article object
                article.parse()
                content = article.text
                updata = (content, id)
                self.cur.execute('update articles set content = ? where id = ?', updata)
            except:
                pass
            total = total - count
        ft = time.time() - self.st
        print('finished updating', count, 'rows in', ft, 'seconds.')
        self.conn.commit()
        self.conn.close()

if __name__ == "__main__":
    program = dMiner()
    program.getcontent()
