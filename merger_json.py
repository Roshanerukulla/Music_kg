import json
import glob
import os

def merge_artist_jsons(input_folder=".", output_file="all_artists.json"):
    all_data = {"artists": []}

    for file in glob.glob(os.path.join(input_folder, "*_data.json")):
        with open(file, "r", encoding="utf-8") as f:
            artist_data = json.load(f)
            all_data["artists"].append(artist_data)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=4, ensure_ascii=False)

    print(f"✅ Merged {len(all_data['artists'])} artists into {output_file}")

if __name__ == "__main__":
    merge_artist_jsons(input_folder=".")
