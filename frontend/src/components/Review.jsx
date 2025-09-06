import React from "react";
import "./styles/Review.css";

export default function Review({title, body}){
    return (
        <>
            <h3>Review Title</h3> {/* Replace with {title} when dynamic */}
            <p>This is the body of the review.</p> {/* Replace with {body} when dynamic */}
        </>
    )
}