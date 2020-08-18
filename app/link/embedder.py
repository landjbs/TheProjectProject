import requests
from bs4 import BeautifulSoup

## matcher for valid url ##



def scrape(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text)
    metas = soup.find_all('meta')
    description = [meta.attrs['content'] for meta in metas if 'name' in meta.attrs and meta.attrs['name'] == 'description' ]
    description = description[0] if len(description)>0 else None
    return {'description':description}
