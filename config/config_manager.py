import os


class ConfigManager:
    def __init__(self, config_file="config.yaml"):
        self.config_file = config_file
        self.config = self._load_config()

    def _load_config(self):
        config = {
            "audio": {
                "chunk_size": 1024,
                "sample_rate": 16000,
                "channels": 1,
                "record_seconds": 5,
            },
            "paths": {
                "audio_output": os.getenv("AUDIO_OUTPUT_PATH", "audio/"),
                "screenshots": os.getenv("SCREENSHOTS_PATH", "screenshots/"),
                "recordings": os.getenv("RECORDINGS_PATH", "screen_recordings/"),
                "models": os.getenv("MODELS_PATH", "models/"),
            },
            "api_keys": {
                "gemini": os.getenv("GEMINI_API_KEY"),
                "picovoice": os.getenv("PICOVOICE_ACCESS_KEY"),
            },
        }
        return config

    def get(self, key, default=None):
        try:
            keys = key.split(".")
            value = self.config
            for k in keys:
                value = value.get(k, default)
            return value
        except Exception:
            return os.getenv(key.upper(), default)
