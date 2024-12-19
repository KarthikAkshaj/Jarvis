import os
import pygame


def handle_play_command(transcription, tts):
    song_name = transcription.lower().split("play", 1)[1].strip()
    if song_name:
        audio_extensions = [".mp3", ".wav", ".ogg", ".flac", ".mp4"]
        file_path = None

        # Search for the song with any supported extension
        for ext in audio_extensions:
            possible_file_path = os.path.join("audio", f"{song_name}{ext}")
            if os.path.exists(possible_file_path):
                file_path = possible_file_path
                break

        if file_path:
            try:
                pygame.mixer.music.load(file_path)
                pygame.mixer.music.play()
                print(f"Now playing: {song_name}")
                tts.speak(f"Now playing {song_name}.")
            except Exception as e:
                print(f"Error playing {song_name}: {e}")
                tts.speak(f"Sorry, I couldn't play {song_name}.")
        else:
            print(f"Song {song_name} not found")
            tts.speak(f"Sorry, I couldn't find {song_name}.")
    else:
        print("No song specified.")
        tts.speak("Please specify the song to play.")
