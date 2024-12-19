import asyncio
import time
import sys
from audio.recorder import Recorder
from dotenv import load_dotenv
from transcription.transcriber import Transcriber
from commands.command_handler import CommandHandler
from config.config_manager import ConfigManager
from utils.logger import Logger
from utils.error_handler import ErrorHandler
from voice_activation.wake_word_detector import WakeWordDetector
from text_to_speech.text_to_speech import TextToSpeech

load_dotenv()


async def main():
    try:
        # Initialize components
        config = ConfigManager()
        logger = Logger.setup_logging()
        logger.info("Starting Jarvis")

        recorder = Recorder(config)
        transcriber = Transcriber()
        command_handler = CommandHandler(config)
        tts = TextToSpeech()

        logger.info("All components initialized successfully")

        await run_assistant(recorder, transcriber, command_handler, tts, logger, config)

    except Exception as e:
        error_msg = ErrorHandler.handle_error(e, "initialization")
        print(error_msg)
        sys.exit(1)


async def run_assistant(recorder, transcriber, command_handler, tts, logger, config):
    try:
        with WakeWordDetector(config) as wake_detector:
            print("\nWaiting for wake word 'Jarvis'...")

            while True:
                try:
                    # Listen for wake word
                    if wake_detector.listen_for_wake_word():
                        # Wake word detected
                        await tts.speak("Yes, I'm listening")

                        # Record command
                        with recorder as r:
                            audio_file = r.record()

                        if not audio_file:
                            logger.error("Failed to record audio")
                            print("\nWaiting for wake word 'Jarvis'...")
                            continue

                        # Transcribe command
                        transcription = transcriber.transcribe_audio(audio_file)
                        if not transcription:
                            logger.warning("No transcription detected")
                            print("\nWaiting for wake word 'Jarvis'...")
                            continue

                        print("You said:", transcription)

                        try:
                            # Process command
                            command_result = await command_handler.process_command(
                                transcription
                            )

                            if command_result == "stop":
                                logger.info("Stopping Jarvis")
                                break
                            elif command_result == "end":
                                print("\nWaiting for wake word 'Jarvis'...")
                                continue

                        except Exception as e:
                            logger.error(f"Error processing command: {e}")
                            await tts.speak(
                                "I encountered an error processing your command."
                            )

                        print("\nWaiting for wake word 'Jarvis'...")

                    # Small delay to prevent high CPU usage
                    await asyncio.sleep(0.1)

                except Exception as e:
                    logger.error(f"Error in main loop: {str(e)}")
                    print("\nWaiting for wake word 'Jarvis'...")
                    await asyncio.sleep(0.5)
                    continue

    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt. Shutting down...")
    except Exception as e:
        error_msg = ErrorHandler.handle_error(e, "voice activation system")
        logger.error(error_msg)
        print(error_msg)
    finally:
        if "wake_detector" in locals():
            wake_detector.cleanup()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
        sys.exit(0)


# import pyaudio
# import numpy as np
# from vosk import Model, KaldiRecognizer
# import json
# import time

# def test_wake_word_detection():
#     # Audio settings
#     CHUNK = 1024
#     FORMAT = pyaudio.paInt16
#     CHANNELS = 1
#     RATE = 16000
#     WAKE_WORD = "jarvis"
#     TEST_DURATION = 30  # Test for 30 seconds

#     # Initialize PyAudio
#     p = pyaudio.PyAudio()
    
#     # Initialize Vosk
#     model = Model("model/vosk")
#     recognizer = KaldiRecognizer(model, RATE)
#     recognizer.SetWords(True)  # Enable word timing

#     # Get default input device
#     default_device = p.get_default_input_device_info()
#     print(f"Using input device: {default_device['name']}")

#     # Open stream
#     stream = p.open(
#         format=FORMAT,
#         channels=CHANNELS,
#         rate=RATE,
#         input=True,
#         frames_per_buffer=CHUNK
#     )

#     print(f"\nListening for 'Jarvis' for {TEST_DURATION} seconds...")
#     print("Speak normally and watch for detections.")
#     print("\nDebug Info:")
#     print("-----------")

#     start_time = time.time()
#     detections = 0

#     try:
#         while time.time() - start_time < TEST_DURATION:
#             # Read audio
#             data = stream.read(CHUNK, exception_on_overflow=False)
            
#             # Calculate audio level for debugging
#             audio_data = np.frombuffer(data, dtype=np.int16)
#             audio_level = np.abs(audio_data).mean()
            
#             # Process with Vosk
#             if recognizer.AcceptWaveform(data):
#                 result = json.loads(recognizer.Result())
#                 text = result.get("text", "").lower()
                
#                 if text:  # Only print if something was recognized
#                     print(f"Heard: '{text}' (Audio Level: {audio_level:.0f})")
                    
#                     if WAKE_WORD in text:
#                         detections += 1
#                         print(f"\n>>> Wake word detected! (Detection #{detections}) <<<\n")

#             # Print audio level periodically
#             if time.time() % 1 < 0.1:  # Roughly every second
#                 print(f"\rAudio Level: {'|' * int(audio_level/100)}{' ' * (50-int(audio_level/100))} {audio_level:.0f}", end="")

#         print(f"\n\nTest finished!")
#         print(f"Total wake word detections: {detections}")
#         print(f"Detection rate: {detections/(TEST_DURATION/60):.1f} detections per minute")

#     except KeyboardInterrupt:
#         print("\nTest stopped by user")
#     finally:
#         # Cleanup
#         stream.stop_stream()
#         stream.close()
#         p.terminate()

# if __name__ == "__main__":
#     test_wake_word_detection()