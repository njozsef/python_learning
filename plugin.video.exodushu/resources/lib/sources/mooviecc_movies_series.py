# -*- coding: utf-8 -*-

import re,urllib,urllib2,urlparse,json
from resources.lib.modules import client
from resources.lib.modules import cleantitle


class source:
    def __init__(self):
        self.domains = ['moovie.cc']
        self.base_link = 'http://www.moovie.cc'
        self.search_link = '/core/search.json'
        self.host_link = 'http://filmbazis.org/'

    def movie(self, imdb, title, year):
        try:
            query = urlparse.urljoin(self.base_link, self.search_link)
            r = client.request(query)
            result = json.loads(r)
            
            t = cleantitle.get(title)
            filter = []
            filter += [i for i in result if t == cleantitle.get(i['title_eng'].encode('utf-8'))]
            
            if len(filter) == 0:
                t = 'http://www.imdb.com/title/%s' % imdb
                t = client.request(t, headers={'Accept-Language':'hu-HU'})
                t = client.parseDOM(t, 'h1', attrs={'itemprop': 'name'})[0].split('&nbsp')[0]
                hun_title = client.replaceHTMLCodes(t).strip()
                try: hun_title = hun_title.encode('utf-8')
                except: pass
                hun_title = cleantitle.get(hun_title)
                filter += [i for i in result if hun_title == cleantitle.get(i['title_hun'].encode('utf-8'))]
            
            result = [i for i in filter if year == i['year']]
            if len(result) == 0: raise Exception()
            
            query = urlparse.urljoin(self.base_link, '/online-filmek/%s' % result[0]['title_url'])
            r = client.request(query)
            result = client.parseDOM(r, 'table', attrs={'class': 'links'})
            query = client.parseDOM(result, 'a', ret='href')[0]
            
            r = client.request(query)
            host_domain = urlparse.urlsplit(query).netloc
            result = client.parseDOM(r, 'tr', attrs={'class': 'jsPlay'})
            return result, host_domain
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
            #parse url to strings
            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])
            title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']
            if 'year' in data: year = data['year']
            
            #get moviecc database in json
            query = urlparse.urljoin(self.base_link, self.search_link)
            r = client.request(query)
            result = json.loads(r)
            
            # search in database with original title
            t = cleantitle.get(title)
            filter = []
            filter += [i for i in result if t == cleantitle.get(i['title_eng'])]
            
            # if no match try with hun title
            if len(filter) == 0:
                t = 'http://www.imdb.com/title/%s' % imdb
                t = client.request(t, headers={'Accept-Language':'hu-HU'})
                t = client.parseDOM(t, 'h1', attrs={'itemprop': 'name'})[0].split('&nbsp')[0]
                hun_title = client.replaceHTMLCodes(t).strip()
                try: hun_title = hun_title.encode('utf-8')
                except: pass
                hun_title = cleantitle.get(hun_title)
                filter += [i for i in result if hun_title == cleantitle.get(i['title_hun'].encode('utf-8'))]
            if len(result) == 0: raise Exception()

            # parse filmbazis url from movie page source
            result = filter
            query = urlparse.urljoin(self.base_link, '/online-filmek/%s' % result[0]['title_url'])
            r = client.request(query)
            result = client.parseDOM(r, 'table', attrs={'class': 'links'})
            query = client.parseDOM(result, 'a', ret='href')[0]

            url = client.request(query, output='headers', redirect=False).dict['location']
            query = urlparse.urljoin(query, '%s/%s-evad' % (url, season))
            r = client.request(query)
            host_domain = urlparse.urlsplit(query).netloc
            result = client.parseDOM(r, 'div', attrs={'class': 'seasonList'})
            result = client.parseDOM(result, 'div', attrs={'class': 'item'})
            result = [i for i in result if client.parseDOM(i, 'input', ret='id')[0] == episode]
            result = client.parseDOM(result, 'tr', attrs={'class': 'jsPlay'})
            if len(result) == 0:raise Exception()
            return result, host_domain
        except:
            return


    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            if url == None: return sources
            
            result = url[0]
            host_domain = url[1]
            locDict = [(i.rsplit('.', 1)[0], i) for i in hostDict]

            for item in result:
                try:
                    host = client.parseDOM(item, 'td')[2].split('.')[0].strip().lower()
                    host = [x[1] for x in locDict if host == x[0]][0]
                    if not host in hostDict: raise Exception()
                    host = host.encode('utf-8')

                    q = client.parseDOM(item, 'span')[0].lower()
                    if ('mozis' in q or 'ts' in q or 'cam' in q): quality = 'CAM'                  
                    else: quality = 'SD'

                    l = client.parseDOM(item, 'img', ret='src')[0]
                    l = l.split('/')[-1].rsplit('.', 1)[0].strip().lower()
                    if (l == 'hu' or l == 'hu-hu'): lang = 'szinkron'
                    else: lang = ''

                    url = client.parseDOM(item, 'a', ret='href')[0]
                    url = urlparse.urljoin('http://' + host_domain, url)
                    url = url.encode('utf-8')

                    sources.append({'source': host, 'quality': quality, 'lang': lang, 'provider': 'Mooviecc', 'url': url, 'direct': False, 'debridonly': False})
                except:
                    pass
            return sources
        except:
            return sources


    def resolve(self, url):
        try:
            r = client.request(url)
            result = client.parseDOM(r, 'div', attrs={'class':'embedHolder'})
            try: url = client.parseDOM(result, 'iframe', ret='src')[0]
            except: url = client.parseDOM(result, 'IFRAME', ret='SRC')[0]
            url = url.encode('utf-8')
            return url
        except:
            return
