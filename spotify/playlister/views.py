from django.shortcuts import render, redirect
from .models import TodoItem
from django.views.decorators.http import require_POST
from django.conf import settings
from .utils import driver
import requests
from django.conf import settings
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

def index(request):
    todo_list = TodoItem.objects.order_by('id')
    return render(request, 'playlister/index.html', {'todo_list': todo_list})

def generate_image(request, playlist_id):
    try:
        # Get a fresh token
        access_token = SpotifyTokenManager.get_token(request)

        headers = {
            'Authorization': f'Bearer {access_token}',
        }

        # Fetch the specific playlist
        response = requests.get(f'https://api.spotify.com/v1/playlists/{playlist_id}', headers=headers)
        
        if response.status_code == 401:  # Unauthorized, token might be expired
            # Force refresh the token
            access_token = SpotifyTokenManager.refresh_token(request)
            headers['Authorization'] = f'Bearer {access_token}'
            # Retry the request
            response = requests.get(f'https://api.spotify.com/v1/playlists/{playlist_id}', headers=headers)

        if response.status_code == 200:
            playlist = response.json()
            playlist_name = playlist['name']
            
            ## DEBUG CODE
            prompt, image_url = driver(playlist_id)  # Call the driver function to get the image URL
            # prompt = "cool awesome image that's really cool and abstract and minimalist and stuff"
            # image_url = ""
            
            return render(request, 'playlister/display_image.html', {
                'playlist_id': playlist_id,
                'playlist_name': playlist_name,
                'prompt': prompt,
                'image_url': image_url
            })
        else:
            error_message = f"Failed to fetch playlist: {response.status_code} {response.text}"
            return render(request, 'playlister/error.html', {'error': error_message})
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        return render(request, 'playlister/error.html', {'error': error_message})


## SPOTIFY --------------------------------------------

def spotify_auth(request):
    client_id = settings.SPOTIFY_CLIENT_ID
    redirect_uri = 'http://127.0.0.1:8081/callback'  # Updated to match your server
    scope = 'playlist-read-private playlist-read-collaborative'

    print(f"Redirect URI: {redirect_uri}")  # For debugging

    auth_url = 'https://accounts.spotify.com/authorize?' + urllib.parse.urlencode({
        'response_type': 'code',
        'client_id': client_id,
        'scope': scope,
        'redirect_uri': redirect_uri,
    })

    return redirect(auth_url)

def spotify_callback(request):
    code = request.GET.get('code')
    
    if not code:
        return HttpResponse("Authorization failed: No code received")

    client_id = settings.SPOTIFY_CLIENT_ID
    client_secret = settings.SPOTIFY_CLIENT_SECRET
    redirect_uri = 'http://127.0.0.1:8081/callback'  # Updated to match your server

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

    return HttpResponse("Authorization successful! Tokens have been saved.")

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

def get_playlists(request):
    try:
        # Get a fresh token
        access_token = SpotifyTokenManager.get_token(request)

        headers = {
            'Authorization': f'Bearer {access_token}',
        }

        response = requests.get('https://api.spotify.com/v1/me/playlists', headers=headers)
        
        if response.status_code == 401:  # Unauthorized, token might be expired
            # Force refresh the token
            access_token = SpotifyTokenManager.refresh_token(request)
            headers['Authorization'] = f'Bearer {access_token}'
            # Retry the request
            response = requests.get('https://api.spotify.com/v1/me/playlists', headers=headers)

        if response.status_code == 200:
            playlists = response.json()['items']
            return render(request, 'playlister/playlists.html', {'playlists': playlists})
        else:
            error_message = f"Failed to fetch playlists: {response.status_code} {response.text}"
            return render(request, 'playlister/playlists.html', {'error': error_message})
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        return render(request, 'playlister/playlists.html', {'error': error_message})