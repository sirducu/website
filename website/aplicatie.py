from flask import Flask, render_template, request, Blueprint
from flask import redirect, url_for, send_file
import psycopg2, yt_dlp
from website.credentials import crede as cr
from website.definitii import shorten, get_db, addlink, verifica, db, downloadfile, checklongandshort
from website.definitii import save_path, mp3, mp4
from requests import post
from io import BytesIO
import time


DOMAIN = "https://radu.ovh/"
apiUrl = "https://lovetik.com/api/ajax/search"


views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@views.route('/short', methods=('GET', 'POST'))
def short():
    conn = get_db()
    cur = conn.cursor()
    if request.method == 'POST':
        url = request.form['shrt'] 
        if "http://" in url or "https://" in url:
            url = url
        else:
            url = f"https://{url}"
        short_url = verifica(url)
        if short_url:
            return render_template('shorturl.html', short_url=short_url)
        else:
            short_url = shorten()
            print(f"url={url}, shrt={short_url}")
            addlink(url, short_url)
            cur.close()
            conn.close()
            return render_template('shorturl.html', short_url=short_url)
    return render_template('short.html')


@views.route('/stats')
def stats():
    conn = get_db()
    cur = conn.cursor()
    cur.execute(f'SELECT id, long, short, clicks FROM {db} order by id')
    db_urls1 = cur.fetchall()
    urls = []
    for url in db_urls1:
        urls.append(url)
    conn.close()
    return render_template('stats.html', urls=urls)

@views.route("/api/short", methods=["GET", "POST"])
def apilong():
    conn = get_db()
    if request.method == "GET":
        url_long = request.args["URL"]
        if "http://" not in url_long and "https://" not in url_long:
            url_long = f"https://{url_long}"
        short_url = verifica(url_long)
        if short_url == "":
            short_url = shorten()
            addlink(url_long, short_url)
            conn.close()
            link = {
        "ShortURL" : f"{DOMAIN}{short_url}",
        "LongUrl" : url_long
                }
        else:
            link = {
        "ShortURL" : f"{DOMAIN}{short_url}",
        "LongUrl" : url_long
                }
        return link

@views.route('/tiktok', methods=['GET', 'POST'])
def tiktok():
    if request.method == "POST":
        url = request.form['tikurl']
        req = post(apiUrl,
            data = {
            "query": url
            },
            headers = {
            "Origin": 'https://ducu.ovh/',
            "Referer": 'https://ducu.ovh/',
            })
        desc = req.json()['desc']
        dllink = req.json()["links"][0]["a"]
        downloadfile(f"{desc}",dllink,'output')
        return send_file(f"{save_path}/{desc}.mp4", as_attachment=True)
    return render_template('tiktok.html')

@views.route('/youtube', methods=['GET', 'POST'])
def youtub3():
    if request.method == "POST":
        if request.form['action'] == 'mp4':
            link = request.form['yturl']
            nume = mp4(link)
            return send_file(f"{save_path}/{nume}.mp4", as_attachment=True)
        if request.form['action'] == 'mp3':
            link = request.form['yturl']
            nume = mp3(link)
            return send_file(f"{save_path}/{nume}.mp3", as_attachment=True)
    return render_template("youtube.html")

@views.route('/facebook', methods=['GET', 'POST'])
def facebook():
    if request.method == "POST":
        link = request.form.get('flink')
        ydl_opts = {
            'outtmpl':save_path + '/%(id)s.%(ext)s',
            'format':'mp4'}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([link])
            meta = ydl.extract_info(
        f'{link}', download=False)
            nume = meta['id']
            print(nume)
            time.sleep(3)
        return send_file(f"{save_path}/{nume}.mp4", as_attachment=True)
    return render_template("facebook.html")


@views.route('/api', methods=['GET'])
def apihtml():
    return render_template("api.html")


@views.route('/<short_url>')
def redirection(short_url):
    long1 = checklongandshort(short_url)
    if long1:
        return redirect(long1)
    else:
        return render_template("error.html")

@views.route('/error', methods=('GET', 'POST'))
def error():
    return render_template("error.html")
