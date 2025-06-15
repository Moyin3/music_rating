from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.template import loader
from .utils.spotify import SpotifyUtils
import json
#import requests

from .models import Song, Album, Artist, Rating, RateSystem
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

def song_detail(request, spotify_id):
    request.GET = request.GET.copy()
    request.GET['type'] = 'tracks'
    request.GET['spotify_id'] = spotify_id
    response = spotify_handler.spotify_get_id(request)# Get from cache or API
    if isinstance(response, JsonResponse) and response.status_code == 200:
        data = json.loads(response.content)
        song_object, created = Song.objects.get_or_create(spotify_id=spotify_id) # Creating an instance of Song in database if it doesn't exist

        community_rating = community_rating_for_track(song_object)
        
        content_type =  ContentType.objects.get_for_model(Song)  # Get the content type for Song
        
        if request.user.is_authenticated:
            existing_rating = Rating.objects.filter(user=request.user, content_type=content_type, object_id=song_object.spotify_id).first()
        if request.method == 'POST':
            if existing_rating:
                form = RatingForm(request.POST, instance=existing_rating, user=request.user, content_object=song_object)
            
            else:
                form = RatingForm(request.POST, user=request.user, content_object=song_object)
            
            if form.is_valid():
                form.save()
                return redirect('song_detail', spotify_id=spotify_id)

        else: 
            # For GET requests, show the form with existing rating if it exists
            if existing_rating:
                form = RatingForm(instance=existing_rating, user=request.user, content_object=song_object)
            else:
                form = RatingForm(user=request.user, content_object=song_object)


        context = {
            'song': data, 
            'song_obj': song_object,  
            'form': form,  
            'community_rating': community_rating, 
            'optional_writing': existing_rating.optional_writing if existing_rating else None,  # Include optional writing if it exists
        }
        if existing_rating:
            context['user_rating'] = existing_rating
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
        # so that I could use the community rating helper function.
        album_object, created = Album.objects.get_or_create(spotify_id=spotify_id)

        # Get the community rating for the album
        community_rating = community_rating_for_album(album_data)

        track_ids = [track_id for track_id, _ in album_data.get('track_list', [])]  # Extract track IDs from the album data
        for track_id in track_ids:
            Song.objects.get_or_create(spotify_id=track_id)

        # Setup user_rating for pre-filling the form if needed
        content_type = ContentType.objects.get_for_model(Album)
        
        if request.user.is_authenticated:
        # Try to get an existing user rating for the album
            existing_rating = Rating.objects.filter(user=request.user, content_type=content_type, object_id=album_object.spotify_id).first() if request.user.is_authenticated else None
        
        if request.method == 'POST':
            rating_system_id = request.POST.get('rate_system')
            if rating_system_id:
                request.session['active_rate_system_id'] = rating_system_id
        else:
            rating_system_id = request.session.get('active_rate_system_id')
        active_rate_system = RateSystem.objects.filter(id=rating_system_id).first() if rating_system_id else RateSystem.objects.first()

        if request.method == 'POST':
            if existing_rating:
                form = RatingForm(request.POST, instance = existing_rating, user=request.user, content_object=album_object, rate_system=active_rate_system)
            else:
                # Create a new rating
                form = RatingForm(request.POST, user=request.user, content_object=album_object, rate_system=active_rate_system)
            if form.is_valid():
                form.save()
                return redirect('album_detail', spotify_id=spotify_id)
        
        else:
            # For GET requests, show the form with existing rating if it exists
            if existing_rating:
                form = RatingForm(instance=existing_rating, user=request.user, content_object=album_object, rate_system=active_rate_system)
            else:
                form = RatingForm(user=request.user, content_object=album_object, rate_system=active_rate_system)
        

        context = {
            'album': album_data, 
            'album_obj': album_object,  
            'form': form,  
            'community_rating': community_rating,
            'optional_writing': existing_rating.optional_writing if existing_rating else None,  # Include optional writing if it exists
        }

         # I've added a check for user_rating to avoid UnboundLocalError if user_rating doesn't exist
        if existing_rating:
            context['user_rating'] = existing_rating  # Include user's previous rating if it exists
        

        # Added this check to make sure that active_rate_system is not None before passing it to final_album_rating
        if active_rate_system:
            context['final_rating'] = final_album_rating(request.user, album_data, active_rate_system)  # Pass the final album rating based on the active rate system

        
        return render(request, 'music_rating/album_detail.html', context)


