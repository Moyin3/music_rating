import NavigationBar from "../components/Navigationbar";
import {useEffect, useState} from "react";
import {useLocation} from "react-router";

const ReviewsPage = () =>{
    let username = useLocation().state;
    console.log("Reviews page arrivals", username)
    const[reviews, setReviews] = useState(null);
    const getReviews = async(event) =>{
        let reviews = null;
        console.log("Is this function being called")
        try{
            console.log("fetch url", `/api/ratings/${username}`)
            const response = await fetch(`/api/ratings/${username}`, {
                method: "GET",
                credentials: "include"

            });
            if (response.ok){
                reviews = await response.json()
            }
        }
        catch(error){
            console.error("Error:", error)
            reviews = null;
        }
        return reviews
    }
    useEffect(()=>{
        const loadReviews = async () =>{
            setReviews(await getReviews());
        }
        console.log("Do we get here?")
        loadReviews();
    }, [])
    console.log("Reviews", reviews)
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