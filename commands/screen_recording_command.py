import cv2
import numpy as np
import pyautogui
import os
import threading
from datetime import datetime


class ScreenRecorder:
    def __init__(self):
        self.recording = False
        self.thread = None

    def start_recording(self, tts):
        if not self.recording:
            self.recording = True
            self.thread = threading.Thread(target=self.record_screen, args=(tts,))
            self.thread.start()
            tts.speak("Started screen recording.")
        else:
            tts.speak("Screen recording is already in progress.")

    def stop_recording(self, tts):
        if self.recording:
            self.recording = False
            if self.thread is not None:
                self.thread.join()
            tts.speak("Stopped screen recording.")
        else:
            tts.speak("No screen recording is in progress.")

    def record_screen(self, tts):
        folder_path = "screen_recordings"
        os.makedirs(folder_path, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        video_path = os.path.join(folder_path, f"screen_recording_{timestamp}.mp4")

        screen_size = pyautogui.size()
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(video_path, fourcc, 20.0, screen_size)

        try:
            while self.recording:
                img = pyautogui.screenshot()
                frame = np.array(img)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                out.write(frame)

            out.release()
            print(f"Screen recording saved at: {video_path}")
        except Exception as e:
            print(f"Error during screen recording: {e}")
            tts.speak("An error occurred during screen recording.")


screen_recorder = ScreenRecorder()
