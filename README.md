# Auto MP3 Metadata & Cover Updater

A lightweight and efficient Python script that cleans messy MP3 filenames, fetches high-quality album artwork and tags (Title, Artist, Album, Year, Genre) using the iTunes API, and embeds them directly into the files.

## Features
- **Smart Filename Cleaning:** Automatically strips YouTube IDs (e.g., `[djV11Xbc914]`) and video clutter like `(Official Video)` or `[4K]`.
- **Automatic Artwork Search:** Downloads high-resolution covers (600x600px) directly from Apple Music/iTunes.
- **Full Tagging:** Overwrites or adds crucial metadata fields (ID3v2.3) for maximum compatibility with Windows and mobile media players.
- **Auto-Replace:** Completely removes old embedded covers before injecting the new ones to avoid duplicate image waste inside the files.

## Prerequisites
Before running the script, make sure you have installed the required libraries inside your environment:

```bash
pip install requests mutagen
```

## How to Use
1. Clone or download this repository.
2. Open the script and update the `ziel_ordner` variable at the bottom with the path to your MP3 files:
   ```python
   target_folder = r"C:\Your\Music\Folder"
   ```
3. Run the script inside your terminal or virtual environment:
   ```bash
   python auto_metadata_updater.py
   ```

## AI Contribution Disclosure
This project was initiated by me and developed with the assistance of **AI (Artificial Intelligence)**. I provided the workflow logic, specific requirements, and real-world testing, while the AI assisted in structuring the clean Python functions and properly implementing the `mutagen` and `requests` frameworks. 

## License
This project is open-source and available under the **MIT License**. Feel free to use, modify, and distribute it!
