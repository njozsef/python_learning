# -*- coding: utf-8 -*-

import re,urllib,urllib2,urlparse,json
from resources.lib.modules import cleantitle
from resources.lib.modules import client


class source:
    def __init__(self):
        self.domains = ['webmoovies.com']
        self.base_link = 'http://webmoovies.com'
        self.search_link = '/ajax/search.php'

    def movie(self, imdb, title, year):
        try:
            post = urllib.urlencode({'q': title, 'limit': '5'})
            query = urlparse.urljoin(self.base_link, self.search_link)
            r = client.request(query, post = post)
            result = json.loads(r)

            result = [i for i in result if 'movie' in i['meta'].lower()]
            for i in result:
                try: t = re.search('\s\((.*)\)$', i['title']).group(1)
                except: t = i['title']
                t = t.encode('utf-8')
                if cleantitle.get(title) == cleantitle.get(t): url = i['permalink'].encode('utf-8'); break
            return url
        except:
            return


    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

            if url == None: return sources

            query = urlparse.urljoin(self.base_link, url)
            r = client.request(url)
            try: r = r.decode('iso-8859-1').encode('utf8')
            except: pass

            result = client.parseDOM(r, 'div', attrs={'id': 'link_list'})[0]
            result = result.split('<div class="span-16')
            
            locDict = [(i.rsplit('.', 1)[0], i) for i in hostDict]
            
            for item in result:
                try:
                    host = client.parseDOM(item, 'span')[0].strip().lower()
                    host = host.split('.', 1)[0]
                    host = [x[1] for x in locDict if host == x[0]][0]
                    if (not host in hostDict or host == 'youtube.com'): raise Exception()
                    host = host.encode('utf-8')
                    url = client.parseDOM(item, 'a', ret='href')
                    url = [i for i in url if i.startswith('http')][0]
                    url = url.encode('utf-8')
                    l = re.search('images\/([a-zA-Z]+)', item).group(1).lower()
                    if l == 'hun': lang = 'szinkron'
                    else: lang = ''
                    
                    sources.append({'source': host, 'quality': 'SD', 'lang': lang, 'provider': 'Webmoovies', 'url': url, 'direct': False, 'debridonly': False})
                except:
                    pass
            return sources
        except:
            return sources


    def resolve(self, url):
        try:
            url = re.search('//adf.ly/[0-9]+/(.*)', url).group(1)
            if not url.startswith('http'): url = 'http://' + url
            return url
        except: 
            return
