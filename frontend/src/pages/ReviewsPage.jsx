import NavigationBar from "../components/Navigationbar";
import {useEffect, useState} from "react";
import {useLocation} from "react-router";
import getReviews from "../functions/getReviews";

const ReviewsPage = () =>{
    let username = useLocation().state;
    console.log("Reviews page arrivals", username)
    const[reviews, setReviews] = useState(null);

    useEffect(()=>{
        const loadReviews = async () =>{
            setReviews((await getReviews({"url": `/api/reviews/?username=${username}`})).json);
        }
        console.log("Do we get here?")
        loadReviews();
    }, [])
return(
    <>
    <NavigationBar />
    {reviews &&
    <div className="reviews">
    {reviews.map((no)=>(
        <p key = {no.spotify_id}>{no.name}: {no.score}<br />{no.optional_writing}<br /> Created on: {no.created_at}</p>
    ))}
    {/* TODO: I need to change how the timestamp is displayed, preferably to something more digestable. */}
    </div>
    
}
{!reviews && 
<p>You haven't reviewed anything chief. Get on it!</p>}
    </>
)
}

export default ReviewsPage;