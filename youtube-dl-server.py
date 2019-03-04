from __future__ import unicode_literals
import json
import os
import subprocess
from queue import Queue
from bottle import route, run, Bottle, request, static_file, template, jinja2_view
from threading import Thread
import youtube_dl
from pathlib import Path
from collections import ChainMap
import urllib.request
import urllib
from bs4 import BeautifulSoup
import pprint
import urllib
import json

app = Bottle()


app_defaults = {
    'YDL_FORMAT': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',
    'YDL_EXTRACT_AUDIO_FORMAT': None,
    'YDL_EXTRACT_AUDIO_QUALITY': '192',
    'YDL_RECODE_VIDEO_FORMAT': None,
    'YDL_OUTPUT_TEMPLATE': '/youtube-dl/%(title)s [%(id)s].%(ext)s',
    'YDL_ARCHIVE_FILE': None,
    'YDL_SERVER_HOST': '0.0.0.0',
    'YDL_SERVER_PORT': 8080,
}


def grab_title(id):
    try:
        params = {"format": "json", "url": "https://www.youtube.com/watch?v={}".format(id)}
        url = "https://www.youtube.com/oembed"
        query_string = urllib.parse.urlencode(params)
        url = url + "?" + query_string
        with urllib.request.urlopen(url) as response:
            response_text = response.read()
            data = json.loads(response_text.decode())
            return(data['title'])
    except:
        return('channel')

@app.route('/youtube-dl')
def dl_queue_list():
    return static_file('index.html', root='./')


@app.route('/youtube-dl/static/:filename#.*#')
def server_static(filename):
    return static_file(filename, root='./static')


@app.route('/youtube-dl/q', method='GET')
def q_size():
    return {"success": True, "size": json.dumps(list(dl_q.queue))}


@app.route('/youtube-dl/q', method='POST')
def q_put():
    url = request.forms.get("url")
    options = {
        'format': request.forms.get("format")
    }

    if not url:
        return {"success": False, "error": "/q called without a 'url' query param"}

    dl_q.put((url, options))
    print("Added url " + url + " to the download queue")
    return {"success": True, "url": url, "options": options}

@app.route('/youtube-dl/search', method='GET')
def q_size():
    return {"success": True, "size": json.dumps(list(dl_q.queue))}


@app.route('/youtube-dl/search', method='POST')
@jinja2_view('search_page.html')
def yt_search():
    textToSearch = request.forms.get("search")
    req_format = request.forms.get("s_format")
    textToSearch = textToSearch.encode(encoding='UTF-8',errors='strict')
    query = urllib.parse.quote(textToSearch)
    url = "https://www.youtube.com/results?search_query=" + query
    response = urllib.request.urlopen(url)
    html = response.read()
    soup = BeautifulSoup(html, 'html.parser')
    title_list = []
    s_list = []
    img_url = []
    for vid in soup.findAll(attrs={'class':'yt-uix-tile-link'}):
        title_list.append(grab_title(vid['href'][9:]))
        s_list.append('https://www.youtube.com' + vid['href'])
        img_url.append('https://img.youtube.com/vi/{}/hqdefault.jpg'.format(vid['href'][9:]))

    button_code = []
    for i in range(len(s_list)):
        button_code.append([i,s_list[i],req_format])
    cards = []
    for i in range(len(s_list)):
        cards.append([img_url[i],title_list[i],i])

    return {'button_code':button_code,'cards':cards}
    
'''
@app.route('/youtube-dl/search', method='POST')
def yt_search():
    textToSearch = request.forms.get("search")
    req_format = request.forms.get("s_format")
    textToSearch = textToSearch.encode(encoding='UTF-8',errors='strict')
    query = urllib.parse.quote(textToSearch)
    url = "https://www.youtube.com/results?search_query=" + query
    response = urllib.request.urlopen(url)
    html = response.read()
    soup = BeautifulSoup(html, 'html.parser')
    title_list = []
    s_list = []
    img_url = []
    for vid in soup.findAll(attrs={'class':'yt-uix-tile-link'}):
        title_list.append(grab_title(vid['href'][9:]))
        s_list.append('https://www.youtube.com' + vid['href'])
        img_url.append('https://img.youtube.com/vi/{}/hqdefault.jpg'.format(vid['href'][9:]))

    button_code = []
    for i in range(len(s_list)):
        button_code.append([i,s_list[i],req_format])
    cards = []
    for i in range(len(s_list)):
        cards.append([img_url[i],title_list[i],i])

    output = template('search_page',cards = cards,button_code = button_code)

    return output
'''


def dl_worker():
    while not done:
        url, options = dl_q.get()
        download(url, options)
        dl_q.task_done()


def get_ydl_options(request_options):
    request_vars = {
        'YDL_EXTRACT_AUDIO_FORMAT': None,
        'YDL_RECODE_VIDEO_FORMAT': None,
    }

    requested_format = request_options.get('format', 'bestvideo')

    if requested_format in ['aac', 'flac', 'mp3', 'm4a', 'opus', 'vorbis', 'wav']:
        request_vars['YDL_EXTRACT_AUDIO_FORMAT'] = requested_format
    elif requested_format == 'bestaudio':
        request_vars['YDL_EXTRACT_AUDIO_FORMAT'] = 'best'
    elif requested_format in ['mp4', 'flv', 'webm', 'ogg', 'mkv', 'avi']:
        request_vars['YDL_RECODE_VIDEO_FORMAT'] = requested_format

    ydl_vars = ChainMap(request_vars, os.environ, app_defaults)

    postprocessors = []

    if(ydl_vars['YDL_EXTRACT_AUDIO_FORMAT']):
        postprocessors.append({
            'key': 'FFmpegExtractAudio',
            'preferredcodec': ydl_vars['YDL_EXTRACT_AUDIO_FORMAT'],
            'preferredquality': ydl_vars['YDL_EXTRACT_AUDIO_QUALITY'],
        })

    if(ydl_vars['YDL_RECODE_VIDEO_FORMAT']):
        postprocessors.append({
            'key': 'FFmpegVideoConvertor',
            'preferedformat': ydl_vars['YDL_RECODE_VIDEO_FORMAT'],
        })

    return {
        'format': ydl_vars['YDL_FORMAT'],
        'postprocessors': postprocessors,
        'outtmpl': ydl_vars['YDL_OUTPUT_TEMPLATE'],
        'download_archive': ydl_vars['YDL_ARCHIVE_FILE']
    }


def download(url, request_options):
    with youtube_dl.YoutubeDL(get_ydl_options(request_options)) as ydl:
        ydl.download([url])


dl_q = Queue()
done = False
dl_thread = Thread(target=dl_worker)
dl_thread.start()

print("Started download thread")

app_vars = ChainMap(os.environ, app_defaults)

app.run(host=app_vars['YDL_SERVER_HOST'], port=app_vars['YDL_SERVER_PORT'], debug=True)
done = True
dl_thread.join()
