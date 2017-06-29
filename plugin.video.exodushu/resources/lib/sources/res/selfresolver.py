
def resolve(u, host):
    try:
        if 'thevideo' in host: import thevideo as resolver

        #elif 'openload' in host: import openload as resolver

        url = resolver.get_media_url(u)
        return url
    except:
        return
