from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from django.conf import settings
from django.core.cache import cache
from django.shortcuts import redirect
from django.http import HttpResponse
from django.urls import reverse
import requests

# from .utils import driver
from .controllers.generate_cover import get_prompt_and_cover
from .controllers.spotify_auth import SpotifyTokenManager
from .controllers.spotify_auth import get_headers
from .controllers.spotify_auth import get_playlist_response


def index(request):
    return render(request, 'playlister/index.html')

def generate_image(request, playlist_id):
    try:
        response = get_playlist_response(request, playlist_id)

        if response.status_code == 200:
            playlist = response.json()
            playlist_name = playlist['name']
            
            ## DEBUG CODE
            prompt, image_url = get_prompt_and_cover(playlist_id, request)  # Call the driver function to get the image URL
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

def get_playlists(request):
    if 'spotify_access_token' not in request.session:
        return render(request, 'playlister/playlists.html', {'not_authenticated': True})
    
    try:
        access_token = SpotifyTokenManager.get_token(request)
        headers = {'Authorization': f'Bearer {access_token}'}
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