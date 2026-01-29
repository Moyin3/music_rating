from django.test import TestCase, Client, RequestFactory
from .models import Song, Artist, Album, Single, EP, Rating, RateSystem
from unittest.mock import patch, Mock
from urllib.parse import urlencode
from django.conf import settings
from django.urls import reverse
from music_rating.utils.spotify import SpotifyUtils
import time
import json
from datetime import timedelta
from django.utils import timezone
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
    community_rating_for_artist,
    community_rating_for_album,
    community_rating_for_song,
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
            album_spotify_id="54321",  # Single, so album_spotify_id is same as song_id
        )

    def test_song_spotify_id(self):
        self.assertEqual(self.song.spotify_id, "54321")


class AlbumModelTest(TestCase):
    def setUp(self):
        self.album = Album.objects.create(spotify_id="11111", artist_spotify_id="artist_001")

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
        self.album = Album.objects.create(spotify_id="album123", artist_spotify_id="artist123")
        self.song = Song.objects.create(spotify_id="song123", album_spotify_id="album123")
        self.artist = Artist.objects.create(spotify_id="artist123")
        self.rate_system_1 = RateSystem.objects.create(
            id=1, key="explicit", description="The default rating system"
        )
        self.rate_system_2 = RateSystem.objects.create(
            id=2, key="average", description="average of relevant ratings"
        )
        self.factory = RequestFactory()
        self.request = self.factory.get("/")

    def test_album_rating_for_rate_system_2(self):
        # User rates two songs in the album
        song2 = Song.objects.create(spotify_id="song456", album_spotify_id="album123")
        
        Rating.objects.create(user=self.user, score=80, rate_system = self.rate_system_2, content_type = ContentType.objects.get_for_model(Song), spotify_id = "song123")
        Rating.objects.create(user=self.user, score=100, rate_system = self.rate_system_2, content_type = ContentType.objects.get_for_model(Song), spotify_id = "song456")
        avg = album_rating_for_rate_system_2(self.user, "album123")
        self.assertEqual(avg, 90)

    def test_artist_rating_for_rate_system_2(self):
        # User rates two albums (directly via rate system 2)
        album2 = Album.objects.create(spotify_id="album456", artist_spotify_id="artist123")
        
        Rating.objects.create(
            user=self.user,
            score=80,
            rate_system=self.rate_system_2,
            content_type = ContentType.objects.get_for_model(Album),
            spotify_id = "album123"
        )
        Rating.objects.create(
            user=self.user,
            score=100,
            rate_system=self.rate_system_2,
            content_type = ContentType.objects.get_for_model(Album),
            spotify_id = "album456"
        )
        avg = artist_rating_for_rate_system_2(self.user, "artist123")
        # Function now correctly filters albums by artist_spotify_id and returns average
        self.assertEqual(avg, 90)


    def test_album_rating_for_rate_system_1(self):
        Rating.objects.create(user=self.user, score=77, spotify_id = "album123", rate_system = self.rate_system_1, content_type = ContentType.objects.get_for_model(Album))
        self.assertEqual(album_rating_for_rate_system_1(self.user, "album123"), 77)

    def test_artist_rating_for_rate_system_1(self):
        Rating.objects.create(user=self.user, score=88, spotify_id = "artist123", rate_system = self.rate_system_1, content_type = ContentType.objects.get_for_model(Artist))
        self.assertEqual(artist_rating_for_rate_system_1(self.user, "artist123"), 88)

    #These tests are simplified versions of community rating to see if the underlying average, (the basic maths) is going wrong.
    def test_community_rating_for_track_simple(self):
        Rating.objects.create(score=80, spotify_id= "song123", user = self.user, content_type = ContentType.objects.get_for_model(Song), rate_system = self.rate_system_1)
        Rating.objects.create(score=50, spotify_id = "song123", user = self.user2, content_type = ContentType.objects.get_for_model(Song), rate_system = self.rate_system_1)
        self.assertEqual(community_rating_for_song("song123"), 65)

    def test_community_rating_for_album_simple(self):
        Rating.objects.create(
            score=70, user = self.user, rate_system=self.rate_system_1, content_type = ContentType.objects.get_for_model(Album), spotify_id = "album123"
            )
        Rating.objects.create(
            score=90, user = self.user2, rate_system=self.rate_system_1, content_type = ContentType.objects.get_for_model(Album), spotify_id = "album123"
        )
        Rating.objects.create(
            score=95, user = self.user3, rate_system=self.rate_system_2, content_type = ContentType.objects.get_for_model(Album), spotify_id = "album123"
        )
        self.assertEqual(community_rating_for_album("album123"), 85)

    def test_community_rating_for_artist_simple(self):
        Rating.objects.create(
            score=60, user = self.user, rate_system=self.rate_system_1, content_type = ContentType.objects.get_for_model(Artist), spotify_id = "artist123"
        )
        Rating.objects.create(
            score=100, user = self.user2, rate_system=self.rate_system_2, content_type = ContentType.objects.get_for_model(Artist), spotify_id = "artist123"
        )
        self.assertEqual(community_rating_for_artist("artist123"), 80)
    

    #Writing these tests to see if the communitry rating functions are choosing the most recent ratings from a user.
    def test_community_rating_for_track(self):
        ct = ContentType.objects.get_for_model(Song)
        
        old_rating, _ = Rating.objects.update_or_create(
        user=self.user,
        spotify_id="song123",
        rate_system=self.rate_system_1,
        content_type=ct,
        defaults={"score": 30}
    )

        # Manually force it to be older
        old_rating.updated_at = timezone.now() - timedelta(days=2)
        old_rating.save(update_fields=["updated_at"])

        # User 1: newer rating, different rate system
        new_rating, _ = Rating.objects.update_or_create(
            user=self.user,
            spotify_id="song123",
            rate_system=self.rate_system_2,
            content_type=ct,
            defaults={"score": 70}
        )

        new_rating.updated_at = timezone.now() - timedelta(days=1)
        new_rating.save(update_fields=["updated_at"])

        # User 1: even newer rating
        Rating.objects.update_or_create(
            user = self.user,
            spotify_id = "song123",
            rate_system = self.rate_system_2,
            content_type = ct,
            defaults={"score": 100}
        )
        Rating.objects.update_or_create(
            user=self.user2,
            spotify_id="song123",
            rate_system=self.rate_system_1,
            content_type=ct,
            defaults={"score": 90}
        )

        Rating.objects.update_or_create(
            user = self.user3,
            spotify_id = "song123",
            rate_system=self.rate_system_1,
            content_type=ct,
            defaults={"score": 5}
        )

        self.assertEqual(community_rating_for_song("song123"), 65)
        
    
    def test_community_rating_for_album(self):
        ct = ContentType.objects.get_for_model(Album)
        
        old_rating, _ = Rating.objects.update_or_create(
        user=self.user,
        spotify_id="album123",
        rate_system=self.rate_system_1,
        content_type=ct,
        defaults={"score": 30}
    )

        # Manually force it to be older
        old_rating.updated_at = timezone.now() - timedelta(days=2)
        old_rating.save(update_fields=["updated_at"])

        old_rating_user_2, _ = Rating.objects.update_or_create(
            user=self.user2,
            spotify_id="album123",
            rate_system=self.rate_system_2,
            content_type=ct,
            defaults={"score": 50}
        )

        old_rating_user_2.updated_at = timezone.now() - timedelta(days=1)
        old_rating_user_2.save(update_fields=["updated_at"])

       
        Rating.objects.update_or_create(
            user = self.user,
            spotify_id = "album123",
            rate_system = self.rate_system_2,
            content_type = ct,
            defaults={"score": 0}
        )
        Rating.objects.update_or_create(
            user=self.user2,
            spotify_id="album123",
            rate_system=self.rate_system_1,
            content_type=ct,
            defaults={"score": 25}
        )

        Rating.objects.update_or_create(
            user = self.user3,
            spotify_id = "album123",
            rate_system=self.rate_system_1,
            content_type=ct,
            defaults={"score": 5}
        )

        self.assertEqual(community_rating_for_album("album123"), 10)
    
    def test_community_rating_for_artist(self):
        ct = ContentType.objects.get_for_model(Artist)
        
        old_rating, _ = Rating.objects.update_or_create(
        user=self.user,
        spotify_id="artist123",
        rate_system=self.rate_system_1,
        content_type=ct,
        defaults={"score": 30}
    )

        # Manually force it to be older
        old_rating.updated_at = timezone.now() - timedelta(days=2)
        old_rating.save(update_fields=["updated_at"])

        old_rating_user_2, _ = Rating.objects.update_or_create(
            user=self.user2,
            spotify_id="artist123",
            rate_system=self.rate_system_2,
            content_type=ct,
            defaults={"score": 50}
        )

        old_rating_user_2.updated_at = timezone.now() - timedelta(days=1)
        old_rating_user_2.save(update_fields=["updated_at"])

       
        Rating.objects.update_or_create(
            user = self.user,
            spotify_id = "artist123",
            rate_system = self.rate_system_2,
            content_type = ct,
            defaults={"score": 22}
        )
        Rating.objects.update_or_create(
            user=self.user2,
            spotify_id="artist123",
            rate_system=self.rate_system_1,
            content_type=ct,
            defaults={"score": 57}
        )

        Rating.objects.update_or_create(
            user = self.user3,
            spotify_id = "artist123",
            rate_system=self.rate_system_1,
            content_type=ct,
            defaults={"score": 8}
        )

        self.assertEqual(community_rating_for_artist("artist123"), 29)


