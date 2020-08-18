import re
import requests
from bs4 import BeautifulSoup

## validate/fix url ##
# matcher for valid route protocol
url_string = r'https://\S+|http://\S+'
url_matcher = re.compile(url_string)

def parsable(url):
    ''' Deterimines if url has valid protocol '''
    return True if url_matcher.fullmatch(url) else False


####################################


def scrape(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text)
    metas = soup.find_all('meta')
    description = [meta.attrs['content'] for meta in metas if 'name' in meta.attrs and meta.attrs['name'] == 'description' ]
    description = description[0] if len(description)>0 else None
    return {'description':description}
