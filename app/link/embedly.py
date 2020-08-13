import requests

query = {
  "url": "https://www.youtube.com/watch?v=jofNR_WkoCE",
  "key": ":9c2832d99ae44fbeb67f5a74439af297"
}

r = requests.get('https://api.embedly.com/1/oembed', params=query)

print(r.json())
