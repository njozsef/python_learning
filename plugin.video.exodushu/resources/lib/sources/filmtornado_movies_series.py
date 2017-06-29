# -*- coding: utf-8 -*-

import re,urllib,urlparse
from resources.lib.modules import cleantitle
from resources.lib.modules import client


class source:
    def __init__(self):
        self.domains = ['filmtornado.eu']
        self.base_link = 'http://filmtornado.eu/'
        self.search_link = 'http://filmtornado.eu/search.php'

    def movie(self, imdb, title, year):
        try:
            post = {'search': title}
            post = urllib.urlencode(post)
            
            t = cleantitle.get(title)
            
            r = client.request(self.search_link, post=post)
            
            r = client.parseDOM(r, 'div', attrs = {'class': 'img-box'})
            r = [client.parseDOM(i, 'a', ret='href')[0] for i in r if 'box-age">' + year + '<' in i]

            for i in r:
                url = client.replaceHTMLCodes(i)
                url = url.encode('utf-8')
                src = client.request(url)
                titl = client.parseDOM(src, 'div', attrs = {'class': 'col-lg-3 col-md-4 col-sm-8 col-xs-6'})[0]
                if cleantitle.get(re.findall('Eredeti.+?\/b>(.+?)<', titl)[0]) == t:
                    src = client.parseDOM(src, 'table', attrs = {'class': 'table table-hover'})
                    return src[0]
        except:
            return


    def tvshow(self, imdb, tvdb, tvshowtitle, year):
        try:
            url = {'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'year': year}
            url = urllib.urlencode(url)
            return url
        except:
            return
        
    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if url == None: return            
            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])
            title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']        
            
            post = {'search': title}
            post = urllib.urlencode(post)
            
            t = cleantitle.get(title)
            
            r = client.request(self.search_link, post=post)
            
            r = client.parseDOM(r, 'div', attrs = {'class': 'img-box'})
            r = [client.parseDOM(i, 'a', ret='href')[0] for i in r if (' ' + season + u'. évad' in i) or (' ' + season + u'. Évad' in i)]

            if len(r) == 0: raise Exception()
            elif len(r) == 1: url = r[0]
            elif len(r) > 1:
                for i in r:
                    src = client.request(i)
                    titl = client.parseDOM(src, 'div', attrs = {'class': 'col-lg-3 col-md-4 col-sm-8 col-xs-6'})[0]
                    if cleantitle.get(re.findall('Eredeti.+?\/b>(.+?)<', titl)[0]) == t:
                        url = i
            
            r = client.request(url)

            r = client.parseDOM(r, 'tbody', attrs = {'class': 'ep-body'})
            r = [i for i in r if ('<div> ' + episode + u'. epizód</div>' in i) or ('<div>' + episode + u'. epizód</div>' in i)]
            
            if not len(r) == 1: raise Exception()
            
            return r[0]
        except:
            return
    

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

            if url == None: return sources

            locDict = [(i.rsplit('.', 1)[0], i) for i in hostDict]

            items = re.findall('href="?\'?([^"\'>]*).+?src.+?img\/(\d{1}).+?<div>(.+?)<.+?td><div>(.+?)<', url)
            for item in items:
                try:
                    host = item[3].split()[0].rsplit('.', 1)[0].strip().lower()
                    host = [x[1] for x in locDict if host == x[0]][0]
                    if not host in hostDict: raise Exception()
                    host = client.replaceHTMLCodes(host)
                    host = host.encode('utf-8')
                    if item[2] == 'DVD' or item[2] == 'TV': quality = 'SD'
                    elif item[2] == 'CAM': quality = 'CAM'
                    else: quality = 'SD'
                    if item[1] == '3': lang = 'szinkron'
                    else: lang = ''
                    url = client.replaceHTMLCodes(item[0])
                    url = url.encode('utf-8')
                    sources.append({'source': host, 'quality': quality, 'lang': lang, 'provider': 'Filmtornado', 'url': url, 'direct': False, 'debridonly': False})
                except:
                    pass

            return sources
        except:
            return sources


    def resolve(self, url):
        try:
            src = client.request(url)
            try: url = client.parseDOM(src, 'iframe', ret='src')[-1]
            except: url = client.parseDOM(src, 'IFRAME', ret='SRC')[-1]
            url = client.replaceHTMLCodes(url)
            url = url.encode('utf-8')
            return url
        except:
            return
