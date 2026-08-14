import { useNavigate } from "react-router";

const SuggestionsDiv = ({results}) => {
    const navigate = useNavigate();


    function selectSuggestion(suggestion) {
    // Determine the type of the suggestion and redirect to the appropriate view
    if (suggestion?.type === 'track') {
        console.log("Data being sent from search:", suggestion)
        navigate(`/song/${suggestion.id}/`, {state: {"data": suggestion}}); // Redirect to track view
    } else if (suggestion?.type === 'artist') {
        console.log("Data being sent from search:", suggestion)
        navigate(`/artist/${suggestion.id}/`, {state: {"data": suggestion}}); // Redirect to artist view
    } else if (suggestion?.type === 'album') {
        console.log("Data being sent from search:", suggestion)
        navigate(`/album/${suggestion.id}/`, {state: {"data": suggestion}}); // Redirect to album view
    } else {
        console.log("Data being sent from search:", suggestion)
        navigate(`/reviews/${suggestion}/`, {state: suggestion})
    }
} return(
        results.length === 0 ? "No results found" :

        <div className="suggestions">
    <>
    {results[1] && results[1].map((item) => {
                    if (item.type === 'track'){
                        return(
                        <div key = {item.id} onClick = {() => selectSuggestion(item)}>
                        TRACK: <strong>{item.name}</strong> by {item.artists.map(artist => artist.name). join(', ')};
                        </div>
                        );
                    }
                    else if (item.type === 'artist'){
                        return(
                            <div key = {item.id} onClick = {() => selectSuggestion(item)}>
                                ARTIST: <strong>{item.name}</strong>;
                            </div>
                        );
                    }
                    else if (item.type === 'album'){
                        return(
                            <div key = {item.id} onClick = {() => selectSuggestion(item)}>
                                ALBUM: <strong>{item.name}</strong> by {item.artists.map(artist => artist.name).join(', ')};
                            </div>
                        )
                    }
                
})}{results[0] && results[0].map((item) => {
    return(
        <div key = {item.username} onClick = {() => selectSuggestion(item.username)}>
        USER: <strong>{item.username}</strong>
        </div>
    )})
}</>
    </div>);
}

export default SuggestionsDiv;