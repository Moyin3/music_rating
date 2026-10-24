import { Link } from 'react-router';

const CreateRatingButton = ({name, type, spotify_id, artist_spotify_id, album_spotify_id, className}) => {
    console.log("Data being sent to rating page", {name, type, "id": spotify_id, "artist_spotify_id": artist_spotify_id, "album_spotify_id": album_spotify_id});
    return(
        <>
        <Link className={className} to= "/rating" state =  {{"data": {name, type, "id": spotify_id, "album_spotify_id": album_spotify_id, "artist_spotify_id": artist_spotify_id}}}>
        <button >Create Rating</button>
        </Link>
        </>
    )
}

export default CreateRatingButton;