import React from "react";
import "./styles/Searchbar.css";

export default function Searchbar(){
    return (
        <div>
            <input type="text" id="nav_search_bar" className="nav_search_bar" placeholder="Search for a song, artist..." />
        </div>
    );
}