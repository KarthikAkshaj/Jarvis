import re
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
import logging


class VoiceCommandProcessor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # Common phrases to clean up
        self.filler_words = [
            "please",
            "could you",
            "would you",
            "can you",
            "i want to",
            "i would like to",
            "i'd like to",
            "i need to",
            "just",
            "um",
            "uh",
            "like",
        ]

        # Command patterns for better recognition
        self.command_patterns = {
            "open": r"(?:open|launch|start|run)\s+(?:the\s+)?(\w+)",
            "play": r'(?:play|start)\s+(?:the\s+)?(?:song|music|track)?\s*["\']?([^"\']+)["\']?',
            "weather": r"(?:weather|temperature|forecast)(?:\s+in\s+|\s+for\s+)?([a-zA-Z\s]+)?",
            "timer": r"(?:set|start)?\s*(?:a|the)?\s*timer\s+(?:for\s+)?(\d+)\s*(minutes?|mins?|hours?|hrs?)",
            "volume": r"(?:set|change|adjust)?\s*(?:the)?\s*volume\s+(?:to\s+)?(\d+)",
            "reminder": r"remind\s+(?:me\s+)?(?:to\s+)?(.+?)(?:\s+at\s+|\s+on\s+)?(\d{1,2}(?::\d{2})?\s*(?:am|pm)?)?",
        }

    def clean_command(self, command: str) -> str:
        """Remove filler words and normalize command"""
        command = command.lower().strip()

        # Remove filler words
        for word in self.filler_words:
            command = command.replace(word, "")

        # Remove multiple spaces
        command = " ".join(command.split())

        return command

    def extract_command_details(self, command: str) -> Tuple[str, Dict]:
        """Extract command type and parameters"""
        command = self.clean_command(command)
        details = {}

        try:
            # Check each command pattern
            for cmd_type, pattern in self.command_patterns.items():
                match = re.search(pattern, command)
                if match:
                    if cmd_type == "timer":
                        amount = match.group(1)
                        unit = match.group(2)
                        details["duration"] = self._parse_duration(amount, unit)
                    elif cmd_type == "reminder":
                        action = match.group(1)
                        time_str = match.group(2)
                        details["action"] = action
                        details["time"] = self._parse_time(time_str)
                    else:
                        details["parameter"] = match.group(1)
                    return cmd_type, details

            # If no pattern matches, try to identify intent
            return self._identify_intent(command), details

        except Exception as e:
            self.logger.error(f"Error extracting command details: {e}")
            return "unknown", {}

    def _parse_duration(self, amount: str, unit: str) -> int:
        """Convert duration to minutes"""
        try:
            amount = int(amount)
            if "hour" in unit or "hr" in unit:
                return amount * 60
            return amount
        except:
            return 0

    def _parse_time(self, time_str: Optional[str]) -> Optional[datetime]:
        """Parse time string into datetime"""
        if not time_str:
            return None

        try:
            # Try different time formats
            formats = ["%I:%M %p", "%H:%M", "%I%p", "%H"]

            for fmt in formats:
                try:
                    time = datetime.strptime(time_str, fmt).time()
                    return datetime.combine(datetime.now().date(), time)
                except ValueError:
                    continue

            return None

        except Exception:
            return None

    def _identify_intent(self, command: str) -> str:
        """Try to identify command intent when no pattern matches"""
        # Check for common keywords
        if any(word in command for word in ["note", "write", "record"]):
            return "note"
        elif any(word in command for word in ["search", "find", "look"]):
            return "search"
        elif any(word in command for word in ["schedule", "calendar", "event"]):
            return "calendar"
        elif any(word in command for word in ["brightness", "screen"]):
            return "brightness"
        elif any(word in command for word in ["shutdown", "restart", "sleep"]):
            return "system"

        return "chat"  # Default to chat if no intent identified

    def enhance_error_message(self, command_type: str, error: Exception) -> str:
        """Generate user-friendly error message"""
        error_str = str(error).lower()

        if "permission" in error_str:
            return f"I don't have permission to {command_type}. Try running with administrator privileges."
        elif "not found" in error_str:
            return f"I couldn't find what you asked for. Please check if it exists."
        elif "timeout" in error_str:
            return "The operation timed out. Please check your internet connection."
        elif "connection" in error_str:
            return (
                "I'm having trouble connecting. Please check your internet connection."
            )

        return (
            f"I encountered an error while trying to {command_type}. Please try again."
        )

    def suggest_correction(self, command: str) -> Optional[str]:
        """Suggest corrections for common command mistakes"""
        common_corrections = {
            "vol": "volume",
            "reminder": "remind me",
            "screen shot": "screenshot",
            "mail": "email",
            "wheather": "weather",
            "weather like": "weather",
        }

        for wrong, correct in common_corrections.items():
            if wrong in command:
                return command.replace(wrong, correct)

        return None
