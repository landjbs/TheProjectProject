import requests

query = {
  "url": "http://stradarouting.com/",
  "key": ":9c2832d99ae44fbeb67f5a74439af297"
}

r = requests.get('https://api.embedly.com/1/oembed', params=query)

print(r.json())



'''
a: 'url'
a-text: 'title'
text:   'description'
'''
