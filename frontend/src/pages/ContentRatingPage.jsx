import NavigationBar from "../components/Navigationbar";
import RatingForm from "../components/RatingForm";
import { useLocation } from "react-router";

const ContentRatingPage = () => {
    console.log("info being sent to the rating", useLocation().state.data);
    let {name, type, id} = useLocation().state.data;
return(
    <>
    <NavigationBar />
    <RatingForm  name = {name} type = {type} spotify_id={id}/>
    </>
)
}

export default ContentRatingPage;