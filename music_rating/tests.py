from django.test import TestCase, Client
from .models import Song, Artist, Album, Single, EP
from unittest.mock import patch
from urllib.parse import urlencode
from django.conf import settings


class ModelTests(TestCase):
    def test_song_name_and_artist(self):
        testArtist = Artist.objects.create(artist_name="Wizkid")
        testSong = Song.objects.create(song_name="Fever")
        testSong.artist_name.set([testArtist])

        self.assertEqual(testSong.song_name, "Fever")
        self.assertEqual(testSong.artist_name.first().artist_name, "Wizkid")

    def test_artist(self):
        testArtist = Artist.objects.create(artist_name="Smino")
        testAlbum = Album.objects.create(album_name="Luv 4 Rent")
        testAlbum.artist_name.set([testArtist])
        testSong1 = Song.objects.create(song_name="90 Proof", album=testAlbum)
        testEP = EP.objects.create(ep_name="blkjuptr")
        testEP.artist_name.set([testArtist])
        testSong2 = Song.objects.create(song_name="Zoom", ep=testEP)
        testSingle = Single.objects.create(single_name="Baguetti")
        testSingle.artist_name.set([testArtist])
        testSong3 = Song.objects.create(song_name="Baguetti", single=testSingle)
        self.assertEqual(testSong1.album.album_name, "Luv 4 Rent")
        self.assertEqual(testSong2.ep.ep_name, "blkjuptr")
        self.assertEqual(testSong3.single.single_name, "Baguetti")
        self.assertEqual(testSong1.get_artist_name, "Smino")
        self.assertEqual(testSong2.get_artist_name, "Smino")
        self.assertEqual(testSong3.get_artist_name, "Smino")
        self.assertEqual(testAlbum.songs_album.first().song_name, "90 Proof")
        self.assertEqual(testEP.songs_ep.first().song_name, "Zoom")
        self.assertEqual(testSingle.songs_single.first().song_name, "Baguetti")

class GetArtistNameTests(TestCase):
    def test_get_artist_name_album(self):
        testArtist = Artist.objects.create(artist_name="Wizkid")
        testAlbum = Album.objects.create(album_name="Made in Lagos")
        testAlbum.artist_name.set([testArtist])
        testSong = Song.objects.create(song_name="Grace", album=testAlbum)
        self.assertEqual(testSong.get_artist_name, "Wizkid")
    
    def test_get_artist_name_ep(self):
        testArtist = Artist.objects.create(artist_name="Namani")
        testEP = EP.objects.create(ep_name="TEXT LANGUAGE")
        testEP.artist_name.set([testArtist])
        testSong = Song.objects.create(song_name="WTF", ep=testEP)
        self.assertEqual(testSong.get_artist_name, "Namani")
    
    def test_get_artist_name_single(self):
        testArtist = Artist.objects.create(artist_name="Davido")
        testSingle = Single.objects.create(single_name="FEM")
        testSingle.artist_name.set([testArtist])
        testSong = Song.objects.create(song_name="FEM", single=testSingle)
        self.assertEqual(testSong.get_artist_name, "Davido")
    
    def test_get_artist_name_null(self):
        testSong = Song.objects.create(song_name="Tweaker")
        self.assertEqual(testSong.get_artist_name, "Unknown")

class StrMethodTests(TestCase):
    def test_str_method_song(self):
        testSong = Song.objects.create(song_name="Fever")
        self.assertEqual(str(testSong), "Fever")
    
    def test_str_method_album(self):
        testAlbum = Album.objects.create(album_name="Made in Lagos")
        self.assertEqual(str(testAlbum), "Made in Lagos")
    
    def test_str_method_single(self):
        testSingle = Single.objects.create(single_name="FEM")
        self.assertEqual(str(testSingle), "FEM")
    
    def test_str_method_ep(self):
        testEP = EP.objects.create(ep_name="TEXT LANGUAGE")
        self.assertEqual(str(testEP), "TEXT LANGUAGE")

class GetAccessTokenTests(TestCase):
    @patch('music_rating.views.requests.post')
    def test_get_access_token_success(self, mock_post):
        # Mock Spotify API response
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            'access_token': 'mock_access_token',
            'expires_in': 3600
        }

        # Simulate a request to the get_access_token function
        from music_rating.views import get_access_token
        request = self.client.request().wsgi_request  # Create a mock request object
        token = get_access_token(request)

        # Assert that the token is correctly retrieved
        self.assertEqual(token, 'mock_access_token')
        self.assertIn('access_token', request.session)
        self.assertIn('token_expiry_time', request.session)
    
    @patch('music_rating.views.requests.post')
    def test_get_access_token_failure(self, mock_post):
        # Mock Spotify API failure response
        mock_post.return_value.status_code = 400
        mock_post.return_value.json.return_value = {
            'error': 'invalid_client'
        }

        # Simulate a request to the get_access_token function
        from music_rating.views import get_access_token
        request = self.client.request().wsgi_request  # Create a mock request object
        token = get_access_token(request)

        # Assert that the token is None (failure case)
        self.assertIsNone(token)

        # Assert that no access token or expiry time is stored in the session
        self.assertNotIn('access_token', request.session)
        self.assertNotIn('token_expiry_time', request.session)

class SpotifySearchTests(TestCase):
    @patch('music_rating.views.requests.get')
    def test_search_spotify_success(self, mock_get):
        # Mock Spotify API response
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            'tracks': {'items': []},
            'albums': {'items': []},
            'artists': {'items': []}
        }

        client = Client()
        query = urlencode({'query': 'test'})
        response = client.get(f'/spotify-search/?{query}')
        self.assertIn('tracks', response.json())
        self.assertIn('albums', response.json())
        self.assertIn('artists', response.json())
    
    @patch('music_rating.views.requests.get')
    def test_spotify_search_failure(self, mock_get):
        # Mock Spotify API failure response
        mock_get.return_value.status_code = 400

        client = Client()
        query = urlencode({'query': 'test'})
        response = client.get(f'/spotify-search/?{query}')  
        self.assertEqual(response.status_code, 400)
        self.assertIn('Failed to fetch data from Spotify', response.json()['error'])

class TemplateViewTests(TestCase):
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
    
    def test_album_detail_view(self):
        testArtist = Artist.objects.create(artist_name="Wizkid")
        testAlbum = Album.objects.create(album_name="Made in Lagos")
        testAlbum.artist_name.set([testArtist])
        testSong = Song.objects.create(song_name="Grace", album=testAlbum)
        
        client = Client()
        response = client.get(f'/album/{testAlbum.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'music_rating/album_detail.html')

