import os
import json
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "neo4j")

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

def ensure_constraints(session):
    session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (a:Artist) REQUIRE a.mbid IS UNIQUE;")
    session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (r:Release) REQUIRE r.mbid IS UNIQUE;")
    session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (rec:Recording) REQUIRE rec.mbid IS UNIQUE;")
    session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (g:Genre) REQUIRE g.name IS UNIQUE;")
    session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (t:Tag) REQUIRE t.name IS UNIQUE;")

def load_artists(json_file: str):
    """Load merged artists JSON into Neo4j."""
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    with driver.session() as session:
        ensure_constraints(session)

        for artist in data["artists"]:
            aliases = artist.get("aliases", [])
            # Artist node + aliases
            session.run(
                """
                MERGE (a:Artist {mbid: $mbid})
                SET a.name = $name,
                    a.country = $country,
                    a.aliases = coalesce($aliases, [])
                """,
                mbid=artist["mbid"],
                name=artist["name"],
                country=artist.get("country"),
                aliases=aliases
            )

            # Artist genres
            for g in artist.get("genres", []):
                g = g.lower()
                session.run(
                    """
                    MERGE (g:Genre {name: $g})
                    MERGE (a:Artist {mbid: $mbid})-[:HAS_GENRE]->(g)
                    """,
                    mbid=artist["mbid"], g=g
                )

            # Artist tags
            for t in artist.get("tags", []):
                t = t.lower()
                session.run(
                    """
                    MERGE (t:Tag {name: $t})
                    MERGE (a:Artist {mbid: $mbid})-[:HAS_TAG]->(t)
                    """,
                    mbid=artist["mbid"], t=t
                )

            # Releases
            for release in artist.get("releases", []):
                session.run(
                    """
                    MERGE (r:Release {mbid: $mbid})
                    SET r.title = $title,
                        r.date  = $date,
                        r.status = $status,
                        r.label = $label
                    MERGE (a:Artist {mbid: $artist_mbid})-[:RELEASED]->(r)
                    """,
                    mbid=release["mbid"],
                    title=release["title"],
                    date=release.get("date"),
                    status=release.get("status"),
                    label=release.get("label"),
                    artist_mbid=artist["mbid"]
                )

                # Release genres
                for g in release.get("genres", []):
                    g = g.lower()
                    session.run(
                        """
                        MERGE (g:Genre {name: $g})
                        MERGE (r:Release {mbid: $mbid})-[:HAS_GENRE]->(g)
                        """,
                        mbid=release["mbid"], g=g
                    )

                # Release tags
                for t in release.get("tags", []):
                    t = t.lower()
                    session.run(
                        """
                        MERGE (t:Tag {name: $t})
                        MERGE (r:Release {mbid: $mbid})-[:HAS_TAG]->(t)
                        """,
                        mbid=release["mbid"], t=t
                    )

                # Recordings (songs)
                for rec in release.get("recordings", []):
                    session.run(
                        """
                        MERGE (rec:Recording {mbid: $mbid})
                        SET rec.title = $title,
                            rec.length_ms = $length_ms
                        MERGE (r:Release {mbid: $release_mbid})-[:HAS_TRACK]->(rec)
                        """,
                        mbid=rec["mbid"],
                        title=rec["title"],
                        length_ms=rec.get("length_ms"),
                        release_mbid=release["mbid"]
                    )

                    # Recording genres
                    for g in rec.get("genres", []):
                        g = g.lower()
                        session.run(
                            """
                            MERGE (g:Genre {name: $g})
                            MERGE (rec:Recording {mbid: $mbid})-[:HAS_GENRE]->(g)
                            """,
                            mbid=rec["mbid"], g=g
                        )

                    # Recording tags
                    for t in rec.get("tags", []):
                        t = t.lower()
                        session.run(
                            """
                            MERGE (t:Tag {name: $t})
                            MERGE (rec:Recording {mbid: $mbid})-[:HAS_TAG]->(t)
                            """,
                            mbid=rec["mbid"], t=t
                        )

    print(f"✅ Loaded {len(data['artists'])} artists into Neo4j")

if __name__ == "__main__":
    load_artists("all_artists.json")
