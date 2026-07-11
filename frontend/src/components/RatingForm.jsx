import { useState, useEffect } from "react";


const RatingForm = ( {name, type, spotify_id} ) => {

    const [rating, setRating] = useState('');
    const [review, setReview] = useState('');
    const [rateSystem, setRateSystem] = useState('');
    const [isVisible, setVisible] = useState(true);
    const handleSave = async (event) => {
        event.preventDefault();

        const data = {"score": rating, "optional_writing":review, "spotify_id": spotify_id, "content_type": type};
        console.log(data);

        try{
            const response = await fetch("/api/ratings/", {
                method: "POST",
                credentials: "include",
                headers:{
                    "Content-Type": "application/json"
                },
                body:JSON.stringify(data)
            });
        }
        catch(error) {
            console.error("Error during fetch:", error);
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