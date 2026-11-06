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
    header_keys = ("title:", "artist:", "youtube:", "singalong:", "christmas:")
    
    for line in lines:
        stripped = line.strip()
        
        # Check for standard dividers (---, ===, ***)
        if stripped in ("---", "===", "***"):
            content_mode = True
            continue
            
        if not content_mode:
            # Check if it's a valid metadata header
            lower_line = line.lower()
            if lower_line.startswith(header_keys):
                if lower_line.startswith("title:"):
                    song["title"] = line.split(":", 1)[1].strip().strip('"\'')
                elif lower_line.startswith("artist:"):
                    song["artist"] = line.split(":", 1)[1].strip()
                elif lower_line.startswith("youtube:"):
                    song["youtube"] = line.split(":", 1)[1].strip()
                elif lower_line.startswith("singalong:"):
                    song["is_sing_along"] = line.split(":", 1)[1].strip().lower() == "true"
                elif lower_line.startswith("christmas:"):
                    song["is_christmas"] = line.split(":", 1)[1].strip().lower() == "true"
            else:
                # If a file doesn't have '---', switch to content mode automatically once we hit non-header lines
                if stripped:
                    content_mode = True
                    song["content"].append(line)
        else:
            song["content"].append(line)
            
    return song

def update_library(input_folder, output_json_path):
    # Use a dictionary keyed by normalized title to handle updates seamlessly
    song_dict = {}
    
    # 1. Load existing library into the dictionary if it exists
    if os.path.exists(output_json_path):
        with open(output_json_path, 'r', encoding='utf-8') as f:
            try:
                existing_list = json.load(f)
                for song in existing_list:
                    title_key = song.get("title", "").strip().lower()
                    if title_key:
                        song_dict[title_key] = song
                print(f"Loaded existing library with {len(song_dict)} songs.")
            except json.JSONDecodeError:
                print("Existing JSON was empty or malformed, starting fresh.")
                
    # 2. Scan text files and update/add them
    added_count = 0
    updated_count = 0
    
    for filename in os.listdir(input_folder):
        if filename.lower().endswith(".txt"):
            filepath = os.path.join(input_folder, filename)
            song_data = parse_song_file(filepath)
            song_title = song_data.get("title", "").strip().lower()
            
            if song_title and song_title != "untitled":
                if song_title in song_dict:
                    # Overwrite/update existing entry with the latest text file data
                    song_dict[song_title] = song_data
                    updated_count += 1
                else:
                    # Add brand new entry
                    song_dict[song_title] = song_data
                    added_count += 1

    # 3. Convert dictionary back to a list and sort alphabetically by title
    song_library = list(song_dict.values())
    song_library.sort(key=lambda x: x.get("title", "").strip().lower())

    # 4. Save back to songs.json
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(song_library, f, indent=4)
            
    print(f"Successfully added {added_count} new songs and updated {updated_count} existing songs. Total library size is now {len(song_library)} songs!")

if __name__ == "__main__":
    update_library("songs_txt", "songs.json")
