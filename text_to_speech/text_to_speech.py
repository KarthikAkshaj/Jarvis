import asyncio
from TTS.api import TTS
import sounddevice as sd
import numpy as np


class TextToSpeech:
    def __init__(self):
        try:
            model_name = "tts_models/en/ljspeech/tacotron2-DDC"
            self.tts = TTS(model_name=model_name, progress_bar=False)
            self.sample_rate = 22050
            self._lock = asyncio.Lock()
        except Exception as e:
            print(f"Error initializing TTS: {str(e)}")
            raise

    async def speak(self, text: str):
        if not text:
            return

        try:
            async with self._lock:

                audio = self.tts.tts(text=text)
                audio_array = np.array(audio)

                sd.play(audio_array, samplerate=self.sample_rate)
                sd.wait()

        except Exception as e:
            print(f"Error in TTS speak: {str(e)}")

    def speak_sync(self, text: str):
        """Synchronous version for compatibility"""
        if not text:
            return

        try:

            audio = self.tts.tts(text=text)
            audio_array = np.array(audio)

            sd.play(audio_array, samplerate=self.sample_rate)
            sd.wait()

        except Exception as e:
            print(f"Error in TTS speak: {str(e)}")
