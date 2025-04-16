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


class ArtistModelTest(TestCase):
    def setUp(self):
        self.artist = Artist.objects.create(
            spotify_id="12345",
            artist_name="Test Artist",
        )

    def test_artist_str(self):
        self.assertEqual(str(self.artist), "Test Artist")

    def test_artist_fields(self):
        self.assertEqual(self.artist.spotify_id, "12345")
        self.assertEqual(self.artist.artist_name, "Test Artist")

class SongModelTest(TestCase):
    def setUp(self):
        self.artist1 = Artist.objects.create(spotify_id="12345", artist_name="Artist 1")
        self.artist2 = Artist.objects.create(spotify_id="67890", artist_name="Artist 2")
        self.song = Song.objects.create(
            spotify_id="54321",
            song_name="Test Song",
        )
        self.song.artists.add(self.artist1, self.artist2)

    def test_song_str(self):
        self.assertEqual(str(self.song), "Test Song")
    
    def test_song_fields(self):
        self.assertEqual(self.song.spotify_id, "54321")
        self.assertEqual(self.song.song_name, "Test Song")

    def test_song_get_artist_names(self):
        self.assertEqual(self.song.get_artist_names, "Artist 1, Artist 2")

class AlbumModelTest(TestCase):
    def setUp(self):
        self.artist1 = Artist.objects.create(spotify_id="12345", artist_name="Artist 1")
        self.artist2 = Artist.objects.create(spotify_id="67890", artist_name="Artist 2")
        self.album = Album.objects.create(
            spotify_id="11111",
            album_name="Test Album",
        )
        self.album.artists.add(self.artist1, self.artist2)

    def test_album_str(self):
        self.assertEqual(str(self.album), "Test Album")
    
    def test_album_fields(self):
        self.assertEqual(self.album.spotify_id, "11111")
        self.assertEqual(self.album.album_name, "Test Album")

    def test_album_get_artist_names(self):
        self.assertEqual(self.album.get_artist_names, "Artist 1, Artist 2")

class SingleModelTest(TestCase):
    def setUp(self):
        self.artist = Artist.objects.create(spotify_id="12345", artist_name="Artist 1")
        self.single = Single.objects.create(
            spotify_id="22222",
            single_name="Test Single",
        )
        self.single.artists.add(self.artist)

    def test_single_str(self):
        self.assertEqual(str(self.single), "Test Single")
    
    def test_single_fields(self):
        self.assertEqual(self.single.spotify_id, "22222")
        self.assertEqual(self.single.single_name, "Test Single")

    def test_single_get_artist_names(self):
        self.assertEqual(self.single.get_artist_names, "Artist 1")

class EPModelTest(TestCase):
    def setUp(self):
        self.artist = Artist.objects.create(spotify_id="12345", artist_name="Artist 1")
        self.ep = EP.objects.create(
            spotify_id="33333",
            ep_name="Test EP",
        )
        self.ep.artists.add(self.artist)

    def test_ep_str(self):
        self.assertEqual(str(self.ep), "Test EP")
    
    def test_ep_fields(self):
        self.assertEqual(self.ep.spotify_id, "33333")
        self.assertEqual(self.ep.ep_name, "Test EP")

    def test_ep_get_artist_names(self):
        self.assertEqual(self.ep.get_artist_names, "Artist 1")
    
class RatingModelTest(TestCase):
    def setUp(self):
        self.rating = Rating.objects.create(score=4.5)

    def test_rating_score(self):
        self.assertEqual(self.rating.score, 4.5)
    
class RateSystemModelTest(TestCase):
    def setUp(self):
        self.rate_system = RateSystem.objects.create(
            name="Custom Rate System",
            description="A custom rating system",
        )

    def test_rate_system_str(self):
        self.assertEqual(str(self.rate_system), "Custom Rate System")

