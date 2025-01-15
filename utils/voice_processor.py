import re
from typing import Optional, Tuple, List, Dict
from difflib import get_close_matches


class VoiceProcessor:
    def __init__(self):
        self.command_patterns = {
            "open": [
                r"open (?:up |the |an? )?(?P<app>.*)",
                r"launch (?:the )?(?P<app>.*)",
                r"start (?:up |the )?(?P<app>.*)",
            ],
            "play": [
                r"play (?:the |some )?(?P<item>.*)",
                r"start playing (?P<item>.*)",
                r"listen to (?P<item>.*)",
            ],
            "search": [
                r"search (?:for )?(?P<query>.*?)(?: on| in) (?P<platform>.*)",
                r"look (?:up |for )?(?P<query>.*?)(?: on| in) (?P<platform>.*)",
                r"find (?:me )?(?P<query>.*?)(?: on| in) (?P<platform>.*)",
            ],
            "volume": [
                r"(?:set |change |adjust )?volume(?: to| at)? (?P<level>\d+)(?:\s*percent)?",
                r"turn (?:the )?volume (?P<direction>up|down)(?: by (?P<amount>\d+))?",
                r"(?P<action>mute|unmute)(?: the)? volume",
            ],
            "timer": [
                r"set (?:a |the )?timer (?:for )?(?P<duration>.*)",
                r"remind me in (?P<duration>.*)",
                r"wake me (?:up )?in (?P<duration>.*)",
            ],
            "reminder": [
                r"remind me to (?P<task>.*?) (?:at|on) (?P<time>.*)",
                r"set (?:a |the )?reminder (?:for |to )?(?P<task>.*?) (?:at|on) (?P<time>.*)",
            ],
        }

        # Common word replacements
        self.word_replacements = {
            "spotify": ["spotifi", "sporify", "spot if i"],
            "chrome": ["google chrome", "chrome browser"],
            "firefox": ["fire fox", "mozilla", "firefox browser"],
            "notepad": ["note pad", "text editor"],
            "calculator": ["calc", "calculate"],
        }

        # Initialize command matching
        self.commands_list = []
        for patterns in self.command_patterns.values():
            for pattern in patterns:
                self.commands_list.append(pattern)

    def preprocess_text(self, text: str) -> str:
        """Clean and normalize text"""
        text = text.lower().strip()

        # Replace common word variations
        for correct, variations in self.word_replacements.items():
            for var in variations:
                text = text.replace(var, correct)

        # Remove multiple spaces
        text = " ".join(text.split())

        return text

    def extract_command_parts(self, text: str) -> Tuple[str, Dict[str, str]]:
        """Extract command and parameters from text"""
        text = self.preprocess_text(text)

        for command_type, patterns in self.command_patterns.items():
            for pattern in patterns:
                match = re.match(pattern, text)
                if match:
                    params = match.groupdict()
                    return command_type, params

        return "unknown", {}

    def get_command_confidence(self, text: str, command_type: str) -> float:
        """Calculate confidence score for command recognition"""
        text = self.preprocess_text(text)

        if command_type not in self.command_patterns:
            return 0.0

        # Check exact matches
        for pattern in self.command_patterns[command_type]:
            if re.match(pattern, text):
                return 1.0

        # Check partial matches
        max_confidence = 0.0
        for pattern in self.command_patterns[command_type]:
            # Convert pattern to words for comparison
            pattern_words = re.sub(r"\([^)]*\)", "", pattern).split()
            text_words = text.split()

            # Calculate word overlap
            matching_words = sum(1 for word in pattern_words if word in text_words)
            confidence = matching_words / len(pattern_words)

            max_confidence = max(max_confidence, confidence)

        return max_confidence

    def suggest_corrections(self, text: str) -> List[str]:
        """Suggest corrections for misheard commands"""
        text = self.preprocess_text(text)
        suggestions = []

        # Check each command pattern
        for command_type, patterns in self.command_patterns.items():
            for pattern in patterns:
                # Convert pattern to example command
                example = re.sub(r"\(\?P<[^>]+>[^)]+\)", "something", pattern)
                example = re.sub(r"[\(\|\)\\]", "", example)

                # Calculate similarity
                if self.get_command_confidence(text, command_type) > 0.5:
                    suggestions.append(example)

        return suggestions[:3]  # Return top 3 suggestions

    def validate_parameters(self, command_type: str, params: Dict[str, str]) -> bool:
        """Validate extracted command parameters"""
        if command_type == "volume":
            if "level" in params:
                try:
                    level = int(params["level"])
                    return 0 <= level <= 100
                except ValueError:
                    return False

        elif command_type == "timer":
            if "duration" in params:
                # Check if duration contains numbers and time units
                return bool(
                    re.search(r"\d+\s*(?:second|minute|hour|day)", params["duration"])
                )

        return True

    def format_command_response(self, command_type: str, params: Dict[str, str]) -> str:
        """Format command for confirmation"""
        if command_type == "open":
            return f"Opening {params.get('app', 'application')}"
        elif command_type == "play":
            return f"Playing {params.get('item', 'media')}"
        elif command_type == "search":
            return f"Searching for {params.get('query', '')} on {params.get('platform', 'Google')}"
        elif command_type == "volume":
            if "level" in params:
                return f"Setting volume to {params['level']}%"
            elif "direction" in params:
                return f"Turning volume {params['direction']}"
        elif command_type == "timer":
            return f"Setting timer for {params.get('duration', '')}"
        elif command_type == "reminder":
            return f"Setting reminder for {params.get('task', '')} at {params.get('time', '')}"

        return "Processing command"
