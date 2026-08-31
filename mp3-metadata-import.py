import os
import re
import requests
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, TIT2, TPE1, TALB, TDRC, TCON, error


def clean_filename(filename):
    name_without_ext = os.path.splitext(filename)[0]
    
    # 1. Remove typical YouTube IDs at the end (e.g., [djV11Xbc914])
    name = re.sub(r'\[[a-zA-Z0-9_-]{11}\]\s*$', '', name_without_ext)
    
    # 2. Remove brackets containing typical video clutter tags
    unwanted_phrases = [
        r'[\(\[\s]*(official\s+video|official\s+audio|lyrics|4k|hd|video|audio|clip|hq)[\)\]\s]*'
    ]
    for phrase in unwanted_phrases:
        name = re.sub(phrase, '', name, flags=re.IGNORECASE)
        
    # 3. Remove any remaining empty brackets or parentheses
    name = re.sub(r'\[\s*\]|\(\s*\)', '', name)
    
    # Clean up excessive whitespaces
    name = re.sub(r'\s+', ' ', name).strip()
    return name

def fetch_cover_from_itunes(search_term):
    print(f"Searching online for: '{search_term}'...")
    url = "https://itunes.apple.com/search"
    params = {"term": search_term, "media": "music", "limit": 1}
    
    # IMPORTANT: Mimic a real web browser to prevent 403 Forbidden errors
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        if response.status_code != 200:
            print(f"Error: Server responded with status code {response.status_code}")
            return None
            
        try:
            data = response.json()
        except Exception:
            print("Error: Server response was not a valid JSON format (possible HTML blockage).")
            # Debug output of the first 200 characters of the server response
            print(f"Server response snippet: {response.text[:200]}")
            return None

        if data.get("resultCount", 0) > 0:
            artwork_url = data["results"][0]["artworkUrl100"]
            high_res_url = artwork_url.replace("100x100bb", "600x600bb")
            
            # Download the image
            img_response = requests.get(high_res_url, headers=headers, timeout=10)
            if img_response.status_code == 200:
                return img_response.content
            else:
                print(f"Error downloading image. Status code: {img_response.status_code}")
    except Exception as e:
        print(f"Network error during online search: {e}")
    return None

def embed_metadata_and_cover(file_path, track_info, image_data):
    try:
        try:
            audio = MP3(file_path, ID3=ID3)
        except error:
            audio = MP3(file_path)
            audio.add_tags()
            
        # 1. Delete old artwork if it exists
        old_covers = [key for key in audio.tags.keys() if key.startswith('APIC')]
        for key in old_covers:
            del audio.tags[key]

        # 2. Write metadata (automatically overwrites existing tags)
        if track_info.get("trackName"):
            audio.tags.add(TIT2(encoding=3, text=track_info["trackName"]))       # Title
        if track_info.get("artistName"):
            audio.tags.add(TPE1(encoding=3, text=track_info["artistName"]))      # Artist
        if track_info.get("collectionName"):
            audio.tags.add(TALB(encoding=3, text=track_info["collectionName"]))  # Album
        if track_info.get("primaryGenreName"):
            audio.tags.add(TCON(encoding=3, text=track_info["primaryGenreName"])) # Genre
        if track_info.get("releaseDate"):
            audio.tags.add(TDRC(encoding=3, text=track_info["releaseDate"][:4])) # Year (first 4 characters)

        # 3. Add the new cover artwork
        if image_data:
            audio.tags.add(
                APIC(
                    encoding=3,       
                    mime='image/jpeg', 
                    type=3,           # Front Cover
                    desc='Front Cover',
                    data=image_data
                )
            )
            
        audio.save(v2_version=3) # Saves in Windows-compatible ID3v2.3 format
        return True
    except Exception as e:
        print(f"Error writing metadata to {os.path.basename(file_path)}: {e}")
        return False

def fetch_data_from_itunes(search_term):
    print(f"Searching online for: '{search_term}'...")
    url = "https://itunes.apple.com/search"
    params = {"term": search_term, "media": "music", "limit": 1}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        if response.status_code != 200:
            return None, None
            
        try:
            data = response.json()
        except Exception:
            return None, None

        if data.get("resultCount", 0) > 0:
            track_info = data["results"][0] # Fixed: Index [0] added to get the first result
            artwork_url = track_info.get("artworkUrl100")
            image_data = None
            
            if artwork_url:
                high_res_url = artwork_url.replace("100x100bb", "600x600bb")
                img_response = requests.get(high_res_url, headers=headers, timeout=10)
                if img_response.status_code == 200:
                    image_data = img_response.content
                    
            return track_info, image_data
    except Exception as e:
        print(f"Network error: {e}")
        
    return None, None


def process_music_folder(folder_path):
    if not os.path.isdir(folder_path):
        print(f"Directory '{folder_path}' does not exist.")
        return

    success_count = 0
    for filename in os.listdir(folder_path):
        if filename.lower().endswith('.mp3'):
            print("-" * 50)
            print(f"File found: {filename}")
            
            search_term = clean_filename(filename)
            if not search_term:
                search_term = os.path.splitext(filename)[0]
                
            # Fetches track_info (metadata) AND image_data (cover) at the same time
            track_info, image_data = fetch_data_from_itunes(search_term)
            
            if track_info:
                full_path = os.path.join(folder_path, filename)
                if embed_metadata_and_cover(full_path, track_info, image_data):
                    print(f"Success: Metadata & Cover saved into '{filename}'!")
                    success_count += 1
            else:
                print(f"Notice: No match found on iTunes for '{search_term}'")
                
    print("-" * 50)
    print(f"Done! Successfully updated metadata for {success_count} files.")


# --- ENTER THE PATH TO YOUR MUSIC FOLDER HERE ---
target_folder = r"C:\Users\Laurin\Desktop\Songdownload\milliondollar"

process_music_folder(target_folder)
