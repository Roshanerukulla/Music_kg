# data_ingestion/relationship_fetcher.py
import musicbrainzngs

musicbrainzngs.set_useragent("MusicGraphProject", "1.0", "https://github.com/your-repo")

def get_artist_relationships(mbid: str):
    """Fetch relationships (collaborations, labels, etc.) for an artist"""
    artist_data = musicbrainzngs.get_artist_by_id(
        mbid,
        includes=["artist-rels", "label-rels"]
    )["artist"]

    relationships = []

    for rel in artist_data.get("relation-list", []):
        for r in rel.get("relation", []):
            relationships.append({
                "type": r["type"],
                "target": r.get("artist", r.get("label", {})).get("name"),
                "target_mbid": r.get("artist", r.get("label", {})).get("id"),
            })

    return relationships
