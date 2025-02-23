from dataclasses import dataclass, field
from pydantic import BaseModel
from typing import List, Optional


@dataclass
class Name:
    name: str


class Streams(BaseModel):
    streams: int

    def __add__(self, other: "Streams") -> "Streams":
        if not isinstance(other, Streams):
            return NotImplementedError(
                f"Expected a {type(self)} object but got a {type(other)} object."
            )
        return Streams(streams=(self.streams + other.streams))


@dataclass
class Minutes:
    minutes: int

    def __add__(self, other: "Minutes") -> "Minutes":
        if not isinstance(other, Minutes):
            return NotImplementedError(
                f"Expected a {type(self)} object but got a {type(other)} object."
            )
        return Minutes(minutes=(self.minutes + other.minutes))


@dataclass
class OptionalWriting:
    writing: str


@dataclass
class Rating:
    rating: float

    def __add__(self, other: "Rating") -> "Rating":
        if not isinstance(other, Rating):
            return NotImplementedError(
                f"Expected a {type(self)} object but got a {type(other)} object."
            )
        return Rating(self.rating + other.rating)

    def __truediv__(self, other: int) -> "Rating":
        if not isinstance(other, int):
            return NotImplementedError(
                f"Expected a {int} object but got a  {type(other)} object."
            )
        return Rating(self.rating / other)


@dataclass
class Song:
    song_name: Name
    no_of_streams: Streams
    no_of_minutes: Minutes
    feat_name: Name
    rating: Rating
    optional_writing: Optional[OptionalWriting] = None
    artist_name: Name = None


@dataclass
class Album:
    album_name: Name
    artist_name: Name
    songs: list[Song]
    album_rating: Rating
    optional_writing: Optional[OptionalWriting] = None

    def __post_init__(self):
        """Automatically set the artist name for each song to be
        the same as the album's artist_name,
        calculate number of streams and number of minutes"""

        self.total_streams = Streams(streams=0)
        self.total_minutes = Minutes(minutes=0)

        for song in self.songs:
            song.artist_name = self.artist_name
            self.total_streams += song.no_of_streams
            self.total_minutes += song.no_of_minutes

    """Taking the average of user input rating of the album and the mean
    rating of the songs in the album. Could be interesting to explore this
    parameter when including machine learning. The perceived score of the
    album versus the average of the song scores given."""

    @property
    def calculate_album_rating(self):

        song_rating_total = Rating(0)
        no_of_songs_in_album = 0

        for song in self.songs:
            song_rating_total += song.rating
            no_of_songs_in_album += 1

        Album_rating = (
            (song_rating_total / no_of_songs_in_album) + self.album_rating
        ) / 2
        return Album_rating


@dataclass
class Single:
    single_name: Name
    artist_name: Name
    songs: list[Song]
    single_rating: Rating
    optional_writing: Optional[OptionalWriting] = None

    def __post_init__(self):
        """set the artist name for the single to be the same as
        the artist name for the song. Also do the calculate number of streams
        and number of minutes"""

        for song in self.songs:
            song.artist_name = self.artist_name

        self.total_streams = sum(
            (song.no_of_streams for song in self.songs), Streams(streams=0)
        )

        self.total_minutes = sum(
            (song.no_of_minutes for song in self.songs), Minutes(minutes=0)
        )

    @property
    def calculate_single_rating(self):
        song_rating_total = Rating(0)
        no_of_songs_in_single = 0

        for song in self.songs:
            song_rating_total += song.rating
            no_of_songs_in_single += 1

        Single_rating = (
            (song_rating_total / no_of_songs_in_single) + self.single_rating
        ) / 2
        return Single_rating


