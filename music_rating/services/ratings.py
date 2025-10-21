from typing import Optional, Tuple, Iterable
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from music_rating.models import Song, Album, Artist, Rating, RateSystem

def community_rating_for_track(track: Song) -> int:
    ct = ContentType.objects.get_for_model(Song)
    qs = Rating.objects.filter(content_type=ct, object_id=track.spotify_id).exclude(score=None)
    scores = list(qs.values_list("score", flat=True))
    return int(sum(scores) / len(scores)) if scores else 0

def community_rating_for_album(album_dict: dict, active_rate_system: Optional[RateSystem] = None) -> Optional[int]:
    ct = ContentType.objects.get_for_model(Album)
    album_id = album_dict.get("id")
    qs = Rating.objects.filter(content_type=ct, object_id=album_id).exclude(score=None)
    if active_rate_system:
        qs = qs.filter(rate_system=active_rate_system)
    scores = list(qs.values_list("score", flat=True))
    return int(sum(scores) / len(scores)) if scores else None

def community_rating_for_artist(artist_dict: dict, active_rate_system: Optional[RateSystem] = None) -> Optional[int]:
    ct = ContentType.objects.get_for_model(Artist)
    artist_id = artist_dict.get("id")
    qs = Rating.objects.filter(content_type=ct, object_id=artist_id).exclude(score=None)
    if active_rate_system:
        qs = qs.filter(rate_system=active_rate_system)
    scores = list(qs.values_list("score", flat=True))
    return int(sum(scores) / len(scores)) if scores else None

@transaction.atomic
def album_rating_for_rate_system_1_upsert(user, album_id: str, score: int) -> Tuple[int, Rating]:
    ct_album = ContentType.objects.get_for_model(Album)
    rs1 = RateSystem.objects.get(id=1)
    rating_obj, _ = Rating.objects.update_or_create(
        user=user,
        content_type=ct_album,
        object_id=album_id,
        rate_system=rs1,
        defaults={"score": int(score)},
    )
    return int(score), rating_obj


def album_rating_for_rate_system_2_compute(user, album_dict: dict) -> Optional[int]:
    """Compute average of the user's rated songs in an album (no DB write)."""
    track_ids: Iterable[str] = [track_id for track_id, _ in album_dict.get("track_list", [])]
    if not track_ids:
        return None
    songs = Song.objects.filter(spotify_id__in=track_ids)
    ct_song = ContentType.objects.get_for_model(Song)
    qs = Rating.objects.filter(user=user, content_type=ct_song, object_id__in=songs.values_list("spotify_id", flat=True)).exclude(score=None)
    scores = list(qs.values_list("score", flat=True))
    return int(sum(scores) / len(scores)) if scores else None

@transaction.atomic
def artist_rating_for_rate_system_1_upsert(user, artist_id: str, score: int) -> Tuple[int, Rating]:
    ct_artist = ContentType.objects.get_for_model(Artist)
    rs1 = RateSystem.objects.get(id=1)
    rating_obj, _ = Rating.objects.update_or_create(
        user=user,
        content_type=ct_artist,
        object_id=artist_id,
        rate_system=rs1,
        defaults={"score": int(score)},
    )
    return int(score), rating_obj

@transaction.atomic
def album_rating_for_rate_system_2_upsert(user, album_dict: dict) -> Tuple[Optional[int], Optional[Rating]]:
    """Compute and persist the user's album rating for rate system 2."""
    avg = album_rating_for_rate_system_2_compute(user, album_dict)
    if avg is None:
        return None
    ct_album = ContentType.objects.get_for_model(Album)
    rs2 = RateSystem.objects.get(id=2)
    rating_obj, _ = Rating.objects.update_or_create(
        user=user,
        content_type=ct_album,
        object_id=album_dict.get("id"),
        rate_system=rs2,
        defaults={"score": int(avg)},
    )
    return int(avg), rating_obj

@transaction.atomic
def artist_rating_for_rate_system_2_upsert(
    user,
    artist_dict: dict,
    fetch_album_dict_by_id,     # callable: (spotify_album_id: str) -> dict
    force_recompute: bool = False,  # if True, ignore cached RS2 and recompute
) -> Tuple[Optional[int], Optional[Rating]]:
    """
    Compute artist RS2 as the average of per-album scores:
      1) Prefer user's RS1 (direct album) score if present
      2) Else use cached RS2 (album) score if present
      3) Else compute RS2 from user's track ratings, then cache it on the album

    Persist artist RS2 (Rating row). Returns (avg_score, artist_rating_obj) or (None, None).
    """
    albums: Iterable[tuple] = artist_dict.get("artist_albums", [])
    if not albums:
        return (None, None)

    album_ids = [a[0] for a in albums if a and len(a) > 0]
    if not album_ids:
        return (None, None)

    ct_album = ContentType.objects.get_for_model(Album)
    ct_artist = ContentType.objects.get_for_model(Artist)
    rs1 = RateSystem.objects.get(id=1)
    rs2 = RateSystem.objects.get(id=2)

    # Bulk fetch RS1 and RS2 album ratings to avoid N+1 queries
    rs1_map = dict(
        Rating.objects
        .filter(user=user, content_type=ct_album, rate_system=rs1, object_id__in=album_ids)
        .exclude(score=None)
        .values_list("object_id", "score")
    )
    rs2_map = dict(
        Rating.objects
        .filter(user=user, content_type=ct_album, rate_system=rs2, object_id__in=album_ids)
        .exclude(score=None)
        .values_list("object_id", "score")
    )

    album_scores: list[int] = []

    for album_id in album_ids:
        # 1) Direct album score (RS1) wins
        if album_id in rs1_map:
            album_scores.append(int(rs1_map[album_id]))
            continue

        # 2) Cached RS2 (unless we force recompute)
        if not force_recompute and album_id in rs2_map:
            album_scores.append(int(rs2_map[album_id]))
            continue

        # 3) Compute RS2 from tracks and cache it on the album
        album_dict = fetch_album_dict_by_id(album_id)
        computed = album_rating_for_rate_system_2_compute(user, album_dict)
        if computed is not None:
            computed = int(computed)
            album_scores.append(computed)
            # cache/update RS2 for this album so next call can reuse
            Rating.objects.update_or_create(
                user=user,
                content_type=ct_album,
                object_id=album_id,
                rate_system=rs2,
                defaults={"score": computed},
            )

    if not album_scores:
        return (None, None)

    avg_score = int(sum(album_scores) / len(album_scores))

    artist_rating_obj, _ = Rating.objects.update_or_create(
        user=user,
        content_type=ct_artist,
        object_id=artist_dict.get("id"),
        rate_system=rs2,
        defaults={"score": avg_score},
    )

    return avg_score, artist_rating_obj

def final_album_rating(user, album_dict: dict, rate_system: RateSystem) -> Optional[int]:
    if rate_system.id == 1:
        return album_rating_for_rate_system_1_upsert(user, album_dict)
    if rate_system.id == 2:
        score, _ = album_rating_for_rate_system_2_upsert(user, album_dict)
        return score
    raise ValueError(f"Unknown rate system: {rate_system.name}")

def final_artist_rating(user, artist_dict: dict, rate_system: RateSystem, fetch_album_dict_by_id) -> Optional[int]:
    if rate_system.id == 1:
        return artist_rating_for_rate_system_1_upsert(user, artist_dict)
    if rate_system.id == 2:
        score, _ = artist_rating_for_rate_system_2_upsert(user, artist_dict, fetch_album_dict_by_id)
        return score
    raise ValueError(f"Unknown rate system: {rate_system.name}")