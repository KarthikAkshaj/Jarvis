import screen_brightness_control as sbc
from typing import List, Optional


class BrightnessController:
    def __init__(self):
        self.monitors = sbc.list_monitors()

    def get_brightness(self, display: Optional[str] = None) -> int:
        """Get current brightness level"""
        try:
            if display:
                return sbc.get_brightness(display=display)[0]
            return sbc.get_brightness()[0]
        except Exception as e:
            print(f"Error getting brightness: {e}")
            return -1

    def set_brightness(self, value: int, display: Optional[str] = None) -> bool:
        """Set brightness level (0-100)"""
        try:
            value = max(0, min(100, value))
            if display:
                sbc.set_brightness(value, display=display)
            else:
                sbc.set_brightness(value)
            return True
        except Exception as e:
            print(f"Error setting brightness: {e}")
            return False

    def get_monitors(self) -> List[str]:
        """Get list of available monitors"""
        return self.monitors

    def fade_brightness(self, end_value: int, duration: float = 1.0) -> bool:
        """Smoothly change brightness over duration in seconds"""
        try:
            current = self.get_brightness()
            sbc.fade_brightness(end_value, start=current, duration=duration)
            return True
        except Exception as e:
            print(f"Error fading brightness: {e}")
            return False

    def adjust_brightness(self, amount: int) -> bool:
        """Adjust brightness by relative amount"""
        try:
            current = self.get_brightness()
            if current == -1:
                return False
            new_brightness = max(0, min(100, current + amount))
            return self.set_brightness(new_brightness)
        except Exception as e:
            print(f"Error adjusting brightness: {e}")
            return False