# ============================================================================
# TESTS WRITTEN BY COPILOT - Serializer Tests, API Integration Tests, 
# and Database Constraint Tests
# ============================================================================

class RatingSerializerTests(TestCase):
    """Test suite for RatingSerializer with both rate systems and error handling."""
    
    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username="testuser", password="testpass123")
        self.user2 = User.objects.create_user(username="testuser2", password="testpass123")
        self.rate_system_explicit = RateSystem.objects.create(key="explicit")
        self.rate_system_average = RateSystem.objects.create(key="average")
        self.album = Album.objects.create(spotify_id="album123", artist_spotify_id="artist123")
        self.song = Song.objects.create(spotify_id="song123", album_spotify_id="album123")

    def _create_request_with_user(self, user):
        """Helper to create a request with authenticated user."""
        request = self.factory.post("/api/ratings")
        request.user = user
        return request

    # Success Tests - Explicit Rate System
    def test_rating_serializer_create_explicit_with_score(self):
        """Test creating a rating with explicit rate system and score."""
        from api.serializers import RatingSerializer
        
        request = self._create_request_with_user(self.user)
        
        data = {
            "score": 85,
            "spotify_id": "album123",
            "content_type": ContentType.objects.get_for_model(Album).id,
            "rate_system": self.rate_system_explicit.id,
            "optional_writing": "Great album!"
        }
        
        serializer = RatingSerializer(data=data, context={"request": request})
        self.assertTrue(serializer.is_valid(), msg=serializer.errors)
        serializer.save()
        
        rating = Rating.objects.filter(
            user=self.user,
            spotify_id="album123",
            rate_system=self.rate_system_explicit
        ).first()
        self.assertIsNotNone(rating)
        self.assertEqual(rating.score, 85)
        self.assertEqual(rating.optional_writing, "Great album!")

    def test_rating_serializer_create_explicit_without_writing(self):
        """Test creating a rating without optional writing."""
        from api.serializers import RatingSerializer
        
        request = self._create_request_with_user(self.user)
        
        data = {
            "score": 75,
            "spotify_id": "song123",
            "content_type": ContentType.objects.get_for_model(Song).id,
            "rate_system": self.rate_system_explicit.id,
        }
        
        serializer = RatingSerializer(data=data, context={"request": request})
        self.assertTrue(serializer.is_valid(), msg=serializer.errors)
        serializer.save()
        
        rating = Rating.objects.filter(
            user=self.user,
            spotify_id="song123",
            rate_system=self.rate_system_explicit
        ).first()
        self.assertIsNotNone(rating)
        self.assertIsNone(rating.optional_writing)

    # Success Tests - Average Rate System (calculates from song ratings)
    def test_rating_serializer_create_average_for_album(self):
        """Test creating an average rating for an album based on song ratings."""
        from api.serializers import RatingSerializer
        
        # Set up: create multiple song ratings
        song1 = Song.objects.create(spotify_id="song_a", album_spotify_id="album123")
        song2 = Song.objects.create(spotify_id="song_b", album_spotify_id="album123")
        
        Rating.objects.create(
            user=self.user,
            spotify_id="song_a",
            content_type=ContentType.objects.get_for_model(Song),
            rate_system=self.rate_system_explicit,
            score=80
        )
        Rating.objects.create(
            user=self.user,
            spotify_id="song_b",
            content_type=ContentType.objects.get_for_model(Song),
            rate_system=self.rate_system_explicit,
            score=90
        )
        
        request = self._create_request_with_user(self.user)
        
        # Note: score is provided but will be overwritten by the average calculation
        data = {
            "score": 50,  # This will be replaced by the average
            "spotify_id": "album123",
            "content_type": ContentType.objects.get_for_model(Album).id,
            "rate_system": self.rate_system_average.id,
            "optional_writing": "Good songs"
        }
        
        serializer = RatingSerializer(data=data, context={"request": request})
        self.assertTrue(serializer.is_valid(), msg=serializer.errors)
        serializer.save()
        
        # Verify the average was calculated and stored (not the provided 50)
        rating = Rating.objects.filter(
            user=self.user,
            spotify_id="album123",
            rate_system=self.rate_system_average
        ).first()
        self.assertIsNotNone(rating)
        self.assertEqual(rating.score, 85)  # (80 + 90) / 2 = 85, not 50

    def test_rating_serializer_update_existing_rating(self):
        """Test updating an existing rating (update_or_create behavior)."""
        from api.serializers import RatingSerializer
        
        # Create initial rating
        initial_rating = Rating.objects.create(
            user=self.user,
            spotify_id="album123",
            content_type=ContentType.objects.get_for_model(Album),
            rate_system=self.rate_system_explicit,
            score=50,
            optional_writing="Initial"
        )
        
        request = self._create_request_with_user(self.user)
        
        # Update with new data
        data = {
            "score": 90,
            "spotify_id": "album123",
            "content_type": ContentType.objects.get_for_model(Album).id,
            "rate_system": self.rate_system_explicit.id,
            "optional_writing": "Updated!"
        }
        
        serializer = RatingSerializer(data=data, context={"request": request})
        self.assertTrue(serializer.is_valid(), msg=serializer.errors)
        serializer.save()
        
        # Verify only one rating exists and it's updated
        ratings = Rating.objects.filter(
            user=self.user,
            spotify_id="album123",
            rate_system=self.rate_system_explicit
        )
        self.assertEqual(ratings.count(), 1)
        self.assertEqual(ratings.first().score, 90)
        self.assertEqual(ratings.first().optional_writing, "Updated!")

    # Validation Failure Tests
    def test_rating_serializer_score_above_100(self):
        """Test that score above 100 raises validation error."""
        from api.serializers import RatingSerializer
        
        request = self._create_request_with_user(self.user)
        
        data = {
            "score": 101,
            "spotify_id": "album123",
            "content_type": ContentType.objects.get_for_model(Album).id,
            "rate_system": self.rate_system_explicit.id,
        }
        
        serializer = RatingSerializer(data=data, context={"request": request})
        self.assertFalse(serializer.is_valid())
        self.assertIn("score", serializer.errors)
        self.assertIn("between 0 and 100", str(serializer.errors["score"]))

    def test_rating_serializer_score_below_0(self):
        """Test that score below 0 raises validation error."""
        from api.serializers import RatingSerializer
        
        request = self._create_request_with_user(self.user)
        
        data = {
            "score": -5,
            "spotify_id": "album123",
            "content_type": ContentType.objects.get_for_model(Album).id,
            "rate_system": self.rate_system_explicit.id,
        }
        
        serializer = RatingSerializer(data=data, context={"request": request})
        self.assertFalse(serializer.is_valid())
        self.assertIn("score", serializer.errors)
        self.assertIn("between 0 and 100", str(serializer.errors["score"]))

    def test_rating_serializer_score_non_integer(self):
        """Test that non-integer score raises validation error."""
        from api.serializers import RatingSerializer
        
        request = self._create_request_with_user(self.user)
        
        data = {
            "score": "not_a_number",
            "spotify_id": "album123",
            "content_type": ContentType.objects.get_for_model(Album).id,
            "rate_system": self.rate_system_explicit.id,
        }
        
        serializer = RatingSerializer(data=data, context={"request": request})
        self.assertFalse(serializer.is_valid())
        self.assertIn("score", serializer.errors)
        self.assertIn("A valid integer is required", str(serializer.errors["score"]))

    def test_rating_serializer_score_float(self):
        """Test that float score raises validation error."""
        from api.serializers import RatingSerializer
        
        request = self._create_request_with_user(self.user)
        
        data = {
            "score": 85.5,
            "spotify_id": "album123",
            "content_type": ContentType.objects.get_for_model(Album).id,
            "rate_system": self.rate_system_explicit.id,
        }
        
        serializer = RatingSerializer(data=data, context={"request": request})
        self.assertFalse(serializer.is_valid())
        self.assertIn("score", serializer.errors)
    
    def test_serializer_creates_average_score_when_score_absent(self):

        from api.serializers import RatingSerializer
        
        # Set up: create multiple song ratings
        song1 = Song.objects.create(spotify_id="song_a", album_spotify_id="album123")
        song2 = Song.objects.create(spotify_id="song_b", album_spotify_id="album123")
        
        Rating.objects.create(
            user=self.user,
            spotify_id="song_a",
            content_type=ContentType.objects.get_for_model(Song),
            rate_system=self.rate_system_explicit,
            score=80
        )
        Rating.objects.create(
            user=self.user,
            spotify_id="song_b",
            content_type=ContentType.objects.get_for_model(Song),
            rate_system=self.rate_system_explicit,
            score=90
        )
        
        request = self._create_request_with_user(self.user)

        data = {
            "spotify_id": "album123",
            "content_type": ContentType.objects.get_for_model(Album).id,
            "rate_system": self.rate_system_average.id,
            "optional_writing": "Good songs"
        }

        serializer = RatingSerializer(data=data, context={"request": request})
        self.assertTrue(serializer.is_valid(), msg=serializer.errors)
        serializer.save()
        
        # Verify the average was calculated and stored (not the provided 50)
        rating = Rating.objects.filter(
            user=self.user,
            spotify_id="album123",
            rate_system=self.rate_system_average
        ).first()
        self.assertIsNotNone(rating)
        self.assertEqual(rating.score, 85)


