import NavigationBar from "../components/Navigationbar";
import RatingForm from "../components/RatingForm";
import { useLocation } from "react-router";

const ContentRatingPage = () => {
    const location = useLocation();
    const d = location.state?.data ?? location.state?.priorData?.data ?? {};
    const {name, type, id, album_spotify_id, artist_spotify_id} = d;
    console.log("info being sent to the rating", location.state);
return(
    <>
    <NavigationBar />
    <RatingForm  name = {name} type = {type} spotify_id={id} album_spotify_id = {album_spotify_id} artist_spotify_id = {artist_spotify_id}/>
    </>
)
}

export default ContentRatingPage;