@dataclass
class EP:
    ep_name: Name
    artist_name: Name
    songs: list[Song]
    ep_rating: Rating
    optional_writing: Optional[OptionalWriting] = None
    """Instead of having an ep rating that is input by a user here I
    think it makes sense to have the algorithm of some sort that works
    out the ep rating based off the rating of the songs in the ep. Could maybe
    take a user input and use it to achieve a final rating."""

    def __post_init__(self):
        """ensure artist name for songs is the same as the artist name of the ep
        and do the calculation of streams and minutes stuff"""

        self.total_minutes = sum(
            (song.no_of_minutes for song in self.songs), Minutes(minutes=0)
        )
        self.total_streams = sum(
            (song.no_of_streams for song in self.songs), Streams(streams=0)
        )
        for song in self.songs:
            song.artist_name = self.artist_name

    @property
    def calculate_EP_rating(self):
        song_rating_total = Rating(0)
        no_of_songs_in_EP = 0

        for song in self.songs:
            song_rating_total += song.rating
            no_of_songs_in_EP += 1

        EP_rating = ((song_rating_total / no_of_songs_in_EP) + self.ep_rating) / 2
        return EP_rating


@dataclass
class Artist:
    name: Name
    albums: Optional[List[Album]] = field(default_factory=list)
    singles: Optional[List[Single]] = field(default_factory=list)
    eps: Optional[List[EP]] = field(default_factory=list)
    optional_writing: Optional[OptionalWriting] = None

    def __post_init__(self):
        # Ensure that albums, singles, and eps are lists
        if not isinstance(self.albums, list):
            self.albums = [self.albums]
        if not isinstance(self.singles, list):
            self.singles = [self.singles]
        if not isinstance(self.eps, list):
            self.eps = [self.eps]
        total_no_of_streams_album = Streams(streams=0)
        total_no_of_minutes_album = Minutes(minutes=0)
        total_no_of_streams_ep = Streams(streams=0)
        total_no_of_minutes_ep = Minutes(minutes=0)
        total_no_of_streams_single = Streams(streams=0)
        total_no_of_minutes_single = Minutes(minutes=0)
        if self.albums:
            for album in self.albums:
                # Calculate total streams and minutes for an Artist's albums
                total_no_of_streams_album += album.total_streams
                total_no_of_minutes_album += album.total_minutes
        if self.singles:
            # Calculate total streams and minutes for an Artist's singles
            for single in self.singles:
                total_no_of_streams_single += single.total_streams
                total_no_of_minutes_single += single.total_minutes
        if self.eps:
            # Calculate total streams and minutes for an Artist's Eps
            for ep in self.eps:
                total_no_of_streams_ep += ep.total_streams
                total_no_of_minutes_ep += ep.total_minutes

        artist_total_minutes = (
            total_no_of_minutes_ep
            + total_no_of_minutes_single
            + total_no_of_minutes_album
        )
        artist_total_streams = (
            total_no_of_streams_album
            + total_no_of_streams_ep
            + total_no_of_streams_single
        )

        self.artist_total_minutes, self.artist_total_streams = (
            artist_total_minutes,
            artist_total_streams,
        )

    def add_album_to_artist(self, new_album: Album) -> None:
        """Adds a new album to the artist"""
        for album in self.albums:
            if album.album_name.name == new_album.album_name.name:
                pass
            else:
                self.albums.append(new_album)

    def add_ep_to_artist(self, new_ep: EP) -> None:
        """Adds a new EP to the artist"""
        for ep in self.eps:
            if ep.ep_name.name == new_ep.ep_name.name:
                pass
            else:
                self.eps.append(new_ep)

    def add_single_to_artist(self, new_single: Single) -> None:
        """Adds a new Single to the artist"""
        for single in self.singles:
            if single.single_name.name == new_single.single_name.name:
                pass
            else:
                self.singles.append(new_single)

    @property
    def calculate_artist_rating(self) -> Optional[Rating]:
        total_album_ratings = Rating(0)
        total_no_of_albums = 0
        total_ep_ratings = Rating(0)
        total_no_of_eps = 0
        total_single_ratings = Rating(0)
        total_no_of_singles = 0
        for album in self.albums:
            total_album_ratings += album.calculate_album_rating
            total_no_of_albums += 1
        for ep in self.eps:
            total_ep_ratings += ep.calculate_EP_rating
            total_no_of_eps += 1
        for single in self.singles:
            total_single_ratings += single.calculate_single_rating
            total_no_of_singles += 1

        if total_no_of_albums > 0:
            mean_album_rating = total_album_ratings / total_no_of_albums
        else:
            mean_album_rating = None

        if total_no_of_eps > 0:
            mean_ep_rating = total_ep_ratings / total_no_of_eps
        else:
            mean_ep_rating = None

        if total_no_of_singles > 0:
            mean_single_rating = total_single_ratings / total_no_of_singles
        else:
            mean_single_rating = None

        # Collect all non-None ratings
        ratings = [
            r
            for r in [mean_album_rating, mean_ep_rating, mean_single_rating]
            if r is not None
        ]

        if not ratings:
            # If there are no ratings, print a message and return None
            print("No albums, EPs, or singles available for this artist.")
            return None

        # Calculate the average of available ratings
        artist_rating = sum((ratings), Rating(rating=0)) / len(ratings)
        return artist_rating


