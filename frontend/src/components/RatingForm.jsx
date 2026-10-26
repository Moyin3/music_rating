import { useState, useEffect } from "react";
import { useNavigate, useLocation} from "react-router";
import post from "../functions/post";
import styles from "./styles/RatingForm.module.css";

const rateMethodHints = {
  1: "You enter the score yourself.",
  2: "Takes an average of songs in an album, or scores in an artist's discography.",
};

const RatingForm = ( {name, type, spotify_id, album_spotify_id, artist_spotify_id} ) => {

    const [rating, setRating] = useState('');
    const [review, setReview] = useState('');
    const [rateSystem, setRateSystem] = useState("1");
    const [isVisible, setVisible] = useState(true);
    const [notice, setNotice] = useState(null);
    let navigate = useNavigate();
    const location = useLocation();

    const handleSave = async (event) => {
        event.preventDefault();

        const data = {"name": name, "score": rating, "optional_writing":review, "spotify_id": spotify_id, "content_type": type, "rate_system": rateSystem, "album_spotify_id": album_spotify_id, "artist_spotify_id": artist_spotify_id};
        if (rating == ""){
            delete data.score;
        }
        console.log("This is the data being sent before validation", data);

        const response = await post({"url": "/api/ratings/", "data": data});
        
        let first = null;

       console.log("offline check", response);
        if (response.status == "success"){
            setNotice({type: "success", message: "Rating saved"});
            navigate(`/${type}/${spotify_id}/`, {state: {"data": {name, type, "id": spotify_id, "album_spotify_id": album_spotify_id, "artist_spotify_id": artist_spotify_id}}})
        }else if (response.status == "need login"){
            navigate("/login", {state: {priorData: {location, Data: {name, type, "id": spotify_id, "album_spotify_id": album_spotify_id, "artist_spotify_id": artist_spotify_id}}}})
        }
        else if (response.status == "error: request failed"){
            first = Object.values(response.json)[0];
            setNotice({type: "alert", message: Array.isArray(first) ? first[0] : first});
        }
        else{
            setNotice({type: "alert", message: "Couldn't save rating, try again"});
        }
            
    }
    console.log("Can't be arsed to see if this should be coming from somewhere", type);
    useEffect(() => {
        if (type == 'song'){
            setVisible(false);
        }
    }, [type]);

    return(
        <main className = {styles.ratingMain}>
        <form className = {styles.ratingForm}>
        <label className={styles.Title}>{name}</label>
            {rateSystem == 1 &&
            <>
            {isVisible &&
           <div className={styles.rateMethodDiv}>
            <label className={styles.rateMethodTitle} htmlFor="rate-method">Rate Method</label>
            <select id="rate-method" aria-describedby="rate-method-hint" className={styles.ratingDropdown} value={rateSystem} onChange={(e) => setRateSystem(e.target.value)} name="rate-system">
                <option value="1">explicit</option>
                <option value="2">average</option>
            </select>
            <p id="rate-method-hint" className={styles.hint}>
                {rateMethodHints[rateSystem]}
            </p>
            </div> 
            }
            <div className = {styles.ratingDiv}>
            <label className = {styles.ratingTitle}>Rating</label>
            <input className = {styles.ratingInput} type = "number" min = "1" max = "100" value = {rating} onChange = {(e) => setRating(e.target.value)} />
            </div>
            <div className = {styles.explicitReviewDiv}>
            <label className = {styles.ReviewTitle}>Review</label>
            <textarea placeholder="Please leave us some choice words regarding your rating. (Optional)" className = {styles.comment} value = {review} onChange = {(e) => setReview(e.target.value)}/>
            </div>
            </>
            }
            {rateSystem == 2 && 
            <>
            <div className={styles.rateMethodDiv}>
            <label className={styles.rateMethodTitle} htmlFor="rate-method">Rate Method</label>
            <select id="rate-method" aria-describedby="rate-method-hint" className={styles.ratingDropdown} value={rateSystem} onChange={(e) => setRateSystem(e.target.value)} name="rate-system">
                <option value="1">explicit</option>
                <option value="2">average</option>
            </select>
            <p id="rate-method-hint" className={styles.hint}>
                {rateMethodHints[rateSystem]}
            </p>
            </div> 
            <div className = {styles.averageReviewDiv}>
            <label className = {styles.ReviewTitle}>Review</label>
            <textarea placeholder="Please leave us some choice words regarding your rating. (Optional)" className = {styles.comment} value = {review} onChange = {(e) => setReview(e.target.value)}/>
            </div>
            </>}
            <button className = {styles.save} onClick = {handleSave}>Save</button>
        </form>
    {notice && (
        <div className = {notice.type}>
            <span className = "closeBtn" onClick = {() => setNotice(null)}>
                &times;
            </span>
            {notice.message}
            </div>
        )}
        </main>
    )
}

export default RatingForm;