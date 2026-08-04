from django.conf import settings
import time
import base64
import requests
from django.http import JsonResponse
from urllib.parse import quote
from django.core.cache import cache
from django_redis import get_redis_connection
import json
import logging

logger = logging.getLogger(__name__)


class SpotifyUtils:
    def __init__(self):
        # Initializing spotify with client credentials for non-user specific access
        self.CLIENT_ID = settings.SPOTIFY_CLIENT_ID
        self.CLIENT_SECRET = settings.SPOTIFY_CLIENT_SECRET
        self.TOKEN_URL = "https://accounts.spotify.com/api/token"

    def _get_access_token(self, request) -> str | None:
        # case 1: token exists and hasn't expired
        if "access_token" in request.session and "token_expiry_time" in request.session:
            token_expiry_time = request.session["token_expiry_time"]
            if time.time() < token_expiry_time:
                return request.session["access_token"]

        # case 2: get new token
        headers = {
            "Authorization": "Basic %s"
            % base64.urlsafe_b64encode(
                (self.CLIENT_ID + ":" + self.CLIENT_SECRET).encode()
            ).decode(),
            "Content-Type": "application/x-www-form-urlencoded",
        }

        data = {"grant_type": "client_credentials"}

        
        response = requests.post(self.TOKEN_URL, headers=headers, data=data, timeout=3)
        # success
        if response.status_code == 200:
            tokens = response.json()

            access_token = tokens["access_token"]
            expires_in = tokens["expires_in"]

            request.session["access_token"] = access_token
            request.session["token_expiry_time"] = time.time() + expires_in

            return access_token
        else:
            logger.error(f"Error:{response.status_code}, {response.text}")
            return None

    def spotify_search(self, request) -> JsonResponse:
        token = self._get_access_token(request)
        if not token:
            return JsonResponse(
                {"error": "Failed to retrieve access token"}, status=400
            )

        query = request.GET.get("query", "")
        encoded_query = quote(query)
        search_url = f"https://api.spotify.com/v1/search?q={encoded_query}&type=track,album,artist&limit=5"

        headers = {"Authorization": f"Bearer {token}"}

        response = requests.get(search_url, headers=headers)

        if response.status_code == 200:
            return JsonResponse(response.json())
        else:
            #TODO: improve error handling, can pass down Spotify's exact error response as done in the get_access_token method
            return JsonResponse(
                {"error": "Failed to fetch data from Spotify"}, status=400
            )
    #Remember to change the None to raises once I've done exception handling
    def spotify_get_id(self, request) -> dict | None:
        spotify_id = request.GET.get("spotify_id", "")
        item_type = request.GET.get("type", "")


        cache_key = f"spotify_{item_type}_{spotify_id}"
        cached_item = cache.get(cache_key)

        if cached_item:
            return cached_item

        token = self._get_access_token(request)
        if not token:
            #TODO: improve error handling, can pass down Spotify's exact error response as done in the get_access_token method
            logger.error("Error: couldn't get access token")
            return None

        encoded_id = quote(spotify_id)
        encoded_type = quote(item_type)
        search_url = f"https://api.spotify.com/v1/{encoded_type}/{encoded_id}"

        headers = {"Authorization": f"Bearer {token}"}

        response = requests.get(search_url, headers=headers, timeout=3)

        logger.debug(response.status_code)

        if response is not None and response.status_code == 200:
            cache_object = self._parse_spotify_item(response.json(), token)
            if cache_object:
                cache.set(cache_key, cache_object, timeout=300)  # 1 hour
                return cache_object
            #Need to fix error handling
            else:
                logger.error("Error: Object couldn't be parsed")
                return None
        else:
            logger.error("Error: Not getting a response for the id and type")
            return None

    # Assuming this function gets the discography not just albums. Change name if true.
    def get_artist_albums(self, spotify_id, type, token) -> dict | None:
        if not token:
            logger.error("error: failed to receive access token")
            return None

        encoded_id = quote(spotify_id)
        encoded_type = quote(type)
        search_url = f"https://api.spotify.com/v1/artists/{encoded_id}/albums?include_groups={encoded_type}"

        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(search_url, headers=headers, timeout=3)
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Error: {response.status_code}, {response.text}")
            return None

    def _parse_spotify_item(self, data, token) -> dict | None:
        if not data:
            return None
        parsed = {
            "spotify_id": data.get("id"),
            "type": f"{data.get('type')}s",
        }
        if data.get("type") == "artist":

            artist_albums = self.get_artist_albums(parsed["spotify_id"], "album", token)
            artist_other = self.get_artist_albums(parsed["spotify_id"], "single", token)

            parsed["artist_name"] = data.get("name")
            parsed["artist_albums"] = [
                (album["id"], album["name"]) for album in artist_albums.get("items", [])
            ]
            parsed["artist_singles"] = [
                (album["id"], album["name"])
                for album in artist_other.get("items", [])
                if album.get("total_tracks") == 1
            ]
            parsed["artist_eps"] = [
                (album["id"], album["name"])
                for album in artist_other.get("items", [])
                if album.get("total_tracks") > 1
            ]

        elif data.get("type") == "album":
            parsed["album_name"] = data.get("name")
            parsed["artist_name"] = [
                artist["name"] for artist in data.get("artists", [])
            ]
            parsed["artist_id"] = [artist["id"] for artist in data.get("artists", [])]
            parsed["track_list"] = [
                (track["id"], track["name"])
                for track in data.get("tracks", {}).get("items", [])
            ]

        elif data.get("type") == "track":
            parsed["track_name"] = data.get("name")
            parsed["album_name"] = data["album"].get("name")
            parsed["album_id"] = data["album"].get("id")
            parsed["artist_name"] = [
                artist["name"] for artist in data.get("artists", [])
            ]
            parsed["artist_id"] = [artist["id"] for artist in data.get("artists", [])]
        else:
            return None

        return parsed

    # JUST FOR DEBUGGING
    def _print_spotify_cache(self):
        # Directly access Redis using Django-Redis
        redis_connection = get_redis_connection(
            "default"
        )  # Use 'default' or your cache alias
        # Get all the keys for cached Spotify items
        keys = redis_connection.keys("::spotify_*")  # Pattern to match all spotify keys
        print(f"Found {len(keys)} cached Spotify items:")

        for key in keys:
            key_str = key.decode("utf-8")
            value = cache.get(key_str[2:])  # Decode key from bytes to string
            print(f"{key_str}: {value}")
