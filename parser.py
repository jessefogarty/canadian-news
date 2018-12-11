#!/usr/bin/python3
import feedparser
import sqlite3
from tqdm import tqdm
import re

# TODO: remove <img> from desc database column in new method or in next module.
# TODO: Consider move to feeds.csv w/ source name for sql column

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
        for feed in self.allfeeds:
            self.count = self.count + 1
            print(self.count)
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
    def submitentries(self):
        '''
        commit queued data from .getfeed()
            close database connection.
        '''
        # TODO: add means to print out queued data / add flag for submit.
        self.conn.commit()
        self.conn.close()

if __name__ == "__main__":
    program = FeedParser()
    program.getfeed()
    program.submitentries()
