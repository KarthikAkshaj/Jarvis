import os
import yaml
import json
from pathlib import Path
from typing import Any, Dict, Optional
import logging
from datetime import datetime


class ConfigManager:
    def __init__(self, config_file="config.yaml"):
        self.logger = logging.getLogger(__name__)
        self.config_dir = Path("config")
        self.data_dir = Path("data")

        # Create necessary directories
        self.config_dir.mkdir(exist_ok=True)
        self.data_dir.mkdir(exist_ok=True)

        # Configuration files
        self.config_file = self.config_dir / config_file
        self.user_prefs_file = self.data_dir / "user_preferences.json"

        # Settings cache
        self.settings_cache: Dict = {}

        # Load configurations
        self._load_config()
        self._load_user_preferences()

        # Initialize default audio settings
        self.default_audio = {
            "chunk_size": 1024,
            "sample_rate": 16000,
            "channels": 1,
            "record_seconds": 5,
        }

        # Initialize default paths
        self.default_paths = {
            "audio_output": os.getenv("AUDIO_OUTPUT_PATH", "audio/"),
            "screenshots": os.getenv("SCREENSHOTS_PATH", "screenshots/"),
            "recordings": os.getenv("RECORDINGS_PATH", "screen_recordings/"),
            "models": os.getenv("MODELS_PATH", "models/"),
        }

        # Initialize API keys
        self.api_keys = {
            "gemini": os.getenv("GEMINI_API_KEY"),
            "picovoice": os.getenv("PICOVOICE_ACCESS_KEY"),
        }

    def _load_config(self):
        """Load or create configuration"""
        try:
            if not self.config_file.exists():
                self._create_default_config()

            with open(self.config_file, "r") as f:
                self.config = yaml.safe_load(f)
        except Exception as e:
            self.logger.error(f"Error loading config: {e}")
            self.config = {}

    def _load_user_preferences(self):
        """Load user preferences"""
        try:
            if self.user_prefs_file.exists():
                with open(self.user_prefs_file, "r") as f:
                    self.user_preferences = json.load(f)
            else:
                self.user_preferences = self._get_default_preferences()
                self._save_user_preferences()
        except Exception as e:
            self.logger.error(f"Error loading user preferences: {e}")
            self.user_preferences = self._get_default_preferences()

    def _create_default_config(self):
        """Create default configuration file"""
        default_config = {
            "audio": self.default_audio,
            "paths": self.default_paths,
            "api_keys": self.api_keys,
            "voice": {
                "wake_word": "jarvis",
                "sensitivity": 0.5,
                "language": "en-US",
                "volume": 1.0,
                "speed": 1.0,
            },
            "system": {
                "max_threads": 3,
                "log_level": "INFO",
                "debug_mode": False,
                "auto_update": True,
            },
            "features": {
                "weather": True,
                "reminders": True,
                "notes": True,
                "calendar": True,
                "voice_memos": True,
                "system_controls": True,
            },
        }

        try:
            with open(self.config_file, "w") as f:
                yaml.dump(default_config, f, default_flow_style=False)
            self.config = default_config
        except Exception as e:
            self.logger.error(f"Error creating default config: {e}")

    def _get_default_preferences(self) -> Dict:
        """Get default user preferences"""
        return {
            "ui": {
                "theme": "light",
                "voice_feedback": True,
                "show_notifications": True,
            },
            "behavior": {
                "auto_listen": True,
                "confirm_actions": True,
                "save_history": True,
                "history_size": 100,
            },
            "voice": {
                "voice_type": "female",
                "speaking_rate": 1.0,
                "pitch": 1.0,
                "volume": 1.0,
            },
            "personalization": {
                "name": "User",
                "location": "",
                "timezone": "",
                "language": "en-US",
            },
        }

    def _save_user_preferences(self):
        """Save user preferences to file"""
        try:
            with open(self.user_prefs_file, "w") as f:
                json.dump(self.user_preferences, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving user preferences: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value with dot notation support"""
        try:
            # Check cache first
            if key in self.settings_cache:
                return self.settings_cache[key]

            # Check user preferences first
            value = self._get_nested_value(self.user_preferences, key)
            if value is not None:
                return value

            # Then cek main config
            value = self._get_nested_value(self.config, key)
            if value is not None:
                return value

            # Checking environment variavles
            env_value = os.getenv(key.upper(), default)
            self.settings_cache[key] = env_value
            return env_value

        except Exception :
            return default

    def set(self, key: str, value: Any, save_to_preferences: bool = False) -> bool:
        """Set configuration value"""
        try:
            keys = key.split(".")

            # Determine whether to save to preferences or config
            target_dict = self.user_preferences if save_to_preferences else self.config
            current = target_dict

            # Navigate to the nested location
            for k in keys[:-1]:
                current = current.setdefault(k, {})
            current[keys[-1]] = value

            # Update cache
            self.settings_cache[key] = value

            # Save to appropriate file
            if save_to_preferences:
                self._save_user_preferences()
            else:
                with open(self.config_file, "w") as f:
                    yaml.dump(self.config, f, default_flow_style=False)

            return True
        except Exception as e:
            self.logger.error(f"Error setting value: {e}")
            return False

    def _get_nested_value(self, d: Dict, key: str) -> Optional[Any]:
        """Get value from nested dictionary using dot notation"""
        try:
            for k in key.split("."):
                d = d[k]
            return d
        except (KeyError, TypeError):
            return None

    def reset_to_default(self, key: Optional[str] = None) -> bool:
        """Reset configuration to default"""
        try:
            if key:
                # Reset specific setting
                default_value = self._get_nested_value(
                    self._get_default_preferences(), key
                )
                if default_value is not None:
                    return self.set(key, default_value, save_to_preferences=True)
            else:
                # Reset all preferences
                self.user_preferences = self._get_default_preferences()
                self._save_user_preferences()
                self.settings_cache = {}
            return True
        except Exception as e:
            self.logger.error(f"Error resetting config: {e}")
            return False

    def export_settings(self, format: str = "yaml") -> Optional[str]:
        """Export all settings to file"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_data = {"config": self.config, "preferences": self.user_preferences}

            if format == "yaml":
                export_file = self.config_dir / f"settings_export_{timestamp}.yaml"
                with open(export_file, "w") as f:
                    yaml.dump(export_data, f, default_flow_style=False)
            else:
                export_file = self.config_dir / f"settings_export_{timestamp}.json"
                with open(export_file, "w") as f:
                    json.dump(export_data, f, indent=2)

            return str(export_file)
        except Exception as e:
            self.logger.error(f"Error exporting settings: {e}")
            return None

    def import_settings(self, filepath: str) -> bool:
        """Import settings from file"""
        try:
            path = Path(filepath)
            if not path.exists():
                return False

            if path.suffix == ".yaml":
                with open(path, "r") as f:
                    data = yaml.safe_load(f)
            elif path.suffix == ".json":
                with open(path, "r") as f:
                    data = json.load(f)
            else:
                return False

            if "config" in data:
                self.config = data["config"]
                with open(self.config_file, "w") as f:
                    yaml.dump(self.config, f, default_flow_style=False)

            if "preferences" in data:
                self.user_preferences = data["preferences"]
                self._save_user_preferences()

            self.settings_cache = {}
            return True
        except Exception as e:
            self.logger.error(f"Error importing settings: {e}")
            return False
