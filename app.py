from flask import Flask, redirect, session, url_for, request, jsonify, render_template
import requests
import os
import logging

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
app.config['SESSION_COOKIE_NAME'] = 'spotify-login-session'

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_URL = "https://api.spotify.com/v1"


def get_spotify_auth_url():
    auth_url = f"{SPOTIFY_AUTH_URL}?response_type=code&client_id={
        SPOTIFY_CLIENT_ID}&redirect_uri={SPOTIFY_REDIRECT_URI}&scope=playlist-modify-private"
    return auth_url


def get_spotify_token(code):
    payload = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': SPOTIFY_REDIRECT_URI,
        'client_id': SPOTIFY_CLIENT_ID,
        'client_secret': SPOTIFY_CLIENT_SECRET
    }
    response = requests.post(SPOTIFY_TOKEN_URL, data=payload)
    return response.json()


def get_spotify_user(token):
    headers = {
        'Authorization': f"Bearer {token}"
    }
    response = requests.get(f"{SPOTIFY_API_URL}/me", headers=headers)
    if response.status_code != 200:
        logging.error(f"Failed to fetch user info: {
                      response.status_code} {response.text}")
        response.raise_for_status()
    return response.json()


@app.route('/')
def login():
    session.clear()  
    auth_url = get_spotify_auth_url()
    return redirect(auth_url)


@app.route('/callback/')
def callback():
    session.clear()
    code = request.args.get('code')
    token_info = get_spotify_token(code)
    session['token_info'] = token_info
    user_info = get_spotify_user(token_info['access_token'])
    logging.debug(f"Logged in user ID: {user_info['id']}")
    logging.debug(f"User info: {user_info}")
    return redirect(url_for('index'))


@app.route('/is_authenticated')
def is_authenticated():
    try:
        token_info = session.get('token_info', None)
        logging.debug(f"Token info: {token_info}")
        if token_info:
            user_info = get_spotify_user(token_info['access_token'])
            logging.debug(f"Authenticated user ID: {user_info['id']}")
            return jsonify({'authenticated': True, 'user_name': user_info['display_name']})
            
        return jsonify({"authenticated": token_info is not None})
    
    except Exception as e:
        logging.error(f"Error in /is_authenticated endpoint: {e}")
        return jsonify({"authenticated": False, "error": str(e)}), 500
    


@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/create_playlist', methods=['POST'])
def create_playlist():
    data = request.json
    songs = data.get('songs', [])
    playlist_name = data.get('playlistName', 'New Playlist')

    token_info = session.get('token_info')
    if not token_info:
        return jsonify({'error': 'User not authenticated'}), 401

    token = token_info['access_token']
    user = get_spotify_user(token)
    user_id = user['id']

    headers = {
        'Authorization': f"Bearer {token}",
        'Content-Type': 'application/json'
    }

    payload = {
        'name': playlist_name,
        'description': 'Created with Spotify Playlist Maker',
        'public': False
    }
    response = requests.post(
        f"{SPOTIFY_API_URL}/users/{user_id}/playlists", headers=headers, json=payload)
    if response.status_code != 201:
        logging.error(f"Failed to create playlist: {
                      response.status_code} {response.text}")
        return jsonify({'error': 'Failed to create playlist'}), response.status_code

    playlist_id = response.json()['id']

    track_uris = []
    for song in songs:
        query = f"track:{song['song']}"
        if song['artist']:
            query += f" artist:{song['artist']}"
        search_response = requests.get(
            f"{SPOTIFY_API_URL}/search", headers=headers, params={'q': query, 'type': 'track', 'limit': 1})
        if search_response.status_code == 200:
            tracks = search_response.json().get('tracks', {}).get('items', [])
            if tracks:
                track_uris.append(tracks[0]['uri'])

    if track_uris:
        add_tracks_response = requests.post(
            f"{SPOTIFY_API_URL}/playlists/{playlist_id}/tracks", headers=headers, json={'uris': track_uris})
        if add_tracks_response.status_code != 201:
            logging.error(f"Failed to add tracks to playlist: {
                          add_tracks_response.status_code} {add_tracks_response.text}")
            return jsonify({'error': 'Failed to add tracks to playlist'}), add_tracks_response.status_code

    return jsonify({'playlistUrl': f"https://open.spotify.com/playlist/{playlist_id}"}), 201


@app.route('/logout')
def logout():
    session.pop('token_info', None)
    session.clear()
    return jsonify({"message": "Logged out successfully"})


if __name__ == '__main__':
    app.run()
