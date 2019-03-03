import urllib.request
from bs4 import BeautifulSoup

def yt_search():
    textToSearch = input()
    query = urllib.parse.quote(textToSearch)
    url = "https://www.youtube.com/results?search_query=" + query
    response = urllib.request.urlopen(url)
    html = response.read()
    soup = BeautifulSoup(html, 'html.parser')
    s_list = []
    for vid in soup.findAll(attrs={'class':'yt-uix-tile-link'}):
        s_list.append('https://www.youtube.com' + vid['href'])
        
    print ({'url':s_list})

yt_search()