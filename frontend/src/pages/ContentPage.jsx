import NavigationBar from "../components/Navigationbar";
import { useLocation, Link } from "react-router";
import CreateRatingButton from "../components/CreateRatingButton";
import { useEffect, useState } from "react";

const ContentPage = () => {
    let metadata = useLocation().state;
    const [backendData, setBackendData] = useState(null);
    const [discography, setDiscography] = useState(null);
    console.log("Data being received", metadata)
    const getData = async(event) => {
        let data = null;
        if (metadata.data.type == "track"){
            metadata.data.type = "song"
        }
        try{
            console.log("is fetch happening")
            const response = await fetch(`/api/${metadata.data.type}/${metadata.data.id}`, {
                method : "GET",
                credentials: "include"
            }
        );
        if (response.ok) {
            data = await response.json();
        }
    } catch(error){
        data = null;
    }
    return data;
    }
        useEffect(()=>{
            const loadData = async () =>{
                setBackendData(await getData());
            }
            console.log("effect running", metadata)
                loadData();
        }, [metadata])

        console.log("Has the frontend connected to the backend", backendData)
    return(
        <>
        <NavigationBar />
        {/*Leaving the metadata stuff behind even though we also get backend data,
        because 1. it works, 2. I don't want to go through the trouble of changing
        the createrating button navigation, the type being returned by the backend doesn't
        quite match, should be easy fix if need be */}

        <h1>{metadata.data.name}</h1>
        <CreateRatingButton type={metadata.data.type} name = {metadata.data.name} spotify_id={metadata.data.id} />
        {metadata.data.type == "album" && backendData != null &&
        <ul>
            {backendData.album_data?.track_list.map((no) =>(
                <Link to= {`/song/${no[0]}/`} state = {{"data": {"name": no[1], "type": "song", "id": no[0]}}}>
                    <li key = {no[0]}>{no[1]}</li>
                </Link>
            ))}
        </ul>}
{metadata.data.type == "artist" && backendData != null && 
        <ul>
            {backendData.artist_data?.artist_albums.map((no) =>(
                <Link to= {`/album/${no[0]}/`} state = {{"data": {"name": no[1], "type": "album", "id": no[0]}}}>
                    <li key = {no[0]}>{no[1]}</li>
                    {console.log("Album data being sent from artist page", {"data": {"name": no[1], "type": "album", "id": no[0]}})}
                </Link>
            ))}
            <br />
            {/*Currently this code below forces the type of the single to be a song, 
            which isn't necessarily true, and can lead to errors and undesired behaviour change this */}
            {backendData.artist_data?.artist_singles.map((no) =>(
                <Link to= {`/song/${no[0]}/`} state = {{"data": {"name": no[1], "type": "song", "id": no[0]}}}>
                    <li key = {no[0]}>{no[1]}</li>
                </Link>
            ))}
        </ul>
        }
        {backendData != null &&(
        <>
        <h3>Community Rating</h3>
        <p>{backendData.community_rating}</p>
        </>
        )}
        {backendData &&(
            <>
            <h3>User Rating</h3>
            <p>{backendData.user_rating}</p>
            </>
        )}
        </>
        )}

export default ContentPage;