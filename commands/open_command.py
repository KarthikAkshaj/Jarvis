import subprocess


def handle_open_command(transcription, tts):
    app_name = transcription.lower().split("open", 1)[1].strip()
    if app_name:
        try:
            print(f"Opening {app_name}...")
            subprocess.Popen(app_name)
            tts.speak(f"Opening {app_name}.")
        except Exception as e:
            print(f"Could not open {app_name}: {e}")
            tts.speak(f"Sorry, I couldn't open {app_name}.")
    else:
        print("No application specified.")
        tts.speak("Please specify the application to open.")
