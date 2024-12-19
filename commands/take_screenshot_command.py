import pyautogui
import os
from datetime import datetime


def handle_take_screenshot_command(tts):
    folder_path = "screenshots"
    os.makedirs(folder_path, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    screenshot_path = os.path.join(folder_path, f"screenshot_{timestamp}.png")

    try:
        screenshot = pyautogui.screenshot()
        screenshot.save(screenshot_path)

        print(f"Screenshot saved at: {screenshot_path}")
        tts.speak(f"Screenshot taken and saved in {folder_path}.")
    except Exception as e:
        print(f"Error taking screenshot: {e}")
        tts.speak("Sorry, I couldn't take the screenshot.")
