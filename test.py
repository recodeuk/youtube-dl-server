import urllib.request
from bs4 import BeautifulSoup
import json
import urllib
import pprint

def grab_title(id):
    params = {"format": "json", "url": "https://www.youtube.com/watch?v={}".format(id)}
    url = "https://www.youtube.com/oembed"
    query_string = urllib.parse.urlencode(params)
    url = url + "?" + query_string

    with urllib.request.urlopen(url) as response:
        response_text = response.read()
        data = json.loads(response_text.decode())
        return(data['title'])

def yt_search():
    textToSearch = input('enter a search query')
    query = urllib.parse.quote(textToSearch)
    url = "https://www.youtube.com/results?search_query=" + query
    response = urllib.request.urlopen(url)
    html = response.read()
    soup = BeautifulSoup(html, 'html.parser')
    s_list = []
    img_url = []
    title_list = []
    for vid in soup.findAll(attrs={'class':'yt-uix-tile-link'}):
        title_list.append(grab_title(vid['href'][9:]))
        s_list.append('https://www.youtube.com' + vid['href'])
        img_url.append('https://img.youtube.com/vi/{}/hqdefault.jpg'.format(vid['href'][9:]))
    return ({'url':s_list,'img':img_url,'title':title_list})



print(yt_search())