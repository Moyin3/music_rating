import { useNavigate } from "react-router";

const SuggestionsDiv = ({results}) => {
    const navigate = useNavigate();


    function selectSuggestion(suggestion) {

    // Determine the type of the suggestion and redirect to the appropriate view
    if (suggestion.type === 'track') {
        navigate(`/song/${suggestion.id}/`, {state: {"data": suggestion}}); // Redirect to track view
    } else if (suggestion.type === 'artist') {
        navigate(`/artist/${suggestion.id}/`, {state: {"data": suggestion}}); // Redirect to artist view
    } else if (suggestion.type === 'album') {
        navigate(`/album/${suggestion.id}/`, {state: {"data": suggestion}}); // Redirect to album view
    }
}
    return(
        results.length === 0 ? "No results found" :
        <div className="suggestions">
    {results.map((item) => {
                //I really like this for debugging, as it shows the jsonresponse I'm being returned in console.
                console.log("Processing item:", item);
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
                
            })
         }</div>);
}

export default SuggestionsDiv;