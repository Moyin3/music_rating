import React from "react";
import Navbar from "../components/Navbar";
import Searchbar from "../components/Searchbar";

export default function Homepage() {
    return (
        <div>
            <Navbar />
            <Searchbar />
            <h1> Homepage </h1>
        </div>
    );
}