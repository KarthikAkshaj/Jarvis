import pyaudio
import wave
import numpy as np

def test_microphone():
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    RECORD_SECONDS = 5
    WAVE_OUTPUT_FILENAME = "test_recording.wav"

    p = pyaudio.PyAudio()

    # Get default input device info
    default_device = p.get_default_input_device_info()
    print(f"\nUsing default device: {default_device['name']} (index: {default_device['index']})")

    print(f"\nRecording for 5 seconds...")
    
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    frames = []
    
    # Monitor audio levels while recording
    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK, exception_on_overflow=False)
        frames.append(data)
        
        # Calculate and display audio level
        audio_data = np.frombuffer(data, dtype=np.int16)
        level = np.abs(audio_data).mean()
        bars = int(50 * level / 10000)
        print(f"\rAudio Level: {'|' * bars}{' ' * (50-bars)} {level:>5.0f}", end='', flush=True)

    print("\n\nFinished recording")

    stream.stop_stream()
    stream.close()

    # Save the recording
    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

    p.terminate()

    print(f"\nRecording saved as {WAVE_OUTPUT_FILENAME}")
    print("Please check if you can hear your voice in the recording.")

if __name__ == "__main__":
    test_microphone()