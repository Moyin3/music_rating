import { useState, useEffect } from "react";
import { useNavigate } from "react-router";
import post from "../functions/post";


const RatingForm = ( {name, type, spotify_id} ) => {

    const [rating, setRating] = useState('');
    const [review, setReview] = useState('');
    const [rateSystem, setRateSystem] = useState('');
    const [isVisible, setVisible] = useState(true);
    let navigate = useNavigate();
    const handleSave = async (event) => {

        event.preventDefault();

        const data = {"score": rating, "optional_writing":review, "spotify_id": spotify_id, "content_type": type};
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
        if (type == 'track'){
            setVisible(false);
        }
    }, [type]);

    return(
        <form>
            <label id = "Form Title">{name}</label>
            <label>Rating</label>
            <input type = "number" min = "1" max = "100" value = {rating} onChange = {(e) => setRating(e.target.value)} />
            <label>Review</label>
            <input type = "text" value = {review} onChange = {(e) => setReview(e.target.value)}/>
            {isVisible && <>
            <label>Rate System</label>
            <select value = {rateSystem} onChange = {(e) => setRateSystem(e.target.value)} name = "rate-system">
                <option value = "1">1</option>
                <option value = "2">2</option>
            </select>
            </>}
            <button onClick = {handleSave}>Save</button>
        </form>
    )
}

export default RatingForm;