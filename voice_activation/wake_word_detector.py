import pvporcupine
import struct
import pyaudio
import numpy as np
import logging
import json
from vosk import Model, KaldiRecognizer
import time


class WakeWordDetector:
    def __init__(self, config_manager=None):
        self.logger = logging.getLogger(__name__)
        self.config = config_manager

        # Audio settings
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 16000

        # Wake word settings
        self.wake_word = "jarvis"
        self.last_detection_time = 0
        self.detection_cooldown = 1.0  # seconds
        self.frame_counter = 0

        # Initialize components
        self._initialize_components()
        print("\nWake word detector initialized")
        print("Listening for: 'Jarvis'")

    def _initialize_components(self):
        try:
            # Initialize Vosk
            model_path = "model/vosk"
            self.model = Model(model_path)
            self.recognizer = KaldiRecognizer(self.model, self.RATE)
            self.recognizer.SetWords(True)

            # Initialize audio
            self._setup_audio_stream()

            # Test the audio stream
            self._test_audio_stream()

        except Exception as e:
            self.logger.error(f"Error initializing components: {e}")
            raise

    def _setup_audio_stream(self):
        try:
            if hasattr(self, "audio_stream") and self.audio_stream.is_active():
                self.audio_stream.stop_stream()
                self.audio_stream.close()
            if hasattr(self, "pa"):
                self.pa.terminate()

            self.pa = pyaudio.PyAudio()
            default_device = self.pa.get_default_input_device_info()
            print(f"Using default input device: {default_device['name']}")

            self.audio_stream = self.pa.open(
                format=self.FORMAT,
                channels=self.CHANNELS,
                rate=self.RATE,
                input=True,
                frames_per_buffer=self.CHUNK,
            )

        except Exception as e:
            self.logger.error(f"Error setting up audio stream: {e}")
            raise

    def _test_audio_stream(self):
        """Test the audio stream and show initial levels"""
        print("\nTesting audio input (speak now)...")
        max_level = 0
        start_time = time.time()

        while time.time() - start_time < 4:  # 4 seconds test
            try:
                data = self.audio_stream.read(self.CHUNK, exception_on_overflow=False)
                audio_data = np.frombuffer(data, dtype=np.int16)
                level = np.abs(audio_data).mean()
                max_level = max(max_level, level)
                bars = int(50 * level / 10000)
                print(
                    f"\rAudio Level: {'|' * bars}{' ' * (50-bars)} {level:>5.0f}",
                    end="",
                    flush=True,
                )
            except Exception as e:
                print(f"Error during audio test: {e}")

        print(f"\nMaximum audio level detected: {max_level:.0f}")

    def listen_for_wake_word(self) -> bool:
        try:
            # Read audio data
            data = self.audio_stream.read(self.CHUNK, exception_on_overflow=False)

            # Show audio levels periodically
            self.frame_counter += 1
            if self.frame_counter % 10 == 0:
                audio_data = np.frombuffer(data, dtype=np.int16)
                level = np.abs(audio_data).mean()
                print(f"\rAudio Level: {level:.0f}", end="", flush=True)

            # Process with Vosk
            if self.recognizer.AcceptWaveform(data):
                result = json.loads(self.recognizer.Result())
                text = result.get("text", "").lower()

                # Only process if we got some text
                if text:
                    current_time = time.time()

                    # Check for wake word with variations
                    if (
                        self.wake_word in text
                        and current_time - self.last_detection_time
                        > self.detection_cooldown
                    ):
                        self.last_detection_time = current_time
                        print(f"\nWake word detected in: '{text}'")
                        return True

            return False

        except Exception as e:
            self.logger.error(f"Error in wake word detection: {e}")
            if "Stream closed" not in str(e):
                try:
                    self._setup_audio_stream()
                except Exception:
                    pass
            return False

    def cleanup(self):
        try:
            if hasattr(self, "audio_stream"):
                if self.audio_stream.is_active():
                    self.audio_stream.stop_stream()
                self.audio_stream.close()
            if hasattr(self, "pa"):
                self.pa.terminate()
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()