def artist_detail(request, spotify_id):
    request.GET = request.GET.copy()
    request.GET['type'] = 'artists'
    request.GET['spotify_id'] = spotify_id
    response = spotify_handler.spotify_get_id(request)
    if isinstance(response, JsonResponse) and response.status_code == 200:
        artist_data = json.loads(response.content)  # Artist details
        print("Artist data:", artist_data)  # Debugging line to check the artist data
        artist_object, created = Artist.objects.get_or_create(spotify_id=spotify_id)  # Get the Artist object if it exists
        rating_system_id = request.POST.get('rate_system', None)
        active_rate_system = RateSystem.objects.filter(id=rating_system_id).first() if rating_system_id else None
        community_rating = community_rating_for_artist(artist_data)
        
        content_type = ContentType.objects.get_for_model(Artist)
        user_rating = None
        if request.user.is_authenticated:
            existing_rating = Rating.objects.filter(user=request.user, content_type=content_type, object_id=artist_object.spotify_id).first()

        if request.method == 'POST':
            rating_system_id = request.POST.get('rate_system')
            if rating_system_id:
                request.session['active_rate_system_id'] = rating_system_id
        else:
            rating_system_id = request.session.get('active_rate_system_id')
        active_rate_system = RateSystem.objects.filter(id=rating_system_id).first() if rating_system_id else RateSystem.objects.first()

        if request.method == 'POST':
            if existing_rating:
                form = RatingForm(request.POST, instance=existing_rating, user=request.user, content_object=artist_object, rate_system=active_rate_system)
            # Instantiate the form with POST data, user, and content_object
            else:
                form = RatingForm(request.POST, user=request.user, content_object=artist_object, rate_system = active_rate_system)
            if form.is_valid():
                form.save()
                return redirect('artist_detail', spotify_id=spotify_id)
            
        else:
            # For GET requests, show the form with existing rating if it exists
            if existing_rating:
                form = RatingForm(instance=existing_rating, user=request.user, content_object=artist_object, rate_system=active_rate_system)
            else:
                form = RatingForm(user=request.user, content_object=artist_object, rate_system=active_rate_system)


        context = {
            'artist': artist_data, 
            'artist_obj': artist_object,
            'form': form, 
            'community_rating': community_rating,
            'optional_writing': existing_rating.optional_writing if existing_rating else None,  # Include optional writing if it exists
        }

         # I've addded a check for user_rating to avoid UnboundLocalError if user_rating doesn't exist
        if user_rating:
            context['user_rating'] = existing_rating
       
        # Added this check to make sure that active_rate_system is not None before passing it to final_artist_rating
        if active_rate_system:
            context['final rating'] = final_artist_rating(request.user, artist_data, active_rate_system)


        return render(request, 'music_rating/artist_detail.html', context)
    
### Spotify Search

def spotify_search(request):
    return spotify_handler.spotify_search(request)

def spotify_id_retrieval(request):
    return spotify_handler.spotify_get_id(request)


# Rating helper functions for songs, albums, and artists

def community_rating_for_track(track) -> int:
    track_ratings = Rating.objects.filter(content_type=ContentType.objects.get_for_model(Song), object_id=track.spotify_id)
    valid_ratings = [rating.score for rating in track_ratings if rating.score is not None]
    return int(sum(valid_ratings) / len(valid_ratings)) if valid_ratings else 0

def community_rating_for_album(album) -> int:
    album_content_type = ContentType.objects.get_for_model(Album)
    album_id = album.get('id')
    album_ratings = Rating.objects.filter(content_type=album_content_type, object_id=album_id)
    valid_album_ratings = [rating.score for rating in album_ratings if rating.score is not None]
    if valid_album_ratings:
        return int(sum(valid_album_ratings) / len(valid_album_ratings))


    # This is used when the album doesn't have a rating, so when the second rating system is used, we calculate the average of the song ratings
    # The same logic is used in the album_rating_for_rate_system_2 function
    song_content_type = ContentType.objects.get_for_model(Song)
    track_ids = [track_id for track_id, _ in album.get('track_list', [])]  # or album_data['track_list'] if using a dict
    song_content_type = ContentType.objects.get_for_model(Song)
    song_ratings = Rating.objects.filter(content_type=song_content_type, object_id__in=track_ids)
    song_scores = [rating.score for rating in song_ratings if rating.score is not None]
    return int(sum(song_scores) / len(song_scores)) if song_scores else 0