@dataclass
class RateSystem:
    artists: list[Artist]

    def add_new_artist_to_rate_system(self, new_artist: Artist) -> None:
        """Adds a new artist to the rate system if they don't exist"""
        for artist in self.artists:
            if artist.name.name == new_artist.name.name:
                pass
            else:
                self.artists.append(new_artist)

    @property
    def get_all_ratings(self) -> list[Rating]:
        ratings = []
        for artist in self.artists:  # Iterates through all artists in rating system
            for (
                album
            ) in artist.albums:  # Iterates through each album in an artist's catalogue
                for song in album.songs:  # Iterates through each song in an album
                    ratings.append(
                        song.rating
                    )  # Adds the rating of each song to a list
            for ep in artist.eps:  # Same thing for EPs.
                for song in ep.songs:
                    ratings.append(song.rating)
            for single in artist.singles:  # Same thing for singles
                for song in single.songs:
                    ratings.append(song.rating)
        return ratings

    @property
    def find_max_streams_for_album(self) -> int:
        max_album_streams = Streams(streams=0)
        for artist in self.artists:
            for album in artist.albums:
                if album.total_streams.streams > max_album_streams.streams:
                    max_album_streams = album.total_streams
        return max_album_streams.streams

    @property
    def find_max_minutes_for_album(self) -> int:
        max_album_minutes = Minutes(minutes=0)
        for artist in self.artists:
            for album in artist.albums:
                if album.total_minutes.minutes > max_album_minutes.minutes:
                    max_album_minutes = album.total_minutes
        return max_album_minutes.minutes

    @property
    def find_max_streams_for_ep(self) -> int:
        max_ep_streams = Streams(streams=0)
        for artist in self.artists:
            for ep in artist.eps:
                if ep.total_streams.streams > max_ep_streams.streams:
                    max_ep_streams = ep.total_streams
        return max_ep_streams.streams

    @property
    def find_max_minutes_for_ep(self) -> int:
        max_ep_minutes = Minutes(minutes=0)
        for artist in self.artists:
            for ep in artist.eps:
                if ep.total_minutes.minutes > max_ep_minutes.minutes:
                    max_ep_minutes = ep.total_minutes
        return max_ep_minutes.minutes

    @property
    def find_max_streams_for_single(self) -> int:
        max_single_streams = Streams(streams=0)
        for artist in self.artists:
            for single in artist.singles:
                if single.total_streams.streams > max_single_streams.streams:
                    max_single_streams = single.total_streams
        return max_single_streams.streams

    @property
    def find_max_minutes_for_single(self) -> int:
        max_single_minutes = Minutes(minutes=0)
        for artist in self.artists:
            for single in artist.singles:
                if single.total_minutes.minutes > max_single_minutes.minutes:
                    max_single_minutes = max_single_minutes
        return max_single_minutes.minutes