class APIRatingCreateIntegrationTest(TestCase):
    """Integration test for RatingCreateView endpoint."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="testpass123")
        self.other_user = User.objects.create_user(username="otheruser", password="testpass123")
        self.rate_system_explicit = RateSystem.objects.create(key="explicit")
        self.rate_system_average = RateSystem.objects.create(key="average")
        self.album = Album.objects.create(spotify_id="album123", artist_spotify_id="artist123")
        self.song = Song.objects.create(spotify_id="song123", album_spotify_id="album123")

    def test_rating_create_authenticated_success(self):
        """Test successful rating creation when authenticated."""
        self.client.login(username="testuser", password="testpass123")
        
        data = {
            "score": 85,
            "spotify_id": "album123",
            "content_type": ContentType.objects.get_for_model(Album).id,
            "rate_system": self.rate_system_explicit.id,
            "optional_writing": "Great album!"
        }
        
        response = self.client.post(
            reverse("ratings-create"),
            data=data,
            content_type="application/json"
        )
        
        # Should succeed with status 201
        self.assertEqual(response.status_code, 201)
        
        # Verify rating was created
        rating = Rating.objects.filter(
            user=self.user,
            spotify_id="album123",
            rate_system=self.rate_system_explicit
        ).first()
        self.assertIsNotNone(rating)
        self.assertEqual(rating.score, 85)

    def test_rating_create_unauthenticated_fails(self):
        """Test that unauthenticated users cannot create ratings."""
        data = {
            "score": 85,
            "spotify_id": "album123",
            "content_type": ContentType.objects.get_for_model(Album).id,
            "rate_system": self.rate_system_explicit.id,
        }
        
        response = self.client.post(
            reverse("ratings-create"),
            data=data,
            content_type="application/json"
        )
        
        # Should fail with 403 Forbidden (DRF returns 403 when auth is required but not provided)
        self.assertEqual(response.status_code, 403)

    def test_rating_create_invalid_score(self):
        """Test that invalid scores are rejected with correct error."""
        self.client.login(username="testuser", password="testpass123")
        
        data = {
            "score": 150,
            "spotify_id": "album123",
            "content_type": ContentType.objects.get_for_model(Album).id,
            "rate_system": self.rate_system_explicit.id,
        }
        
        response = self.client.post(
            reverse("ratings-create"),
            data=data,
            content_type="application/json"
        )
        
        # Should fail with 400 Bad Request
        self.assertEqual(response.status_code, 400)
        response_data = response.json()
        self.assertIn("score", response_data)


class APIRatingDetailIntegrationTest(TestCase):
    """Integration test for RatingDetailView endpoint (Retrieve, Update, Destroy)."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="testpass123")
        self.other_user = User.objects.create_user(username="otheruser", password="testpass123")
        self.rate_system_explicit = RateSystem.objects.create(key="explicit")
        self.album = Album.objects.create(spotify_id="album123", artist_spotify_id="artist123")
        
        self.rating = Rating.objects.create(
            user=self.user,
            spotify_id="album123",
            content_type=ContentType.objects.get_for_model(Album),
            rate_system=self.rate_system_explicit,
            score=80,
            optional_writing="Original review"
        )

    def test_rating_retrieve_authenticated_success(self):
        """Test successful retrieval of a rating when authenticated."""
        self.client.login(username="testuser", password="testpass123")
        
        response = self.client.get(
            reverse("ratings-RUD", kwargs={"pk": self.rating.id})
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["score"], 80)
        self.assertEqual(data["optional_writing"], "Original review")

    def test_rating_retrieve_unauthenticated_success(self):
        """Test that unauthenticated users cannot retrieve without authentication."""
        response = self.client.get(
            reverse("ratings-RUD", kwargs={"pk": self.rating.id})
        )
        
        # RatingDetailView requires authentication, should return 403
        self.assertEqual(response.status_code, 403)

    def test_rating_update_own_rating_success(self):
        """Test that user can update their own rating."""
        self.client.login(username="testuser", password="testpass123")
        
        data = {
            "score": 95,
            "optional_writing": "Updated review!",
            "spotify_id": "album123",
            "content_type": ContentType.objects.get_for_model(Album).id,
            "rate_system": self.rate_system_explicit.id,
        }
        
        response = self.client.put(
            reverse("ratings-RUD", kwargs={"pk": self.rating.id}),
            data=data,
            content_type="application/json"
        )
        
        self.assertEqual(response.status_code, 200)
        self.rating.refresh_from_db()
        self.assertEqual(self.rating.score, 95)
        self.assertEqual(self.rating.optional_writing, "Updated review!")

    def test_rating_update_other_user_rating_fails(self):
        """Test that users cannot update other users' ratings (permission check)."""
        self.client.login(username="otheruser", password="testpass123")
        
        data = {
            "score": 50,
            "optional_writing": "Hacked!",
            "spotify_id": "album123",
            "content_type": ContentType.objects.get_for_model(Album).id,
            "rate_system": self.rate_system_explicit.id,
        }
        
        response = self.client.put(
            reverse("ratings-RUD", kwargs={"pk": self.rating.id}),
            data=data,
            content_type="application/json"
        )
        
        self.assertEqual(response.status_code, 403)
        self.rating.refresh_from_db()
        self.assertEqual(self.rating.score, 80)

    def test_rating_delete_own_rating_success(self):
        """Test that user can delete their own rating."""
        self.client.login(username="testuser", password="testpass123")
        
        response = self.client.delete(
            reverse("ratings-RUD", kwargs={"pk": self.rating.id})
        )
        
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Rating.objects.filter(id=self.rating.id).exists())

    def test_rating_delete_other_user_rating_fails(self):
        """Test that users cannot delete other users' ratings (permission check)."""
        self.client.login(username="otheruser", password="testpass123")
        
        response = self.client.delete(
            reverse("ratings-RUD", kwargs={"pk": self.rating.id})
        )
        
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Rating.objects.filter(id=self.rating.id).exists())

    def test_rating_update_invalid_score(self):
        """Test that updating with invalid score fails with correct error."""
        self.client.login(username="testuser", password="testpass123")
        
        data = {
            "score": -10,
            "optional_writing": "Bad score",
            "spotify_id": "album123",
            "content_type": ContentType.objects.get_for_model(Album).id,
            "rate_system": self.rate_system_explicit.id,
        }
        
        response = self.client.put(
            reverse("ratings-RUD", kwargs={"pk": self.rating.id}),
            data=data,
            content_type="application/json"
        )
        
        self.assertEqual(response.status_code, 400)
        response_data = response.json()
        self.assertIn("score", response_data)


