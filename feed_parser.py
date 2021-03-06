#!/usr/bin/python3
import feedparser
import sqlite3
from tqdm import tqdm
import re
import time
from newspaper import Article
# TODO: make the class more modular
'''
    A Breif description for the feed_parser
        - Get title, link, publish date and description from feeds.
            - Store in DB.
        - Update / Add article source to each row in database.
        - Update / Add article content text to each row in database.
'''


class FeedParser():
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
        self.conn = sqlite3.connect('articles_raw.db')
        self.cur = self.conn.cursor()
        self.count = 0
        # TODO: add getauthor to getcontent
        # TODO: remove getauthor_sp 0; remove comment for below
            # useless when fixed getauthor + getcontent
        #self.getauthor_sp = self.cur.execute('''select id from articles
                                #order by id DESC limit 1''').fetchall()[0][0]
        self.getauthor_sp = 0

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
        self.sources = {'cbc.ca': 'CBC', 'thestar.com': 'Toronto Star',
                        'macleans.ca': 'Macleans Magazine',
                        'ottawacitizen.com': 'Ottawa Citizen',
                        'montrealgazette.com': 'Montreal Gazette',
                        'vancouversun.com': 'Vancouver Sun',
                        'financialpost.com': 'Financial Post',
                        'torontosun.com': 'Toronto Sun',
                        'nationalpost.com': 'National Post',
                        'globalnews.ca': 'Global News',
                        'ctvnews.ca': 'CTV News',
                        'edmontonjournal.com': 'Edmonton Journal',
                        'vice.com': 'VICE',
                        'torontoist.com': 'Torontoist',
                        'nationalobserver.com': 'National Observer',
                        '680news.com ': '680'}
        allrows = self.cur.execute('''select id, link from articles
            where source is null''').fetchall()
        count = 0
        for row in tqdm(allrows):
            count += 1
            # Define id : row variables
            id = row[0]
            link = row[1]
            # use dict to find / add source dynamically
            for key, value in self.sources.items():
                search = key
                source = value
                if re.search(search, link):
                    self.cur.execute('''
                          update articles set source = ? where id = ?''',
                                     (source, id))
        self.conn.commit()
        print('Finished adding the sources to', count, 'articles.', '\n')

    def getcontent(self):
        print('Getting the text for articles in the database.')
        links = self.cur.execute('''
            select id,link from articles where content is null''').fetchall()
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
                self.cur.execute('''
                    update articles set content = ? where id = ?''', updata)
            except:
                pass
        self.conn.commit()
        self.conn.close()
        ft = time.time() - self.st
        print('Finished adding & updating records in',
              round(ft, 2), 'seconds.')

    def getauthors(self):
        links = cur.execute('''select id,link from articles where
         author is null''').fetchall()
        for link in tqdm(links):
            id = link[0]
            # skip row if id is less than starting point (no new rows added)
            if id > self.getauthor_sp:
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
                        self.cur.execute('''UPDATE articles SET author = ? WHERE id = ? ''', (updata))
                        count += 1
                except:
                    #TODO: Add print to log file - error downloading row = id url = link
                    pass

        self.conn.commit()


if __name__ == "__main__":
    program = FeedParser()
    program.getfeed()
    program.getsources()
    program.getcontent()
    program.getauthors()