class ViewTests(TestCase):
    def test_entrypage_view(self):
        client = Client()
        response = client.get('/entries/') 
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'music_rating/entrypage.html')
    
    def test_userhome_view(self):
        client = Client()
        response = client.get('')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'music_rating/userhome.html')
    
    def test_artistpage_view(self):
        client = Client()
        response = client.get('/artists/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'music_rating/artistpage.html')
    
    def test_albumpage_view(self):
        client = Client()
        response = client.get('/albums/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'music_rating/albumpage.html')
    
    def test_songspage_view(self):
        client = Client()
        response = client.get('/songs/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'music_rating/songspage.html')
    
    def test_compage_view(self):
        client = Client()
        response = client.get('/community/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'music_rating/compage.html')

class DetailViewTests(TestCase):
    def setUp(self):
        self.client = Client()

    @patch('music_rating.views.spotify_handler.spotify_get_id')
    def test_album_detail_success(self, mock_spotify_get_id):
        # Mock Spotify API response
        mock_response_data = {
            "album_name": "Test Album",
            "artist_name": "Test Artist",
            "tracks": ["Track 1", "Track 2"]
        }
        mock_spotify_get_id.return_value = JsonResponse(mock_response_data, status=200)

        # Call the view
        url = reverse('album_detail', args=['test-spotify-id'])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'music_rating/album_detail.html')
        self.assertContains(response, "Test Album")
        #self.assertContains(response, "Test Artist")

    @patch('music_rating.views.spotify_handler.spotify_get_id')
    def test_song_detail_success(self, mock_spotify_get_id):
        # Mock Spotify API response
        mock_response_data = {
            "track_name": "Test Song",
            "artist_name": ["Artist 1", "Artist 2"],
            "artist_id": ["id1", "id2"],
            "album_name": "Test Album",
            "album_id": "album1"
        }
        mock_spotify_get_id.return_value = JsonResponse(mock_response_data, status=200)

        # Generate the URL dynamically
        url = reverse('song_detail', args=['test-spotify-id'])
        response = self.client.get(url)

        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'music_rating/song_detail.html')
        self.assertContains(response, "Test Song")
        self.assertContains(response, "Test Album")
        self.assertContains(response, "Artist 1")
        self.assertContains(response, "Artist 2")
        self.assertContains(response, '<a href="/artist/id1/">Artist 1</a>', html=True)
        self.assertContains(response, '<a href="/artist/id2/">Artist 2</a>', html=True)

    @patch('music_rating.views.spotify_handler.spotify_get_id')
    def test_artist_detail_success(self, mock_spotify_get_id):
        # Mock Spotify API response
        mock_response_data = {
            "artist_name": "Test Artist",
            "albums": ["Album 1", "Album 2"],
            "songs": ["Song 1", "Song 2"]
        }
        mock_spotify_get_id.return_value = JsonResponse(mock_response_data, status=200)

        # Call the view
        url = reverse('artist_detail', args=['test-spotify-id'])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'music_rating/artist_detail.html')
        self.assertContains(response, "Test Artist")
        #self.assertContains(response, "Album 1")

    @patch('music_rating.views.spotify_handler.spotify_get_id')
    def test_album_detail_error(self, mock_spotify_get_id):
        # Mock Spotify API error response
        mock_spotify_get_id.return_value = JsonResponse({}, status=404)

        # Call the view
        url = reverse('album_detail', args=['test-spotify-id'])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 500)
        self.assertContains(response, "Error retrieving album details", status_code=500)

    @patch('music_rating.views.spotify_handler.spotify_get_id')
    def test_song_detail_error(self, mock_spotify_get_id):
        # Mock Spotify API error response
        mock_spotify_get_id.return_value = JsonResponse({}, status=404)

        # Call the view
        url = reverse('song_detail', args=['test-spotify-id'])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 500)
        self.assertContains(response, "Error retrieving song details", status_code=500)

    @patch('music_rating.views.spotify_handler.spotify_get_id')
    def test_artist_detail_error(self, mock_spotify_get_id):
        # Mock Spotify API error response
        mock_spotify_get_id.return_value = JsonResponse({}, status=404)

        # Call the view
        url = reverse('artist_detail', args=['test-spotify-id'])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 500)
        self.assertContains(response, "Error retrieving artist details", status_code=500)
  
