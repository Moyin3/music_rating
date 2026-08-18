import { useState, useEffect } from 'react';
import SuggestionsDiv from './SuggestionsDiv';

export default function Searchbar(){

    const [query, setQuery] = useState('');
    const [isBoxVisible, setBoxVisible] = useState(true);
    const [results, setResults] = useState([]);

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
        let distA = null;
        let distB = null;
        if (a.name){
            distA = levenshtein(a.name, targetString);
        }else if (a.username){
            distA = levenshtein(a.username, targetString);
        }
        if (b.name){
            distB = levenshtein(b.name, targetString);
        }else if (b.username){
            distB = levenshtein(b.username, targetString);
        }
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

const userSearch = async(event) => {
    if (query) setBoxVisible(true);

    try{
        const response = await fetch(`/api/search/users/?username=${encodeURIComponent(query)}`)
        const data = await response.json();
        console.log("user search data", data)

        if (data){
            const maxResults = 5;
            let tempResults = [];
            tempResults = tempResults.concat(data);
            console.log("user temp", tempResults)
            let sortedTempResults = sortByCloseness(tempResults, query);
            return sortedTempResults.slice(0, maxResults);

        }
    }catch(error){
        console.error("Error during fetch:", error);
    }
}


const spotifySearch = async(event) => {
    if(query.length < 2){
        setBoxVisible(false);
        return(
            null
        )
    }else{
        setBoxVisible(true);
    }
    try{
        const response = await fetch(`/api/search/?query=${encodeURIComponent(query)}`)
        const data = await response.json();
        if (data.tracks.total != 0 || data.artists.total != 0 || data.albums.total != 0) {
            //More css suggestion box stuff

            const maxResults = 10;

            let tempResults = [];

            tempResults = tempResults.concat(data.tracks.items);
            tempResults = tempResults.concat(data.artists.items);
            tempResults = tempResults.concat(data.albums.items);
            
            console.log("temp", tempResults)
            let sortedTempResults = sortByCloseness(tempResults, query);
            return sortedTempResults.slice(0, maxResults);

            }} 
                catch (error) {
                    console.error("Error during fetch:", error);
                    // Suggestions
                }
            }
        
        useEffect(()=> {
            async function fetchData(){
                const [resA, resB] = await Promise.all([userSearch(), spotifySearch()]);
                setResults([resA, resB]);
            }
            fetchData();
            console.log("These are the results:", results)
        }, [query]);

    return (
    <>
        <input type = "text" placeholder = "Search..." value = {query} onChange={(e) => setQuery(e.target.value)} />
        {isBoxVisible&&
        <SuggestionsDiv results = {results} />}
        </>
    );

}
