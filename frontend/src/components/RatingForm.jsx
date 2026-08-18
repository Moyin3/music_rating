import { useState, useEffect } from "react";
import { useNavigate } from "react-router";
import post from "../functions/post";


const RatingForm = ( {name, type, spotify_id, album_spotify_id, artist_spotify_id} ) => {

    const [rating, setRating] = useState('');
    const [review, setReview] = useState('');
    const [rateSystem, setRateSystem] = useState("1");
    const [isVisible, setVisible] = useState(true);
    let navigate = useNavigate();

    console.log("Genuinely confused", name, type, spotify_id, album_spotify_id, artist_spotify_id)
    const handleSave = async (event) => {
        event.preventDefault();

        const data = {"name": name, "score": rating, "optional_writing":review, "spotify_id": spotify_id, "content_type": type, "rate_system": rateSystem, "album_spotify_id": album_spotify_id, "artist_spotify_id": artist_spotify_id};
        if (rating == ""){
            delete data.score;
        }
        console.log("This is the data being sent before validation", data);

        const response = await post({"url": "/api/ratings/", "data": data});
        
        if (response.status == "success"){
            console.log(response)
            //Do nothing I guess
        }else if (response.status == "need login"){
            navigate("/login")
        }
        else if (response.status == "error: request failed"){
            //Also need to handle this later, but should be easier to fix
        }
        else{
            //Need to handle this later
        }
            
    }
    useEffect(() => {
        if (type == 'song'){
            setVisible(false);
        }
    }, [type]);

    return(
        <form>{rateSystem == 1 &&
            <>
            <label id = "Form Title">{name}</label>
            <label>Review</label>
            <input type = "text" value = {review} onChange = {(e) => setReview(e.target.value)}/>
            <label>Rating</label>
            <input type = "number" min = "1" max = "100" value = {rating} onChange = {(e) => setRating(e.target.value)} />
            <select value = {rateSystem} onChange = {(e) => setRateSystem(e.target.value)} name = "rate-system">
                <option value = "1">explicit</option>
                <option value = "2">average</option>
            </select>
            </>
            }
            {rateSystem == 2 && 
            <>
            <label>Review</label>
            <input type = "text" value = {review} onChange = {(e) => setReview(e.target.value)}/>
            <label>Rate System</label>
            <select value = {rateSystem} onChange = {(e) => setRateSystem(e.target.value)} name = "rate-system">
                <option value = "1">explicit</option>
                <option value = "2">average</option>
            </select>
            </>}
            <button onClick = {handleSave}>Save</button>
        </form>
    )
}

export default RatingForm;