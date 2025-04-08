import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# Pull variables from environment
SPOTIPY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
SPOTIPY_REDIRECT_URI = os.getenv("SPOTIPY_REDIRECT_URI")

scope = "user-read-playback-state user-modify-playback-state user-read-currently-playing"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET,
    redirect_uri=SPOTIPY_REDIRECT_URI,
    scope=scope
))

# Example call to get current song
current = sp.current_playback()

if current and current['is_playing']:
    track = current['item']
    artists = ', '.join([artist['name'] for artist in track['artists']])
    print(f"Now playing: {track['name']} by {artists}")
    print(f"Album: {track['album']['name']}")
    print(f"Link: {track['external_urls']['spotify']}")
    print(f"Duration: {track['duration_ms'] // 1000} sec")
    print(f"Volume: {current['device']['volume_percent']}%")
    print(f"Progress: {current['progress_ms'] // 1000}s")
else:
    print("Nothing is currently playing.")