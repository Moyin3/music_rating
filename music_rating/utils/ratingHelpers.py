from .spotify import SpotifyUtils
import json
from django.contrib.contenttypes.models import ContentType
from music_rating.models import Song, Album, Artist, Rating, RateSystem
from django.db.models import Avg


spotify_handler = SpotifyUtils()


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
    #TODO: fix this and other divisions to avoid rounding and floating point errors, can be done using the django Avg method I'm sure
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