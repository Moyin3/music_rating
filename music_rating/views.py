from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.conf import settings
import requests
import time
import base64
from urllib.parse import quote

from .models import Song, Album

def entrypage(request):
    template = loader.get_template("music_rating/entrypage.html")
    return HttpResponse(template.render({}, request))

def userhome(request):
    template = loader.get_template("music_rating/userhome.html")
    return HttpResponse(template.render({}, request))

def artistpage(request):
    template = loader.get_template("music_rating/artistpage.html")
    return HttpResponse(template.render({}, request))

def albumpage(request):
    album_list = Album.objects.all()
    return render(request, "music_rating/albumpage.html", {'album_list': album_list})

def songspage(request):
    template = loader.get_template("music_rating/songspage.html")
    return HttpResponse(template.render({}, request))

def compage(request):
    template = loader.get_template("music_rating/compage.html")
    return HttpResponse(template.render({}, request))

def album_detail(request, album_id):
    album = Album.objects.get(id=album_id)
    return render(request, 'music_rating/album_detail.html', {'album': album})




### Spotify Access Token

CLIENT_ID = settings.SPOTIFY_CLIENT_ID
CLIENT_SECRET = settings.SPOTIFY_CLIENT_SECRET

TOKEN_URL = "https://accounts.spotify.com/api/token"
 
# get Client Credentials flow token 

def get_access_token(request):

    # case 1: token exists and hasn't expired
    request.session['token_expiry_time'] = time.time() - 3600
    if 'access_token' in request.session and 'token_expiry_time' in request.session:
        token_expiry_time = request.session['token_expiry_time']
        if time.time() < token_expiry_time:
            return request.session['access_token']

    # case 2: get new token
    headers = {
        'Authorization': 'Basic %s' % base64.urlsafe_b64encode((CLIENT_ID + ':' + CLIENT_SECRET).encode()).decode(),
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    data = {
        'grant_type': 'client_credentials'
    }

    
    response = requests.post(TOKEN_URL, headers=headers, data=data)
    #success
    if response.status_code == 200:
        tokens = response.json()


        access_token = tokens['access_token']
        expires_in = tokens['expires_in'] 
        
        request.session['access_token'] = access_token
        request.session['token_expiry_time'] = time.time() + expires_in
        
        return access_token
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None

def get_spotify_token(request):
    token = get_access_token(request)
    if token:
        return token
    else:
        return JsonResponse({'error': 'Failed to retrieve access token'}, status=400)


### Spotify Search

def spotify_search(request):
    token = get_spotify_token(request)
    if not token:
        return JsonResponse({'error': 'Failed to retrieve access token'}, status=400)
    
    query = request.GET.get('query', '')
    encoded_query = quote(query)
    search_url = f'https://api.spotify.com/v1/search?q={encoded_query}&type=track&limit=5'
    # params = {
    #     'q': query,
    #     'type': 'track',  # You can also use 'album', 'artist', etc.
    #     'limit': 5
    # }
    # encoded_params = urlencode(params)
    # search_url = f"https://api.spotify.com/v1/search?{encoded_params}"
    
    headers = {
        'Authorization': f'Bearer {token}'
    }

    response = requests.get(search_url, headers=headers)
    
    if response.status_code == 200:
        return JsonResponse(response.json())
    else:
        return JsonResponse({'error': 'Failed to fetch data from Spotify'}, status=400)
