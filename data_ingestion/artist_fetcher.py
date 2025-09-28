# data_ingestion/artist_fetcher.py
import musicbrainzngs

musicbrainzngs.set_useragent("MusicGraphProject", "1.0", "https://github.com/your-repo")

def search_artist(name: str, limit: int = 5):
    """Search for artists by name and return list of matches"""
    result = musicbrainzngs.search_artists(artist=name, limit=limit)
    return [
        {
            "mbid": a["id"],
            "name": a["name"],
            "country": a.get("country"),
            "disambiguation": a.get("disambiguation", ""),
        }
        for a in result["artist-list"]
    ]

def get_artist(mbid: str):
    """Fetch full artist info by MBID (genres via tags)"""
    artist_data = musicbrainzngs.get_artist_by_id(
        mbid,
        includes=["tags", "aliases"]  # 🔹 removed "genres"
    )["artist"]

    # MusicBrainz treats genres as tagged categories
    tags = [t["name"].lower() for t in artist_data.get("tag-list", [])]

    # A small curated list of known music genres (can expand later)
    known_genres = {
        "rock", "pop", "jazz", "hip hop", "rap", "classical", "electronic",
        "r&b", "soul", "punk", "metal", "indie", "folk", "blues", "country",
        "reggae", "ska", "k-pop", "j-pop"
    }

    genres = sorted([t for t in tags if t in known_genres])
    free_tags = sorted([t for t in tags if t not in genres])

    return {
        "mbid": artist_data["id"],
        "name": artist_data["name"],
        "country": artist_data.get("country"),
        "genres": genres,
        "tags": free_tags,
        "aliases": [al["alias"] for al in artist_data.get("alias-list", [])] if "alias-list" in artist_data else [],
    }
