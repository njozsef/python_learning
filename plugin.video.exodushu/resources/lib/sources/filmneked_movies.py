# -*- coding: utf-8 -*-

import re,urllib,urllib2,urlparse,json

from resources.lib.modules import client


class source:
    def __init__(self):
        self.domains = ['filmneked.com']
        self.base_link = 'http://filmneked.com/'
        self.search_link = 'http://filmneked.com/titles/paginate?_token=%s&perPage=100&page=1&query=%s&type=movie&availToStream=true'

    def movie(self, imdb, title, year):
        try:
            years = [str(int(year)-1), str(int(year)+1)] 
            
            t = 'http://www.imdb.com/title/%s' % imdb
            t = client.request(t, headers={'Accept-Language':'hu-HU'})
            t = client.parseDOM(t, 'title')[0]
            originaltitle = re.sub('(?:\(|\s)\d{4}.+', '', t).strip()
            originaltitle = originaltitle.split('-')[0].split(':')[0].strip()
            originaltitle = originaltitle.replace(' ','+')

            result = client.request(self.base_link)
            try: token = re.search('token\s*:\s*\\\'([^\\\']+)', result).group(1)
            except: token = ''
            query = self.search_link % (token, originaltitle.encode('utf-8'))
            result = client.request(query)
            result = json.loads(result)
            if result['totalItems'] == 0: raise Exception()

            for i in result['items']:
                if i['imdb_id'] == imdb:
                    return i
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            if url == None: return sources
            
            result = url
            
            locDict = [(i.rsplit('.', 1)[0], i) for i in hostDict]
            
            if 'mm-site' in result['link'][0]['url']:
                quality = result['link'][0]['quality']
                result = client.request(result['link'][0]['url'])
                result = result.split('<tr')
                for i in result:
                    try:
                        l = client.parseDOM(i, 'img', ret='alt')[0]
                        if l.lower() == 'magyar': lang = 'szinkron'
                        else: lang = ''
                        host = client.parseDOM(i, 'td', attrs={'class': 'links'})[1]
                        host = host.split('<')[0].strip()
                        host = host.split()[0].rsplit('.', 1)[0].strip().lower()
                        try: host = host.split('(')[0].strip()
                        except: pass
                        host = [x[1] for x in locDict if host == x[0]][0]
                        if not host in hostDict: raise Exception()
                        host = client.replaceHTMLCodes(host)
                        host = host.encode('utf-8')
                        url = client.parseDOM(i, 'a', ret='href')[0]
                        url = url.encode('utf-8')
                        sources.append({'source': host, 'quality': quality, 'lang': lang, 'provider': 'Filmneked', 'url': url, 'direct': False, 'debridonly': False})
                    except:
                        pass

            else:
                for i in result['link']:
                    try: 
                        if i['quality'] == 'M': quality = 'CAM'
                        else: quality = 'SD'                    
                        if 'hun' in i['language'].lower(): lang = 'szinkron'
                        else: lang = ''
                        url = i['orig_url']
                        url = url.encode('utf-8') 
                        host = i['label'].split('.')[0].strip().lower()
                        host = [x[1] for x in locDict if host == x[0]][0]
                        if not host in hostDict: raise Exception()
                        host = client.replaceHTMLCodes(host)
                        host = host.encode('utf-8')  
                        sources.append({'source': host, 'quality': quality, 'lang': lang, 'provider': 'Filmneked', 'url': url, 'direct': False, 'debridonly': False})
                    except:
                        pass
            return sources
        except:
            return sources


    def resolve(self, url):
        if not 'mm-site' in url: return url
        
        r = client.request(url)
        result = client.parseDOM(r, 'div', attrs={'class': 'tab'})
        url = client.parseDOM(result, 'a', ret='href')[0]
        url = url.encode('utf-8')
        return url