class APIAlbumDetailIntegrationTest(TestCase):
    """Integration test for AlbumDetailAPIView endpoint."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="testpass123")
        self.rate_system_explicit = RateSystem.objects.create(key="explicit")
        self.album = Album.objects.create(spotify_id="album_spotify_123", artist_spotify_id="artist_spotify_456")

    @patch("api.views.spotify_handler.spotify_get_id")
    def test_album_detail_authenticated_success(self, mock_spotify_get_id):
        """Test successful album detail retrieval when authenticated."""
        mock_spotify_get_id.return_value = {
            "id": "album_spotify_123",
            "type": "album",
            "name": "Test Album",
            "artists": [{"id": "artist1", "name": "Test Artist"}],
            "tracks": {"items": [{"id": "track1", "name": "Track 1"}]}
        }
        
        self.client.login(username="testuser", password="testpass123")
        
        response = self.client.get(
            reverse("api_album_detail", kwargs={"spotify_id": "album_spotify_123"})
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("album_data", data)
        self.assertIn("community_rating", data)
        self.assertIn("user_rating", data)
        self.assertEqual(data["album_data"]["name"], "Test Album")

    @patch("api.views.spotify_handler.spotify_get_id")
    def test_album_detail_unauthenticated_success(self, mock_spotify_get_id):
        """Test that unauthenticated users can view album details (ReadOnly)."""
        mock_spotify_get_id.return_value = {
            "id": "album_spotify_123",
            "type": "album",
            "name": "Test Album",
            "artists": [{"id": "artist1", "name": "Test Artist"}],
            "tracks": {"items": []}
        }
        
        response = self.client.get(
            reverse("api_album_detail", kwargs={"spotify_id": "album_spotify_123"})
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsNone(data["user_rating"])

    @patch("api.views.spotify_handler.spotify_get_id")
    def test_album_detail_spotify_error(self, mock_spotify_get_id):
        """Test handling of Spotify API errors."""
        mock_spotify_get_id.return_value = None
        
        response = self.client.get(
            reverse("api_album_detail", kwargs={"spotify_id": "invalid_id"})
        )
        
        self.assertEqual(response.status_code, 500)
        data = response.json()
        self.assertIn("detail", data)


class APISongDetailIntegrationTest(TestCase):
    """Integration test for SongDetailAPIView endpoint."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="testpass123")
        self.rate_system_explicit = RateSystem.objects.create(key="explicit")
        self.song = Song.objects.create(spotify_id="song_spotify_123", album_spotify_id="album_spotify_123")

    @patch("api.views.spotify_handler.spotify_get_id")
    def test_song_detail_authenticated_success(self, mock_spotify_get_id):
        """Test successful song detail retrieval when authenticated."""
        mock_spotify_get_id.return_value = {
            "id": "song_spotify_123",
            "type": "track",
            "name": "Test Song",
            "artists": [{"id": "artist1", "name": "Test Artist"}],
            "album": {"id": "album1", "name": "Test Album"}
        }
        
        self.client.login(username="testuser", password="testpass123")
        
        response = self.client.get(
            reverse("api_song_detail", kwargs={"spotify_id": "song_spotify_123"})
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("song_data", data)
        self.assertIn("community_rating", data)
        self.assertIn("user_rating", data)
        self.assertEqual(data["song_data"]["name"], "Test Song")

    @patch("api.views.spotify_handler.spotify_get_id")
    def test_song_detail_unauthenticated_success(self, mock_spotify_get_id):
        """Test that unauthenticated users can view song details."""
        mock_spotify_get_id.return_value = {
            "id": "song_spotify_123",
            "type": "track",
            "name": "Test Song",
            "artists": [{"id": "artist1", "name": "Test Artist"}],
            "album": {"id": "album1", "name": "Test Album"}
        }
        
        response = self.client.get(
            reverse("api_song_detail", kwargs={"spotify_id": "song_spotify_123"})
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsNone(data["user_rating"])

    @patch("api.views.spotify_handler.spotify_get_id")
    def test_song_detail_spotify_error(self, mock_spotify_get_id):
        """Test handling of Spotify API errors."""
        mock_spotify_get_id.return_value = None
        
        response = self.client.get(
            reverse("api_song_detail", kwargs={"spotify_id": "invalid_id"})
        )
        
        self.assertEqual(response.status_code, 500)


class APIArtistDetailIntegrationTest(TestCase):
    """Integration test for ArtistDetailAPIView endpoint."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="testpass123")
        self.rate_system_explicit = RateSystem.objects.create(key="explicit")
        self.artist = Artist.objects.create(spotify_id="artist_spotify_123")

    @patch("api.views.spotify_handler.spotify_get_id")
    def test_artist_detail_authenticated_success(self, mock_spotify_get_id):
        """Test successful artist detail retrieval when authenticated."""
        mock_spotify_get_id.return_value = {
            "id": "artist_spotify_123",
            "type": "artist",
            "name": "Test Artist",
            "artist_albums": [],
            "artist_singles": [],
            "artist_eps": []
        }
        
        self.client.login(username="testuser", password="testpass123")
        
        response = self.client.get(
            reverse("api_artist_detail", kwargs={"spotify_id": "artist_spotify_123"})
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("artist_data", data)
        self.assertIn("community_rating", data)
        self.assertIn("user_rating", data)
        self.assertEqual(data["artist_data"]["name"], "Test Artist")

    @patch("api.views.spotify_handler.spotify_get_id")
    def test_artist_detail_unauthenticated_success(self, mock_spotify_get_id):
        """Test that unauthenticated users can view artist details."""
        mock_spotify_get_id.return_value = {
            "id": "artist_spotify_123",
            "type": "artist",
            "name": "Test Artist",
            "artist_albums": [],
            "artist_singles": [],
            "artist_eps": []
        }
        
        response = self.client.get(
            reverse("api_artist_detail", kwargs={"spotify_id": "artist_spotify_123"})
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsNone(data["user_rating"])

    @patch("api.views.spotify_handler.spotify_get_id")
    def test_artist_detail_spotify_error(self, mock_spotify_get_id):
        """Test handling of Spotify API errors."""
        mock_spotify_get_id.return_value = None
        
        response = self.client.get(
            reverse("api_artist_detail", kwargs={"spotify_id": "invalid_id"})
        )
        
        self.assertEqual(response.status_code, 500)


class RatingDatabaseConstraintTests(TestCase):
    """Test database constraints for Rating model."""
    
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass123")
        self.rate_system_explicit = RateSystem.objects.create(key="explicit")
        self.album = Album.objects.create(spotify_id="album123", artist_spotify_id="artist123")
        self.album_content_type = ContentType.objects.get_for_model(Album)

    def test_unique_constraint_same_user_spotify_item_rate_system(self):
        """Test UniqueConstraint prevents duplicate ratings for same user/item/system."""
        Rating.objects.create(
            user=self.user,
            spotify_id="album123",
            content_type=self.album_content_type,
            rate_system=self.rate_system_explicit,
            score=80
        )
        
        # Attempting to create duplicate should raise IntegrityError
        from django.db import IntegrityError
        
        with self.assertRaises(IntegrityError):
            Rating.objects.create(
                user=self.user,
                spotify_id="album123",
                content_type=self.album_content_type,
                rate_system=self.rate_system_explicit,
                score=90
            )

    def test_unique_constraint_different_users_allowed(self):
        """Test that different users can rate the same item."""
        user2 = User.objects.create_user(username="testuser2", password="testpass123")
        
        rating1 = Rating.objects.create(
            user=self.user,
            spotify_id="album123",
            content_type=self.album_content_type,
            rate_system=self.rate_system_explicit,
            score=80
        )
        
        rating2 = Rating.objects.create(
            user=user2,
            spotify_id="album123",
            content_type=self.album_content_type,
            rate_system=self.rate_system_explicit,
            score=90
        )
        
        self.assertEqual(rating1.score, 80)
        self.assertEqual(rating2.score, 90)

    def test_unique_constraint_different_rate_systems_allowed(self):
        """Test that same user can rate item with different rate systems."""
        rate_system_average = RateSystem.objects.create(key="average")
        
        rating1 = Rating.objects.create(
            user=self.user,
            spotify_id="album123",
            content_type=self.album_content_type,
            rate_system=self.rate_system_explicit,
            score=80
        )
        
        rating2 = Rating.objects.create(
            user=self.user,
            spotify_id="album123",
            content_type=self.album_content_type,
            rate_system=rate_system_average,
            score=75  # All ratings must have scores now
        )
        
        self.assertEqual(
            Rating.objects.filter(user=self.user, spotify_id="album123").count(), 2
        )

    def test_check_constraint_score_at_minimum(self):
        """Test CheckConstraint allows score of 0."""
        rating = Rating.objects.create(
            user=self.user,
            spotify_id="album123",
            content_type=self.album_content_type,
            rate_system=self.rate_system_explicit,
            score=0
        )
        
        self.assertEqual(rating.score, 0)

    def test_check_constraint_score_at_maximum(self):
        """Test CheckConstraint allows score of 100."""
        rating = Rating.objects.create(
            user=self.user,
            spotify_id="album123",
            content_type=self.album_content_type,
            rate_system=self.rate_system_explicit,
            score=100
        )
        
        self.assertEqual(rating.score, 100)

    def test_check_constraint_score_below_zero_fails(self):
        """Test CheckConstraint prevents score below 0."""
        from django.db import IntegrityError
        
        with self.assertRaises(IntegrityError):
            Rating.objects.create(
                user=self.user,
                spotify_id="album123",
                content_type=self.album_content_type,
                rate_system=self.rate_system_explicit,
                score=-1
            )

    def test_check_constraint_score_above_100_fails(self):
        """Test CheckConstraint prevents score above 100."""
        from django.db import IntegrityError
        
        with self.assertRaises(IntegrityError):
            Rating.objects.create(
                user=self.user,
                spotify_id="album123",
                content_type=self.album_content_type,
                rate_system=self.rate_system_explicit,
                score=101
            )