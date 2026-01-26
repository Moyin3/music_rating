from django.test import TestCase, Client, RequestFactory
from .models import Song, Artist, Album, Single, EP, Rating, RateSystem
from unittest.mock import patch, Mock
from urllib.parse import urlencode
from django.conf import settings
from django.urls import reverse
from music_rating.utils.spotify import SpotifyUtils
import time
import json
from django.http import JsonResponse
from django.contrib.contenttypes.models import ContentType
from django.contrib.sessions.middleware import SessionMiddleware
from .forms import RatingForm
from django.contrib.auth import get_user_model
from music_rating.views import (
    album_rating_for_rate_system_2,
    artist_rating_for_rate_system_2,
    album_rating_for_rate_system_1,
    artist_rating_for_rate_system_1,
    final_album_rating,
    final_artist_rating,
    community_rating_for_artist,
    community_rating_for_track,
    community_rating_for_album,
)

User = get_user_model()


class ArtistModelTest(TestCase):
    def setUp(self):
        self.artist = Artist.objects.create(spotify_id="12345")

    def test_artist_spotify_id(self):
        self.assertEqual(self.artist.spotify_id, "12345")


class SongModelTest(TestCase):
    def setUp(self):
        self.song = Song.objects.create(
            spotify_id="54321",
        )

    def test_song_spotify_id(self):
        self.assertEqual(self.song.spotify_id, "54321")


class AlbumModelTest(TestCase):
    def setUp(self):
        self.album = Album.objects.create(spotify_id="11111")

    def test_album_spotify_id(self):
        self.assertEqual(self.album.spotify_id, "11111")


class SingleModelTest(TestCase):
    def setUp(self):
        self.single = Single.objects.create(
            spotify_id="22222",
        )

    def test_single_spotify_id(self):
        self.assertEqual(self.single.spotify_id, "22222")


class EPModelTest(TestCase):
    def setUp(self):
        self.ep = EP.objects.create(spotify_id="33333")

    def test_ep_spotify_id(self):
        self.assertEqual(self.ep.spotify_id, "33333")


#TODO: Write these tests
class DetailViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.explicit = RateSystem.objects.create(key = "explicit")
        self.average = RateSystem.objects.create(key = "average")

    @patch("api.views.spotify_handler.spotify_get_id")
    def test_album_detail_success(self, mock_spotify_get_id):
        # Mock Spotify API response
        mock_response_data = {
            "id": "test-spotify-id",
            "type": "album",
            "name": "Test Album",
            "artists": [
                {"id": "artist1-id", "name": "Test Artist"}
            ],
            "tracks": {
                "items": [
                    {"id": "track1-id", "name": "Track 1"},
                    {"id": "track2-id", "name": "Track 2"},
                ]
            }
        }

