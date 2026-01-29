from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.template import loader
from .utils.spotify import SpotifyUtils
import json
from django.db.models import Avg

# import requests

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
    request.GET["type"] = "tracks"
    request.GET["spotify_id"] = spotify_id
    response = spotify_handler.spotify_get_id(request)  # Get from cache or API
    if isinstance(response, JsonResponse) and response.status_code == 200:
        data = json.loads(response.content)
        song_object, created = Song.objects.get_or_create(
            spotify_id=spotify_id
        )  # Creating an instance of Song in database if it doesn't exist

        community_rating = community_rating_for_track(song_object)

        content_type = ContentType.objects.get_for_model(
            Song
        )  # Get the content type for Song

        existing_rating = None

        if request.user.is_authenticated:
            existing_rating = Rating.objects.filter(
                user=request.user,
                content_type=content_type,
                spotify_id=song_object.spotify_id,
            ).first()
        if request.method == "POST":
            if existing_rating:
                form = RatingForm(
                    request.POST,
                    instance=existing_rating,
                    user=request.user,
                    content_object=song_object,
                )

            else:
                form = RatingForm(
                    request.POST, user=request.user, content_object=song_object
                )

            if form.is_valid():
                form.save()
                return redirect("song_detail", spotify_id=spotify_id)

        else:
            # For GET requests, show the form with existing rating if it exists
            if existing_rating:
                form = RatingForm(
                    instance=existing_rating,
                    user=request.user,
                    content_object=song_object,
                )
            else:
                form = RatingForm(user=request.user, content_object=song_object)

        context = {
            "song": data,
            "song_obj": song_object,
            "form": form,
            "community_rating": community_rating,
            "optional_writing": (
                existing_rating.optional_writing if existing_rating else None
            ),  # Include optional writing if it exists
        }
        if existing_rating:
            context["user_rating"] = existing_rating
        # I've addded a check for user_rating to avoid UnboundLocalError if user_rating doesn't exist
        return render(request, "music_rating/song_detail.html", context)
    # Handle error cases explicitly
    print("ERROR: Failed to retrieve song details")
    if isinstance(response, JsonResponse):
        if response.status_code == 404:
            return HttpResponse("Song not found", status=404)
        return HttpResponse("Error retrieving song details", status=500)


def album_detail(request, spotify_id):
    request.GET = request.GET.copy()
    request.GET["type"] = "albums"
    request.GET["spotify_id"] = spotify_id
    response = spotify_handler.spotify_get_id(request)  # Get from cache or API

    if isinstance(response, JsonResponse) and response.status_code == 200:
        album_data = json.loads(response.content)

        # Get or create the Album object; this creates a tuple object, which I unpacked by writing ',created'
        # so that I could use the community rating helper function.
        album_object, created = Album.objects.get_or_create(spotify_id=spotify_id)

        if request.method == "POST":
            rating_system_id = request.POST.get("rate_system")
            if rating_system_id:
                request.session["active_rate_system_id"] = rating_system_id
        else:
            rating_system_id = request.session.get("active_rate_system_id")
        active_rate_system = (
            RateSystem.objects.filter(id=rating_system_id).first()
            if rating_system_id
            else RateSystem.objects.first()
        )

        # Get the community rating for the album
        community_rating = community_rating_for_album(album_data, active_rate_system)

        existing_rating = None

        track_ids = [
            track_id for track_id, _ in album_data.get("track_list", [])
        ]  # Extract track IDs from the album data
        for track_id in track_ids:
            Song.objects.get_or_create(spotify_id=track_id)

        # Setup user_rating for pre-filling the form if needed
        content_type = ContentType.objects.get_for_model(Album)

        if request.user.is_authenticated:
            # Try to get an existing user rating for the album
            existing_rating = (
                Rating.objects.filter(
                    user=request.user,
                    content_type=content_type,
                    spotify_id=album_object.spotify_id,
                ).first()
                if request.user.is_authenticated
                else None
            )

        if request.method == "POST":
            if existing_rating:
                form = RatingForm(
                    request.POST,
                    instance=existing_rating,
                    user=request.user,
                    content_object=album_object,
                    rate_system=active_rate_system,
                )
            else:
                # Create a new rating
                form = RatingForm(
                    request.POST,
                    user=request.user,
                    content_object=album_object,
                    rate_system=active_rate_system,
                )
            if form.is_valid():
                form.save()
                return redirect("album_detail", spotify_id=spotify_id)

        else:
            # For GET requests, show the form with existing rating if it exists
            if existing_rating:
                form = RatingForm(
                    instance=existing_rating,
                    user=request.user,
                    content_object=album_object,
                    rate_system=active_rate_system,
                )
            else:
                form = RatingForm(
                    user=request.user,
                    content_object=album_object,
                    rate_system=active_rate_system,
                )

        context = {
            "album": album_data,
            "album_obj": album_object,
            "form": form,
            "community_rating": community_rating,
            "optional_writing": (
                existing_rating.optional_writing if existing_rating else None
            ),  # Include optional writing if it exists
        }

        # I've added a check for user_rating to avoid UnboundLocalError if user_rating doesn't exist
        if existing_rating:
            context["user_rating"] = (
                existing_rating  # Include user's previous rating if it exists
            )

        return render(request, "music_rating/album_detail.html", context)

    # Handle error cases explicitly
    if isinstance(response, JsonResponse) and response.status_code == 404:
        return HttpResponse("Album not found", status=404)
    return HttpResponse("Error retrieving album details", status=500)


