import pyaudio
import wave
from datetime import datetime
from pathlib import Path
import logging
from typing import Optional, Tuple


class VoiceMemoRecorder:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.data_dir = Path("data/notes/voice_memos")
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Audio settings
        self.chunk = 1024
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 44100
        self.frames = []

    def start_recording(self) -> Tuple[str, Optional[pyaudio.Stream]]:
        """Start recording a voice memo"""
        try:
            p = pyaudio.PyAudio()
            stream = p.open(
                format=self.format,
                channels=self.channels,
                rate=self.rate,
                input=True,
                frames_per_buffer=self.chunk,
            )
            self.frames = []
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = self.data_dir / f"voice_memo_{timestamp}.wav"
            return str(filename), stream
        except Exception as e:
            self.logger.error(f"Error starting recording: {e}")
            return None, None

    def record_chunk(self, stream: pyaudio.Stream) -> bool:
        """Record a chunk of audio"""
        try:
            data = stream.read(self.chunk)
            self.frames.append(data)
            return True
        except Exception as e:
            self.logger.error(f"Error recording chunk: {e}")
            return False

    def stop_recording(self, filename: str, stream: pyaudio.Stream) -> bool:
        """Stop recording and save the voice memo"""
        try:
            stream.stop_stream()
            stream.close()

            p = pyaudio.PyAudio()
            wf = wave.open(filename, "wb")
            wf.setnchannels(self.channels)
            wf.setsampwidth(p.get_sample_size(self.format))
            wf.setframerate(self.rate)
            wf.writeframes(b"".join(self.frames))
            wf.close()

            p.terminate()
            return True
        except Exception as e:
            self.logger.error(f"Error saving voice memo: {e}")
            return False

    def play_memo(self, filename: str) -> bool:
        """Play a voice memo"""
        try:
            if not Path(filename).exists():
                return False

            p = pyaudio.PyAudio()
            wf = wave.open(filename, "rb")

            stream = p.open(
                format=p.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output=True,
            )

            data = wf.readframes(self.chunk)
            while data:
                stream.write(data)
                data = wf.readframes(self.chunk)

            stream.stop_stream()
            stream.close()
            p.terminate()
            return True
        except Exception as e:
            self.logger.error(f"Error playing voice memo: {e}")
            return False

    def list_memos(self) -> list:
        """List all voice memos"""
        try:
            return sorted(list(self.data_dir.glob("*.wav")))
        except Exception as e:
            self.logger.error(f"Error listing voice memos: {e}")
            return []

    def delete_memo(self, filename: str) -> bool:
        """Delete a voice memo"""
        try:
            memo_path = Path(filename)
            if memo_path.exists():
                memo_path.unlink()
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error deleting voice memo: {e}")
            return False
