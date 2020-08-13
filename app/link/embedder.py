import requests
from bs4 import BeautifulSoup


def get_description(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text)
    metas = soup.find_all('meta')
    description = [meta.attrs['content'] for meta in metas if 'name' in meta.attrs and meta.attrs['name'] == 'description' ]
    title = soup.find('title').string
    return {'title':title, 'description':description}
