# -*- coding: utf-8 -*-

import re,urllib,urlparse,json
from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import cache


class source:
    def __init__(self):
        self.domains = ['online-pont.site']
        self.base_link = 'http://online-pont.site'
        self.search_link = '/index.php?%s'

    def movie(self, imdb, title, year):
        try:
            t = 'http://www.imdb.com/title/%s' % imdb
            t = client.request(t, headers={'Accept-Language':'hu-HU'})
            t = client.parseDOM(t, 'h1', attrs={'itemprop': 'name'})[0].split('&nbsp')[0]
            t = client.replaceHTMLCodes(t).strip()
            try: t = t.encode('utf-8')
            except: pass

            query = urllib.urlencode({'s': t})
            query = urlparse.urljoin(self.base_link, self.search_link % query)
            r = client.request(query)
   
            result = client.parseDOM(r, 'div', attrs = {'id': 'moviefilm'})
            if not result: raise Exception()
            result = [(client.parseDOM(i, 'img', ret='alt')[0], i) for i in result]
            result = [i[1] for i in result if cleantitle.get(t) == cleantitle.get(i[0].encode('utf-8'))]
            result = [i for i in result if re.search(':\s*(\d{4})\s*</span', i).group(1) == year]

            if not result: raise Exception()
            
            host_url = client.parseDOM(r, 'ul', attrs = {'id': 'nav'})
            host_url = client.parseDOM(host_url, 'li')
            host_url = [client.parseDOM(i, 'a', ret='href')[0] for i in host_url if not self.base_link in i]
            host_url = 'http://' + urlparse.urlparse(host_url[0]).netloc
            
            try: tag = re.search('"tag"\s*>([^<]+)', result[0]).group(1)
            except: tag = ''
            tag = tag.encode('utf-8')
            
            url = client.parseDOM(result[0], 'a', ret='href')[0]
            url = urlparse.urlparse(url).path.split('/')[1]
            url = urlparse.urljoin(host_url, url)
            try: url = url.encode('utf-8')
            except: pass
            return [url, tag]
        except:
            return


    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

            if url == None: return sources
            tag = url[1].lower()
            
            post = urllib.urlencode({'lock_password': '', 'Submit': 'Online Linkek'})
            r = client.request(url[0], post=post)

            result = client.parseDOM(r, 'a', ret = 'href')
            result += client.parseDOM(r.lower(), 'iframe', ret='src')
            result = [i for i in result if not 'youtube.com' in i]
            if not result: return sources
            
            for item in result:
                try:
                    host = re.findall('([\w]+[.][\w]+)$', urlparse.urlparse(item.strip().lower()).netloc)[0]
                    if not host in hostDict: raise Exception()
                    host = client.replaceHTMLCodes(host)
                    host = host.encode('utf-8')
                    url = item.encode('utf-8')
                    if ('kamer\xc3\xa1s' in tag or 'cam' in tag): quality = 'CAM'
                    else: quality = 'SD'
                    if 'feliratos' in tag: lang = ''
                    else: lang = 'szinkron'
                    sources.append({'source': host, 'quality': quality, 'lang': lang, 'provider': 'Onlinepont', 'url': url, 'direct': False, 'debridonly': False})
                except:
                    pass
            return sources
        except:
            return sources


    def resolve(self, url):
        return url
