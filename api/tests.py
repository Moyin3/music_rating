from django.test import TestCase, Client, RequestFactory
from music_rating.models import Song, Artist, Album, Single, EP, Rating, RateSystem
from unittest.mock import patch, Mock
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse


User = get_user_model()

class RatingSerializerTests(TestCase):
    """Test suite for RatingSerializer with both rate systems and error handling."""

    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.user2 = User.objects.create_user(
            username="testuser2", password="testpass123"
        )
        self.rate_system_explicit = RateSystem.objects.create(key="explicit")
        self.rate_system_average = RateSystem.objects.create(key="average")
        self.album = Album.objects.create(
            spotify_id="album123", artist_spotify_id="artist123"
        )
        self.song = Song.objects.create(
            spotify_id="song123", album_spotify_id="album123"
        )

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
            "optional_writing": "Great album!",
        }

        serializer = RatingSerializer(data=data, context={"request": request})
        self.assertTrue(serializer.is_valid(), msg=serializer.errors)
        serializer.save()

        rating = Rating.objects.filter(
            user=self.user, spotify_id="album123", rate_system=self.rate_system_explicit
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
            user=self.user, spotify_id="song123", rate_system=self.rate_system_explicit
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
            score=80,
        )
        Rating.objects.create(
            user=self.user,
            spotify_id="song_b",
            content_type=ContentType.objects.get_for_model(Song),
            rate_system=self.rate_system_explicit,
            score=90,
        )

        request = self._create_request_with_user(self.user)

        # Note: score is provided but will be overwritten by the average calculation
        data = {
            "score": 50,  # This will be replaced by the average
            "spotify_id": "album123",
            "content_type": ContentType.objects.get_for_model(Album).id,
            "rate_system": self.rate_system_average.id,
            "optional_writing": "Good songs",
        }

        serializer = RatingSerializer(data=data, context={"request": request})
        self.assertTrue(serializer.is_valid(), msg=serializer.errors)
        serializer.save()

        # Verify the average was calculated and stored (not the provided 50)
        rating = Rating.objects.filter(
            user=self.user, spotify_id="album123", rate_system=self.rate_system_average
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
            optional_writing="Initial",
        )

        request = self._create_request_with_user(self.user)

        # Update with new data
        data = {
            "score": 90,
            "spotify_id": "album123",
            "content_type": ContentType.objects.get_for_model(Album).id,
            "rate_system": self.rate_system_explicit.id,
            "optional_writing": "Updated!",
        }

        serializer = RatingSerializer(data=data, context={"request": request})
        self.assertTrue(serializer.is_valid(), msg=serializer.errors)
        serializer.save()

        # Verify only one rating exists and it's updated
        ratings = Rating.objects.filter(
            user=self.user, spotify_id="album123", rate_system=self.rate_system_explicit
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
            score=80,
        )
        Rating.objects.create(
            user=self.user,
            spotify_id="song_b",
            content_type=ContentType.objects.get_for_model(Song),
            rate_system=self.rate_system_explicit,
            score=90,
        )

        request = self._create_request_with_user(self.user)

        data = {
            "spotify_id": "album123",
            "content_type": ContentType.objects.get_for_model(Album).id,
            "rate_system": self.rate_system_average.id,
            "optional_writing": "Good songs",
        }

        serializer = RatingSerializer(data=data, context={"request": request})
        self.assertTrue(serializer.is_valid(), msg=serializer.errors)
        serializer.save()

        # Verify the average was calculated and stored (not the provided 50)
        rating = Rating.objects.filter(
            user=self.user, spotify_id="album123", rate_system=self.rate_system_average
        ).first()
        self.assertIsNotNone(rating)
        self.assertEqual(rating.score, 85)


