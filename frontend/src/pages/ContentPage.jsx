import NavigationBar from "../components/Navigationbar";
import { useLocation, Link } from "react-router";
import CreateRatingButton from "../components/CreateRatingButton";
import { useEffect, useState } from "react";
import styles from "./styles/ContentPage.module.css";

const isScore = (v) => typeof v === "number";

const ratingClass = (v, extra = "") =>
  `${extra} ${isScore(v) ? "score" : styles.message}`;

const ratingStyle = (v) => (isScore(v) ? {"--score": v} : undefined)

const ContentPage = () => {
    let metadata = useLocation().state;
    const [backendData, setBackendData] = useState(null);
    console.log("Data being received", metadata)
    const typeClass = {artist: styles.artist, album: styles.album, song: styles.song};
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
        <main className = {` ${styles.contentMain} ${typeClass[metadata.data.type] ?? ""} `}>
        <h1 className = {styles.title}>{metadata.data.name}</h1>
        {metadata.data.type == "album" && backendData != null &&
        <>
        <div className = {styles.tracklistDiv}>
        <h2 className = {styles.trackList}>Tracklist</h2>
        <ul className = {styles.albumList}>
            {backendData.album_data?.track_list.map((no) =>(
                    <li className = {styles.trackInAlbum} key = {no[0]}>
                <Link to= {`/song/${no[0]}/`} state = {{"data": {"name": no[1], "type": "song", "id": no[0], "album_id": backendData.album_data.spotify_id, "artist_id": null}}}>
                    {no[1]}
                </Link>
                </li>
            ))}
        </ul>
        </div>
        </>}
{metadata.data.type == "artist" && backendData != null && 
<>
<div className = {styles.albumDiv}>
<h2 className= {styles.albumsTitle}>Albums</h2>
        <ul className = {styles.albumList}>
            {backendData.artist_data?.artist_albums.map((no) =>(
                    <li className = {styles.albumInArtist} key = {no[0]}>
                <Link to= {`/album/${no[0]}/`} state = {{"data": {"name": no[1], "type": "album", "id": no[0], album_spotify_id: null, artist_spotify_id: backendData.artist_data.spotify_id}}}>
                    {console.log("Album data being sent from artist page", {"data": {"name": no[1], "type": "album", "id": no[0], album_spotify_id: null, artist_spotify_id: backendData.artist_data.spotify_id}})}
                    {no[1]}
                </Link>
                </li>
            ))}
        </ul>
</div>
            {/*Currently this code below forces the type of the single to be a song, 
            which isn't necessarily true, and can lead to errors and undesired behaviour change this */}
<div className = {styles.singleEpDiv}>
<h2 className = {styles.epsSinglesTitle}>EPs & Singles</h2>
        <ul className = {styles.epSingleList}>
            {backendData.artist_data?.artist_singles.map((no) =>(
                    <li className = {styles.singleInArtist} key = {no[0]}>
                <Link to= {`/song/${no[0]}/`} state = {{"data": {"name": no[1], "type": "album", "id": no[0]}}}>
                {no[1]}
                </Link>
                </li>
            ))}
        </ul>
</div>
        </>
        }
        {/* I only send album id for songs, and artist id for albums because I believe the workflow down the line is dependent the other field being null if isn't used, will look into this later */}
        <CreateRatingButton className = {styles.createRatingButton} type={metadata.data.type} name = {metadata.data.name} spotify_id={metadata.data.id} album_spotify_id={metadata.data.type === "song" ? backendData?.song_data?.album_id: null} artist_spotify_id={metadata.data.type === "album" ? backendData?.album_data?.artist_id[0]: null}/>
        {backendData != null &&(
        <>
        <div className = {styles.communityDiv}>
        <h3 className = {styles.communityRatingTitle}>Community Rating</h3>
        <p className = {ratingClass(backendData.community_rating, styles.communityRating)} style = {ratingStyle(backendData.community_rating)}>{backendData.community_rating}</p>
        </div>
        </>
        )}
        {backendData &&(
            <>
            <div className = {styles.userDiv}>
            <h3 className = {styles.userRatingTitle}>User Rating</h3>
            <p className = {ratingClass(backendData.user_rating, styles.userRating)} style = {ratingStyle(backendData.user_rating)}>{backendData.user_rating}</p>
            </div>
            </>
        )}
        </main>
        </>
        )}

export default ContentPage;