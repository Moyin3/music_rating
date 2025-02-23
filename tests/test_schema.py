from src.schema import (
    Name,
    Streams,
    Minutes,
    Rating,
    Song,
    Album,
    Single,
    EP,
    Artist,
    RateSystem,
)

album_test = Album(
    Name("4 Your Eyez Only"),
    Name("J.Cole"),
    [
        Song(
            Name("For Whom The Bell Tolls"),
            Streams(streams=1),
            Minutes(10),
            Name(None),
            Rating(70),
            None,
        ),
        Song(
            Name("Immortal"),
            Streams(streams=5),
            Minutes(1),
            Name(None),
            Rating(70),
            None,
        ),
        Song(
            Name("Deja Vu"),
            Streams(streams=1),
            Minutes(1),
            Name(None),
            Rating(70),
            None,
        ),
        Song(
            Name("Ville Mentality"),
            Streams(streams=1),
            Minutes(1),
            Name(None),
            Rating(70),
            None,
        ),
        Song(
            Name("She's Mine Pt. 1"),
            Streams(streams=1),
            Minutes(1),
            Name(None),
            Rating(70),
            None,
        ),
        Song(
            Name("Change"),
            Streams(streams=1),
            Minutes(1),
            Name(None),
            Rating(70),
            None,
        ),
        Song(
            Name("Neighbors"),
            Streams(streams=1),
            Minutes(1),
            Name(None),
            Rating(70),
            None,
        ),
        Song(
            Name("Foldin Clothes"),
            Streams(streams=1),
            Minutes(1),
            Name(None),
            Rating(70),
            None,
        ),
        Song(
            Name("She's Mine Pt.2"),
            Streams(streams=1),
            Minutes(1),
            Name(None),
            Rating(70),
            None,
        ),
        Song(
            Name("4 Your Eyez Only"),
            Streams(streams=1),
            Minutes(1),
            Name(None),
            Rating(70),
            None,
        ),
    ],
    Rating(80),
    None,
)

single_test = Single(
    Name("Elon Musk"),
    Name("Shallipopi"),
    [
        Song(
            Name("Elon musk"),
            Streams(streams=1),
            Minutes(1),
            Name(None),
            Rating(84),
            None,
        )
    ],
    Rating(84),
    None,
)

ep_test = EP(
    Name("Buckles Laboratories Presents: The Intermission"),
    Name("Mariah the Scientist"),
    [
        Song(
            Name("Church"),
            Streams(streams=1),
            Minutes(1),
            Name(None),
            Rating(60),
            None,
        ),
        Song(
            Name("Only Human"),
            Streams(streams=1),
            Minutes(1),
            Name(None),
            Rating(60),
            None,
        ),
        Song(
            Name("Spread Thin"),
            Streams(streams=1),
            Minutes(1),
            Name(None),
            Rating(90),
            None,
        ),
        Song(
            Name("Boys Don't Cry"),
            Streams(streams=1),
            Minutes(1),
            Name(None),
            Rating(60),
            None,
        ),
    ],
    Rating(65),
)

Jermaine_Cole = Artist(Name("J.Cole"), [album_test], [], [], None)


rate_system_test = RateSystem(
    [
        Jermaine_Cole,
        Artist(Name("Mariah the Scientist"), [], [], [ep_test], None),
    ]
)


def test_album_post_init() -> None:
    assert album_test.total_streams.streams == 14
    assert album_test.songs[0].artist_name.name == "J.Cole"
    assert album_test.total_minutes.minutes == 19


def test_single_post_init() -> None:
    assert single_test.total_streams.streams == 1
    assert single_test.songs[0].artist_name.name == "Shallipopi"
    assert single_test.total_minutes.minutes == 1


def test_ep_post_init() -> None:
    assert ep_test.total_streams.streams == 4
    assert ep_test.songs[2].artist_name.name == "Mariah the Scientist"
    assert ep_test.total_minutes.minutes == 4


def test_rate_system() -> None:
    assert rate_system_test.find_max_minutes_for_album == 19
    assert rate_system_test.find_max_streams_for_album == 14
    assert rate_system_test.find_max_minutes_for_ep == 4
    assert rate_system_test.find_max_streams_for_ep == 4
    assert rate_system_test.find_max_minutes_for_single == 0
    assert rate_system_test.find_max_streams_for_single == 0
    assert len(rate_system_test.artists) == 2


def test_artist_rating() -> None:
    assert Jermaine_Cole.calculate_artist_rating.rating == 75
