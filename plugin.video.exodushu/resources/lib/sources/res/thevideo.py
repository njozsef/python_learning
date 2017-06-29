import re
import urlparse
import random
from resources.lib.modules import jsunpack
from resources.lib.modules import client


def get_media_url(url):
    try:
        path = random.choice(['jwjsv', 'jwv'])
        host, media_id = get_host_id(url)
        web_url = get_url(host, media_id)
        headers = {
            'User-Agent': client.randomagent(),
            'Referer': web_url
        }
        html = client.request(web_url, headers=headers)
        
        sources = parse_sources_list(html)

        if not sources:
            return
        else:
            js_path = re.search('(?:/|\'|")([a-z0-9A-Z+?]{24})(?:/|\'|")', html)
            if not js_path:
                return

            js_url = urlparse.urljoin('https://' + host, '%s/%s' % (path, js_path.group(1)))

            js_data = client.request(js_url, headers=headers)

            match = re.search('(eval\(function.*?)(?:$|</script>)', js_data, re.DOTALL)
            if match:
                js_data = jsunpack.unpack(match.group(1))
            
            r = re.search('vt\s*=\s*([^"]+)', js_data)
            if r:
                return '%s?direct=false&ua=1&vt=%s|User-Agent=%s' % (sources[0][1], r.group(1), client.agent())

            else:
                return
    except:
        return


def parse_sources_list(html):
    sources = []
    match = re.search('sources\s*:\s*\[(.*?)\]', html, re.DOTALL)
    if match:
        for match in re.finditer('''['"]?file['"]?\s*:\s*['"]([^'"]+)['"][^}]*['"]?label['"]?\s*:\s*['"]([^'"]*)''', match.group(1), re.DOTALL):
            stream_url, label = match.groups()
            stream_url = stream_url.replace('\/', '/')
            sources.append((label, stream_url))
    if len(sources) > 1 and sources[0][0] < sources [-1][0]:
        sources.reverse()
    return sources


def get_host_id(url):
    match = re.search('(?://|\.)(thevideo\.me)/(?:embed-|download/)?([0-9a-zA-Z]+)', url)
    return (match.group(1), match.group(2))


def get_url(host, media_id):
    return 'http://%s/embed-%s.html' % (host, media_id)
