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
    header_keys = ("title", "artist", "youtube", "singalong", "christmas")
    
    for line in lines:
        stripped = line.strip()
        
        # Check for standard dividers
        if stripped in ("---", "===", "***"):
            content_mode = True
            continue
            
        if not content_mode:
            # Handle both colons and semicolons in headers (e.g., "title:" or "Title;")
            if ":" in line or ";" in line:
                parts = line.split(":", 1) if ":" in line else line.split(";", 1)
                key = parts[0].strip().lower()
                val = parts[1].strip().strip('"\'')
                
                if key == "title":
                    song["title"] = val
                elif key == "artist":
                    song["artist"] = val
                elif key == "youtube":
                    song["youtube"] = val
                elif key == "singalong":
                    song["is_sing_along"] = val.lower() == "true"
                elif key == "christmas":
                    song["is_christmas"] = val.lower() == "true"
                else:
                    # If it looks like text rather than a header, start content mode
                    if stripped:
                        content_mode = True
                        song["content"].append(line)
            else:
                if stripped:
                    content_mode = True
                    song["content"].append(line)
        else:
            song["content"].append(line)
            
    return song

def update_library(input_folder, output_json_path):
    song_dict = {}
    
    # 1. LOAD EXISTING LIBRARY FIRST so we don't lose any songs!
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

    if not os.path.exists(input_folder):
        print(f"Error: Folder '{input_folder}' does not exist!")
        return

    added_count = 0
    updated_count = 0
    
    # 2. Scan and update/add files from the folder
    for filename in os.listdir(input_folder):
        if filename.lower().endswith(".txt"):
            filepath = os.path.join(input_folder, filename)
            song_data = parse_song_file(filepath)
            song_title = song_data.get("title", "").strip()
            
            if song_title and song_title.lower() != "untitled":
                key = song_title.lower()
                if key in song_dict:
                    updated_count += 1
                else:
                    added_count += 1
                song_dict[key] = song_data
            else:
                print(f"Skipping file with invalid/missing title: {filename}")

    # 3. Sort alphabetically and save
    song_library = list(song_dict.values())
    song_library.sort(key=lambda x: x.get("title", "").strip().lower())

    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(song_library, f, indent=4)
            
    print(f"Success! Added {added_count} new, updated {updated_count}. Total library size is now {len(song_library)} songs.")

if __name__ == "__main__":
    update_library("songs_txt", "songs.json")