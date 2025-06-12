import requests
from django.http import JsonResponse
from urllib.parse import quote


def get_local_artist_ids(request):
    try:
        zoom = int(request.GET.get('zoom'))
        lat = float(request.GET.get('lat'))
        lon = float(request.GET.get('lon'))
    except (TypeError, ValueError):
        return JsonResponse({'error': 'Invalid or missing parameters'}, status=400)
    artists = []
    wiki_location = ''
    while len(artists) == 0 and wiki_location != None:
        
        location = get_location_name_from_coords(lat, lon, zoom)
        wiki_location = get_wikidata_qid(location)
        artists = query_music_artists_by_location(wiki_location)
        zoom -= 2
        print(wiki_location)
        print(zoom)
        print(artists)
    
    return JsonResponse({'location': location, 'artists' : list(set(artists))})




def get_location_name_from_coords(lat, lon, zoom):
   
    params = {
        'lat': str(lat),
        'lon': str(lon),
        'format': 'json',
        'zoom': str(zoom),      # 10 = city; increase for more niche
        'addressdetails': 1
    }
    url = "https://nominatim.openstreetmap.org/reverse"
    res = requests.get(url, params=params, headers={"User-Agent": "YourApp"})
    data = res.json()
    address = data.get("address", {})

    if not address:
        return "Unknown address"

    # Return more specific values at higher zooms, fallback to general
    if zoom >= 13:
        return (
            address.get("city") or
            address.get("town") or
            address.get("village") or
            address.get("hamlet")
        )
    elif 9 <= zoom < 13:
        return (
            address.get("county") or
            address.get("state_district") or
            address.get("state")
        )
    else:  # zoom < 9
        return address.get("country")

def get_wikidata_qid(location):
    if location != 'Unknown address':
        url = f"https://www.wikidata.org/w/api.php"
        params = {
            "action": "wbsearchentities",
            "search": location,
            "language": "en",
            "format": "json",
            "type": "item"
        }
        res = requests.get(url, params=params)
        data = res.json()
        if data['search']:
            return data['search'][0]['id']
    return None



def query_music_artists_by_location(qid):
    if qid:
        query = f"""
        SELECT ?artist ?artistLabel ?birthDate ?genreLabel WHERE {{
        ?artist wdt:P31 wd:Q5;
                wdt:P106 ?occupation;
                wdt:P19 wd:{qid}.
        ?occupation wdt:P279* wd:Q639669.
        OPTIONAL {{ ?artist wdt:P136 ?genre. }}
        OPTIONAL {{ ?artist wdt:P569 ?birthDate. }}
        SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
        }}
        LIMIT 5
        """
        headers = {"Accept": "application/sparql-results+json"}
        res = requests.get("https://query.wikidata.org/sparql", params={"query": query}, headers=headers)
        data = res.json()
        # Parse out artist names
        artists = [
            result["artistLabel"]["value"]
            for result in data.get("results", {}).get("bindings", [])
            if "artistLabel" in result
        ]
        return artists
    return []



