from django.shortcuts import render, redirect
from .models import TodoItem
from django.views.decorators.http import require_POST
from django.conf import settings
from .utils import driver
import requests
from django.conf import settings
import requests
import time

def index(request):
    todo_list = TodoItem.objects.order_by('id')
    return render(request, 'playlister/index.html', {'todo_list': todo_list})

def generate_image(request, playlist_id):
    # prompt = driver(playlist_id)  # Call the driver function to get the image URL
    prompt = "testing debug prompt mmmm I love prompting language models with dynamic data mmmm " + playlist_id 
    image_url = ""
    # return render(request, 'playlister/display_image.html', {'image_url': image_url})
    return render(request, 'playlister/display_image.html', {'playlist_id': playlist_id, 'prompt': prompt, 'image_url': image_url})

class SpotifyAuth:
    def __init__(self, client_id, client_secret, refresh_token):
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token = refresh_token
        self.access_token = settings.SPOTIFY_ACCESS_TOKEN
        self.token_expiration = 0  # We'll assume the token is expired initially

    def get_access_token(self):
        if time.time() > self.token_expiration:
            self.refresh_access_token()
        return self.access_token

    def refresh_access_token(self):
        token_url = "https://accounts.spotify.com/api/token"
        data = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        response = requests.post(token_url, data=data)
        if response.status_code == 200:
            token_info = response.json()
            self.access_token = token_info["access_token"]
            self.token_expiration = time.time() + token_info["expires_in"]
            # Update the access token in settings
            settings.SPOTIFY_ACCESS_TOKEN = self.access_token
        else:
            raise Exception("Failed to refresh access token")

# Initialize the SpotifyAuth object
spotify_auth = SpotifyAuth(
    settings.SPOTIFY_CLIENT_ID,
    settings.SPOTIFY_CLIENT_SECRET,
    settings.SPOTIFY_REFRESH_TOKEN
)

def get_playlists(request):
    # Ideally, you'd store this securely and refresh when needed
    access_token = settings.SPOTIFY_ACCESS_TOKEN

    headers = {
        'Authorization': f'Bearer {access_token}',
    }

    response = requests.get('https://api.spotify.com/v1/me/playlists', headers=headers)
    
    if response.status_code == 200:
        playlists = response.json()['items']
        return render(request, 'playlister/playlists.html', {'playlists': playlists})
    else:
        error_message = f"Failed to fetch playlists: {response.status_code} {response.text}"
        return render(request, 'playlister/playlists.html', {'error': error_message})