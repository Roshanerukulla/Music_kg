# data_ingestion/recording_fetcher.py
import musicbrainzngs

musicbrainzngs.set_useragent("MusicGraphProject", "1.0", "https://github.com/your-repo")

def get_recordings(release_mbid: str):
    """Fetch tracks from a given release, with genres/tags if available"""
    release_data = musicbrainzngs.get_release_by_id(
        release_mbid,
        includes=["recordings", "tags"]   # ✅ removed "genres"
    )["release"]

    known_genres = {
        "rock", "pop", "jazz", "hip hop", "rap", "classical", "electronic",
        "r&b", "soul", "punk", "metal", "indie", "folk", "blues", "country",
        "reggae", "ska", "k-pop", "j-pop"
    }

    tracks = []
    for medium in release_data.get("medium-list", []):
        for track in medium.get("track-list", []):
            rec = track["recording"]

            tags = [t["name"].lower() for t in rec.get("tag-list", [])]
            genres = sorted([t for t in tags if t in known_genres])
            free_tags = sorted([t for t in tags if t not in genres])

            tracks.append({
                "mbid": rec["id"],
                "title": rec["title"],
                "length_ms": int(rec["length"]) if "length" in rec else None,
                "genres": genres,
                "tags": free_tags
            })
    return tracks
