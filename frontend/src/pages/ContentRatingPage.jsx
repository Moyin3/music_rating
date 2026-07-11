import NavigationBar from "../components/Navigationbar";
import RatingForm from "../components/RatingForm";
import { useLocation } from "react-router";

const ContentRatingPage = () => {
    let {name, type, spotify_id} = useLocation().state.data;
return(
    <>
    <NavigationBar />
    <RatingForm  name = {name} type = {type} spotify_id={spotify_id}/>
    </>
)
}

export default ContentRatingPage;