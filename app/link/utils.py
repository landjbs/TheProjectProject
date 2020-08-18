import url

# matcher for valid route protocol
url_string = r'https://\S+|http://\S+'
url_matcher = re.compile(url_string)

def parsable(url:str):
    ''' Deterimines if url has valid protocol '''
    return True if url_matcher.fullmatch(url) else False

def fix_url(url:str):
    ''' Adds proper route to url '''
    if not parsable(url):
        if url.startswith('http'):
            pass
        elif url.startswith('www'):
            url = f'https://{url}'
        else:
            url = f'https://{url}'
    return url