class SpotifyUtilsTests(TestCase):
    def setUp(self):
        self.spotify_utils = SpotifyUtils()
        self.factory = RequestFactory()
    
    @patch('music_rating.utils.spotify.requests.post')  # Mock requests.post
    def test_get_access_token_success(self, mock_post):
        # Mock a successful token response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'access_token': 'mock_access_token',
            'expires_in': 3600
        }
        mock_post.return_value = mock_response

        # Simulate a request without a valid token in the session
        request = self.factory.get('/')
        request.session = {}

        # Call the method
        token = self.spotify_utils._get_access_token(request)

        # Assertions
        self.assertEqual(token, 'mock_access_token')
        self.assertIn('access_token', request.session)
        self.assertIn('token_expiry_time', request.session)
        mock_post.assert_called_once()  # API call should be made

    @patch('music_rating.utils.spotify.requests.post')
    def test_get_access_token_failure(self, mock_post):
        # Mock a failed token response
        mock_response = Mock()
        mock_response.status_code = 400
        mock_post.return_value = mock_response

        # Simulate a request
        request = self.factory.get('/')
        request.session = {}

        # Call the method
        token = self.spotify_utils._get_access_token(request)

        # Assertions
        self.assertIsNone(token)
    
    @patch('music_rating.utils.spotify.requests.post')  # Mock requests.post
    def test_get_access_token_with_valid_token(self, mock_post):
        # Simulate a request with a valid token in the session
        request = self.factory.get('/')
        request.session = {
            'access_token': 'mock_access_token',
            'token_expiry_time': time.time() + 3600  # Token expires in 1 hour
        }

        # Call the method
        token = self.spotify_utils._get_access_token(request)

        # Assertions
        self.assertEqual(token, 'mock_access_token')  # Should return the existing token
        mock_post.assert_not_called()  # No API call should be made
    
    @patch('music_rating.utils.spotify.requests.post')  # Mock requests.post
    def test_get_access_token_expired_token(self, mock_post):
        # Mock a successful token response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'access_token': 'new_mock_access_token',
            'expires_in': 3600
        }
        mock_post.return_value = mock_response

        # Simulate a request with an expired token in the session
        request = self.factory.get('/')
        request.session = {
            'access_token': 'expired_mock_access_token',
            'token_expiry_time': time.time() - 3600  # Token expired 1 hour ago
        }

        # Call the method
        token = self.spotify_utils._get_access_token(request)

        # Assertions
        self.assertEqual(token, 'new_mock_access_token')  # Should retrieve a new token
        self.assertIn('access_token', request.session)
        self.assertIn('token_expiry_time', request.session)
        self.assertGreater(request.session['token_expiry_time'], time.time())
        mock_post.assert_called_once()  # API call should be made
    
    @patch('music_rating.utils.spotify.requests.get')  # Mock requests.get
    @patch('music_rating.utils.spotify.SpotifyUtils._get_access_token')  # Mock _get_access_token
    def test_spotify_search_success(self, mock_get_access_token, mock_requests_get):
        # Mock the access token
        mock_get_access_token.return_value = "mock_access_token"

        # Mock the Spotify API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'tracks': {
                'items': [
                    {'name': 'Test Track', 'id': 'track123'},
                ]
            }
        }
        mock_requests_get.return_value = mock_response

        # Simulate a request
        request = self.factory.get('/?query=Test')
        request.session = {}

        # Call the method
        response = self.spotify_utils.spotify_search(request)

        # Assertions
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content.decode('utf-8'))
        self.assertIn('tracks', response_data)
        self.assertEqual(response_data['tracks']['items'][0]['name'], 'Test Track')
        self.assertEqual(response_data['tracks']['items'][0]['id'], 'track123')

    @patch('music_rating.utils.spotify.requests.get')
    @patch('music_rating.utils.spotify.SpotifyUtils._get_access_token')
    def test_spotify_search_failure(self, mock_get_access_token, mock_requests_get):
        # Mock the access token
        mock_get_access_token.return_value = "mock_access_token"

        # Mock a failed Spotify API response
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {'error': 'Failed to fetch data from Spotify'}
        mock_requests_get.return_value = mock_response

        # Simulate a request
        request = self.factory.get('/?query=Test')
        request.session = {}

        # Call the method
        response = self.spotify_utils.spotify_search(request)

        # Assertions
        self.assertEqual(response.status_code, 400)
        
        response_data = json.loads(response.content.decode('utf-8'))
        self.assertIn('error', response_data)
        self.assertEqual(response_data['error'], 'Failed to fetch data from Spotify')
    
    @patch('music_rating.utils.spotify.requests.get')  # Mock requests.get
    @patch('music_rating.utils.spotify.cache')  # Mock cache
    @patch('music_rating.utils.spotify.SpotifyUtils._get_access_token')  # Mock _get_access_token
    def test_spotify_get_id_success(self, mock_get_access_token, mock_cache, mock_requests_get):
        # Mock the access token
        mock_get_access_token.return_value = "mock_access_token"

        # Mock the cache
        mock_cache.get.return_value = None  # No cached data

        # Mock the Spotify API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'id': 'test_spotify_id',
            'type': 'track',
            'name': 'Test Track',
            'album': {'name': 'Test Album', 'id': 'album123'},
            'artists': [{'name': 'Test Artist', 'id': 'artist123'}]
        }
        mock_requests_get.return_value = mock_response

        # Simulate a request
        request = self.factory.get('/?spotify_id=test_spotify_id&type=track')
        request.session = {}

