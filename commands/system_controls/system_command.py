import os
import subprocess
import platform
import logging
from typing import Optional
from datetime import datetime, timedelta


class SystemController:
    def __init__(self):
        self.system = platform.system().lower()
        self.logger = logging.getLogger(__name__)

    def shutdown(self, delay_minutes: int = 0) -> bool:
        """Schedule system shutdown"""
        try:
            if self.system == "windows":
                delay_seconds = delay_minutes * 60
                cmd = f"shutdown /s /t {delay_seconds}"
                subprocess.run(cmd, shell=True, check=True)
            elif self.system == "linux":
                delay_minutes = max(0, delay_minutes)
                cmd = f"shutdown -h +{delay_minutes}"
                subprocess.run(cmd, shell=True, check=True)
            else:
                return False
            return True
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")
            return False

    def restart(self, delay_minutes: int = 0) -> bool:
        """Schedule system restart"""
        try:
            if self.system == "windows":
                delay_seconds = delay_minutes * 60
                cmd = f"shutdown /r /t {delay_seconds}"
                subprocess.run(cmd, shell=True, check=True)
            elif self.system == "linux":
                delay_minutes = max(0, delay_minutes)
                cmd = f"shutdown -r +{delay_minutes}"
                subprocess.run(cmd, shell=True, check=True)
            else:
                return False
            return True
        except Exception as e:
            self.logger.error(f"Error during restart: {e}")
            return False

    def cancel_shutdown(self) -> bool:
        """Cancel scheduled shutdown/restart"""
        try:
            if self.system == "windows":
                subprocess.run("shutdown /a", shell=True, check=True)
            elif self.system == "linux":
                subprocess.run("shutdown -c", shell=True, check=True)
            else:
                return False
            return True
        except Exception as e:
            self.logger.error(f"Error canceling shutdown: {e}")
            return False

    def lock_screen(self) -> bool:
        """Lock the screen"""
        try:
            if self.system == "windows":
                subprocess.run(
                    "rundll32.exe user32.dll,LockWorkStation", shell=True, check=True
                )
            elif self.system == "linux":
                subprocess.run("xdg-screensaver lock", shell=True, check=True)
            else:
                return False
            return True
        except Exception as e:
            self.logger.error(f"Error locking screen: {e}")
            return False

    def sleep(self) -> bool:
        """Put system to sleep"""
        try:
            if self.system == "windows":
                subprocess.run(
                    "rundll32.exe powrprof.dll,SetSuspendState 0,1,0",
                    shell=True,
                    check=True,
                )
            elif self.system == "linux":
                subprocess.run("systemctl suspend", shell=True, check=True)
            else:
                return False
            return True
        except Exception as e:
            self.logger.error(f"Error putting system to sleep: {e}")
            return False

    def get_system_info(self) -> dict:
        """Get basic system information"""
        try:
            info = {
                "system": platform.system(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor(),
                "python_version": platform.python_version(),
            }
            return info
        except Exception as e:
            self.logger.error(f"Error getting system info: {e}")
            return {}
