import cv2
import mediapipe as mp
import time
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

class VisionEngine:
    def __init__(self, width=1280, height=720):
        # Load the model
        base_options = python.BaseOptions(model_asset_path='hand_landmarker.task')
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            num_hands=2,
            min_hand_detection_confidence=0.5,
            min_hand_presence_confidence=0.5,
            min_tracking_confidence=0.5,
            running_mode=vision.RunningMode.VIDEO
        )
        self.landmarker = vision.HandLandmarker.create_from_options(options)
        self.width = width
        self.height = height
        # Timestamp tracking
        self.start_timestamp = int(time.time() * 1000)
        
    def process_frame(self, frame):
        # Convert BGR (OpenCV) to RGB (MediaPipe)
        # Create MediaPipe Image
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        
        # Calculate milliseconds relative to start
        current_timestamp = int(time.time() * 1000) - self.start_timestamp
        
        # Detect
        result = self.landmarker.detect_for_video(mp_image, current_timestamp)
        
        fingertips = []
        
        if result.hand_landmarks:
            for hand_pd in result.hand_landmarks:
                # hand_pd is a list of objects with x, y, z
                # Loop through all 5 fingertips
                # 4=Thumb, 8=Index, 12=Middle, 16=Ring, 20=Pinky
                for tip_id in [4, 8, 12, 16, 20]:
                    if len(hand_pd) > tip_id:
                        tip = hand_pd[tip_id]
                        fingertips.append((tip.x, tip.y))
                    
        return result, fingertips
