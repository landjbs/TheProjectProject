import re
import requests
from bs4 import BeautifulSoup


def scrape(url, timeout=2):
    response = requests.get(url, timeout=timeout)
    soup = BeautifulSoup(response.text, 'html.parser')
    metas = soup.find_all('meta')
    text = [meta.attrs['content'] for meta in metas if 'name' in meta.attrs and meta.attrs['name'] == 'description' ]
    text = text[0] if len(text)>0 else None
    # get text if no description
    # if not text:
    #     # kill all script and style elements
    #     for script in soup(["script", "style"]):
    #         script.extract()
    #     # get text
    #     text = soup.get_text()
    #     # break into lines and remove leading and trailing space on each
    #     lines = (line.strip() for line in text.splitlines())
    #     # break multi-headlines into a line each
    #     chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    #     # drop blank lines
    #     text = ('\n'.join(chunk for chunk in chunks if chunk)).encode('utf-8')
    #     print(text)
    description = text[:min(len(text), 1000)] if text else None
    return {'description':description}
