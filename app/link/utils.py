import re
import requests
# TODO: consider switching to HTTPConnection as per https://stackoverflow.com/questions/16778435/python-check-if-website-exists for head requests
# from http.client import HTTPConnection


# matcher for valid route protocol
url_string = r'https://\S+|http://\S+'
url_matcher = re.compile(url_string)

def parsable(url:str):
    ''' Deterimines if url has valid protocol '''
    return True if url_matcher.fullmatch(url) else False

def valid(url:str, timeout:int=2):
    ''' Determines if url is valid by requesting head '''
    try:
        request = requests.get(url)
        return (request.status_code==200)
    except Exception as e:
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
    print(url)
    # try connecting to url to validate
    return (url if valid(url) else False)
