import NavigationBar from "../components/Navigationbar";
import { useLocation, Link } from "react-router";
import CreateRatingButton from "../components/CreateRatingButton";
import { useEffect, useState } from "react";

const ContentPage = () => {
    let metadata = useLocation().state;
    console.log("Data being received", metadata)
    const [discography, setDiscography] = useState(null);

    const getDiscography = async(event) => {
    let data = null;
    try{
        console.log("Is it even trying the fetch")
        const response = await fetch(`/api/discography/?type=${metadata.data.type}&spotify_id=${metadata.data.id}`, {
            method: "GET",
            credentials: "include"
            }
        );
        if (response.ok) {
            data = await response.json();
        }
    } catch(error){
        console.log("Error", error)
        data = null;
    }
    return data;
}

        useEffect(()=>{
            const loadDiscography = async () =>{
                setDiscography(await getDiscography());
            }
            console.log("effect running", metadata)
            if (metadata.data.type == "album" || metadata.data.type == "artist"){
                loadDiscography();
            }
        }, [metadata])

        console.log("Discography data", discography)
    return(
        <>
        <NavigationBar />
        <h1>{metadata.data.name}</h1>
        <CreateRatingButton type={metadata.data.type} name = {metadata.data.name} spotify_id={metadata.data.id} />
        {metadata.data.type == "album" && discography?.type =="albums" &&
        <ul>
            {discography?.track_list.map((no) =>(
                <Link to= {`/song/${no[0]}/`} state = {{"data": {"name": no[1], "type": "song", "id": no[0]}}}>
                <li key = {no[0]}>{no[1]}</li>
                </Link>
            ))}
        </ul>}
        {metadata.data.type == "artist" && discography?.type =="artists" && 
        <ul>
            {discography?.artist_albums.map((no) =>(
                <Link to= {`/album/${no[0]}/`} state = {{"data": {"name": no[1], "type": "album", "id": no[0]}}}>
                    <li key = {no[0]}>{no[1]}</li>
                    {console.log("Album data being sent from artist page", {"data": {"name": no[1], "type": "album", "id": no[0]}})}
                </Link>
            ))}
            <br />
            {discography?.artist_singles.map((no) =>(
                <Link to= {`/song/${no[0]}/`} state = {{"data": {"name": no[1], "type": "song", "id": no[0]}}}>
                    <li key = {no[0]}>{no[1]}</li>
                </Link>
            ))}
        </ul>
        }
        </>
    )
}

export default ContentPage;