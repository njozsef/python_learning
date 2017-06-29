# -*- coding: utf-8 -*-

import re,urllib,urllib2,urlparse
from resources.lib.modules import cleantitle
from resources.lib.modules import client


class source:
    def __init__(self):
        self.domains = ['filmezz.eu']
        self.base_link = 'http://filmezz.eu'
        self.search_link = '/kereses.php?%s'

    def movie(self, imdb, title, year):
        try:
            s_titles = [title]
            
            t = 'http://www.imdb.com/title/%s' % imdb
            t = client.request(t, headers={'Accept-Language':'hu-HU'})
            t = client.parseDOM(t, 'h1', attrs={'itemprop': 'name'})[0].split('&nbsp')[0]
            t = client.replaceHTMLCodes(t).strip()
            try: t = t.encode('utf-8')
            except: pass

            s_titles.append(t)
            
            for a in s_titles:
                try:
                    query = urllib.urlencode({'s': a, 't': '1'})
                    query = urlparse.urljoin(self.base_link, self.search_link % query)
                    r = client.request(query)
                    result = client.parseDOM(r, 'div', attrs={'class': 'boxcont'})[0]
                    result = result.split('div onmouseover')
                    result = [i for i in result if 'film.php?' in i]
                    result = [(re.search('center>\s*<b>(.+?)\s*(?:\(\d{4}\))?<', i).group(1), i) for i in result]
                    result = [i[1] for i in result if cleantitle.get(s_titles[0]) == cleantitle.get(i[0].encode('utf-8')) or cleantitle.get(s_titles[1]) == cleantitle.get(i[0].encode('utf-8'))]
                    if len(result) > 0: break
                except:
                    pass
            if len(result) == 0: raise Exception()
            
            list = []
            
            for x in result:
                try:
                    try: y = re.search('>\\xc9v\s*:\s*<\/u>\s*(\d{4})', x).group(1)
                    except: y = re.search('<center>.+?(\d{4})', x).group(1)
                    list.append((y, x))
                except:
                    pass
            
            result = [i[1] for i in list if i[0] == year]
            
            if len(result) == 0: raise Exception()

            url = client.parseDOM(result[0], 'a', ret='href')[0]
            return (url, '')
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
            s_titles = []
                    
            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])
            title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']    

            s_titles.append(title)

            t = 'http://www.imdb.com/title/%s' % imdb
            t = client.request(t, headers={'Accept-Language':'hu-HU'})
            t = client.parseDOM(t, 'h1', attrs={'itemprop': 'name'})[0].split('&nbsp')[0]
            t = client.replaceHTMLCodes(t).strip()
            try: t = t.encode('utf-8')
            except: pass

            s_titles.append(t)

            for a in s_titles:
                try:
                    query = urllib.urlencode({'s': a, 't': '2'})
                    query = urlparse.urljoin(self.base_link, self.search_link % query)
                    r = client.request(query)
                    result = client.parseDOM(r, 'div', attrs={'class': 'boxcont'})[0]
                    result = result.split('div onmouseover')
                    result = [i for i in result if 'film.php?' in i]
                    result = [(re.search('b>(.+?)\s\d+\.\s\\xe9vad<', i).group(1).strip(), i) for i in result]
                    result = [i[1] for i in result if cleantitle.get(a) == cleantitle.get(i[0].encode('utf-8'))]
                    if len(result) > 0: break
                except:
                    pass
            if len(result) == 0: raise Exception()

            result = [i for i in result if '-%s-evad&' % season in i]

            url = client.parseDOM(result[0], 'a', ret='href')[0]
            url = url.encode('utf-8')
            return (url, episode)
        except:
            return


    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

            if url == None: return sources

            query = urlparse.urljoin(self.base_link, url[0])

            r = client.request(query)

            result = r.split('<tr>')
            result = [i for i in result if urlparse.urljoin(self.base_link, '/linkek.php') in i]

            if url[1].isdigit():
                result = [i for i in result if '%s. epiz\xc3\xb3d' % url[1] in i]

            locDict = [(i.rsplit('.', 1)[0], i) for i in hostDict]

            host_corr = [('vidtome', 'vidto')]

            for i in result:
                try:
                    host = client.parseDOM(i, 'td')[0]
                    host = re.sub('<.*>', '', host).strip().lower().rsplit('.', 1)[0]
                    try: host = [y[1] for y in host_corr if host == y[0]][0]
                    except: pass
                    host = [x[1] for x in locDict if host == x[0]][0]
                    if not host in hostDict: raise Exception()
                    host = host.encode('utf-8')
                    url = client.parseDOM(i, 'a', ret='id')[0]
                    url = client.replaceHTMLCodes(url)
                    url = url.encode('utf-8')
                    url = urlparse.urljoin(self.base_link, '/linkek.php?id=%s' % url)
                    q = re.search('qual/([0-9])\.', i).group(1)
                    if q == '1': quality = 'CAM'
                    elif q == '2' or q == '3': quality = 'SD'
                    elif q == '5': quality = 'HD'
                    else: quality = 'SD'
                    l = re.search('lang/([0-9])\.', i).group(1)
                    if l == '3': lang = 'szinkron'
                    else: lang = ''
                    sources.append({'source': host, 'quality': quality, 'lang': lang, 'provider': 'Filmezz', 'url': url, 'direct': False, 'debridonly': False})
                except:
                    pass

            return sources
        except:
            return sources


    def resolve(self, url):
        location = ''
        try:
            r = client.request(url, output='headers', redirect=False).headers
            try: location = [i.replace('Location:', '').strip() for i in r if 'Location:' in i][0]
            except: location = client.request(url)
            if not location.startswith('http'):
                try: location = client.parseDOM(location, 'iframe', ret='src')[0]
                except: location = client.parseDOM(location, 'IFRAME', ret='SRC')[0]
            if not location.startswith('http'): raise Exception()
            url = client.replaceHTMLCodes(location)
            url = re.sub(r'^"|"$', '', url)
            try: url = url.encode('utf-8')
            except: pass
            return url
        except: 
            return
