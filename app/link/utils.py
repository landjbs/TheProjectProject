import re
from http.client import HTTPConnection


# matcher for valid route protocol
url_string = r'https://\S+|http://\S+'
url_matcher = re.compile(url_string)

def parsable(url:str):
    ''' Deterimines if url has valid protocol '''
    return True if url_matcher.fullmatch(url) else False

def valid(url:str, timeout:int=2):
    ''' Determines if url is valid by requesting head '''
    try:
        c = HTTPConnection(url, timeout=timeout)
        c.request("HEAD", '')
        return (c.getresponse().status==200)
    except Exception as e:
        print(f'ERROR: {e}')
        return False

def fix_url(url:str):
    ''' Adds proper route to url. Returns url if fixed else return False '''
    if not parsable(url):
        if url.startswith('http'):
            pass
        elif url.startswith('www'):
            url = f'https://{url}'
        else:
            url = f'https://{url}'
    # try connecting to url to validate
    return (url if valid(url) else False)
