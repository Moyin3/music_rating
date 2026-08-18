import NavigationBar from "../components/Navigationbar";
import RatingForm from "../components/RatingForm";
import { useLocation } from "react-router";

const ContentRatingPage = () => {
    console.log("info being sent to the rating", useLocation().state.data);
    let {name, type, id, album_spotify_id, artist_spotify_id} = useLocation().state.data;
return(
    <>
    <NavigationBar />
    <RatingForm  name = {name} type = {type} spotify_id={id} album_spotify_id = {album_spotify_id} artist_spotify_id = {artist_spotify_id}/>
    </>
)
}

export default ContentRatingPage;