#TODO: Review these tests
class SpotifyUtilsTests(TestCase):
    def setUp(self):
        self.spotify_utils = SpotifyUtils()
        self.factory = RequestFactory()

    @patch("music_rating.utils.spotify.requests.post")  # Mock requests.post
    def test_get_access_token_success(self, mock_post):
        # Mock a successful token response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "mock_access_token",
            "expires_in": 3600,
        }
        mock_post.return_value = mock_response

        # Simulate a request without a valid token in the session
        request = self.factory.get("/")
        request.session = {}

        # Call the method
        token = self.spotify_utils._get_access_token(request)

        # Assertions
        self.assertEqual(token, "mock_access_token")
        self.assertIn("access_token", request.session)
        self.assertIn("token_expiry_time", request.session)
        mock_post.assert_called_once()  # API call should be made

    @patch("music_rating.utils.spotify.requests.post")
    def test_get_access_token_failure(self, mock_post):
        # Mock a failed token response
        mock_response = Mock()
        mock_response.status_code = 400
        mock_post.return_value = mock_response

        # Simulate a request
        request = self.factory.get("/")
        request.session = {}

        # Call the method
        token = self.spotify_utils._get_access_token(request)

        # Assertions
        self.assertIsNone(token)

    @patch("music_rating.utils.spotify.requests.post")  # Mock requests.post
    def test_get_access_token_with_valid_token(self, mock_post):
        # Simulate a request with a valid token in the session
        request = self.factory.get("/")
        request.session = {
            "access_token": "mock_access_token",
            "token_expiry_time": time.time() + 3600,  # Token expires in 1 hour
        }

        # Call the method
        token = self.spotify_utils._get_access_token(request)

        # Assertions
        self.assertEqual(token, "mock_access_token")  # Should return the existing token
        mock_post.assert_not_called()  # No API call should be made

    @patch("music_rating.utils.spotify.requests.post")  # Mock requests.post
    def test_get_access_token_expired_token(self, mock_post):
        # Mock a successful token response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "new_mock_access_token",
            "expires_in": 3600,
        }
        mock_post.return_value = mock_response

        # Simulate a request with an expired token in the session
        request = self.factory.get("/")
        request.session = {
            "access_token": "expired_mock_access_token",
            "token_expiry_time": time.time() - 3600,  # Token expired 1 hour ago
        }

        # Call the method
        token = self.spotify_utils._get_access_token(request)

        # Assertions
        self.assertEqual(token, "new_mock_access_token")  # Should retrieve a new token
        self.assertIn("access_token", request.session)
        self.assertIn("token_expiry_time", request.session)
        self.assertGreater(request.session["token_expiry_time"], time.time())
        mock_post.assert_called_once()  # API call should be made

    @patch("music_rating.utils.spotify.requests.get")  # Mock requests.get
    @patch(
        "music_rating.utils.spotify.SpotifyUtils._get_access_token"
    )  # Mock _get_access_token
    def test_spotify_search_success(self, mock_get_access_token, mock_requests_get):
        # Mock the access token
        mock_get_access_token.return_value = "mock_access_token"

        # Mock the Spotify API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "tracks": {
                "items": [
                    {"name": "Test Track", "id": "track123"},
                ]
            }
        }
        mock_requests_get.return_value = mock_response

        # Simulate a request
        request = self.factory.get("/?query=Test")
        request.session = {}

        # Call the method
        response = self.spotify_utils.spotify_search(request)

        # Assertions
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content.decode("utf-8"))
        self.assertIn("tracks", response_data)
        self.assertEqual(response_data["tracks"]["items"][0]["name"], "Test Track")
        self.assertEqual(response_data["tracks"]["items"][0]["id"], "track123")

    @patch("music_rating.utils.spotify.requests.get")
    @patch("music_rating.utils.spotify.SpotifyUtils._get_access_token")
    def test_spotify_search_failure(self, mock_get_access_token, mock_requests_get):
        # Mock the access token
        mock_get_access_token.return_value = "mock_access_token"

        # Mock a failed Spotify API response
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"error": "Failed to fetch data from Spotify"}
        mock_requests_get.return_value = mock_response

        # Simulate a request
        request = self.factory.get("/?query=Test")
        request.session = {}

        # Call the method
        response = self.spotify_utils.spotify_search(request)

        # Assertions
        self.assertEqual(response.status_code, 400)

        response_data = json.loads(response.content.decode("utf-8"))
        self.assertIn("error", response_data)
        self.assertEqual(response_data["error"], "Failed to fetch data from Spotify")

    @patch("music_rating.utils.spotify.requests.get")  # Mock requests.get
    @patch("music_rating.utils.spotify.cache")  # Mock cache
    @patch(
        "music_rating.utils.spotify.SpotifyUtils._get_access_token"
    )  # Mock _get_access_token
    def test_spotify_get_id_success(
        self, mock_get_access_token, mock_cache, mock_requests_get
    ):
        # Mock the access token
        mock_get_access_token.return_value = "mock_access_token"

        # Mock the cache
        mock_cache.get.return_value = None  # No cached data

        # Mock the Spotify API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "test_spotify_id",
            "type": "track",
            "name": "Test Track",
            "album": {"name": "Test Album", "id": "album123"},
            "artists": [{"name": "Test Artist", "id": "artist123"}],
        }
        mock_requests_get.return_value = mock_response

        # Simulate a request
        request = self.factory.get("/?spotify_id=test_spotify_id&type=track")
        request.session = {}

