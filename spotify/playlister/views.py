from django.shortcuts import render, redirect
from .models import TodoItem
from django.views.decorators.http import require_POST
from django.conf import settings
from .utils import driver
import requests

def index(request):
    todo_list = TodoItem.objects.order_by('id')
    return render(request, 'playlister/index.html', {'todo_list': todo_list})

def generate_image(request, playlist_id):
    # prompt = driver(playlist_id)  # Call the driver function to get the image URL
    prompt = "testing debug prompt mmmm I love prompting language models with dynamic data mmmm " + playlist_id 
    image_url = ""
    # return render(request, 'playlister/display_image.html', {'image_url': image_url})
    return render(request, 'playlister/display_image.html', {'playlist_id': playlist_id, 'prompt': prompt, 'image_url': image_url})

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