import cv2
import pygame
import sys
import numpy as np
from vision_engine import VisionEngine
from audio_engine import AudioEngine

# Configuration
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
TOTAL_SEGMENTS = 12
KEY_ZONE_THRESHOLD = 0.6 # Bottom 40%

def main():
    # Initialize Pygame
    pygame.init()
    try:
        pygame.font.init()
    except:
        print("Warning: Font module failed to initialize")

    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Virtuoso Piano (Python)")
    clock = pygame.time.Clock()

    # Initialize Engines
    print("Initialize Audio...")
    audio = AudioEngine()
    print("Initialize Vision...")
    try:
        vision = VisionEngine(WINDOW_WIDTH, WINDOW_HEIGHT)
    except Exception as e:
        print(f"Failed to init vision: {e}")
        return

    # Webcam Setup
    cap = cv2.VideoCapture(0)
    # Increase buffer size or wait?
    
    if not cap.isOpened():
        print("Error: Could not open camera (Index 0). Trying Index 1...")
        cap = cv2.VideoCapture(1)
        if not cap.isOpened():
            print("Error: Could not open camera (Index 1). Exiting.")
            return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, WINDOW_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, WINDOW_HEIGHT)
    print(f"Camera opened successfully: {WINDOW_WIDTH}x{WINDOW_HEIGHT}")

    # State
    segment_state = [False] * TOTAL_SEGMENTS
    running = True

    # SCALES CONFIGURATION
    # 0 = Chromatic (12 notes)
    # 1 = C Major Diatonic (Song Mode)
    current_scale_mode = 0 
    
    # Octave Offset (0 = Start at C3, 1 = Start at C4, 2 = Start at C5)
    # Default to C4 (Index 12 in our 36-note array)
    # Our array is C3...B3 (0-11), C4...B4 (12-23), C5...B5 (24-35)
    octave_shift = 1 
    
    def get_note_index(segment_i, mode, shift):
        base_index = shift * 12
        
        if mode == 0: # Chromatic
            return base_index + segment_i
        elif mode == 1: # C Major (Song Mode)
            # Map 12 segments to White Keys starting from Base C
            # 0->C, 1->D, 2->E, 3->F, 4->G, 5->A, 6->B, 7->C, 8->D...
            # Major Scale Steps: 2, 2, 1, 2, 2, 2, 1
            # Indices relative to C: 0, 2, 4, 5, 7, 9, 11, 12, 14, 16, 17, 19
            diatonic_offsets = [0, 2, 4, 5, 7, 9, 11, 12, 14, 16, 17, 19]
            if segment_i < len(diatonic_offsets):
                return base_index + diatonic_offsets[segment_i]
            return base_index
        return 0
        
    def get_scale_name(mode, shift):
        base_note = f"C{shift + 3}"
        if mode == 0: return f"Chromatic ({base_note} start)"
        if mode == 1: return f"C Major Song ({base_note} start)"
        return "Unknown"

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    running = False
                elif event.key == pygame.K_s:
                    current_scale_mode = (current_scale_mode + 1) % 2
                    print(f"Switched to {get_scale_name(current_scale_mode, octave_shift)}")
                elif event.key == pygame.K_UP:
                    octave_shift = min(octave_shift + 1, 2)
                    print(f"Octave Up: {get_scale_name(current_scale_mode, octave_shift)}")
                elif event.key == pygame.K_DOWN:
                    octave_shift = max(octave_shift - 1, 0)
                    print(f"Octave Down: {get_scale_name(current_scale_mode, octave_shift)}")

        # 1. Capture Frame
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        # Flip frame horizontally for mirror effect
        frame_flipped = cv2.flip(frame, 1)

        # 2. Vision Processing
        results, fingertips = vision.process_frame(frame_flipped)

        # 3. Logic: Check Triggers
        current_active_segments = set()
        
        if fingertips:
            for (x, y) in fingertips:
                if y > KEY_ZONE_THRESHOLD:
                    segment_index = int(x * TOTAL_SEGMENTS)
                    if 0 <= segment_index < TOTAL_SEGMENTS:
                        current_active_segments.add(segment_index)

        # Trigger Sounds
        for i in range(TOTAL_SEGMENTS):
            is_active = i in current_active_segments
            
            if is_active and not segment_state[i]:
                # On Press
                mapped_note = get_note_index(i, current_scale_mode, octave_shift)
                audio.play_note(mapped_note)
                segment_state[i] = True
            elif not is_active and segment_state[i]:
                # On Release
                segment_state[i] = False

        # 4. Rendering
        frame_rgb = cv2.cvtColor(frame_flipped, cv2.COLOR_BGR2RGB)
        frame_rgb = np.rot90(frame_rgb)
        frame_rgb = np.flipud(frame_rgb)
        
        pygame_frame = pygame.surfarray.make_surface(frame_rgb)
        screen.blit(pygame_frame, (0, 0))

        # Draw Grid & UI
        segment_width = WINDOW_WIDTH / TOTAL_SEGMENTS
        
        # Transparent overlay surface
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        
        for i in range(TOTAL_SEGMENTS):
            x = i * segment_width
            
            # Vertical Line
            pygame.draw.line(overlay, (255, 255, 255, 50), (x, 0), (x, WINDOW_HEIGHT), 2)
            
            # Key Zone Highlight
            rect_color = (255, 255, 255, 20)
            if segment_state[i]:
                rect_color = (100, 255, 100, 100)
            
            zone_height = WINDOW_HEIGHT * (1 - KEY_ZONE_THRESHOLD)
            zone_y = WINDOW_HEIGHT * KEY_ZONE_THRESHOLD
            
            pygame.draw.rect(overlay, rect_color, (x, zone_y, segment_width, zone_height))
            
            # Optional: Draw Note Name in Segment
            # (Requires font init)

        # "Key Zone" Line
        pygame.draw.line(overlay, (200, 200, 200), (0, WINDOW_HEIGHT * KEY_ZONE_THRESHOLD), (WINDOW_WIDTH, WINDOW_HEIGHT * KEY_ZONE_THRESHOLD), 2)

        screen.blit(overlay, (0, 0))
        
        # Draw fingertips debugging
        for (x, y) in fingertips:
            px, py = int(x * WINDOW_WIDTH), int(y * WINDOW_HEIGHT)
            pygame.draw.circle(screen, (255, 0, 0), (px, py), 12)
            
        # UI Text: Scale Mode
        try:
            if pygame.font.get_init():
                font = pygame.font.SysFont("Arial", 24)
                label = font.render(f"Mode: {get_scale_name(current_scale_mode, octave_shift)} | S: Switch | Up/Down: Octave", True, (255, 255, 255))
                screen.blit(label, (10, 10))
        except Exception as e:
            # If font fails, just ignore it so app doesn't crash
            pass

        pygame.display.flip()

        clock.tick(60)

    cap.release()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
