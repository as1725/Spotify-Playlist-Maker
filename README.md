# Spotify Playlist Maker

Spotify Playlist Maker is an open-source web application built with Flask that allows users to create and manage their Spotify playlists. Users can log in with their Spotify account, search for songs, and add them to a new or existing playlist.

## Features

- User authentication with Spotify
- Create new playlists
- Search for songs and add them to playlists
- View and manage existing playlists

## Prerequisites

- Python 3.6+
- Spotify Developer Account

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/spotify-playlist-maker.git
cd spotify-playlist-maker
```
2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

3. Install the required packages:

```bash
pip install -r requirements.txt
```

4. Create a .env file in the root directory and add your Spotify API credentials:

```env
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
SPOTIFY_REDIRECT_URI=http://localhost:5000/callback/
SECRET_KEY=your_flask_secret_key
```

## Usage

1. Run the Flask application:

```bash
python ./app.py
```

2. Open your web browser and go to http://localhost:5000.
3. Log in with your Spotify account and start creating playlists!

## Project Structure:

```bash
spotify-playlist-maker/
├── app.py              # Main application file
├── create_playlist.py  # Helper functions for playlist creation
├── templates/
│   └── index.html      # HTML template for the main page
├── static/
│   └── style.css       # CSS file for styling
├── .env                # Environment variables
├── requirements.txt    # Python dependencies
└── README.md           # This README file
```

## Code Excerpt:

Here is an excerpt from the app.py file:

```python
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
    auth_url = f"{SPOTIFY_AUTH_URL}?response_type=code&client_id={SPOTIFY_CLIENT_ID}&redirect_uri={SPOTIFY_REDIRECT_URI}&scope=playlist-modify-private"
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
```

## Contributing:
Contributions are welcome! Please open an issue or submit a pull request for any changes or improvements.

## License:
This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgements:
[Flask](https://flask.palletsprojects.com/) - The web framework used
[Spotify for Developers](https://developer.spotify.com/) - Spotify API documentation

## Contact:
For any questions or suggestions, please open an issue or contact the repository owner.
