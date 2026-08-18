import NavigationBar from "../components/Navigationbar";
import {useEffect, useState, useContext} from "react";
import {useLocation} from "react-router";
import getReviews from "../functions/getReviews";
import AuthContext from "../functions/AuthContext";

const ReviewsPage = () =>{
    let username = useLocation().state;
    console.log("Reviews page arrivals", username)
    const[reviews, setReviews] = useState(null);
    const{user, setUser} = useContext(AuthContext);

    useEffect(()=>{
        const loadReviews = async () =>{
            setReviews((await getReviews({"url": `/api/reviews/?username=${username}`})).json);
        }
        console.log("Do we get here?")
        loadReviews();
    }, [username])
return(
    <>{(user == null || user.username != username) &&(
        <>
        <h1>{username}'s Ratings:</h1>
        </>
    )
    }
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
<p>No reviews to be found here</p>}
    </>
)
}

export default ReviewsPage;