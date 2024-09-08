import requests
import os
from PIL import Image
import requests
import base64
import urllib.parse

from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from django.conf import settings
from django.core.cache import cache
from django.shortcuts import redirect
from django.http import HttpResponse
from django.urls import reverse
from django.contrib.auth import logout as auth_logout
from django.shortcuts import redirect
from django.contrib import messages


class SpotifyTokenManager:
    @staticmethod
    def get_token(request):
        # Try to get the token from cache
        access_token = cache.get('spotify_access_token')
        if access_token:
            return access_token
        
        # If not in cache, refresh the token
        return SpotifyTokenManager.refresh_token(request)

    @staticmethod
    def refresh_token(request):
        token_url = "https://accounts.spotify.com/api/token"
        refresh_token = request.session.get('spotify_refresh_token')
        client_id = settings.SPOTIFY_CLIENT_ID
        client_secret = settings.SPOTIFY_CLIENT_SECRET

        if not refresh_token:
            raise Exception("No refresh token available")

        client_creds = f"{client_id}:{client_secret}"
        client_creds_b64 = base64.b64encode(client_creds.encode()).decode()

        headers = {
            "Authorization": f"Basic {client_creds_b64}"
        }

        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        }

        response = requests.post(token_url, headers=headers, data=data)
        
        if response.status_code == 200:
            token_info = response.json()
            access_token = token_info['access_token']
            expires_in = token_info['expires_in']

            # Cache the new token
            cache.set('spotify_access_token', access_token, expires_in - 300)  # Cache for token lifetime minus 5 minutes

            # Update the session with the new access token
            request.session['spotify_access_token'] = access_token

            # If a new refresh token is provided, update it in the session
            if 'refresh_token' in token_info:
                request.session['spotify_refresh_token'] = token_info['refresh_token']

            return access_token
        else:
            raise Exception("Failed to refresh access token")

def spotify_auth(request):
    client_id = settings.SPOTIFY_CLIENT_ID
    redirect_uri = 'http://127.0.0.1:8081/callback'  
    # redirect_uri = 'http://18.117.227.7:8000/callback'  
    # redirect_uri = 'http://3.145.113.169:8000/callback'  
    scope = 'playlist-read-private playlist-read-collaborative'

    print(f"Redirect URI: {redirect_uri}")  # For debugging

    auth_url = 'https://accounts.spotify.com/authorize?' + urllib.parse.urlencode({
        'response_type': 'code',
        'client_id': client_id,
        'scope': scope,
        'redirect_uri': redirect_uri,
        'show_dialog': 'true' 
    })

    return redirect(auth_url)

def spotify_callback(request):
    code = request.GET.get('code')
    
    if not code:
        return HttpResponse("Authorization failed: No code received")

    client_id = settings.SPOTIFY_CLIENT_ID
    client_secret = settings.SPOTIFY_CLIENT_SECRET
    redirect_uri = 'http://127.0.0.1:8081/callback'  
    # redirect_uri = 'http://18.117.227.7:8000/callback'  
    # redirect_uri = 'http://3.145.113.169:8000/callback'  

    print(f"Callback Redirect URI: {redirect_uri}")  # For debugging

    token_url = 'https://accounts.spotify.com/api/token'
    authorization = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()

    headers = {
        'Authorization': f'Basic {authorization}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': redirect_uri
    }

    response = requests.post(token_url, headers=headers, data=data)
    token_info = response.json()

    print(f"Token Info: {token_info}")  # For debugging

    if 'error' in token_info:
        return HttpResponse(f"Error: {token_info['error']}")

    access_token = token_info.get('access_token')
    refresh_token = token_info.get('refresh_token')

    if not access_token or not refresh_token:
        return HttpResponse("Failed to obtain tokens")

    request.session['spotify_access_token'] = access_token
    request.session['spotify_refresh_token'] = refresh_token

    print(f"Session after storing tokens: {dict(request.session)}")  # For debugging

    print("Authorization successful! Tokens have been saved.")
    return redirect('playlists')

# USING CLIENT AUTH AKA BAD 
# ---------------------------------------------------------------------
# Spotify
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
    
# Authentication
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
# ---------------------------------------------------------------------

def get_auth_header(token):
    return {"Authorization": "Bearer " + token}

def get_playlist_response(request, playlist_id):
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
    access_token = SpotifyTokenManager.get_token(request)

    headers = {
        'Authorization': f'Bearer {access_token}',
    }
    
    return headers


def spotify_logout(request):
    # Clear Spotify-related session data
    keys_to_remove = ['spotify_access_token', 'spotify_refresh_token', 'last_spotify_auth_time']
    for key in keys_to_remove:
        request.session.pop(key, None)
    return redirect('playlists')  # Redirect to the playlists page, which will now show the login prompt