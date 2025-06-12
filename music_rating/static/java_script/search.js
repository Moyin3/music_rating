document.addEventListener("DOMContentLoaded", () => {
    // Initialize the search box and suggestions div
    const searchBox = document.getElementById("nav_search_bar");
    const suggestionsDiv = document.getElementById("suggestions");

    if (!searchBox || !suggestionsDiv) {
        console.error("One or more required DOM elements are missing.");
        return;
    }
    let debounceTimeout;

    searchBox.addEventListener("input", () => {
        clearTimeout(debounceTimeout);


        debounceTimeout = setTimeout(async () => {
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
                    var pop_success = true;

                    combinedResults = combinedResults.concat(data.tracks.items);
                    combinedResults = combinedResults.concat(data.artists.items);
                    
                    // Get Album popularity
                    if (data.albums.total != 0) {
                        
                        var id_string = '';
                        for (const album of data.albums.items) {
                            id_string = id_string + album.id + ',';
                        }
                        try {
                            const response = await fetch(`/album-pop/?query=${encodeURIComponent(id_string.slice(0, -1))}`);
                            const album_pops = await response.json();
                            for (const album of data.albums.items) {
                                album.popularity = album_pops[album.id];
                            }
                        } catch {
                            pop_success = false;
                        }
                    }

                    combinedResults = combinedResults.concat(data.albums.items);
                    //const sortedCombinedResults = sortByCloseness(combinedResults, query);
                    const sortedCombinedResults = sortByCloseness(combinedResults, query, pop_success);
                    const results = sortedCombinedResults.slice(0, maxResults);
                
                    // Display the limited results
                    results.forEach(item => {
                        console.log("Processing item:", item);
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
                        console.log("Updated suggestionsDiv content:", suggestionsDiv.innerHTML);
                    });
                
                    // Show the suggestions
                    suggestionsDiv.style.display = 'block';

                } else {
                    suggestionsDiv.innerHTML = '<p>No results found</p>';
                }
            } catch (error) {
                console.error('Error during fetch:', error);
                suggestionsDiv.innerHTML = '<p>Error fetching suggestions</p>';
            }
        }, 350);
    });

    document.addEventListener('click', function(event) {
        if (!event.target.closest('.search_container')) {
            suggestionsDiv.style.display = 'none';
        }
    });

    const mapToggleBtn = document.getElementById("mapToggleBtn");
    const mapContainer = document.getElementById("mapContainer");

    let mapInitialized = false;
    let map;

    mapToggleBtn.addEventListener("click", () => {
        if (mapContainer.style.display === "none") {
            mapContainer.style.display = "block";
            mapToggleBtn.textContent = "Hide Map";
            if (!mapInitialized) {
                map = L.map('mapContainer').setView([20, 0], 2);
                L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
                    attribution: '&copy; <a href="https://carto.com/">CARTO</a>'
                }).addTo(map);

                map.on('click', async function (e) {
                    const lat = e.latlng.lat.toFixed(5);
                    const lon = e.latlng.lng.toFixed(5);
                    const currentZoom = map.getZoom();
                    map.setView(e.latlng, Math.max(currentZoom + 3, 10));
                    const params = new URLSearchParams({
                        zoom: currentZoom,
                        lat: lat,
                        lon: lon
                    });
                    try {
                        const response = await fetch(`/map-search/?${params.toString()}`);
                        const data = await response.json();
                        if (data.location) {
                            const locationName = data.location;
                            const artists = data.artists || [];

                            const resultDiv = document.getElementById("coordsDisplay");
                            resultDiv.innerHTML = `<h3>Artists from ${locationName}:</h3>`;

                            if (artists.length > 0) {
                                const ul = document.createElement('ul');
                                artists.forEach(name => {
                                    const li = document.createElement('li');
                                    li.textContent = name;
                                    ul.appendChild(li);
                                });
                                resultDiv.appendChild(ul);
                            } else {
                                resultDiv.innerHTML += `<p>No artists found.</p>`;
                            }
                        }
                    } catch (err) {
                        console.error("Error fetching artist data:", err);
                    }
                });

                mapInitialized = true;
            }
        } else {
            mapContainer.style.display = "none";
            mapToggleBtn.textContent = "Select Location on Map";
        }
    });
});





function selectSuggestion(suggestion) {

    // Determine the type of the suggestion and redirect to the appropriate view
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


function sortByCloseness(list, targetString, pop_success) {
    // First: compute max possible distance for normalization
    const maxDist = Math.max(...list.map(item => levenshtein(item.name, targetString))) || 1;

    const sorted = list.sort((a, b) => {
        console.log(a.name);
        console.log(a.popularity);
        console.log(b.name);
        console.log(b.popularity);
        const distA = levenshtein(a.name.toLowerCase(), targetString.toLowerCase());
        const distB = levenshtein(b.name.toLowerCase(), targetString.toLowerCase());

        if (pop_success) {

            // Normalize distance (0 = close, 1 = far)
            const normDistA = distA / maxDist;
            const normDistB = distB / maxDist;

            // Normalize popularity (0 = least popular, 1 = most popular)
            const normPopA = (a.popularity ?? 20) / 100;
            const normPopB = (b.popularity ?? 20) / 100;

            // Weights: tune these if needed
            const weightDist = 0.92;
            const weightPop = 0.08;

            var scoreA = normDistA * weightDist + (1 - normPopA) * weightPop;
            var scoreB = normDistB * weightDist + (1 - normPopB) * weightPop;

            const aContainsQuery = a.name.toLowerCase().includes(targetString.toLowerCase());
            const bContainsQuery = b.name.toLowerCase().includes(targetString.toLowerCase());
            if (distA > 3 && !aContainsQuery) {
                scoreA *= 2; 
            }
             if (distB > 3 && !bContainsQuery) {
                scoreB *= 2; 
            }

            if (scoreA !== scoreB) {
                console.log(scoreA - scoreB);
                return scoreA - scoreB; // lower score = better
            }
        } else {
            console.log('not using pop');
            // If not considering popularity
            if (distA !== distB) {
                return distA - distB;
            }
        }
        
        if (a.popularity !== undefined && b.popularity !== undefined && a.popularity !== b.popularity) {
            return b.popularity - a.popularity; // more popular = higher rank
        }   
        // Final fallback: alphabetical
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
