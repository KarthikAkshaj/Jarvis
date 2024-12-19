import pyaudio
import wave
import os
import numpy as np
from utils.error_handler import ErrorHandler
from typing import Optional, Tuple


class Recorder:
    def __init__(self, config_manager=None, device_index=None):
        self.audio = pyaudio.PyAudio()
        self.config = config_manager

        # Optimized settings for better speech recognition
        self.chunk = 1024
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 16000  # Standard rate for speech recognition
        self.record_seconds = 7  # Increased recording time
        self.frames = []

        # Audio level monitoring
        self.min_audio_level = 0.01
        self.audio_threshold = 500  # Adjust this value based on testing

        # Find or use specified input device
        self.input_device_index = (
            device_index if device_index is not None else self._get_best_input_device()
        )

        if self.input_device_index is None:
            raise ValueError("No suitable audio input device found")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.audio.terminate()

    def _get_best_input_device(self) -> Optional[int]:
        """Find the best available input device with testing"""
        try:
            # Try to get the default input device first
            default_device = self.audio.get_default_input_device_info()
            device_index = default_device["index"]

            # Test the default device
            if self._test_device(device_index):
                print(f"Using default input device: {default_device['name']}")
                return device_index

            # If default device fails, try other devices
            print("Default device test failed, searching for alternative devices...")
            return self._find_working_device()

        except Exception as e:
            print(f"Error getting default device: {e}")
            return self._find_working_device()

    def _find_working_device(self) -> Optional[int]:
        """Find a working input device through testing"""
        for i in range(self.audio.get_device_count()):
            try:
                device_info = self.audio.get_device_info_by_index(i)
                if device_info["maxInputChannels"] > 0:
                    if self._test_device(i):
                        print(f"Using input device: {device_info['name']}")
                        return i
            except Exception:
                continue
        return None

    def _test_device(self, device_index: int) -> bool:
        """Test if a device works properly"""
        try:
            stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.rate,
                input=True,
                frames_per_buffer=self.chunk,
                input_device_index=device_index,
                stream_callback=None,
            )

            # Read a small amount of data to test
            data = stream.read(self.chunk, exception_on_overflow=False)
            audio_level = self._calculate_audio_level(data)

            stream.stop_stream()
            stream.close()

            return len(data) > 0
        except Exception:
            return False

    def _calculate_audio_level(self, audio_data: bytes) -> float:
        """Calculate RMS audio level from raw audio data"""
        try:
            # Convert bytes to numpy array
            audio_array = np.frombuffer(audio_data, dtype=np.int16)
            # Calculate RMS value
            rms = np.sqrt(np.mean(np.square(audio_array)))
            return float(rms)
        except Exception:
            return 0.0

    def record(self) -> Optional[str]:
        """Record audio with level monitoring"""
        try:
            print("Recording...")
            stream = self._setup_stream()
            if not stream:
                raise Exception("Failed to setup audio stream")

            # Initialize variables for audio level monitoring
            max_level = 0
            silence_counter = 0

            self.frames = []
            total_frames = int(self.rate / self.chunk * self.record_seconds)

            print("Listening...")
            for _ in range(total_frames):
                try:
                    data = stream.read(self.chunk, exception_on_overflow=False)
                    audio_level = self._calculate_audio_level(data)

                    # Update max level
                    max_level = max(max_level, audio_level)

                    # Monitor audio levels
                    if audio_level < self.min_audio_level:
                        silence_counter += 1
                    else:
                        silence_counter = 0

                    # Visual feedback of audio level
                    if audio_level > self.audio_threshold:
                        print("*", end="", flush=True)

                    self.frames.append(data)

                except Exception as e:
                    print(f"\nWarning: Error reading audio chunk: {e}")
                    continue

            print("\nRecording finished.")

            # Check if any sound was detected
            if max_level < self.min_audio_level:
                print("Warning: No significant audio detected during recording")

            return self._save_audio()

        except Exception as e:
            error_msg = ErrorHandler.handle_error(e, "recording audio")
            print(error_msg)
            return None
        finally:
            if "stream" in locals() and stream:
                self._cleanup_stream(stream)

    def _setup_stream(self):
        """Setup audio stream with retry mechanism"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                stream = self.audio.open(
                    format=self.format,
                    channels=self.channels,
                    rate=self.rate,
                    input=True,
                    frames_per_buffer=self.chunk,
                    input_device_index=self.input_device_index,
                    stream_callback=None,
                )
                return stream
            except Exception as e:
                print(f"Attempt {attempt + 1}/{max_retries} failed: {e}")
                if attempt == max_retries - 1:
                    print(f"Error setting up audio stream: {e}")
                    return None

    def _save_audio(self) -> Optional[str]:
        """Save recorded audio to file"""
        audio_path = "audio/"
        os.makedirs(audio_path, exist_ok=True)
        audio_file = os.path.join(audio_path, "recording.wav")

        try:
            with wave.open(audio_file, "wb") as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(self.audio.get_sample_size(self.format))
                wf.setframerate(self.rate)
                wf.writeframes(b"".join(self.frames))
            print("Recording saved successfully.")
            return audio_file
        except Exception as e:
            print(f"Error saving audio file: {e}")
            return None

    def _cleanup_stream(self, stream):
        """Clean up audio stream"""
        try:
            stream.stop_stream()
            stream.close()
        except Exception as e:
            print(f"Error cleaning up stream: {e}")

    def list_audio_devices(self) -> list[Tuple[int, str]]:
        """List all available audio input devices and return them"""
        devices = []
        print("\nAvailable Audio Input Devices:")
        for i in range(self.audio.get_device_count()):
            try:
                device_info = self.audio.get_device_info_by_index(i)
                if device_info["maxInputChannels"] > 0:
                    name = device_info["name"]
                    print(f"Device {i}: {name}")
                    devices.append((i, name))
            except Exception:
                continue
        return devices

    def test_recording(self, duration: int = 3) -> bool:
        """Test recording functionality"""
        try:
            print(f"\nTesting recording for {duration} seconds...")
            stream = self._setup_stream()
            if not stream:
                return False

            frames = []
            for _ in range(int(self.rate / self.chunk * duration)):
                data = stream.read(self.chunk, exception_on_overflow=False)
                frames.append(data)

            # Calculate average audio level
            avg_level = np.mean(
                [self._calculate_audio_level(frame) for frame in frames]
            )
            print(f"Average audio level: {avg_level:.2f}")

            return avg_level > self.min_audio_level

        except Exception as e:
            print(f"Error testing recording: {e}")
            return False
