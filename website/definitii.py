from website.credentials import crede as cr
import random, os, requests, string, psycopg2
from io import BytesIO
from flask import send_file, session, request, redirect
import yt_dlp
save_path = "website/output"



db = "site"
def get_db():
    conn = psycopg2.connect(database=cr["d"], host=cr["h"], user=cr["u"], password=cr["pss"], port=cr["p"])
    return conn


def shorten():
    conn = get_db()
    cur = conn.cursor()
    letters = string.ascii_lowercase + string.ascii_uppercase + string.digits
    while True:
        rand_letters = random.choices(letters, k=6)
        rand_letters = "".join(rand_letters)
        short_url = cur.execute(f"SELECT short from {db} WHERE short=%s", [f"{rand_letters}"])
        if not short_url:
            return rand_letters

def addlink(url, shorturl):
    conn = get_db()
    cur = conn.cursor()
    postgres_insert_query = f""" INSERT INTO {db} (long, short) VALUES (%s,%s)"""
    record_to_insert = (f'{url}', f'{shorturl}')
    cur.execute(postgres_insert_query, record_to_insert)
    conn.commit()
    short_url = shorturl
    return short_url

def verifica(url):
    conn = get_db()
    cur = conn.cursor()
    short_url=""
    try:
        cur.execute(f"SELECT short from {db} WHERE long=%s", [f"{url}"])
        short_url = cur.fetchone()[0]
        print(f"Short Gasit:{short_url}")
        return short_url
    except TypeError as e:
        print("Facem alt Short")
    if short_url == "":
        return short_url
    else:
        print(f"Short Gasit:{short_url}")
    return short_url


def downloadfile(name,url,dest_folder):
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)
    name=name+".mp4"
    r=requests.get(url)
    with open(f"/website/output/{name}",'wb') as f:
        for chunk in r.iter_content(chunk_size=255):
            if chunk:
                f.write(chunk)


def checklongandshort(short_url):
    conn = get_db()
    cur = conn.cursor()
    long1 = ""
    try:
        cur.execute(f"SELECT long from {db} WHERE short=%s", [f"{short_url}"])
        long1 = cur.fetchone()[0]
        cur.execute(f'SELECT clicks FROM {db}'
                                ' WHERE short = %s', (f"{short_url}",))
        clicks = cur.fetchone()[0]
        cur.execute(f'UPDATE {db} SET clicks = %s WHERE short = %s',
                     (clicks+1, short_url))
        conn.commit()
        return long1
    except:
        print("Long-ul nu a fost gasit! error.html")
    cur.close()
    conn.close()
    if long1 == "":
        long1 = "https://radu.ovh/8atYP"
    else:
        return long1
    return long1

def mp4(link):
    ydl_opts = {
            'outtmpl':save_path + '/radu.ovh-YT-id-%(id)s.%(ext)s',
            'format':'mp4'}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([link])
        meta = ydl.extract_info(
        f'{link}', download=False)
        nume = f"radu.ovh-YT-id-{meta['id']}"
    return nume

def mp3(link):
    ydl_opts = {
            'outtmpl':save_path + '/radu.ovh-YT-id-%(id)s.%(ext)s',
            'format':'bestaudio',
             'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320',
                                }]}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([link])
        meta = ydl.extract_info(
        f'{link}', download=False)
        nume = f"radu.ovh-YT-id-{meta['id']}"
    return nume