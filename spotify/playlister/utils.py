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

# Claude
def set_up_claude():
    api_key = os.environ.get("ANTHROPIC_API_KEY_PERSONAL")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY environment variable is not set.")
        exit(1)

    # Set up the client
    client = anthropic.Anthropic(api_key=api_key)
    
def get_conversation(prompt):
    message = [{
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt,
                        }
                    ]
                }]
    return message

def send_message(conversation):
    message = anthropic.Anthropic().messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=1024,
        messages=conversation
    )
    # print(f"response to followup: {message.content}")
    pure_text = message.content[0].text
    # print(f"pure text: {pure_text}")
    return pure_text

def extract_description(text):
    start = text.index('[') + 1
    end = text.index(']')
    result = text[start:end]
    return result

# Spotify
def set_up_spotify():
    # Replace these with your actual Client ID and Client Secret
    CLIENT_ID = os.environ.get('SPOTIFY_CLIENT_ID')
    CLIENT_SECRET = os.environ.get('SPOTIFY_CLIENT_SECRET')

    client_creds = f"{CLIENT_ID}:{CLIENT_SECRET}"
    client_creds_b64 = base64.b64encode(client_creds.encode())

    # Token URL
    token_url = 'https://accounts.spotify.com/api/token'

    # Request Body Parameters
    token_data = {
        'grant_type': 'client_credentials'
    }

    # Request Headers
    token_headers = {
        'Authorization': f'Basic {client_creds_b64.decode()}'
    }
    
# Authentication
def get_token():
    CLIENT_ID = os.environ.get('SPOTIFY_CLIENT_ID')
    CLIENT_SECRET = os.environ.get('SPOTIFY_CLIENT_SECRET')

    if not CLIENT_ID or not CLIENT_SECRET:
        print("Error: SPOTIFY_CLIENT_ID and/or SPOTIFY_CLIENT_SECRET environment variables are not set.")
        exit(1)

    auth_string = f"{CLIENT_ID}:{CLIENT_SECRET}"
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    result = requests.post(url, headers=headers, data=data)
    json_result = result.json()
    token = json_result.get("access_token")

    if not token:
        print("Error: Could not retrieve Spotify token.")
        exit(1)

    return token

    auth_string = f"{CLIENT_ID}:{CLIENT_SECRET}"
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    result = requests.post(url, headers=headers, data=data)
    json_result = result.json()
    token = json_result["access_token"]
    return token

def get_auth_header(token):
    return {"Authorization": "Bearer " + token}

# Get playlist tracks
def get_playlist_tracks(token, playlist_id):
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    headers = get_auth_header(token)
    
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
    headers = get_auth_header(token)
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
    token = get_token()
    tracks = get_playlist_tracks(token, PLAYLIST_ID)

    # Get audio features for all tracks
    track_ids = [track['id'] for track in tracks]
    # print(f"token: {token}, track_ids: {track_ids}")
    audio_features = get_audio_features(token, track_ids)

    # Calculate averages
    avg_valence = mean(feature['valence'] for feature in audio_features)
    avg_energy = mean(feature['energy'] for feature in audio_features)

    # print(f"Tracks in the playlist (total: {len(tracks)}):")
    playlist_description = ""

    for i, (track, features) in enumerate(zip(tracks, audio_features), 1):
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
    set_up_claude()
    set_up_spotify()
    
    # bossa = '6cGZkPs8wimEZBDzpVNaut'
    # jazz = '71vvwEbxgXqHZ7ONA6WGxt'
    PLAYLIST_ID = '2djCZlngGykIYIvhRtPq39'
    playlist_description = get_playlist_details(PLAYLIST_ID)
    prompt = f"""Give me a prompt that will be able represent this playlist in a latent diffusion model. Make it minimalist and abstract but still keep it interesting. I don't want hotel art level minimalism, I want something raw and artistic. If relevant, incorporate imagery that relates to the specific songs or artists. Put your description in square brackets like this [description].\n\n{playlist_description}"""
    
    # convo = get_conversation(prompt)
    # response = send_message(convo)
    # description = extract_description(response)
    # return description

    #temporarily commented out 
    # print(description)
    description = "really cool awesome image that's really cool and abstract and minimalist and stuff"
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
    print(output)
    image_url = output[0]

    return image_url
