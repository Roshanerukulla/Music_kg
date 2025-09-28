# data_ingestion/release_fetcher.py
import musicbrainzngs

musicbrainzngs.set_useragent("MusicGraphProject", "1.0", "https://github.com/your-repo")

def get_releases(artist_mbid: str, limit: int = 10):
    """Fetch releases (albums, EPs, singles) for an artist, with tags/genres"""
    releases = musicbrainzngs.browse_releases(
        artist=artist_mbid,
        includes=["release-groups", "labels"],  # ✅ removed "tags"
        limit=limit
    )["release-list"]

    results = []
    known_genres = {
        "rock", "pop", "jazz", "hip hop", "rap", "classical", "electronic",
        "r&b", "soul", "punk", "metal", "indie", "folk", "blues", "country",
        "reggae", "ska", "k-pop", "j-pop"
    }

    for r in releases:
        # Step 2: lookup release again to fetch tags
        try:
            release_full = musicbrainzngs.get_release_by_id(
                r["id"],
                includes=["tags", "artist-credits", "labels"]
            )["release"]

            tags = [t["name"].lower() for t in release_full.get("tag-list", [])]
            genres = sorted([t for t in tags if t in known_genres])
            free_tags = sorted([t for t in tags if t not in genres])

        except Exception:
            genres, free_tags = [], []

        results.append({
            "mbid": r["id"],
            "title": r["title"],
            "date": r.get("date", "Unknown"),
            "status": r.get("status", "Unknown"),
            "label": r["label-info-list"][0]["label"]["name"] if "label-info-list" in r else None,
            "genres": genres,
            "tags": free_tags
        })

    return results
