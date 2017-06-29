# -*- coding: utf-8 -*-

import re,urllib,urllib2,urlparse,json
from resources.lib.modules import client
from resources.lib.modules import control
from resources.lib.modules import cleantitle


class source:
    def __init__(self):
        self.domains = ['sorozat-barat.com']
        self.base_link = 'http://www.sorozat-barat.club'
        self.host_link = 'http://www.filmorias.com'
        self.search_link = '/series/autocompleteV2?%s'
        self.user = control.setting('sorozatbarat.user')
        self.password = control.setting('sorozatbarat.pass')

    def tvshow(self, imdb, tvdb, tvshowtitle, year):
        try:
            if (self.user == '' or self.password == ''): raise Exception()
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

            if (self.user == '' or self.password == ''): raise Exception()

            season = season.zfill(2)
            episode = episode.zfill(2)
            
            query = urllib.urlencode({'term': title})
            query = urlparse.urljoin(self.base_link, self.search_link % query)

            cookie = self.get_cookie()
            
            result = client.request(query, cookie=cookie)
            if result == '[]' or result == None: raise Exception()
            result = json.loads(result)
            for i in result:
                i['label'] = re.search('\(([^\)]+)', i['label']).group(1) if '(' in i['label'] else i['label']
            result = [i for i in result if cleantitle.get(title) == cleantitle.get(i['label'])]
            if len(result) == 0: raise Exception()
            url = [i['url'] for i in result][0]

            query = urlparse.urljoin(self.base_link, url + '/' + season + '_evad')
            result = client.request(query, cookie=cookie)
            
            seasons = client.parseDOM(result, 'ul', attrs={'class': 'seasons'})
            seasons = client.parseDOM(seasons, 'a', ret ='href')
            seasons = [i for i in seasons if '/' + season + '_evad' in i]
            if len(seasons) == 0: raise Exception()
            url = seasons[0]
            
            query = urlparse.urljoin(self.base_link, url)
            result = client.request(query, cookie=cookie)
            
            episodes = client.parseDOM(result, 'ul', attrs={'class': 'episodes active'})
            episodes = client.parseDOM(episodes, 'a', ret='href')
            episodes = [i for i in episodes if '_' + episode + '_resz' in i]
            if len(episodes) == 0: raise Exception()
            url = episodes[0]
            return url
        except:
            return


    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            
            if url == None: return sources

            cookie = self.get_cookie()

            query = urlparse.urljoin(self.base_link, url)
            result = client.request(query, cookie=cookie)

            items = client.parseDOM(result, 'table', attrs={'class': 'episodes'})
            items = client.parseDOM(items, 'tbody')
            items = client.parseDOM(items, 'tr')
            items = [i for i in items if 'watch.png' in i]
            if len(items) == 0: raise Exception()
            
            for i in items:
                try:
                    host = client.parseDOM(i, 'td')[1]
                    host = host.split('&')[0].strip().lower()
                    host = host.encode('utf-8')
                    if not host in hostDict: raise Exception()
                    l = client.parseDOM(i, 'img', ret='src')[0]
                    l = l.rsplit('/', 1)[1].split('.')[0].strip()
                    if l == 'hu' or l == 'hu-hu': lang = 'szinkron'
                    else: lang = ''
                    links = client.parseDOM(i, 'a', ret='href')
                    url = [i for i in links if i.startswith('http')][0]
                    url = client.replaceHTMLCodes(url)
                    url = url.encode('utf-8')
                    sources.append({'source': host, 'quality': 'SD', 'lang': lang, 'provider': 'SorozatBarat', 'url': url, 'direct': False, 'debridonly': False})
                except:
                    pass
            return sources
        except:
            return sources


    def resolve(self, url):
        try:
            result = client.request(url)
            url = client.parseDOM(result, 'puremotion', ret='data-url')[0]
            url = client.replaceHTMLCodes(url)
            url = url.encode('utf-8')
            return url
        except:
            return


    def get_cookie(self):
        try:
            login = urlparse.urljoin(self.base_link, '/login')  
            post = urllib.urlencode({'login': self.user, 'password': self.password, 'redirect': self.base_link, 'loginsubmit': 'Belépés'})
            cookie = client.request(login, post=post, output='cookie', close=False)
            if not 'member' in cookie:
                raise Exception()
            return cookie
        except:
            return
