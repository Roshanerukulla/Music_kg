import musicbrainzngs

musicbrainzngs.set_useragent(
    "Musickg",
    "1.0",
    "https://github.com/Roshanerukulla/Music_kg"
)

result = musicbrainzngs.search_artists(artist="The Beatles", limit=2)
for artist in result['artist-list']:
    print(artist['id'], artist['name'], artist.get('country'))