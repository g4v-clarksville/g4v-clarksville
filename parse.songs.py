import os
import json

def parse_song_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = [line.rstrip('\n') for line in f]
    
    song = {
        "title": "Untitled",
        "artist": "Unknown",
        "youtube": "",
        "is_sing_along": False,
        "is_christmas": False,
        "content": []
    }
    
    content_mode = False
    for line in lines:
        if line.strip() == "---":
            content_mode = True
            continue
            
        if not content_mode:
            if line.lower().startswith("title:"):
                song["title"] = line.split(":", 1)[1].strip().strip('"\'')
            elif line.lower().startswith("artist:"):
                song["artist"] = line.split(":", 1)[1].strip()
            elif line.lower().startswith("youtube:"):
                song["youtube"] = line.split(":", 1)[1].strip()
            elif line.lower().startswith("singalong:"):
                song["is_sing_along"] = line.split(":", 1)[1].strip().lower() == "true"
            elif line.lower().startswith("christmas:"):
                song["is_christmas"] = line.split(":", 1)[1].strip().lower() == "true"
        else:
            song["content"].append(line)
            
    return song

def append_to_library(input_folder, output_json_path):
    song_library = []
    if os.path.exists(output_json_path):
        with open(output_json_path, 'r', encoding='utf-8') as f:
            try:
                song_library = json.load(f)
                print(f"Loaded existing library with {len(song_library)} songs.")
            except json.JSONDecodeError:
                print("Existing JSON was empty or malformed, starting fresh.")
                
    # Clean out duplicates by title
    seen_titles = set()
    deduped_library = []
    for song in song_library:
        title = song.get("title", "").strip().lower()
        if title and title not in seen_titles:
            seen_titles.add(title)
            deduped_library.append(song)
    song_library = deduped_library
    
    # Parse text files
    new_songs = []
    skipped_count = 0
    for filename in os.listdir(input_folder):
        if filename.lower().endswith(".txt"):
            filepath = os.path.join(input_folder, filename)
            song_data = parse_song_file(filepath)
            
            song_title = song_data.get("title", "").strip().lower()
            
            if song_title and song_title not in seen_titles:
                new_songs.append(song_data)
                seen_titles.add(song_title)
            else:
                skipped_count += 1
                print(f"Skipping duplicate or empty title: {song_data.get('title')}")
                
    if new_songs:
        song_library.extend(new_songs)
        
    # CRITICAL: Sort the entire library alphabetically by title for the menu
    song_library.sort(key=lambda x: x.get("title", "").strip().lower())

    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(song_library, f, indent=4)
            
    print(f"Successfully added {len(new_songs)} new songs. Skipped {skipped_count} duplicates. Total library size is now {len(song_library)} songs!")
                
if __name__ == "__main__":
    append_to_library("songs_txt", "songs.json")
