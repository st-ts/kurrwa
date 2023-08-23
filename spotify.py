import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Set your Spotify credentials and redirect URI
client_id = 'afbfbcc551db4d07a20280c475576e62'
client_secret = '101c9a2e38dd43319bd70ca73043d5b8'
redirect_uri = 'http://localhost:8888/callback'

# Initialize Spotify authentication with refresh token flow
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id, client_secret, redirect_uri, scope='user-modify-playback-state', cache_path='.cache'))

# Now you can use the 'sp' instance to interact with the Spotify Web API
track_uri = 'spotify:track:49eccJME4fYJnOwCmJMXfV' 
sp.start_playback(uris=[track_uri])
