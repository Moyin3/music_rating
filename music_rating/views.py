from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.template import loader
from .utils.spotify import SpotifyUtils
import json
import requests

from .models import Song, Album, Artist, Rating
from .forms import AlbumRatingForm, ArtistRatingForm, SongRatingForm
from django.contrib.contenttypes.models import ContentType


spotify_handler = SpotifyUtils()

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
    return render(request, "music_rating/albumpage.html", {"album_list": album_list})


def songspage(request):
    template = loader.get_template("music_rating/songspage.html")
    return HttpResponse(template.render({}, request))


def compage(request):
    template = loader.get_template("music_rating/compage.html")
    return HttpResponse(template.render({}, request))

def rate_song(request, spotify_id):
    if request.method == 'POST':
        form = SongRatingForm(request.POST)
        if form.is_valid():
            rating = form.cleaned_data['rating']
            song = get_object_or_404(Song, spotify_id=spotify_id)
            song.rating = rating
            song.save()
        return redirect('song_detail', spotify_id=spotify_id)

def rate_album(request, spotify_id):
    if request.method == 'POST':
        form = AlbumRatingForm(request.POST)
        if form.is_valid():
            rating = form.cleaned_data['rating']
            album = get_object_or_404(Album, spotify_id=spotify_id)
            album.album_rating = rating
            album.save()
        return redirect('album_detail', spotify_id=spotify_id)

def rate_artist(request, spotify_id):
    if request.method == 'POST':
        form = ArtistRatingForm(request.POST)
        if form.is_valid():
            rating = form.cleaned_data['rating']
            artist = get_object_or_404(Artist, spotify_id=spotify_id)
            artist.artist_rating = rating
            artist.save()
        return redirect('artist_detail', spotify_id=spotify_id)

def song_detail(request, spotify_id):
    request.GET = request.GET.copy()
    request.GET['type'] = 'tracks'
    request.GET['spotify_id'] = spotify_id
    response = spotify_handler.spotify_get_id(request)# Get from cache or API
    if isinstance(response, JsonResponse) and response.status_code == 200:
        data = json.loads(response.content)
        song_object = Song.objects.filter(spotify_id=spotify_id).first()
        form = SongRatingForm()
        return render(request, 'music_rating/song_detail.html', {
            'song': data, 
            'song_obj': song_object, 
            'form': form,
            })
   # Handle error cases explicitly
    print("ERROR: Failed to retrieve song details")
    if isinstance(response, JsonResponse):
        return HttpResponse("Error retrieving song details", status=500)
    return HttpResponse("Song not found", status=404)


def album_detail(request, spotify_id):
    request.GET = request.GET.copy()
    request.GET['type'] = 'albums'
    request.GET['spotify_id'] = spotify_id
    response = spotify_handler.spotify_get_id(request)# Get from cache or API
    if isinstance(response, JsonResponse) and response.status_code == 200:
        album_data = json.loads(response.content)
        album_object = Album.objects.filter(spotify_id=spotify_id).first()
        form = AlbumRatingForm()  # Initialize the form for album rating
        if album_object:
            content_type = ContentType.objects.get_for_model(Album)
            user_rating = None
            if request.user.is_authenticated:
                user_rating = Rating.objects.filter(user=request.user, content_type=content_type, object_id = album_object.spotify_id).first()
                if user_rating:
                    form = AlbumRatingForm(initial={'rating': user_rating.score})
        return render(request, 'music_rating/album_detail.html', {
            'album': album_data,
            'album_obj': album_object,  # Pass the Album object if it exists
            'form': form,  # Pass the form for album rating
            'user_rating': user_rating,  # Pass the user's rating if it exists
        })


# def album_detail(request, spotify_id):
#     # Spotify API endpoint for album details
#     album_url = f"https://api.spotify.com/v1/albums/{spotify_id}"
#     headers = {
#         "Authorization": f"Bearer {request.session.get('spotify_access_token')}"  # Use Spotify access token
#     }

#     # Make the API call
#     album_response = requests.get(album_url, headers=headers)

#     if album_response.status_code == 200:
#         album_data = album_response.json()
#         tracks = album_data.get('tracks', {}).get('items', [])  # Extract tracks from the album data
#         album_object = Album.objects.filter(spotify_id=spotify_id).first()
#         form = AlbumRatingForm()  # Initialize the form for album rating
#         return render(request, 'music_rating/album_detail.html', {
#             'album': album_data,
#             'tracks': tracks,
#             'album_obj': album_object,  # Pass the Album object if it exists
#             'form': form,  # Pass the form for album rating
#         })
#     elif album_response.status_code == 401:  # Unauthorized (invalid or expired token)
#         print("Access token expired. Refreshing token...")
#         new_token = spotify_handler._get_access_token(request)
#         if new_token:
#             # Update the session with the new token
#             request.session['spotify_access_token'] = new_token
#             headers["Authorization"] = f"Bearer {new_token}"
#             # Retry the API call
#             album_response = requests.get(album_url, headers=headers)
#             if album_response.status_code == 200:
#                 album_data = album_response.json()
#                 tracks = album_data.get('tracks', {}).get('items', [])
#                 album_object = Album.objects.filter(spotify_id=spotify_id).first()
#                 form = AlbumRatingForm()
#                 return render(request, 'music_rating/album_detail.html', {
#                     'album': album_data,
#                     'tracks': tracks,
#                     'album_obj': album_object,  # Pass the Album object if it exists
#                     'form': form,  # Pass the form for album rating
#                 })
#         print("ERROR: Failed to refresh access token")
#         return HttpResponse("Error refreshing access token", status=500)
#     elif album_response.status_code == 404:
#         print(f"Album not found: {spotify_id}")
#         return HttpResponse("Album not found", status=404)
#     else:
#         print(f"ERROR: Failed to retrieve album details. Status code: {album_response.status_code}")
#         print(f"Response: {album_response.text}")
#         return HttpResponse("Error retrieving album details", status=500)