def artist_detail(request, spotify_id):
    request.GET = request.GET.copy()
    request.GET["type"] = "artists"
    request.GET["spotify_id"] = spotify_id
    response = spotify_handler.spotify_get_id(request)
    if isinstance(response, JsonResponse) and response.status_code == 200:
        artist_data = json.loads(response.content)  # Artist details
        artist_object, created = Artist.objects.get_or_create(
            spotify_id=spotify_id
        )  # Get the Artist object if it exists
        rating_system_id = request.POST.get("rate_system", None)
        active_rate_system = (
            RateSystem.objects.filter(id=rating_system_id).first()
            if rating_system_id
            else None
        )
        community_rating = community_rating_for_artist(artist_data, active_rate_system)
        existing_rating = None

        content_type = ContentType.objects.get_for_model(Artist)
        user_rating = None
        if request.user.is_authenticated:
            existing_rating = Rating.objects.filter(
                user=request.user,
                content_type=content_type,
                spotify_id=artist_object.spotify_id,
            ).first()

        if request.method == "POST":
            rating_system_id = request.POST.get("rate_system")
            if rating_system_id:
                request.session["active_rate_system_id"] = rating_system_id
        else:
            rating_system_id = request.session.get("active_rate_system_id")
        active_rate_system = (
            RateSystem.objects.filter(id=rating_system_id).first()
            if rating_system_id
            else RateSystem.objects.first()
        )

        if request.method == "POST":
            if existing_rating:
                form = RatingForm(
                    request.POST,
                    instance=existing_rating,
                    user=request.user,
                    content_object=artist_object,
                    rate_system=active_rate_system,
                )
            # Instantiate the form with POST data, user, and content_object
            else:
                form = RatingForm(
                    request.POST,
                    user=request.user,
                    content_object=artist_object,
                    rate_system=active_rate_system,
                )
            if form.is_valid():
                form.save()
                return redirect("artist_detail", spotify_id=spotify_id)

        else:
            # For GET requests, show the form with existing rating if it exists
            if existing_rating:
                form = RatingForm(
                    instance=existing_rating,
                    user=request.user,
                    content_object=artist_object,
                    rate_system=active_rate_system,
                )
            else:
                form = RatingForm(
                    user=request.user,
                    content_object=artist_object,
                    rate_system=active_rate_system,
                )

        context = {
            "artist": artist_data,
            "artist_obj": artist_object,
            "form": form,
            "community_rating": community_rating,
            "optional_writing": (
                existing_rating.optional_writing if existing_rating else None
            ),  # Include optional writing if it exists
        }

        # I've addded a check for user_rating to avoid UnboundLocalError if user_rating doesn't exist
        if user_rating:
            context["user_rating"] = existing_rating

        return render(request, "music_rating/artist_detail.html", context)

    # Handle error cases explicitly
    if isinstance(response, JsonResponse) and response.status_code == 404:
        return HttpResponse("Artist not found", status=404)
    return HttpResponse("Error retrieving artist details", status=500)


### Spotify Search


def spotify_search(request):
    return spotify_handler.spotify_search(request)


def spotify_id_retrieval(request):
    return spotify_handler.spotify_get_id(request)


# Rating helper functions for songs, albums, and artists

#Definitely can be refactored
def get_album_dict_from_id(request, spotify_id):
    request.GET = request.GET.copy()
    request.GET["type"] = "albums"
    request.GET["spotify_id"] = spotify_id
    response = spotify_handler.spotify_get_id(request)
    return json.loads(response.content)

