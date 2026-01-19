import sounddevice as sd
import miniaudio
import numpy as np
import os

class NotePlayer:
    def __init__(self, data):
        self.data = data
        self.cursor = 0
        
    def get_next_chunk(self, frames):
        remaining = len(self.data) - self.cursor
        if remaining <= 0:
            return np.zeros((0, 2), dtype=np.float32)
            
        count = min(frames, remaining)
        chunk = self.data[self.cursor : self.cursor + count]
        self.cursor += count
        return chunk

class AudioEngine:
    def __init__(self):
        self.sample_rate = 44100
        self.sounds = {}
        self.active_notes = [] # List of NotePlayer instances
        self.master_volume = 0.5
        
        print("Loading samples...")
        self.load_samples()
        
        print("Starting Audio Stream...")
        # Open 2-channel float32 stream
        self.stream = sd.OutputStream(
            samplerate=self.sample_rate,
            channels=2,
            callback=self.audio_callback,
            blocksize=512, # Low latency
            latency='low'
        )
        self.stream.start()
        
    def load_samples(self):
        notes = [
            "C3", "Cs3", "D3", "Ds3", "E3", "F3", 
            "Fs3", "G3", "Gs3", "A3", "As3", "B3",
            "C4", "Cs4", "D4", "Ds4", "E4", "F4", 
            "Fs4", "G4", "Gs4", "A4", "As4", "B4",
            "C5", "Cs5", "D5", "Ds5", "E5", "F5", 
            "Fs5", "G5", "Gs5", "A5", "As5", "B5"
        ]
        
        for i, note in enumerate(notes):
            path = f"assets/{note}.mp3"
            if os.path.exists(path):
                try:
                    # Decode to int16
                    decoded = miniaudio.decode_file(path, nchannels=2, sample_rate=self.sample_rate)
                    
                    # Convert to float32 normalized
                    # miniaudio returns signed 16-bit PCM (usually)
                    # We need to verify what miniaudio.decode_file returns. 
                    # Docs say it returns an object with .samples (memoryview/bytes).
                    # We need to interpret it as int16, then convert to float.
                    
                    # Wait, miniaudio python binding might return raw bytes.
                    audio_data = np.frombuffer(decoded.samples, dtype=np.int16)
                    audio_data = audio_data.astype(np.float32) / 32768.0
                    
                    # Reshape to (N, 2)
                    audio_data = audio_data.reshape(-1, 2)
                    
                    self.sounds[i] = audio_data
                    print(f"Loaded {note} ({len(audio_data)} frames)")
                except Exception as e:
                    print(f"Failed to load {path}: {e}")
            else:
                print(f"Missing asset: {path}")

    def audio_callback(self, outdata, frames, time, status):
        if status:
            print(status)
            
        outdata.fill(0)
        
        # Mix active notes
        removals = []
        for note in self.active_notes:
            chunk = note.get_next_chunk(frames)
            
            # Mix
            # Note: outdata is shape (frames, 2)
            # chunk might be smaller
            if len(chunk) > 0:
                outdata[:len(chunk)] += chunk * self.master_volume
                
            if len(chunk) < frames:
                removals.append(note)
                
        for r in removals:
            self.active_notes.remove(r)

    def play_note(self, index):
        if index in self.sounds:
            # Create a new playback instance for this sound
            player = NotePlayer(self.sounds[index])
            # Add to active list (thread safety might be needed for robust apps, but list append is atomicish in GIL)
            self.active_notes.append(player)

    def close(self):
        self.stream.stop()
        self.stream.close()
