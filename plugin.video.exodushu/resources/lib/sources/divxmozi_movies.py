# -*- coding: utf-8 -*-

import re,urllib,urllib2,urlparse
from resources.lib.modules import cleantitle
from resources.lib.modules import client


class source:
    def __init__(self):
        self.domains = ['divxmozi.eu']
        self.base_link = 'http://divxmozi.eu'
        self.search_link = '/search_movies'

    def movie(self, imdb, title, year):
        try:
            t = 'http://www.imdb.com/title/%s' % imdb
            t = client.request(t, headers={'Accept-Language':'hu-HU'})
            t = client.parseDOM(t, 'h1', attrs={'itemprop': 'name'})[0].split('<')[0]
            t = client.replaceHTMLCodes(t).strip()
            try: t = t.encode('utf-8')
            except: pass

            post = urllib.urlencode({'q': t.replace('.', ''), 'sb': ''})
            query = urlparse.urljoin(self.base_link, self.search_link)
            r = client.request(query, post = post)

            result = client.parseDOM(r, 'div', attrs={'class': 'small-item'})
            result = [(client.parseDOM(i, 'img', ret='alt')[0].encode('utf-8'), i) for i in result]
            result = [i[1] for i in result if cleantitle.get(t) == cleantitle.get(i[0])]
            result = [(re.findall('\s\((\d{4})\)\s*<', i)[0], i) for i in result]
            result = [client.parseDOM(i[1], 'a', ret='href')[0] for i in result if year == i[0]]

            if len(result) == 0: raise Exception()
            
            return result[0]
        except:
            return


    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

            if url == None: return sources

            query = urlparse.urljoin(self.base_link, url)
            r = client.request(query)

            result = client.parseDOM(r, 'div', attrs={'class': 'tab-content'})[0]
            result = result.split('<div class="tab-pane')
            
            for item in result:
                try:
                    q = re.search('id\s*=\s*"\s*([^"]+)', item).group(1).lower()
                    if 'szinkron' in q: lang = 'szinkron'
                    else: lang = ''
                    
                    if '-cam' in q: quality = 'CAM'
                    elif '-dvd' in q: quality = 'SD'
                    else: quality = 'SD'
                    
                    items = client.parseDOM(item, 'div', attrs={'class': 'span4'})
                    
                    locDict = [(i.rsplit('.', 1)[0], i) for i in hostDict]

                    for i in items:
                        try:
                            host = client.parseDOM(i, 'a')[0].strip().lower()
                            host = [x[1] for x in locDict if host == x[0]][0]
                            if not host in hostDict: raise Exception()
                            host = host.encode('utf-8')
                            url = client.parseDOM(i, 'a', ret='href')[0]
                            url = url.encode('utf-8')
         
                            sources.append({'source': host, 'quality': quality, 'lang': lang, 'provider': 'Divxmozi', 'url': url, 'direct': False, 'debridonly': False})
                        except:
                            pass
                    
                except:
                    pass
            return sources
        except:
            return sources


    def resolve(self, url):
        try:
            url = client.request(url, output='headers', redirect = False).dict['location']
            return url
        except: 
            return