def community_rating_for_artist(artist_dict) -> int:
    artist_id = artist_dict.get('id')
    album_dicts = artist_dict.get('artist_albums', [])

    album_scores = []
    for album in album_dicts:
        print(album)
        album_artist_ids = album[0]
        if artist_id in album_artist_ids:
            score = community_rating_for_album(album)
            if score:
                album_scores.append(score)
    return int(sum(album_scores) / len(album_scores)) if album_scores else 0



def album_rating_for_rate_system_2(user, album) -> int:
    track_ids = [track_id for track_id, _ in album.get('track_list', [])]
    if not track_ids:
        return 0
    song_content_type = ContentType.objects.get_for_model(Song)
    total_rating = 0
    number_of_ratings = 0
    songs = Song.objects.filter(spotify_id__in=track_ids)
    print("Songs found:", list(songs))
    for song in songs:
        print(f"Checking ratings for song: {song} (spotify_id={song.spotify_id})")
        ratings = Rating.objects.filter(user=user, content_type=song_content_type, object_id=song.spotify_id)
        print(f"Ratings found for song {song.spotify_id} and user {user}: {list(ratings)}")
        for rating in ratings:
            print(f"Adding rating: {rating.score}")
            total_rating += rating.score
            number_of_ratings += 1
    print("Total rating:", total_rating, "Number of ratings:", number_of_ratings)
    return int(total_rating / number_of_ratings) if number_of_ratings > 0 else 0

def artist_rating_for_rate_system_2(user, artist) -> int:
    albums = artist.get('artist_albums', [])
    print("Albums found:", albums)
    
    if not albums:
        return 0
    album_content_type = ContentType.objects.get_for_model(Album)
    song_content_type = ContentType.objects.get_for_model(Song)
    album_scores = []
    
    for album in albums:
        # Try to get user's direct album rating
        album_id = album[0]
        rating = Rating.objects.filter(user=user, content_type=album_content_type, object_id=album_id).first()
        if rating and rating.score is not None:
            album_scores.append(rating.score)
        else:
            # Fallback: average of user's song ratings for this album (based off the second rating system)
            
            """TODO: Currently, able to get a list of album IDs from the artist, but not the actual album dicts
             where the album_dict contains the track_list of the album, this is needed to calculate the average of the song ratings, 
             when an album doesn't have a direct rating from the user, because the second rating system has been chosen."""

            """track_ids = [track_id for track_id, _ in album_dict.get('track_list', [])]
            song_ratings = Rating.objects.filter(user=user, content_type=song_content_type, object_id__in=track_ids)
            song_scores = [r.score for r in song_ratings if r.score is not None]
            if song_scores:
                album_scores.append(sum(song_scores) / len(song_scores))

    return int(sum(album_scores) / len(album_scores)) if album_scores else 0"""

def album_rating_for_rate_system_1(user, album) -> int:
    album_content_type = ContentType.objects.get_for_model(Album)
    object_id = album.get('id')
    rating = Rating.objects.filter(user=user, content_type=album_content_type, object_id=object_id).first()
    return rating.score if rating else 0

def artist_rating_for_rate_system_1(user, artist) -> int:
    artist_content_type = ContentType.objects.get_for_model(Artist)
    object_id = artist.get('id')
    rating = Rating.objects.filter(user = user, content_type=artist_content_type, object_id=object_id).first()
    return rating.score if rating else 0


def final_album_rating(user, album, rate_system) -> int:
    if rate_system.id == 1:
        return album_rating_for_rate_system_1(user, album)
    elif rate_system.id == 2:
        return album_rating_for_rate_system_2(user, album)
    else:
        raise ValueError(f"Unknown rate system: {rate_system.name}")

def final_artist_rating(user, artist, rate_system) -> int:
    if rate_system.id == 1:
        return artist_rating_for_rate_system_1(user, artist)
    elif rate_system.id == 2:
        return artist_rating_for_rate_system_2(user, artist)
    else:
        raise ValueError(f"Unknown rate system: {rate_system.name}")