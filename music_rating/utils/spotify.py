from django.conf import settings
import time
import base64
import requests
from django.http import JsonResponse
from urllib.parse import quote
from django.core.cache import cache
from django_redis import get_redis_connection

class SpotifyUtils:
    def __init__(self):
        # Initializing spotipy with client credentials for non-user specific access
        self.CLIENT_ID = settings.SPOTIFY_CLIENT_ID
        self.CLIENT_SECRET = settings.SPOTIFY_CLIENT_SECRET
        self.TOKEN_URL = "https://accounts.spotify.com/api/token"

    def _get_access_token(self, request):
        # case 1: token exists and hasn't expired
        if 'access_token' in request.session and 'token_expiry_time' in request.session:
            token_expiry_time = request.session['token_expiry_time']
            if time.time() < token_expiry_time:
                return request.session['access_token']

        # case 2: get new token
        headers = {
            'Authorization': 'Basic %s' % base64.urlsafe_b64encode((self.CLIENT_ID + ':' + self.CLIENT_SECRET).encode()).decode(),
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        data = {
            'grant_type': 'client_credentials'
        }

        
        response = requests.post(self.TOKEN_URL, headers=headers, data=data)
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
        
        

    def spotify_search(self, request):
        token = self._get_access_token(request)
        if not token:
            return JsonResponse({'error': 'Failed to retrieve access token'}, status=400)
        
        query = request.GET.get('query', '')
        encoded_query = quote(query)
        search_url = f'https://api.spotify.com/v1/search?q={encoded_query}&type=track,album,artist&limit=5'
        
        headers = {
            'Authorization': f'Bearer {token}'
        }

        response = requests.get(search_url, headers=headers)
        
        if response.status_code == 200:
            return JsonResponse(response.json())
        else:
            return JsonResponse({'error': 'Failed to fetch data from Spotify'}, status=400)
        
    def spotify_get_id(self, request):

        spotify_id = request.GET.get('spotify_id', '')
        encoded_id = quote(spotify_id)
        type = request.GET.get('type', '')
        encoded_type = quote(type)

        cache_key = f"spotify_{type}_{spotify_id}"
        cached_item = cache.get(cache_key)

        if cached_item:
            return JsonResponse(cached_item)


        token = self._get_access_token(request)
        if not token:
            return JsonResponse({'error': 'Failed to retrieve access token'}, status=400)
        spotify_id = request.GET.get('spotify_id', '')
        encoded_id = quote(spotify_id)
        type = request.GET.get('type', '')
        encoded_type = quote(type)
        search_url = f"https://api.spotify.com/v1/{encoded_type}/{encoded_id}"

        headers = {
            'Authorization': f'Bearer {token}'
        }

        response = requests.get(search_url, headers=headers)

        if response.status_code == 200:
            cache_object = self._parse_spotify_item(response.json(), request)
            if cache_object:
                cache.set(cache_key, cache_object, timeout=300) # 1 hour
                return JsonResponse(cache_object)
            else:
                return JsonResponse({'error': 'Incorrect response format'})
        else:
            return JsonResponse({'error': 'Failed to fetch id from Spotify'}, status=400)
    
    def get_album_dict_from_id(self, id, request):
        return

    def get_artist_albums(self, id, type, request):
        token = self._get_access_token(request)
        if not token:
            return JsonResponse({'error': 'Failed to retrieve access token'}, status=400)
        
        encoded_id = quote(id)
        encoded_type = quote(type)
        search_url = f"https://api.spotify.com/v1/artists/{encoded_id}/albums?include_groups={encoded_type}"

        headers = {
            'Authorization': f'Bearer {token}'
        }
        response = requests.get(search_url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            return JsonResponse({'error': 'Failed to fetch id from Spotify'}, status=400)


    def _parse_spotify_item(self, data, request):
        if not data:
            return None
        parsed = {
            'id': data.get('id'),
            'type': f"{data.get('type')}s",
        }
        if data.get('type') == 'artist':
    
            artist_albums = self.get_artist_albums(parsed['id'], 'album', request)
            artist_other = self.get_artist_albums(parsed['id'], 'single', request)

            parsed['artist_name'] = data.get('name')
            parsed['artist_albums'] = [
                (album['id'], album['name']) for album in artist_albums.get('items', [])
            ]
            parsed['artist_singles'] = [
                (album['id'], album['name']) for album in artist_other.get('items', [])
                if album.get('total_tracks') == 1
            ]
            parsed['artist_eps'] = [
                (album['id'], album['name']) for album in artist_other.get('items', [])
                if album.get('total_tracks') > 1
            ]

        
        elif data.get('type') == 'album':
            parsed['album_name'] = data.get('name')
            parsed['artist_name'] = [artist['name'] for artist in data.get('artists', [])]
            parsed['artist_id'] = [artist['id'] for artist in data.get('artists', [])]
            parsed['track_list'] = [(track['id'], track['name']) for track in data.get('tracks', []).get('items', [])]

        elif data.get('type') == 'track':
            parsed['track_name'] = data.get('name')
            parsed['album_name'] = data['album'].get('name')
            parsed['album_id'] = data['album'].get('id')
            parsed['artist_name'] = [artist['name'] for artist in data.get('artists', [])]
            parsed['artist_id'] = [artist['id'] for artist in data.get('artists', [])]
        else:
            return None

        return parsed
    

    
    #JUST FOR DEBUGGING
    def _print_spotify_cache(self):
        # Directly access Redis using Django-Redis
        redis_connection = get_redis_connection("default")  # Use 'default' or your cache alias
        # Get all the keys for cached Spotify items
        keys = redis_connection.keys("::spotify_*")  # Pattern to match all spotify keys
        print(f"Found {len(keys)} cached Spotify items:")

        for key in keys:
            key_str = key.decode('utf-8')
            value = cache.get(key_str[2:])  # Decode key from bytes to string
            print(f"{key_str}: {value}")



