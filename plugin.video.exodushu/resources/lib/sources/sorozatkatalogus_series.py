# -*- coding: utf-8 -*-

import re,urllib,urlparse
from resources.lib.modules import client
from resources.lib.modules import cleantitle

class source:
    def __init__(self):
        self.domains = ['sorozatkatalogus.cc']
        self.base_link = 'http://sorozatkatalogus.cc'
        self.search_link = '/wp-admin/admin-ajax.php'

    def tvshow(self, imdb, tvdb, tvshowtitle, year):
        try:
            query = urlparse.urljoin(self.base_link, self.search_link)
            post = urllib.urlencode({'action': 'ajaxsearchlite_search', 'aslp': tvshowtitle, 'asid': '1', 'options': 'qtranslate_lang=0&set_exactonly=checked&set_intitle=None&set_incontent=None&set_inposts=None&categoryset%5B%5D=2&categoryset%5B%5D=43&categoryset%5B%5D=160&categoryset%5B%5D=3&categoryset%5B%5D=157&categoryset%5B%5D=4&categoryset%5B%5D=44&categoryset%5B%5D=5&categoryset%5B%5D=6&categoryset%5B%5D=7&categoryset%5B%5D=8&categoryset%5B%5D=9&categoryset%5B%5D=10&categoryset%5B%5D=11&categoryset%5B%5D=12&categoryset%5B%5D=13&categoryset%5B%5D=81&categoryset%5B%5D=15&categoryset%5B%5D=14&categoryset%5B%5D=16'})
            r = client.request(query, post=post)
            
            result = client.parseDOM(r, 'div', attrs={'class': 'asl_content'})
            if len(result) == 0: raise Exception()
            
            for i in result:
                try:
                    titles = []
                    try:
                        title = re.search('desc">\n.+?:\s*([^\n]+)', i).group(1)
                        title = client.replaceHTMLCodes(title)
                        title = title.encode('utf-8')
                        title = title.replace('\xc2\xa0', '')
                    except:
                        title = '0'
                    if not title == '0': titles.append(title)
                    
                    try: title2 = re.search('\(([^\)]+)', title).group(1)
                    except: title2 = '0'
                    if not title2 == '0': titles.append(title2)
                    
                    try:
                        title3 = client.parseDOM(i, 'a', attrs={'class': 'asl_res_url'})[0]
                        title3 = re.sub('(<.+>)', '', title3).strip()
                    except:
                        title3 = '0'
                    if not title3 == '0': titles.append(title3)
                    
                    try: title4 = re.search('\(([^\)]+)', title3).group(1)
                    except: title4 = '0'
                    if not title4 == '0': titles.append(title4)

                    t = cleantitle.get(tvshowtitle)
                    for c in titles: 
                        if cleantitle.get(c) == t: url = client.parseDOM(i, 'a', ret='href')[0] ; break
                except:
                    pass
            return url
        except:
            return


    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if url == None: return
            
            r = client.request(url)
            try: r = r.decode('iso-8859-1').encode('utf8')
            except: pass

            result = client.parseDOM(r, 'div', attrs={'class': 'su-box su-box-style-default'})
            result = [(client.parseDOM(i, 'div', attrs={'class': 'su-box-title'})[0].strip(), i) for i in result]
            result = [i for i in result if u'\xc3\xa9vad' in i[0]]
            result = [i[1] for i in result if re.findall('\d+', i[0])[0] == season]
            if not len(result) == 1: raise Exception()
            
            episodes = client.parseDOM(result[0], 'tr')
            episodes = [(client.parseDOM(i, 'span')[0], i) for i in episodes]
            episodes = [i[1] for i in episodes if re.findall('\d+', i[0])[0] == episode]
            if not len(episodes) == 1: raise Exception()
            
            url = client.parseDOM(episodes[0], 'a', ret='href')[0]
            return url
        except:
            return


    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            
            if url == None: return sources
            
            r = client.request(url)
            try: r = r.decode('iso-8859-1').encode('utf8')
            except: pass
            
            result = client.parseDOM(r, 'div', attrs={'class': 'entry-content'})[0]
            result = client.parseDOM(result, 'td')
            if len(result) == 0: raise Exception() 
            
            locDict = [(i.rsplit('.', 1)[0], i) for i in hostDict]
            host_corr = ['flashx', 'vidto']
            
            for item in result:
                try:
                    l = client.parseDOM(item, 'img', ret='src')[0]
                    l = l.rsplit('/', 1)[1].split('.')[0].strip()
                    host = ''.join(c for c in l if c.islower())
                    try: host = [i for i in host_corr if i in host][0]
                    except: pass
                    host = [x[1] for x in locDict if host == x[0]][0]
                    if not host in hostDict: raise Exception()
                    host = host.encode('utf-8')
                    url = client.parseDOM(item, 'a', ret='href')[0]
                    url = url.encode('utf-8')
                    if l[0] == 'H' or l[0].islower(): lang = 'szinkron'
                    else: lang = ''
                    sources.append({'source': host, 'quality': 'SD', 'lang': lang, 'provider': 'Sorozatkatalogus', 'url': url, 'direct': False, 'debridonly': False})
                except:
                    pass
            return sources
        except:
            return sources


    def resolve(self, url):
        try:
            url = url.split('//')[-1]
            r = client.request('http://' + url)
            result = client.parseDOM(r, 'div', attrs={'class': 'entry-content'})[0]
            result = client.parseDOM(result, 'p')[0].lower()
            url = client.parseDOM(result, 'iframe', ret='src')[0]
            url = client.replaceHTMLCodes(url)
            url = url.encode('utf-8')
            return url
        except:
            return
