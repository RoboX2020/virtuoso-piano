import requests
import os

# New Source: fuhton/piano-mp3
BASE_URL = "https://raw.githubusercontent.com/fuhton/piano-mp3/master/piano-mp3/"

# Map keys. This repo uses "C4.mp3", "Db4.mp3" etc.
# We need to check naming convention for sharps/flats.
# Usually: C4, Db4, D4, Eb4, E4, F4, Gb4, G4, Ab4, A4, Bb4, B4
# So we need to map our sharp notes to their flat equivalents.
NOTES_MAP = {
    # Octave 3
    "C3": "C3.mp3",
    "Cs3": "Db3.mp3", 
    "D3": "D3.mp3",
    "Ds3": "Eb3.mp3",
    "E3": "E3.mp3",
    "F3": "F3.mp3",
    "Fs3": "Gb3.mp3",
    "G3": "G3.mp3",
    "Gs3": "Ab3.mp3",
    "A3": "A3.mp3",
    "As3": "Bb3.mp3",
    "B3": "B3.mp3",

    "C4": "C4.mp3",
    "Cs4": "Db4.mp3", 
    "D4": "D4.mp3",
    "Ds4": "Eb4.mp3",
    "E4": "E4.mp3",
    "F4": "F4.mp3",
    "Fs4": "Gb4.mp3",
    "G4": "G4.mp3",
    "Gs4": "Ab4.mp3",
    "A4": "A4.mp3",
    "As4": "Bb4.mp3",
    "B4": "B4.mp3",
    
    # Octave 5
    "C5": "C5.mp3",
    "Cs5": "Db5.mp3", 
    "D5": "D5.mp3",
    "Ds5": "Eb5.mp3",
    "E5": "E5.mp3",
    "F5": "F5.mp3",
    "Fs5": "Gb5.mp3",
    "G5": "G5.mp3",
    "Gs5": "Ab5.mp3",
    "A5": "A5.mp3",
    "As5": "Bb5.mp3",
    "B5": "B5.mp3"
}

def download_file(target_name, remote_name):
    url = f"{BASE_URL}{remote_name}"
    print(f"Downloading {target_name} from {url}...")
    try:
        r = requests.get(url)
        if r.status_code == 200:
            with open(f"assets/{target_name}.mp3", 'wb') as f:
                f.write(r.content)
            print(f"Saved assets/{target_name}.mp3")
        else:
            print(f"Failed to download {target_name}: {r.status_code}")
    except Exception as e:
        print(f"Error downloading {target_name}: {e}")

if __name__ == "__main__":
    if not os.path.exists("assets"):
        os.makedirs("assets")
        
    for target, remote in NOTES_MAP.items():
        download_file(target, remote)
    
    print("Download complete.")
