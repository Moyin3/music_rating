import React from "react";
import Searchbar from "./Searchbar";
import "./styles/Navbar.css";
export default function Navbar(){ 
    return (
        <nav>
            <a href="/homepage">Home</a>
            <a href="/albums">Albums</a>
            <a href="/artists">Artists</a>
            <a href="/community">Community Page</a>
            <a href="/entries">Rating Entries</a>
            <a href="/songs">Songs</a>
            <Searchbar />
        </nav>
    );
}