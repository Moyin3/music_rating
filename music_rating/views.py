from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.template import loader
from .utils.spotify import SpotifyUtils
import json
#import requests

from .models import Song, Album, Artist, Rating
from .forms import RatingForm
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
        form = RatingForm(request.POST, user = request.user, content_object = Song.objects.filter(spotify_id=spotify_id).first())
        if form.is_valid():
            form.save()
        else:
            form = RatingForm(user=request.user, content_object=Song.objects.filter(spotify_id=spotify_id).first())
        return redirect('song_detail', spotify_id=spotify_id)

def rate_album(request, spotify_id):
    if request.method == 'POST':
        form = RatingForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect('album_detail', spotify_id=spotify_id)

def rate_artist(request, spotify_id):
    if request.method == 'POST':
        form = RatingForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect('artist_detail', spotify_id=spotify_id)

def song_detail(request, spotify_id):
    request.GET = request.GET.copy()
    request.GET['type'] = 'tracks'
    request.GET['spotify_id'] = spotify_id
    response = spotify_handler.spotify_get_id(request)# Get from cache or API
    if isinstance(response, JsonResponse) and response.status_code == 200:
        data = json.loads(response.content)
        song_object = Song.objects.get_or_create(spotify_id=spotify_id) # Creating an instance of Song in database if it doesn't exist
        form = RatingForm(user=request.user, content_object=song_object)  # Initialize the form for song rating
        if song_object:
            content_type = ContentType.objects.get_for_model(Song)
            user_rating = None
            if request.user.is_authenticated:
                user_rating = Rating.objects.filter(user=request.user, content_type=content_type, object_id=song_object.spotify_id).first()
                if user_rating:
                    form = RatingForm(initial={'rating': user_rating.score})
        
        context = {
            'song': data, 
            'song_obj': song_object,  # Pass the Song object if it exists
            'form': form,  # Pass the form for song rating
        }
        if user_rating:
            context['user_rating'] = user_rating
        # I've addded a check for user_rating to avoid UnboundLocalError if user_rating doesn't exist
        return render(request, 'music_rating/song_detail.html', context)
   # Handle error cases explicitly
    print("ERROR: Failed to retrieve song details")
    if isinstance(response, JsonResponse):
        return HttpResponse("Error retrieving song details", status=500)
    return HttpResponse("Song not found", status=404)


def album_detail(request, spotify_id):
    request.GET = request.GET.copy()
    request.GET['type'] = 'albums'
    request.GET['spotify_id'] = spotify_id
    response = spotify_handler.spotify_get_id(request)  # Get from cache or API

    if isinstance(response, JsonResponse) and response.status_code == 200:
        album_data = json.loads(response.content)
        
        # Get or create the Album object; this creates a tuple object, which I unpacked by writing ',created'
        # so that I could use the community helper function.
        album_object, created = Album.objects.get_or_create(spotify_id=spotify_id)

        # Get the community rating for the album
        community_rating = community_rating_for_album(album_object)

        # Setup user_rating for pre-filling the form if needed
        content_type = ContentType.objects.get_for_model(Album)
        user_rating = None
        if request.user.is_authenticated:
            user_rating = Rating.objects.filter(
                user=request.user,
                content_type=content_type,
                object_id=album_object.spotify_id
            ).first()

        if request.method == 'POST':
            # Instantiate the form with POST data, user, and content_object
            form = RatingForm(request.POST, user=request.user, content_object=album_object)
            if form.is_valid():
                print("Saving form...")
                form.save()
                return redirect('album_detail', spotify_id=spotify_id)
            else:
                print("Form is not valid:", form.errors)
        else:
            # If there's a previous user rating, pre-fill the form with it
            if user_rating:
                form = RatingForm(
                    initial={'score': user_rating.score},
                    user=request.user,
                    content_object=album_object
                )
            else:
                # Initialize the form for album rating
                form = RatingForm(user=request.user, content_object=album_object)

        context = {
            'album': album_data, 
            'album_obj': album_object,  # Pass the Album object if it exists
            'form': form,  # Pass the form for album rating
            'community_rating': community_rating,  # Pass the community rating for the album
        }

        if user_rating:
            context['user_rating'] = user_rating  # Include user's previous rating if it exists

        # I've added a check for user_rating to avoid UnboundLocalError if user_rating doesn't exist
        return render(request, 'music_rating/album_detail.html', context)


def artist_detail(request, spotify_id):
    request.GET = request.GET.copy()
    request.GET['type'] = 'artists'
    request.GET['spotify_id'] = spotify_id
    response = spotify_handler.spotify_get_id(request)
    if isinstance(response, JsonResponse) and response.status_code == 200:
        artist_data = json.loads(response.content)  # Artist details
        artist_object, created = Artist.objects.get_or_create(spotify_id=spotify_id)  # Get the Artist object if it exists
        form = RatingForm()
        if artist_object:
            content_type = ContentType.objects.get_for_model(Artist)
            user_rating = None
            if request.user.is_authenticated:
                user_rating = Rating.objects.filter(user=request.user, content_type=content_type, object_id=artist_object.spotify_id).first()
                if user_rating:
                    form = RatingForm(initial={'rating': user_rating.score})
        context = {
            'artist': artist_data, 
            'artist_obj': artist_object,  # Pass the Song object if it exists
            'form': form,  # Pass the form for song rating
        }
        if user_rating:
            context['user_rating'] = user_rating
        # I've addded a check for user_rating to avoid UnboundLocalError if user_rating doesn't exist
        return render(request, 'music_rating/artist_detail.html', context)
    
### Spotify Search

def spotify_search(request):
    return spotify_handler.spotify_search(request)

def spotify_id_retrieval(request):
    return spotify_handler.spotify_get_id(request)


# Rating helper functions for songs, albums, and artists

def community_rating_for_album(album) -> float:
    album_ratings = Rating.objects.filter(content_type=ContentType.objects.get_for_model(Album), object_id=album.spotify_id)
    return sum(rating.score for rating in album_ratings) / len(album_ratings) if album_ratings else 0

def community_rating_for_artist(artist) -> float:
    artist_ratings = Rating.objects.filter(content_type=ContentType.objects.get_for_model(Artist), object_id=artist.spotify_id)
    return sum(rating.score for rating in artist_ratings) / len(artist_ratings) if artist_ratings else 0


def album_rating(album):
    return

def average_rating_for_album(album) -> float:
    songs = Song.objects.filter(album=album)
    if not songs:
        return 0
    total_rating = sum(song.rating for song in songs if song.rating is not None)
    number_of_ratings = sum(1 for song in songs if song.rating is not None)
    return total_rating / number_of_ratings if number_of_ratings > 0 else 0

def average_rating_for_artist(artist) -> float:
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