class ParseSpotifyItemTests(TestCase):
    def setUp(self):
        self.spotify_utils = SpotifyUtils()

    def test_parse_artist_data(self):
        # Mock artist data
        artist_data = {
            'id': 'artist123',
            'type': 'artist',
            'name': 'Test Artist'
        }

        # Call the method
        parsed = self.spotify_utils._parse_spotify_item(artist_data)

        # Assertions
        self.assertEqual(parsed['id'], 'artist123')
        self.assertEqual(parsed['type'], 'artists')
        self.assertEqual(parsed['artist_name'], 'Test Artist')

    def test_parse_album_data(self):
        # Mock album data
        album_data = {
            'id': 'album123',
            'type': 'album',
            'name': 'Test Album',
            'artists': [
                {'name': 'Artist One', 'id': 'artist1'},
                {'name': 'Artist Two', 'id': 'artist2'}
            ]
        }

        # Call the method
        parsed = self.spotify_utils._parse_spotify_item(album_data)

        # Assertions
        self.assertEqual(parsed['id'], 'album123')
        self.assertEqual(parsed['type'], 'albums')
        self.assertEqual(parsed['album_name'], 'Test Album')
        self.assertEqual(parsed['artist_name'], ['Artist One', 'Artist Two'])
        self.assertEqual(parsed['artist_id'], ['artist1', 'artist2'])

    def test_parse_track_data(self):
        # Mock track data
        track_data = {
            'id': 'track123',
            'type': 'track',
            'name': 'Test Track',
            'album': {'name': 'Test Album', 'id': 'album123'},
            'artists': [
                {'name': 'Artist One', 'id': 'artist1'},
                {'name': 'Artist Two', 'id': 'artist2'}
            ]
        }

        # Call the method
        parsed = self.spotify_utils._parse_spotify_item(track_data)

        # Assertions
        self.assertEqual(parsed['id'], 'track123')
        self.assertEqual(parsed['type'], 'tracks')
        self.assertEqual(parsed['track_name'], 'Test Track')
        self.assertEqual(parsed['album_name'], 'Test Album')
        self.assertEqual(parsed['album_id'], 'album123')
        self.assertEqual(parsed['artist_name'], ['Artist One', 'Artist Two'])
        self.assertEqual(parsed['artist_id'], ['artist1', 'artist2'])

    def test_parse_invalid_data(self):
        # Mock invalid data
        invalid_data = {
            'id': 'invalid123',
            'type': 'unknown'
        }

        # Call the method
        parsed = self.spotify_utils._parse_spotify_item(invalid_data)

        # Assertions
        self.assertIsNone(parsed)

    def test_parse_empty_data(self):
        # Call the method with empty data
        parsed = self.spotify_utils._parse_spotify_item(None)

        # Assertions
        self.assertIsNone(parsed)