# Average rating for track for all users across platform
def community_rating_for_track(track) -> int:
    song_content_type = ContentType.objects.get_for_model(Song)
    song_id = track.get("id")
    latest_rating_per_user = (
        Rating.objects.filter(
        content_type=song_content_type, 
        spotify_id=song_id,
        score__isnull = False
    )
    .order_by("user_id", "-updated_at")
    .distinct("user_id")
    )
    #TODO: fix this and other divisions to avoid rounding and floating point errors
    scores = [r.score for r in latest_rating_per_user]
    return sum(scores) / len(scores) if scores else None

#TODO: Refactor the community ratings into one big function, everyone similar right now, want DRY code
# Average rating for album for all users across platform
def community_rating_for_album(album_spotify_id) -> int | None:
    album_ct = ContentType.objects.get_for_model(Album)

    latest_rating_per_user = (
        Rating.objects
        .filter(
            content_type=album_ct,
            spotify_id=album_spotify_id,
            score__isnull=False,
        )
        .order_by("user_id", "-updated_at")
        .distinct("user_id")
    )

    scores = [r.score for r in latest_rating_per_user]
    return int(sum(scores) / len(scores)) if scores else None

# Average rating for artist for all users across platform
def community_rating_for_artist(artist_spotify_id) -> int | None:
    artist_ct = ContentType.objects.get_for_model(Artist)

    latest_rating_per_user = (
        Rating.objects
        .filter(
            content_type=artist_ct,
            spotify_id=artist_spotify_id,
            score__isnull=False,
        )
        .order_by("user_id", "-updated_at")
        .distinct("user_id")
    )

    scores = [r.score for r in latest_rating_per_user]
    return int(sum(scores) / len(scores)) if scores else None

def community_rating_for_song(track_spotify_id) -> int | None:
    song_ct = ContentType.objects.get_for_model(Song)

    latest_rating_per_user = (
        Rating.objects
        .filter(
            content_type = song_ct,
            spotify_id = track_spotify_id,
            score__isnull = False,
        )
        .order_by("user_id", "-updated_at")
        .distinct("user_id")
    )
    scores = [r.score for r in latest_rating_per_user]
    return int(sum(scores) / len(scores)) if scores else None

# Takes an average of rated songs in the album
def album_rating_for_rate_system_2(user, album_spotify_id) -> int:
    song_ct = ContentType.objects.get_for_model(Song)
    album_ct = ContentType.objects.get_for_model(Album)
    rate_system = RateSystem.objects.get(key="average")

    # All songs that belong to this album
    songs = Song.objects.filter(album_spotify_id=album_spotify_id)
    if not songs.exists():
        return 0

    # User's ratings for those songs
    ratings = Rating.objects.filter(
        user=user,
        content_type=song_ct,
        spotify_id__in=songs.values_list("spotify_id", flat=True),
    )

    if not ratings.exists():
        return 0

    avg_score = int(ratings.aggregate(avg=Avg("score"))["avg"])

    Rating.objects.update_or_create(
        user=user,
        content_type=album_ct,
        spotify_id=album_spotify_id,
        rate_system=rate_system,
        defaults={"score": avg_score},
    )

    return avg_score

# Takes an average of rated albums an artist has
def artist_rating_for_rate_system_2(user, artist_spotify_id) -> int:
    album_ct = ContentType.objects.get_for_model(Album)
    artist_ct = ContentType.objects.get_for_model(Artist)
    rate_system = RateSystem.objects.get(key="average")

    # Albums by this artist that exist in the DB
    albums = Album.objects.filter(artist_spotify_id=artist_spotify_id)
    if not albums.exists():
        return 0

    # User's album ratings for those albums
    ratings = Rating.objects.filter(
        user=user,
        content_type=album_ct,
        spotify_id__in=albums.values_list("spotify_id", flat=True),
        rate_system=rate_system,
    )

    if not ratings.exists():
        return 0

    avg_score = int(ratings.aggregate(avg=Avg("score"))["avg"])

    Rating.objects.update_or_create(
        user=user,
        content_type=artist_ct,
        spotify_id=artist_spotify_id,
        rate_system=rate_system,
        defaults={"score": avg_score},
    )

    return avg_score

def album_rating_for_rate_system_1(user, album_spotify_id) -> int | None:
    album_ct = ContentType.objects.get_for_model(Album)

    rating = (
        Rating.objects
        .filter(
            user=user,
            content_type=album_ct,
            spotify_id=album_spotify_id,
        )
        .order_by("-updated_at")
        .first()
    )

    return rating.score if rating else None


def artist_rating_for_rate_system_1(user, artist_spotify_id) -> int | None:
    artist_ct = ContentType.objects.get_for_model(Artist)

    rating = (
        Rating.objects
        .filter(
            user=user,
            content_type=artist_ct,
            spotify_id=artist_spotify_id,
        )
        .order_by("-updated_at")
        .first()
    )

    return rating.score if rating else None