#TODO: Review these tests
class ParseSpotifyItemTests(TestCase):
    def setUp(self):
        self.spotify_utils = SpotifyUtils()
        self.factory = RequestFactory()

    def test_parse_artist_data(self):
        # Mock artist data
        artist_data = {"id": "artist123", "type": "artist", "name": "Test Artist"}

        request = self.factory.get("/")
        middleware = SessionMiddleware(get_response=lambda x: None)
        middleware.process_request(request)
        request.session.save()

        # Call the method
        parsed = self.spotify_utils._parse_spotify_item(artist_data, request)

        # Assertions
        self.assertEqual(parsed["spotify_id"], "artist123")
        self.assertEqual(parsed["type"], "artists")
        self.assertEqual(parsed["artist_name"], "Test Artist")

    def test_parse_album_data(self):
        # Mock album data
        album_data = {
            "id": "album123",
            "type": "album",
            "name": "Test Album",
            "artists": [
                {"name": "Artist One", "id": "artist1"},
                {"name": "Artist Two", "id": "artist2"},
            ],
            "tracks": {
                "items": [
                    {"id": "track1", "name": "Track One"},
                    {"id": "track2", "name": "Track Two"},
                ]
            },
        }

        request = self.factory.get("/")

        # Call the method
        parsed = self.spotify_utils._parse_spotify_item(album_data, request)

        # Assertions
        self.assertEqual(parsed["spotify_id"], "album123")
        self.assertEqual(parsed["type"], "albums")
        self.assertEqual(parsed["album_name"], "Test Album")
        self.assertEqual(parsed["artist_name"], ["Artist One", "Artist Two"])
        self.assertEqual(parsed["artist_id"], ["artist1", "artist2"])
        self.assertEqual(
            parsed["track_list"], [("track1", "Track One"), ("track2", "Track Two")]
        )

    def test_parse_track_data(self):
        # Mock track data
        track_data = {
            "id": "track123",
            "type": "track",
            "name": "Test Track",
            "album": {"name": "Test Album", "id": "album123"},
            "artists": [
                {"name": "Artist One", "id": "artist1"},
                {"name": "Artist Two", "id": "artist2"},
            ],
        }

        request = self.factory.get("/")

        # Call the method
        parsed = self.spotify_utils._parse_spotify_item(track_data, request)

        # Assertions
        self.assertEqual(parsed["spotify_id"], "track123")
        self.assertEqual(parsed["type"], "tracks")
        self.assertEqual(parsed["track_name"], "Test Track")
        self.assertEqual(parsed["album_name"], "Test Album")
        self.assertEqual(parsed["album_id"], "album123")
        self.assertEqual(parsed["artist_name"], ["Artist One", "Artist Two"])
        self.assertEqual(parsed["artist_id"], ["artist1", "artist2"])

    def test_parse_invalid_data(self):
        # Mock invalid data
        invalid_data = {"id": "invalid123", "type": "unknown"}

        request = self.factory.get("/")

        # Call the method
        parsed = self.spotify_utils._parse_spotify_item(invalid_data, request)

        # Assertions
        self.assertIsNone(parsed)

    def test_parse_empty_data(self):

        request = self.factory.get("/")
        # Call the method with empty data
        parsed = self.spotify_utils._parse_spotify_item(None, request)

        # Assertions
        self.assertIsNone(parsed)

class RatingHelpersTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.user2 = User.objects.create_user(
            username="testuser2", password="testpass2"
        )
        self.user3 = User.objects.create_user(username = "testuser3", password = "testpass3")
        self.album = Album.objects.create(spotify_id="album123")
        self.song = Song.objects.create(spotify_id="song123")
        self.artist = Artist.objects.create(spotify_id="artist123")
        self.rate_system_1 = RateSystem.objects.create(
            id=1, key="explicit", description="The default rating system"
        )
        self.rate_system_2 = RateSystem.objects.create(
            id=2, key="average", description="average of relevant ratings"
        )
        self.factory = RequestFactory()
        self.request = self.factory.get("/")

    def test_community_rating_for_track(self):
        Rating.objects.create(score=80, spotify_id= "song123", user = self.user, content_type = ContentType.objects.get_for_model(Song), rate_system = self.rate_system_1)
        Rating.objects.create(score=100, spotify_id = "song123", user = self.user2, content_type = ContentType.objects.get_for_model(Song), rate_system = self.rate_system_1)
        self.assertEqual(community_rating_for_track(self.song), 90)

    def test_community_rating_for_album(self):
        album_dict = {"id": self.album.spotify_id}
        Rating.objects.create(
            score=70, user = self.user, rate_system=self.rate_system_1, content_type = ContentType.objects.get_for_model(Album), spotify_id = "album123"
            )
        Rating.objects.create(
            score=90, user = self.user2, rate_system=self.rate_system_1, content_type = ContentType.objects.get_for_model(Album), spotify_id = "album123"
        )
        Rating.objects.create(
            score=95, user = self.user3, rate_system=self.rate_system_2, content_type = ContentType.objects.get_for_model(Album), spotify_id = "album123"
        )
        self.assertEqual(community_rating_for_album(album_dict), 85)

    def test_community_rating_for_artist(self):
        artist_dict = {"id": self.artist.spotify_id}
        Rating.objects.create(
            score=60, user = self.user, rate_system=self.rate_system_1, content_type = ContentType.objects.get_for_model(Artist), spotify_id = "artist123"
        )
        Rating.objects.create(
            score=100, user = self.user2, rate_system=self.rate_system_2, content_type = ContentType.objects.get_for_model(Artist), spotify_id = "artist123"
        )
        self.assertEqual(community_rating_for_artist(artist_dict), 80)

    def test_album_rating_for_rate_system_2(self):
        # User rates two songs in the album
        song2 = Song.objects.create(spotify_id="song456")
        album_dict = {
            "id": self.album.spotify_id,
            "track_list": [
                (self.song.spotify_id, "Song 1"),
                (song2.spotify_id, "Song 2"),
            ],
        }
        Rating.objects.create(user=self.user, score=80, rate_system = self.rate_system_2, content_type = ContentType.objects.get_for_model(Song), spotify_id = "song123")
        Rating.objects.create(user=self.user, score=100, rate_system = self.rate_system_2, content_type = ContentType.objects.get_for_model(Song), spotify_id = "song456")
        avg = album_rating_for_rate_system_2(self.user, album_dict)
        self.assertEqual(avg, 90)
