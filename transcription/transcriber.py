import os
import wave
from vosk import Model, KaldiRecognizer
import json
import time



class Transcriber:
    def __init__(self):
        model_path = "D:/Projects  ^_^/Jaarvis/model/vosk"
        print(f"Checking model path: {model_path}")

        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model directory does not exist: {model_path}")

        max_retries = 3
        for attempt in range(max_retries):
            try:
                print(
                    f"Attempting to load model (attempt {attempt + 1}/{max_retries})..."
                )
                self.model = Model(model_path)
                print("Model loaded successfully")
                break
            except Exception as e:
                if attempt == max_retries - 1:
                    raise Exception(
                        f"Failed to load model after {max_retries} attempts: {str(e)}"
                    )
                print(f"Failed to load model (attempt {attempt + 1}), retrying...")
                time.sleep(1)

        self.recognizer = KaldiRecognizer(self.model, 16000)

    def transcribe_audio(self, audio_file):
        if not os.path.exists(audio_file):
            print(f"Audio file not found: {audio_file}")
            return None

        try:
            with wave.open(audio_file, "rb") as wf:
                if (
                    wf.getnchannels() != 1
                    or wf.getsampwidth() != 2
                    or wf.getframerate() != 16000
                ):
                    print("Audio file must be WAV format mono PCM.")
                    return None

                results = []
                while True:
                    data = wf.readframes(4000)
                    if len(data) == 0:
                        break
                    if self.recognizer.AcceptWaveform(data):
                        result = json.loads(self.recognizer.Result())
                        results.append(result.get("text", ""))

                final_result = json.loads(self.recognizer.FinalResult())
                results.append(final_result.get("text", ""))

                return " ".join(filter(None, results))

        except Exception as e:
            print(f"Error during transcription: {str(e)}")
            return None
