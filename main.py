# main.py
import json
from data_ingestion.artist_fetcher import search_artist, get_artist
from data_ingestion.release_fetcher import get_releases
from data_ingestion.recording_fetcher import get_recordings

def build_artist_package(artist_name: str, release_limit: int = 3):
    """End-to-end ingestion: artist → releases → recordings"""
    search_results = search_artist(artist_name, limit=1)
    if not search_results:
        return {"error": "Artist not found"}

    # Step 1: Artist details
    artist = get_artist(search_results[0]["mbid"])
    artist["releases"] = []

    # Step 2: Releases for artist
    releases = get_releases(artist["mbid"], limit=release_limit)
    for r in releases:
        # Step 3: Recordings (songs) for each release
        r["recordings"] = get_recordings(r["mbid"])
        artist["releases"].append(r)

    return artist

if __name__ == "__main__":
    artists = ["Coldplay", "Taylor Swift", "BTS" ,"Kanye West","Arijit Singh"]
    
    for name in artists:
        data = build_artist_package(name, release_limit=2)

        # Save to JSON file
        output_file = f"{name.replace(' ', '_').lower()}_data.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        print(f"✅ Data for {name} saved to {output_file}")

