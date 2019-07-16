from apiclient.discovery import build
import urllib.parse as urlparse


url_data = urlparse.urlparse("https://www.youtube.com/watch?v=sEAWam8NnvA")
query = urlparse.parse_qs(url_data.query)
id = query["v"][0]
print('Video id = ' + id)

DEVELOPER_KEY = 'AIzaSyDDh4akmSBgNntLYpc4gJIe3u8kP5lzZLU'
youtube = build('youtube', 'v3', developerKey=DEVELOPER_KEY)


results = youtube.videos().list(id=id, part='snippet').execute()
print(len(results))

for result in results.get('items', []):
    print('ID = ' + result['id'])
    print('Title = ' + result['snippet']['title'].lower())