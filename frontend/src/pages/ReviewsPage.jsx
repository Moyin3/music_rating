import NavigationBar from "../components/Navigationbar";
import {useEffect, useState, useContext} from "react";
import {useLocation} from "react-router";
import getReviews from "../functions/getReviews";
import AuthContext from "../functions/AuthContext";
import styles from "./styles/ReviewsPage.module.css";

const formatReviewDate = (iso) => {
  const d = new Date(iso);
  return `${d.toLocaleDateString(undefined, { day: "numeric", month: "short", year: "numeric" })} ${d.toLocaleTimeString(undefined, { hour: "2-digit", minute: "2-digit"})}`;
};

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
    <>
    <NavigationBar />
    {(user == null || user.username != username) &&(
        <>
        <h1 className = {styles.title}>{username}'s Ratings:</h1>
        </>
    )
    }
    {reviews && reviews.length != 0 &&
    <div className={styles.reviewList}>
    {reviews.map((no)=>(
        <article className={styles.review} key = {no.spotify_id}>
        <header className={styles.reviewHeader}>
            <h2 className={styles.reviewName}>{no.name}</h2>
            <span className = "score" style={{ "--score": no.score }}>
                {no.score}
            </span>
            </header>
        {no.optional_writing && (
      <p className={styles.reviewText}>{no.optional_writing}</p>
    )}
    <time className={styles.reviewDate} dateTime={no.created_at}>
    {formatReviewDate(no.created_at)}
    </time>
  </article>
    ))}
    </div>
    
}
{(!reviews || reviews.length == 0) && 
<p className = {styles.noReviews}>No reviews to be found here</p>}
    </>
)
}

export default ReviewsPage;