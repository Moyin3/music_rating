import { useState } from 'react';
import SuggestionsDiv from './SuggestionsDiv';

export default function Searchbar(){

    const [query, setQuery] = useState('');
    const [isBoxVisible, setBoxVisible] = useState(false);
    const [combinedResults, setCombinedResults] = useState([]);
    const [results, setResults] = useState('');
    const [sortedCombinedResults, setSortedCombinedResults] = useState([]);

    function selectSuggestion(suggestion) {

    // Determine the type of the suggestion and redirect to the appropriate view
    console.log("Here");
    if (suggestion.type === 'track') {
        window.location.href = `/song/${suggestion.id}/`; // Redirect to track view
    } else if (suggestion.type === 'artist') {
        window.location.href = `/artist/${suggestion.id}/`; // Redirect to artist view
    } else if (suggestion.type === 'album') {
        window.location.href = `/album/${suggestion.id}/`; // Redirect to album view
    }
}

function levenshtein(a, b) {
    const tmp = [];
    let i, j;
    for (i = 0; i <= b.length; i++) {
        tmp[i] = [i];
    }
    for (j = 0; j <= a.length; j++) {
        tmp[0][j] = j;
    }
    for (i = 1; i <= b.length; i++) {
        for (j = 1; j <= a.length; j++) {
            tmp[i][j] = Math.min(
                tmp[i - 1][j] + 1, // deletion
                tmp[i][j - 1] + 1, // insertion
                tmp[i - 1][j - 1] + (a[j - 1] === b[i - 1] ? 0 : 1) // substitution
            );
        }
    }
    return tmp[b.length][a.length];
}

// Function to sort items by how close they are to a given string
function sortByCloseness(list, targetString) {
    const sorted = list.sort((a, b) => {
        const distA = levenshtein(a.name, targetString);
        const distB = levenshtein(b.name, targetString);
        if (distA !== distB) {
            return distA - distB;
        }
        return a.name.localeCompare(b.name);
    });
    return sorted;
}

//Exporting functions so they can be tested
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        levenshtein,
        sortByCloseness
    };
} else {
    window.levenshtein = levenshtein;
    window.sortByCloseness = sortByCloseness;
}

// Will need this function later

// async function id_retrieval(itemType, itemId) {
//     const response = await fetch(`/id-retrieval/?type=${encodeURIComponent(itemType)}&spotify_id=${encodeURIComponent(itemId)}`);
//     const data = await response.json();
//     return data
// }



const search = async(event) => {
    if(query.length < 2){
    }
    try{
        const response = await fetch(`/spotify-search/?query=${encodeURIComponent(query)}`)
        const data = await response.json();
        if (data.tracks.total != 0 || data.artists.total != 0 || data.albums.total != 0) {
            //More css suggestion box stuff

            const maxResults = 5;

            let tempCombinedResults = [];

            tempCombinedResults = tempCombinedResults.concat(data.tracks.items);
            tempCombinedResults = tempCombinedResults.concat(data.artists.items);
            tempCombinedResults = tempCombinedResults.concat(data.albums.items);

            setCombinedResults(tempCombinedResults);

            setSortedCombinedResults(sortByCloseness(combinedResults, query));
            setResults(sortedCombinedResults.slice(0, maxResults));

            //Display the limited results
            results.forEach(item => {
                console.log("Processing item:", item);
                let itemElement;
                if (item.type === 'track'){
                    itemElement = document.createElement('div');
                    itemElement.innerHTML = `TRACK: <strong>${item.name}</strong> by ${item.artists.map(artist => artist.name).join(', ')}`;
                    itemElement.onclick = () => selectSuggestion(item);
                } else if (item.type === 'artist') {
                    itemElement = document.createElement('div');
                    itemElement.innerHTML = `ARTIST: <strong>${item.name}</strong>`;
                    itemElement.onclick = () => selectSuggestion(item);
                } else if (item.type === 'album') {
                    itemElement = document.createElement('div');
                    itemElement.innerHTML = `ALBUM: <strong>${item.name}</strong> by ${item.artists.map(artist => artist.name).join(', ')}`;
                    itemElement.onclick = () => selectSuggestion(item);
                }
                // Append the item to the suggestions div
                suggestionsDiv.appendChild(itemElement);
                console.log("Updated suggestionsDiv content:", suggestionsDiv.innerHTML);
            });

            results.map((item) => {
                //I think this might be a debugging line, keeping it in because why not, and I'm unsure.
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

            //Show the suggestions
            // Even more CSS stuff
            } else {
                // suggestions div stuff

            }} 
                catch (error) {
                    console.error("Error during fetch:", error);
                    // Suggestions
                }
            }

    return (
        <input type = "text" placeholder = "Search..." value = {query} onChange={(e) => setQuery(e.target.value)} />
    );

}
