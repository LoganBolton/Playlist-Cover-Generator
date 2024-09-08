import requests
import base64
import os
import anthropic
import base64
from anthropic import Anthropic
from PIL import Image
import replicate
import requests
from statistics import mean 

from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from django.conf import settings
import requests
import requests
import base64
from django.core.cache import cache

from django.conf import settings
from django.shortcuts import redirect
from django.http import HttpResponse
from django.urls import reverse
import requests
import base64
import urllib.parse

from .controllers import claude
from .controllers import spotify_auth

# class SpotifyTokenManager:
#     @staticmethod
#     def get_token(request):
#         # Try to get the token from cache
#         access_token = cache.get('spotify_access_token')
#         if access_token:
#             return access_token
        
#         # If not in cache, refresh the token
#         return SpotifyTokenManager.refresh_token(request)

#     @staticmethod
#     def refresh_token(request):
#         token_url = "https://accounts.spotify.com/api/token"
#         refresh_token = request.session.get('spotify_refresh_token')
#         client_id = settings.SPOTIFY_CLIENT_ID
#         client_secret = settings.SPOTIFY_CLIENT_SECRET

#         if not refresh_token:
#             raise Exception("No refresh token available")

#         client_creds = f"{client_id}:{client_secret}"
#         client_creds_b64 = base64.b64encode(client_creds.encode()).decode()

#         headers = {
#             "Authorization": f"Basic {client_creds_b64}"
#         }

#         data = {
#             "grant_type": "refresh_token",
#             "refresh_token": refresh_token
#         }

#         response = requests.post(token_url, headers=headers, data=data)
        
#         if response.status_code == 200:
#             token_info = response.json()
#             access_token = token_info['access_token']
#             expires_in = token_info['expires_in']

#             # Cache the new token
#             cache.set('spotify_access_token', access_token, expires_in - 300)  # Cache for token lifetime minus 5 minutes

#             # Update the session with the new access token
#             request.session['spotify_access_token'] = access_token

#             # If a new refresh token is provided, update it in the session
#             if 'refresh_token' in token_info:
#                 request.session['spotify_refresh_token'] = token_info['refresh_token']

#             return access_token
#         else:
#             raise Exception("Failed to refresh access token")

# def spotify_auth(request):
#     client_id = settings.SPOTIFY_CLIENT_ID
#     redirect_uri = 'http://127.0.0.1:8081/callback'  # Updated to match your server
#     scope = 'playlist-read-private playlist-read-collaborative'

#     print(f"Redirect URI: {redirect_uri}")  # For debugging

#     auth_url = 'https://accounts.spotify.com/authorize?' + urllib.parse.urlencode({
#         'response_type': 'code',
#         'client_id': client_id,
#         'scope': scope,
#         'redirect_uri': redirect_uri,
#     })

#     return redirect(auth_url)

# def spotify_callback(request):
#     code = request.GET.get('code')
    
#     if not code:
#         return HttpResponse("Authorization failed: No code received")

#     client_id = settings.SPOTIFY_CLIENT_ID
#     client_secret = settings.SPOTIFY_CLIENT_SECRET
#     redirect_uri = 'http://127.0.0.1:8081/callback'  # Updated to match your server

#     print(f"Callback Redirect URI: {redirect_uri}")  # For debugging

#     token_url = 'https://accounts.spotify.com/api/token'
#     authorization = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()

#     headers = {
#         'Authorization': f'Basic {authorization}',
#         'Content-Type': 'application/x-www-form-urlencoded'
#     }

#     data = {
#         'grant_type': 'authorization_code',
#         'code': code,
#         'redirect_uri': redirect_uri
#     }

#     response = requests.post(token_url, headers=headers, data=data)
#     token_info = response.json()

#     print(f"Token Info: {token_info}")  # For debugging

#     if 'error' in token_info:
#         return HttpResponse(f"Error: {token_info['error']}")

#     access_token = token_info.get('access_token')
#     refresh_token = token_info.get('refresh_token')

