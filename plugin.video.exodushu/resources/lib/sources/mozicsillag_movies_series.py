# -*- coding: utf-8 -*-

import re,urllib,urllib2,urlparse,base64
from resources.lib.modules import cleantitle
from resources.lib.modules import client


class source:
    def __init__(self):
        self.domains = ['mozicsillag.cc']
        self.base_link = 'http://mozicsillag.cc'
        self.search_link = '/filter-search/%s'
        self.host_link = 'http://filmbirodalmak.com/'

    def movie(self, imdb, title, year):
        try:    
            t = 'http://www.imdb.com/title/%s' % imdb
            t = client.request(t, headers={'Accept-Language':'hu-HU'})
            t = client.parseDOM(t, 'h1', attrs={'itemprop': 'name'})[0].split('&nbsp')[0]
            t = client.replaceHTMLCodes(t).strip()
            t = t.replace('!', '').replace('?', '').replace(',', ' ').replace('  ', ' ')
            try: t = t.encode('utf-8')
            except: pass
            
            query = urlparse.urljoin(self.base_link, self.search_link % urllib.quote(t))
            r = client.request(query)
            result = r.split('</a>')

            result = [i for i in result if self.base_link + '/film/' in i]
            result = [(client.parseDOM(i, 'div', attrs={'class': 'small-12 columns text-left'})[0], i) for i in result]
            result = [(client.replaceHTMLCodes(i[0].replace('\n', '')), i[1]) for i in result]
            result = [i[1] for i in result if cleantitle.get(t) == cleantitle.get(i[0].encode('utf-8'))]
            if len(result) == 0: raise Exception()
            
            result = [(re.search('\s*:\s*(\d{4})', i).group(1), i) for i in result]
            result = [i[1] for i in result if year == i[0]]
            url = client.parseDOM(result, 'a', ret='href')[0]
            
            r = client.request(url)
            result = client.parseDOM(r, 'div', attrs={'class': 'small-12 medium-7 small-centered columns'})
            url = client.parseDOM(result, 'a', ret='href')[0]
            
            r = client.request(url)
            try: r = r.decode('iso-8859-1').encode('utf8')
            except: pass
            url = client.parseDOM(r, 'div', attrs={'class': 'panel\s*'})
            
            return url
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
            t = 'http://www.imdb.com/title/%s' % imdb
            t = client.request(t, headers={'Accept-Language':'hu-HU'})
            t = client.parseDOM(t, 'h1', attrs={'itemprop': 'name'})[0].split('&nbsp')[0]
            t = client.replaceHTMLCodes(t).strip()
            t = t.replace('!', '').replace('?', '').replace(',', ' ').replace('  ', ' ')
            try: t = t.encode('utf-8')
            except: pass
            
            query = urlparse.urljoin(self.base_link, self.search_link % urllib.quote(t))
            r = client.request(query)
            result = r.split('</a>')
            
            result = [i for i in result if self.base_link + '/sorozat/' in i]
            result = [(client.parseDOM(i, 'div', attrs={'class': 'small-12 columns text-left'})[0], i) for i in result]
            result = [(client.replaceHTMLCodes(i[0].replace('\n', '')), i[1]) for i in result]
            result = [(i[0].rsplit(':', 1)[0], i[1]) for i in result if '/%s-evad"' % season in i[1]]
            result = [i[1] for i in result if cleantitle.get(t) == cleantitle.get(i[0].encode('utf-8'))]
            url = client.parseDOM(result, 'a', ret='href')[0]
            
            r = client.request(url)
            result = client.parseDOM(r, 'div', attrs={'class': 'small-12 medium-7 small-centered columns'})
            url = client.parseDOM(result, 'a', ret='href')[0]
                    
            r = client.request(url)
            try: r = r.decode('iso-8859-1').encode('utf8')
            except: pass
            result = client.parseDOM(r, 'div', attrs = {'class': 'accordion-episodes'})
            result = [i for i in result if re.search('d\s*(.*)', client.parseDOM(i, 'a')[0]).group(1).strip() == episode]
            ep_url = client.parseDOM(result, 'div', attrs={'class': 'panel\s*'})
            
            return ep_url
        except:
            return
    

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            if url == None: return sources

            items = url

            locDict = [(i.rsplit('.', 1)[0], i) for i in hostDict]         

            for i in items:
                try:  
                    host, q = client.parseDOM(i, 'a', ret='title')[0].split('-')
                    host = host.rsplit('.', 1)[0].strip().lower()
                    host = [x[1] for x in locDict if host == x[0]][0]
                    if not host in hostDict: raise Exception()
                    host = client.replaceHTMLCodes(host)
                    host = host.encode('utf-8')
                    if 'CAM' in q: quality = 'CAM'
                    elif 'HD' in q: quality = 'HD'               
                    else: quality = 'SD'
                    l = client.parseDOM(i, 'img', ret='src')[1]
                    l = l.rsplit('/', 1)[-1].split('.')[0].strip()
                    if l == 'HU': lang = 'szinkron'
                    else: lang = ''
                    url = client.parseDOM(i, 'a', ret='href')
                    url = [i for i in url if 'watch-' in i][0]
                    url = url.encode('utf-8')
                    sources.append({'source': host, 'quality': quality, 'lang': lang, 'provider': 'Mozicsillag', 'url': url, 'direct': False, 'debridonly': False})
                except:
                    pass
            return sources
        except:
            return sources


    def resolve(self, url):
        try:
            query = urlparse.urljoin(self.host_link, url)
            result = client.request(query)
            if 'FilmBirodalom' in result:
                url = client.parseDOM(result, 'div', attrs={'class': 'content'})[0]
                url = client.parseDOM(url, 'a', ret='href')[0]
            else:
                url = client.request(query, output='geturl')
            url = url.encode('utf-8')
            return url
        except:
            return