def artist_detail(request, spotify_id):
    request.GET = request.GET.copy()
    request.GET['type'] = 'artists'
    request.GET['spotify_id'] = spotify_id
    response = spotify_handler.spotify_get_id(request)
    if isinstance(response, JsonResponse) and response.status_code == 200:
        artist_data = json.loads(response.content)  # Artist details
        artist_object = Artist.objects.filter(spotify_id=spotify_id).first()  # Get the Artist object if it exists
        form = ArtistRatingForm()
        return render(request, 'music_rating/artist_detail.html', {
            'artist': artist_data,
            'artist_obj': artist_object,  # Pass the Artist object if it exists
            'form': form,  # Pass the form for artist rating
        })


# def artist_detail(request, spotify_id):
#     # Fetch artist details
#     request.GET = request.GET.copy()
#     request.GET['type'] = 'artists'
#     request.GET['spotify_id'] = spotify_id
#     response = spotify_handler.spotify_get_id(request)  # Get artist details from cache or API


#     if isinstance(response, JsonResponse) and response.status_code == 200:
#         artist_data = json.loads(response.content)  # Artist details
#         artist_object = Artist.objects.filter(spotify_id=spotify_id).first()  # Get the Artist object if it exists
#         form = ArtistRatingForm()  # Initialize the form for artist rating

#         # Fetch albums for the artist using Spotify API
#         albums = []
#         albums_url = f"https://api.spotify.com/v1/artists/{spotify_id}/albums"
#         headers = {
#             "Authorization": f"Bearer {request.session.get('spotify_access_token')}"  # Use Spotify access token
#         }
#         albums_response = requests.get(albums_url, headers=headers)

#         if albums_response.status_code == 401:  # Unauthorized (invalid or expired token)
#             print("Access token expired. Refreshing token...")
#             # Refresh the access token
#             new_token = spotify_handler._get_access_token(request)
#             if new_token:
#                 # Update the session with the new token
#                 request.session['spotify_access_token'] = new_token
#                 headers["Authorization"] = f"Bearer {new_token}"
#                 # Retry the API call
#                 albums_response = requests.get(albums_url, headers=headers)
#             else:
#                 print("ERROR: Failed to refresh access token")
#                 return HttpResponse("Error refreshing access token", status=500)

#         if albums_response.status_code == 200:
#             albums_data = albums_response.json()
#             albums = [
#         album for album in albums_data.get('items', [])
#         if album.get('album_type') == 'album'
#     ]
#         print(f"Albums API Response: {albums_response.status_code}")

#         # Pass both artist details and albums to the template
#         return render(request, 'music_rating/artist_detail.html', {
#             'artist': artist_data,
#             'albums': albums,
#             'artist_obj': artist_object,  # Pass the Artist object if it exists
#             'form': form,  # Pass the form for artist rating
#         })

#     # Handle error cases explicitly
#     print("ERROR: Failed to retrieve artist or album details")
#     if isinstance(response, JsonResponse):
#         return HttpResponse("Error retrieving artist details", status=500)
#     return HttpResponse("Artist not found", status=404)





### Spotify Search

def spotify_search(request):
    return spotify_handler.spotify_search(request)

def spotify_id_retrieval(request):
    return spotify_handler.spotify_get_id(request)


# Rating logic for songs, albums, and artists

def album_rating(album):
    return

def average_rating_for_album(album):
    songs = Song.objects.filter(album=album)
    if not songs:
        return 0
    total_rating = sum(song.rating for song in songs if song.rating is not None)
    number_of_ratings = sum(1 for song in songs if song.rating is not None)
    return total_rating / number_of_ratings if number_of_ratings > 0 else 0

def average_rating_for_artist(artist):
    albums = Album.objects.filter(artist=artist)
    if not albums:
        return 0
    total_rating = sum(average_rating_for_album(album) for album in albums)
    number_of_ratings = sum(1 for album in albums if album.album_rating is not None)
    return total_rating / number_of_ratings if number_of_ratings > 0 else 0

def album_rating_for_rate_system_2(album):
    return album.average_rating_for_album()

def artist_rating_for_rate_system_2(artist):
    return artist.average_rating_for_artist()