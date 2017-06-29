# -*- coding: utf-8 -*-

import re,urllib,urllib2,urlparse

from resources.lib.modules import client
from resources.lib.modules import cleantitle


class source:
    def __init__(self):
        self.domains = ['filminvazio.com']
        self.base_link = 'http://filminvazio.com'
        self.search_link = '/filmkereso/?%s'
        self.host_link = 'http://filmbirodalmak.com/'

    def movie(self, imdb, title, year):
        try:
            t = 'http://www.imdb.com/title/%s' % imdb
            t = client.request(t, headers={'Accept-Language':'hu-HU'})
            t = client.parseDOM(t, 'h1', attrs={'itemprop': 'name'})[0].split('&nbsp')[0]
            t = client.replaceHTMLCodes(t).strip()
            try: t = t.encode('utf-8')
            except: pass

            query = urllib.urlencode({'search_query': t, 'orderby': '', 'order': '', 'tax_fecha-estreno[]': year, 'wpas': '1'})
            query = urlparse.urljoin(self.base_link, self.search_link % query)
            result = client.request(query)

            result = client.parseDOM(result, 'div', attrs={'class': 'datos'})
            if len(result) == 0: raise Exception()
            result = [(client.parseDOM(i, 'a')[0], client.parseDOM(i, 'a', ret = 'href')[0]) for i in result]
            result = [i[1] for i in result if cleantitle.get(t) == cleantitle.get(i[0].encode('utf-8'))]
            
            if not result: raise Exception()
                
            r = client.request(result[0])
            result = client.parseDOM(r, 'div', attrs={'class': 'enlaces_box'})
            url = client.parseDOM(result, 'a', ret = 'href')[0]
            return url
            
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            if url == None: return sources
            
            r = client.request(url)
            #result = result.decode('iso-8859-1').encode('utf-8')
            result = client.parseDOM(r, 'div', attrs={'class': 'enlaces_box'})
            result = client.parseDOM(result, 'li', attrs={'class': 'elemento'})
            for item in result:
                try:
                    url = client.parseDOM(item, 'a', ret = 'href')[0]
                    url = url.encode('utf-8')
                    host = re.findall('([\w]+[.][\w]+)$', urlparse.urlparse(url.strip().lower()).netloc)[0]
                    if not host in hostDict: raise Exception()
                    host = client.replaceHTMLCodes(host)
                    host = host.encode('utf-8')
                    q = client.parseDOM(item, 'span', attrs={'class': 'd'})[0].strip().lower()
                    if q == 'hd': quality = 'HD'
                    elif 'ts' in q or 'cam' in q: quality = 'CAM'
                    else: quality = 'SD'
                    l = client.parseDOM(item, 'span', attrs={'class': 'c'})[0].strip().lower()
                    if l == 'magyar' or 'szinkron' in l: lang = 'szinkron'
                    else: lang = ''  
                    sources.append({'source': host, 'quality': quality, 'lang': lang, 'provider': 'Filminvazio', 'url': url, 'direct': False, 'debridonly': False})
                except:
                    pass
            return sources
        except:
            return sources


    def resolve(self, url):
        return url