#     if not access_token or not refresh_token:
#         return HttpResponse("Failed to obtain tokens")

#     request.session['spotify_access_token'] = access_token
#     request.session['spotify_refresh_token'] = refresh_token

#     print(f"Session after storing tokens: {dict(request.session)}")  # For debugging

#     return HttpResponse("Authorization successful! Tokens have been saved.")

# # Spotify
# def set_up_spotify():
    
#     # Replace these with your actual Client ID and Client Secret
#     CLIENT_ID = os.environ.get('SPOTIFY_CLIENT_ID')
#     CLIENT_SECRET = os.environ.get('SPOTIFY_CLIENT_SECRET')

#     client_creds = f"{CLIENT_ID}:{CLIENT_SECRET}"
#     client_creds_b64 = base64.b64encode(client_creds.encode())

#     # Token URL
#     token_url = 'https://accounts.spotify.com/api/token'

#     # Request Body Parameters
#     token_data = {
#         'grant_type': 'client_credentials'
#     }

#     # Request Headers
#     token_headers = {
#         'Authorization': f'Basic {client_creds_b64.decode()}'
#     }
    
# # Authentication
# def get_token():
#     CLIENT_ID = os.environ.get('SPOTIFY_CLIENT_ID')
#     CLIENT_SECRET = os.environ.get('SPOTIFY_CLIENT_SECRET')

#     if not CLIENT_ID or not CLIENT_SECRET:
#         print("Error: SPOTIFY_CLIENT_ID and/or SPOTIFY_CLIENT_SECRET environment variables are not set.")
#         exit(1)

#     auth_string = f"{CLIENT_ID}:{CLIENT_SECRET}"
#     auth_bytes = auth_string.encode("utf-8")
#     auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

#     url = "https://accounts.spotify.com/api/token"
#     headers = {
#         "Authorization": "Basic " + auth_base64,
#         "Content-Type": "application/x-www-form-urlencoded"
#     }
#     data = {"grant_type": "client_credentials"}
#     result = requests.post(url, headers=headers, data=data)
#     json_result = result.json()
#     token = json_result.get("access_token")

#     if not token:
#         print("Error: Could not retrieve Spotify token.")
#         exit(1)

#     return token

# def get_auth_header(token):
#     return {"Authorization": "Bearer " + token}

# # Get playlist tracks
def get_playlist_tracks(token, playlist_id):
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    headers = spotify_auth.get_auth_header(token)
    
    tracks = []
    while url:
        result = requests.get(url, headers=headers)
        json_result = result.json()
        
        for item in json_result['items']:
            track = item['track']
            tracks.append({
                'id': track['id'],
                'name': track['name'],
                'artist': track['artists'][0]['name']
            })
        
        url = json_result.get('next')  # Get the next page URL, if it exists

    return tracks

# Get audio features for tracks
def get_audio_features(token, track_ids):
    url = f"https://api.spotify.com/v1/audio-features"
    headers = spotify_auth.get_auth_header(token)
    params = {'ids': ','.join(track_ids)}
    
    result = requests.get(url, headers=headers, params=params)
    return result.json()['audio_features']

# Analyze vibe based on audio features
def analyze_vibe(features):
    valence = features['valence']
    energy = features['energy']
    danceability = features['danceability']
    tempo = features['tempo']
    
    vibe = []
    if valence > 0.6:
        vibe.append("positive")
    elif valence < 0.4:
        vibe.append("melancholic")
    
    if energy > 0.7:
        vibe.append("energetic")
    elif energy < 0.3:
        vibe.append("calm")
    
    if danceability > 0.7:
        vibe.append("danceable")
    
    if tempo > 120:
        vibe.append("upbeat")
    elif tempo < 80:
        vibe.append("slow")
    
    return ", ".join(vibe) if vibe else "neutral"

