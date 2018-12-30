#!/usr/bin/python3
import feedparser
import sqlite3
from tqdm import tqdm
import re
import time
from newspaper import Article
# TODO: remove <img> from desc database column in new method or in next module.

class FeedParser():
    '''
    Retrieve and parse XML/ATOM feeds from Canadian news sources.
    allfeeds : Text File
        one feed per line.
    conn : Database File
        output to news-articles.db.
    '''
    def __init__(self):
        '''
        allfeeds : raw read of feeds.txt.
        conn / cur : sqlite3 database connectors.
        '''
        # Setup run timer - finished in submitentries()
        self.st = time.time()
        self.feederror = []
        # Open Feeds.txt
        self.allfeeds = open('feeds.txt', 'r').readlines()
        # Establish DB ConnectionError
        self.conn = sqlite3.connect('testdb.db')
        self.cur = self.conn.cursor()
        self.count = 0

    def getfeed(self):
        '''
        Fetch RSS/Atom feed and parse for database submission.
        xmlfeed : object
            feedparser parsed feed.
        entries : list
            entry data such as title, link, description.
        if : http:// elif : https://
            used to skip comment lines starting with #
        REQUIRED .submitentries()
            commit and close databse connection.
        '''
        print('Parsing website feeds.')
        for feed in tqdm(self.allfeeds):
            self.count = self.count + 1
            # Ignore comment lines
            if re.findall('(^https://.+$)', feed):
                xmlfeed = feedparser.parse(feed)
                entries = xmlfeed['entries']
                for entry in entries:
                    # catch AttributeError due to no feed element specified
                    try:
                        title = entry.title
                        link = entry.link
                        pub_date = entry.published
                        desc = entry.description
                        # strip any html tags from entry.description
                        desc = re.sub('<[^<]+?>', '', desc)
                        data = (title, link, pub_date, desc)
                        self.cur.execute('''
                                            INSERT OR IGNORE INTO articles
                                            (title, link, pub_date, desc)
                                            VALUES (?,?,?,?)
                                            ''', data)
                    except AttributeError:
                        pass
            elif re.findall('(^http://.+?$)', feed):
                xmlfeed = feedparser.parse(feed)
                entries = xmlfeed['entries']
                for entry in entries:
                    # catch AttributeError due to no feed element specified
                    try:
                        title = entry.title
                        link = entry.link
                        pub_date = entry.published
                        desc = entry.description
                        data = (title, link, pub_date, desc)
                        self.cur.execute('''
                                            INSERT OR IGNORE INTO articles
                                            (title, link, pub_date, desc)
                                            VALUES (?,?,?,?)
                                            ''', data)
                    except AttributeError:
                        pass
        self.conn.commit()
        print('Finished parsing website RSS/ATOM feeds.', self.count,
              'new articles were processed.', '\n')

    def getsources(self):
        print('Updating/Adding sources for articles.')
        self.sources = {'cbc.ca':'CBC','thestar.com':'Toronto Star','macleans.ca':'Macleans Magazine',
                        'ottawacitizen.com':'Ottawa Citizen','montrealgazette.com':'Montreal Gazette',
                        'vancouversun.com':'Vancouver Sun','financialpost.com':'Financial Post',
                        'torontosun.com':'Toronto Sun','nationalpost.com':'National Post',
                        'globalnews.ca':'Global News','ctvnews.ca':'CTV News',
                        'edmontonjournal.com':'Edmonton Journal','vice.com':'VICE',
                        'torontoist.com':'Torontoist','nationalobserver.com':'National Observer',
                        '680news.com':'680'}
        allrows = self.cur.execute('select id, link from articles where source is null').fetchall()
        count = 0
        for row in tqdm(allrows):
            count += 1
            # Define id : row variables
            id = row[0] ; link = row[1]
            # use dict to find / add source dynamically
            for key, value in self.sources.items():
                search = key ; source = value
                if re.search(search, link):
                    self.cur.execute('update articles set source = ? where id = ?', (source, id))
        self.conn.commit()
        print('Finished adding the sources to', count, 'articles.', '\n')

    def getcontent(self):
        print('Getting the text for articles in the database.')
        links = self.cur.execute('select id,link from articles where content is null').fetchall()
        for link in tqdm(links):
            id = link[0]
            url = link[1]
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
        self.conn.commit()
        self.conn.close()
        ft = time.time() - self.st
        print('Finished adding & updating records in', round(ft, 2), 'seconds.')

if __name__ == "__main__":
    program = FeedParser()
    program.getfeed()
    program.getsources()
    program.getcontent()
