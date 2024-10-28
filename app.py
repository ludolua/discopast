from flask import Flask, redirect, render_template, request, session, url_for
from flask_session import Session
import sqlite3
import spotipy
from spotipy.oauth2 import SpotifyOAuth

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'
app.config['SESSION_COOKIE_NAME'] = 'flask_spotify_app'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

sp_oauth = SpotifyOAuth(
    client_id='',
    client_secret='',
    redirect_uri='http://localhost:5000/callback',
    scope="user-library-read"
)

def init_db():
    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS collection 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, artist TEXT, release_date TEXT, cover_url TEXT)''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/callback')
def callback():
    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session['token_info'] = token_info
    return redirect(url_for('home'))

@app.route('/home')
def home():
    token_info = session.get('token_info', None)
    if not token_info:
        return redirect(url_for('login'))
    sp = spotipy.Spotify(auth=token_info['access_token'])
    current_user = sp.current_user()
    return render_template('home.html', user=current_user)

@app.route('/add_album/<album_id>')
def add_album(album_id):
    token_info = session.get('token_info', None)
    if not token_info:
        return redirect(url_for('login'))
    sp = spotipy.Spotify(auth=token_info['access_token'])
    album = sp.album(album_id)
    title = album['name']
    artist = album['artists'][0]['name']
    release_date = album['release_date']
    cover_url = album['images'][0]['url']
    
    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()
    c.execute("INSERT INTO collection (title, artist, release_date, cover_url) VALUES (?, ?, ?, ?)",
              (title, artist, release_date, cover_url))
    conn.commit()
    conn.close()
    
    return redirect(url_for('collection'))

@app.route('/collection')
def collection():
    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()
    c.execute("SELECT * FROM collection")
    albums = c.fetchall()
    conn.close()
    return render_template('collection.html', albums=albums)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)

@app.route('/search', methods=['GET', 'POST'])
def search():
    token_info = session.get('token_info', None)
    if not token_info:
        return redirect(url_for('login'))
    
    albums = []
    if request.method == 'POST':
        query = request.form.get('query')
        sp = spotipy.Spotify(auth=token_info['access_token'])
        results = sp.search(q=query, type='album', limit=10)
        albums = results['albums']['items']
    
    return render_template('search.html', albums=albums)


@app.route('/search', methods=['GET', 'POST'])
def search():
    token_info = session.get('token_info', None)
    if not token_info:
        return redirect(url_for('login'))
    
    albums = []
    if request.method == 'POST':
        query = request.form.get('query')
        sp = spotipy.Spotify(auth=token_info['access_token'])
        results = sp.search(q=query, type='album', limit=10)
        albums = results['albums']['items']
    
    return render_template('search.html', albums=albums)

@app.route('/add_album/<album_id>')
def add_album(album_id):
    token_info = session.get('token_info', None)
    if not token_info:
        return redirect(url_for('login'))
    sp = spotipy.Spotify(auth=token_info['access_token'])
    album = sp.album(album_id)
    title = album['name']
    artist = album['artists'][0]['name']
    release_date = album['release_date']
    cover_url = album['images'][0]['url']
    
    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()
    c.execute("INSERT INTO collection (title, artist, release_date, cover_url) VALUES (?, ?, ?, ?)",
              (title, artist, release_date, cover_url))
    conn.commit()
    conn.close()
    
    return redirect(url_for('collection'))
