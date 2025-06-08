const { levenshtein } = require('./search');
const { sortByCloseness } = require('./search');
const { waitFor } = require('@testing-library/dom');

global.fetch = jest.fn(); // Mock the Fetch API

beforeEach(() => {
    // Set up a mock DOM
    document.body.innerHTML = `
        <input id="nav_search_bar" value="" />
        <div id="suggestions"></div>
        <div id="search_results"></div>
    `;
    fetch.mockClear(); // Clear any previous mock calls
});

it('should fetch search results and display suggestions on success', async () => {
    // Mock a successful API response
    require('./search')

    console.log("Triggering DOMContentLoaded event");
    document.dispatchEvent(new Event('DOMContentLoaded'));
    fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
            tracks: { items: [{ name: 'Test Track', type: 'track', id: 'track123', artists: [{ name: 'Artist1' }] }] },
            artists: { items: [{ name: 'Test Artist', type: 'artist', id: 'artist123' }] },
            albums: { items: [{ name: 'Test Album', type: 'album', id: 'album123', artists: [{ name: 'Artist1' }] }] }
        })
    });

    // Simulate user input
    const searchBox = document.getElementById('nav_search_bar');
    searchBox.value = 'Test Query';
    const event = new Event('input');
    searchBox.dispatchEvent(event);

    // Wait for the async function to complete
    await new Promise((resolve) => setTimeout(resolve, 0));

    // Assertions
    const suggestionsDiv = document.getElementById('suggestions');
    expect(fetch).toHaveBeenCalledWith('/spotify-search/?query=Test%20Query');
    await waitFor(() => {
        
        expect(suggestionsDiv.innerHTML).toContain('TRACK: <strong>Test Track</strong> by Artist1');
        expect(suggestionsDiv.innerHTML).toContain('ARTIST: <strong>Test Artist</strong>');
        expect(suggestionsDiv.innerHTML).toContain('ALBUM: <strong>Test Album</strong> by Artist1');
});
});

it('should display "No results found" if the API returns no results', async () => {
    // Mock an API response with no results
    fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
            tracks: {total: 0, items: [] },
            artists: {total: 0, items: [] },
            albums: {total: 0, items: [] }
        })
    });

    // Trigger DOMContentLoaded
    document.dispatchEvent(new Event('DOMContentLoaded'));

    // Simulate user input
    const searchBox = document.getElementById('nav_search_bar');
    searchBox.value = 'Test Query'; // Set a valid query string
    const event = new Event('input');
    searchBox.dispatchEvent(event);

    // Wait for the async function to complete
    await new Promise((resolve) => setTimeout(resolve, 0));

    // Assertions
    const suggestionsDiv = document.getElementById('suggestions');
    console.log("Suggestions div content:", suggestionsDiv.innerHTML); // Debugging log
    expect(suggestionsDiv.innerHTML).toBe('<p>No results found</p>');
});

it('should display an error message if the API call fails', async () => {
    // Mock a failed API response
    fetch.mockRejectedValueOnce(new Error('Network error'));
    console.log("Mock fetch set up to reject");

    // Trigger DOMContentLoaded
    document.dispatchEvent(new Event('DOMContentLoaded'));

    // Simulate user input
    const searchBox = document.getElementById('nav_search_bar');
    searchBox.value = 'Test Query';
    const event = new Event('input');
    searchBox.dispatchEvent(event);

    // Wait for the DOM to update
    const suggestionsDiv = document.getElementById('suggestions');
    await waitFor(() => {
        console.log("Suggestions div content:", suggestionsDiv.innerHTML); // Debugging log
        expect(suggestionsDiv.innerHTML).toBe('<p>Error fetching suggestions</p>');
    });
});

it('should calculate the correct Levenshtein distance', () => {
    expect(levenshtein('kitten', 'sitting')).toBe(3);
    expect(levenshtein('flaw', 'lawn')).toBe(2);
    expect(levenshtein('test', 'test')).toBe(0);
});

it('should sort items by closeness to the target string', () => {
    const items = [
        { name: 'kitten' },
        { name: 'sitting' },
        { name: 'kit' }
    ];
    const sorted = sortByCloseness(items, 'kitten');
    expect(sorted[0].name).toBe('kitten'); // Closest match
    expect(sorted[1].name).toBe('kit');    // Second closest
    expect(sorted[2].name).toBe('sitting'); // Farthest match
});