"""
    def test_artist_rating_for_rate_system_2(self):
        # User rates two albums (directly via rate system 2)
        album2 = Album.objects.create(spotify_id="album456")
        artist_dict = {
            "id": self.artist.spotify_id,
            "artist_albums": [
                [self.album.spotify_id, "Album 1"],
                [album2.spotify_id, "Album 2"],
            ],
        }
        Rating.objects.create(
            user=self.user,
            score=80,
            rate_system=self.rate_system_2,
        )
        Rating.objects.create(
            user=self.user,
            score=100,
            rate_system=self.rate_system_2,
        )
        avg, rating_obj = artist_rating_for_rate_system_2(
            self.user, artist_dict, self.request
        )
        self.assertEqual(avg, 90)
        self.assertEqual(rating_obj.user, self.user)
        self.assertEqual(rating_obj.spotify_id, self.artist.spotify_id)

    def test_album_rating_for_rate_system_1(self):
        album_dict = {"id": self.album.spotify_id}
        Rating.objects.create(user=self.user, score=77)
        self.assertEqual(album_rating_for_rate_system_1(self.user, album_dict), 77)

    def test_artist_rating_for_rate_system_1(self):
        artist_dict = {"id": self.artist.spotify_id}
        Rating.objects.create(user=self.user, score=88)
        self.assertEqual(artist_rating_for_rate_system_1(self.user, artist_dict), 88)

    def test_final_album_rating(self):
        album_dict = {
            "id": self.album.spotify_id,
            "track_list": [(self.song.spotify_id, "Song 1")],
        }
        Rating.objects.create(
            user=self.user,
            score=55,
            rate_system=self.rate_system_1,
        )
        self.assertEqual(
            final_album_rating(self.user, album_dict, self.rate_system_1), 55
        )
        Rating.objects.create(user=self.user, score=99)
        avg = album_rating_for_rate_system_2(self.user, album_dict)
        self.assertEqual(
            final_album_rating(self.user, album_dict, self.rate_system_2), avg
        )

    def test_final_artist_rating(self):
        artist_dict = {
            "id": self.artist.spotify_id,
            "artist_albums": [[self.album.spotify_id, "Album 1"]],
        }
        Rating.objects.create(
            user=self.user,
            score=66,
            rate_system=self.rate_system_1,
        )
        self.assertEqual(
            final_artist_rating(
                self.user, artist_dict, self.rate_system_1, self.request
            ),
            66,
        )
        # For rate system 2
        Rating.objects.create(
            user=self.user,
            score=80,
            rate_system=self.rate_system_2,
        )
        avg, _ = artist_rating_for_rate_system_2(self.user, artist_dict, self.request)
        self.assertEqual(
            final_artist_rating(
                self.user, artist_dict, self.rate_system_2, self.request
            ),
            avg,
        )
        """
