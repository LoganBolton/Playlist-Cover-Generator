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

from . import claude
from . import spotify_auth

def get_playlist_tracks(token, playlist_id):
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    headers = spotify_auth.get_auth_header(token)
    
    tracks = []
    while url:
        result = requests.get(url, headers=headers)
        json_result = result.json()
        
        for item in json_result['items']:
            track = item.get('track')
            if track:
                tracks.append({
                    'id': track.get('id', 'Unknown'),
                    'name': track.get('name', 'Unknown'),
                    'artist': track['artists'][0]['name'] if track.get('artists') else 'Unknown'
                })
        
        url = json_result.get('next')  # Get the next page URL, if it exists

    return tracks

# Get audio features for tracks
def get_audio_features(token, track_ids):
    track_ids = track_ids[:99]  # Spotify API only allows 100 track IDs at a time
    url = f"https://api.spotify.com/v1/audio-features"
    headers = spotify_auth.get_auth_header(token)
    params = {'ids': ','.join(track_ids)}
    print()
    print(headers)
    print(params)
    print()
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

def get_prompt_and_cover(PLAYLIST_ID):
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