def get_playlist_details(PLAYLIST_ID):
    token = spotify_auth.get_token()
    tracks = get_playlist_tracks(token, PLAYLIST_ID)

    # Get audio features for all tracks
    track_ids = [track['id'] for track in tracks]
    # print(f"token: {token}, track_ids: {track_ids}")
    audio_features = get_audio_features(token, track_ids)
    valid_features = [f for f in audio_features if f is not None]

    # Calculate averages
    try:
        avg_valence = mean(feature['valence'] for feature in valid_features)
        avg_energy = mean(feature['energy'] for feature in valid_features)
    except:
        avg_valence = 0
        avg_energy = 0
    # print(f"Tracks in the playlist (total: {len(tracks)}):")
    playlist_description = ""

    for i, (track, features) in enumerate(zip(tracks, valid_features), 1):
        vibe = analyze_vibe(features)
        playlist_description += f"{i}. {track['name']} by {track['artist']}\n"
        playlist_description += f"   Vibe: {vibe}\n"
        playlist_description += f"   Valence: {features['valence']:.2f}, Energy: {features['energy']:.2f}\n\n"

    playlist_description += f"Playlist Averages:\n"
    playlist_description += f"Average Valence: {avg_valence:.2f}\n"
    playlist_description += f"Average Energy: {avg_energy:.2f}\n\n"

    # Analyze overall playlist vibe
    playlist_vibe = []
    if avg_valence > 0.6:
        playlist_vibe.append("positive")
    elif avg_valence < 0.4:
        playlist_vibe.append("melancholic")
    else:
        playlist_vibe.append("mix of positive and melancholic")

    if avg_energy > 0.7:
        playlist_vibe.append("high-energy")
    elif avg_energy < 0.3:
        playlist_vibe.append("low-energy")
    else:
        playlist_vibe.append("moderate energy")

    playlist_description += f"Overall Playlist Vibe: {', '.join(playlist_vibe)}"

    # Print the entire playlist description
    return playlist_description

def driver(PLAYLIST_ID):
    claude.set_up_claude()
    spotify_auth.set_up_spotify()
    
    # bossa = '6cGZkPs8wimEZBDzpVNaut'
    # jazz = '71vvwEbxgXqHZ7ONA6WGxt'
    # PLAYLIST_ID = '2djCZlngGykIYIvhRtPq39'
    playlist_description = get_playlist_details(PLAYLIST_ID)
    prompt = f"""Give me a prompt that will be able represent this playlist in a latent diffusion model. Make it minimalist and abstract but still keep it interesting. I don't want hotel art level minimalism, I want something raw and artistic. If relevant, incorporate imagery that relates to the specific songs or artists. For example, if one of the tracks was named "The Girl from Ipanema", then it would be relevant to add the Ipanema beach to the prompt. Put your description in square brackets like this [description].\n\n{playlist_description}"""
    
    convo = claude.get_conversation(prompt)
    response = claude.send_message(convo)
    description = claude.extract_description(response)
    # return description, ""

    #temporarily commented out 
    # print(description)
    # description = "really cool awesome image that's really cool and abstract and minimalist and stuff"
    output = replicate.run(
        "black-forest-labs/flux-schnell",
        input={
            "prompt": description,
            "num_outputs": 1,
            "aspect_ratio": "1:1",
            "output_format": "webp",
            "output_quality": 80
        }
    )
    # print(output)
    image_url = output[0]

    return description, image_url


def prelim_spotify(request, playlist_id):
    headers = get_headers(request)
    # Fetch the specific playlist
    response = requests.get(f'https://api.spotify.com/v1/playlists/{playlist_id}', headers=headers)
    
    if response.status_code == 401:  # Unauthorized, token might be expired
        # Force refresh the token
        access_token = spotify_auth.SpotifyTokenManager.refresh_token(request)
        headers['Authorization'] = f'Bearer {access_token}'
        # Retry the request
        response = requests.get(f'https://api.spotify.com/v1/playlists/{playlist_id}', headers=headers)
    return response 

def get_headers(request):
    access_token = spotify_auth.SpotifyTokenManager.get_token(request)

    headers = {
        'Authorization': f'Bearer {access_token}',
    }
    
    return headers