from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import math


class VolumeController:
    def __init__(self):
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        self.volume = cast(interface, POINTER(IAudioEndpointVolume))

    def get_volume(self) -> int:
        """Get current volume level as percentage"""
        current_vol = self.volume.GetMasterVolumeLevelScalar()
        return int(current_vol * 100)

    def set_volume(self, volume_percent: int) -> bool:
        """Set volume level (0-100)"""
        try:
            volume_percent = max(0, min(100, volume_percent))
            self.volume.SetMasterVolumeLevelScalar(volume_percent / 100, None)
            return True
        except Exception as e:
            print(f"Error setting volume: {e}")
            return False

    def mute(self) -> bool:
        """Mute audio"""
        try:
            self.volume.SetMute(1, None)
            return True
        except Exception as e:
            print(f"Error muting: {e}")
            return False

    def unmute(self) -> bool:
        """Unmute audio"""
        try:
            self.volume.SetMute(0, None)
            return True
        except Exception as e:
            print(f"Error unmuting: {e}")
            return False

    def get_mute_state(self) -> bool:
        """Check if system is muted"""
        return bool(self.volume.GetMute())

    def adjust_volume(self, amount: int) -> bool:
        """Adjust volume by relative amount"""
        try:
            current = self.get_volume()
            new_volume = max(0, min(100, current + amount))
            return self.set_volume(new_volume)
        except Exception as e:
            print(f"Error adjusting volume: {e}")
            return False
