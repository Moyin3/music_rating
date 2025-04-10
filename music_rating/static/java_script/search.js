
const searchBox = document.getElementById("nav_search_bar");
const suggestionsDiv = document.getElementById("suggestions");
const resultDiv = document.getElementById("search_results");


searchBox.addEventListener("input", async () => {
    const query = searchBox.value.trim();
    if (query.length < 2) {
        suggestionsDiv.classList.remove('show');
        suggestionsDiv.innerHTML = '';
        return;
    }
    try {
        const response = await fetch(`/spotify-search/?query=${encodeURIComponent(query)}`);
        const data = await response.json();
        if (data.tracks.total != 0 || data.artists.total != 0 || data.albums.total != 0) {
            suggestionsDiv.innerHTML = '';
            
            const maxResults = 5;
            let combinedResults = [];

            combinedResults = combinedResults.concat(data.tracks.items);
            combinedResults = combinedResults.concat(data.artists.items);
            combinedResults = combinedResults.concat(data.albums.items);
            sortedCombinedResults = sortByCloseness(combinedResults, query)
            results = combinedResults.slice(0, maxResults);
        
            // Display the limited results
            results.forEach(item => {
                let itemElement;
                if (item.type === 'track') {
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
            });
        
            // Show the suggestions
            suggestionsDiv.style.display = 'block';

        } else {
            suggestionsDiv.innerHTML = '<p>No results found</p>';
        }
    } catch (error) {
        console.error('Error:', error);
        suggestionsDiv.innerHTML = '<p>Error fetching suggestions</p>';
    }
});

document.addEventListener('click', function(event) {
    if (!event.target.closest('.search_container')) {
        suggestionsDiv.style.display = 'none';
    }
});
    
function selectSuggestion(suggestion) {
    suggestionsDiv.style.display = 'none';
    id_retrieval(suggestion.type + "s", suggestion.id);
}
    
function displayResult(data) {
    console.log(data)
    console.log(data.id)
    resultDiv.innerHTML = `<p>You selected: ${data['id']}</p>`;
}

async function id_retrieval(itemType, itemId) {
    const response = await fetch(`/id-retrieval/?type=${encodeURIComponent(itemType)}&spotify_id=${encodeURIComponent(itemId)}`);
    const data = await response.json();
    displayResult(data)
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
    return list.sort((a, b) => {
        const distA = levenshtein(a.name, targetString);
        const distB = levenshtein(b.name, targetString);
        return distA - distB; // Sort by smallest distance (more similar)
    });
}