class APIRatingCreateIntegrationTest(TestCase):
    """Integration test for RatingCreateView endpoint."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.other_user = User.objects.create_user(
            username="otheruser", password="testpass123"
        )
        self.rate_system_explicit = RateSystem.objects.create(key="explicit")
        self.rate_system_average = RateSystem.objects.create(key="average")
        self.album = Album.objects.create(
            spotify_id="album123", artist_spotify_id="artist123"
        )
        self.song = Song.objects.create(
            spotify_id="song123", album_spotify_id="album123"
        )

    def test_rating_create_authenticated_success(self):
        """Test successful rating creation when authenticated."""
        self.client.login(username="testuser", password="testpass123")

        data = {
            "score": 85,
            "spotify_id": "album123",
            "content_type": ContentType.objects.get_for_model(Album).id,
            "rate_system": self.rate_system_explicit.id,
            "optional_writing": "Great album!",
        }

        response = self.client.post(
            reverse("ratings-create"), data=data, content_type="application/json"
        )

        # Should succeed with status 201
        self.assertEqual(response.status_code, 201)

        # Verify rating was created
        rating = Rating.objects.filter(
            user=self.user, spotify_id="album123", rate_system=self.rate_system_explicit
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
            reverse("ratings-create"), data=data, content_type="application/json"
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
            reverse("ratings-create"), data=data, content_type="application/json"
        )

        # Should fail with 400 Bad Request
        self.assertEqual(response.status_code, 400)
        response_data = response.json()
        self.assertIn("score", response_data)


class APIRatingDetailIntegrationTest(TestCase):
    """Integration test for RatingDetailView endpoint (Retrieve, Update, Destroy)."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.other_user = User.objects.create_user(
            username="otheruser", password="testpass123"
        )
        self.rate_system_explicit = RateSystem.objects.create(key="explicit")
        self.album = Album.objects.create(
            spotify_id="album123", artist_spotify_id="artist123"
        )

        self.rating = Rating.objects.create(
            user=self.user,
            spotify_id="album123",
            content_type=ContentType.objects.get_for_model(Album),
            rate_system=self.rate_system_explicit,
            score=80,
            optional_writing="Original review",
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
            content_type="application/json",
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
            content_type="application/json",
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
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        response_data = response.json()
        self.assertIn("score", response_data)


class APIAlbumDetailIntegrationTest(TestCase):
    """Integration test for AlbumDetailAPIView endpoint."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.rate_system_explicit = RateSystem.objects.create(key="explicit")
        self.album = Album.objects.create(
            spotify_id="album_spotify_123", artist_spotify_id="artist_spotify_456"
        )

    @patch("api.views.spotify_handler.spotify_get_id")
    def test_album_detail_authenticated_success(self, mock_spotify_get_id):
        """Test successful album detail retrieval when authenticated."""
        mock_spotify_get_id.return_value = {
            "id": "album_spotify_123",
            "type": "album",
            "name": "Test Album",
            "artists": [{"id": "artist1", "name": "Test Artist"}],
            "tracks": {"items": [{"id": "track1", "name": "Track 1"}]},
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
            "tracks": {"items": []},
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
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.rate_system_explicit = RateSystem.objects.create(key="explicit")
        self.song = Song.objects.create(
            spotify_id="song_spotify_123", album_spotify_id="album_spotify_123"
        )

    @patch("api.views.spotify_handler.spotify_get_id")
    def test_song_detail_authenticated_success(self, mock_spotify_get_id):
        """Test successful song detail retrieval when authenticated."""
        mock_spotify_get_id.return_value = {
            "id": "song_spotify_123",
            "type": "track",
            "name": "Test Song",
            "artists": [{"id": "artist1", "name": "Test Artist"}],
            "album": {"id": "album1", "name": "Test Album"},
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
            "album": {"id": "album1", "name": "Test Album"},
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
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
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
            "artist_eps": [],
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
            "artist_eps": [],
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



class DetailViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.explicit = RateSystem.objects.create(key="explicit")
        self.average = RateSystem.objects.create(key="average")

    @patch("api.views.spotify_handler.spotify_get_id")
    def test_album_detail_success(self, mock_spotify_get_id):
        # Mock Spotify API response
        mock_response_data = {
            "id": "test-spotify-id",
            "type": "album",
            "name": "Test Album",
            "artists": [{"id": "artist1-id", "name": "Test Artist"}],
            "tracks": {
                "items": [
                    {"id": "track1-id", "name": "Track 1"},
                    {"id": "track2-id", "name": "Track 2"},
                ]
            },
        }