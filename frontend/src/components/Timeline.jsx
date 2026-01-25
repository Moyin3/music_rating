import React from "react";
import Review from "./Review.jsx";
import "./styles/Timeline.css";


export default function Timeline(){
    return (
        <>
            <h2>Timeline</h2>
            <div className = "review_container">
            <Review />
            </div>
            <div className = "review_container">
                <Review />
        </div>
        <div className = "review_container">
            <Review />
        </div>
        </>
    )
}