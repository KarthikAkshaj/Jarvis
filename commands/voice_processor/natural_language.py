from typing import Dict, List, Optional
import re
from datetime import datetime, timedelta


class NaturalLanguageProcessor:
    def __init__(self):
        # Time-related patterns
        self.time_patterns = {
            "in (\d+) (minute|hour|day)s?": self._handle_relative_time,
            "at (\d{1,2}(?::\d{2})?\s*(?:am|pm))": self._handle_specific_time,
            "tomorrow at (\d{1,2}(?::\d{2})?\s*(?:am|pm))": self._handle_tomorrow_time,
            "next (week|month|year)": self._handle_next_period,
        }

        # Quantity patterns
        self.quantity_patterns = {
            "increase|raise|up": 1,
            "decrease|lower|down": -1,
            "max|maximum|full": 100,
            "min|minimum|zero": 0,
        }

        # Location patterns
        self.location_words = ["in", "at", "for", "near"]

    def parse_time_expression(self, text: str) -> Optional[datetime]:
        """Parse natural time expressions"""
        text = text.lower()

        for pattern, handler in self.time_patterns.items():
            match = re.search(pattern, text)
            if match:
                return handler(match)

        return None

    def _handle_relative_time(self, match) -> datetime:
        """Handle relative time expressions (in X minutes/hours/days)"""
        amount = int(match.group(1))
        unit = match.group(2)

        now = datetime.now()
        if unit == "minute":
            return now + timedelta(minutes=amount)
        elif unit == "hour":
            return now + timedelta(hours=amount)
        elif unit == "day":
            return now + timedelta(days=amount)

        return now

    def _handle_specific_time(self, match) -> datetime:
        """Handle specific time expressions (at X:XX am/pm)"""
        time_str = match.group(1)
        try:
            time = datetime.strptime(time_str, "%I:%M %p").time()
            return datetime.combine(datetime.now().date(), time)
        except ValueError:
            try:
                time = datetime.strptime(time_str, "%I %p").time()
                return datetime.combine(datetime.now().date(), time)
            except ValueError:
                return datetime.now()

    def _handle_tomorrow_time(self, match) -> datetime:
        """Handle tomorrow time expressions"""
        time_str = match.group(1)
        try:
            time = datetime.strptime(time_str, "%I:%M %p").time()
            tomorrow = datetime.now().date() + timedelta(days=1)
            return datetime.combine(tomorrow, time)
        except ValueError:
            try:
                time = datetime.strptime(time_str, "%I %p").time()
                tomorrow = datetime.now().date() + timedelta(days=1)
                return datetime.combine(tomorrow, time)
            except ValueError:
                return datetime.now() + timedelta(days=1)

    def _handle_next_period(self, match) -> datetime:
        """Handle 'next week/month/year' expressions"""
        period = match.group(1)
        now = datetime.now()

        if period == "week":
            return now + timedelta(days=7)
        elif period == "month":
            # Roughly one month
            return now + timedelta(days=30)
        elif period == "year":
            return now.replace(year=now.year + 1)

        return now

    def parse_quantity(self, text: str) -> Optional[int]:
        """Parse quantity expressions"""
        text = text.lower()

        # Check for percentage
        match = re.search(r"(\d+)\s*(?:percent|%)", text)
        if match:
            return min(100, max(0, int(match.group(1))))

        # Check for descriptive terms
        for pattern, value in self.quantity_patterns.items():
            if re.search(pattern, text):
                return value

        # Check for number words
        number_words = {
            "zero": 0,
            "one": 1,
            "two": 2,
            "three": 3,
            "four": 4,
            "five": 5,
            "six": 6,
            "seven": 7,
            "eight": 8,
            "nine": 9,
            "ten": 10,
            "half": 50,
            "quarter": 25,
        }

        for word, value in number_words.items():
            if word in text:
                return value

        return None

    def parse_location(self, text: str) -> Optional[str]:
        """Extract location from text"""
        text = text.lower()

        # Try to find location after location words
        for word in self.location_words:
            pattern = f"{word}\\s+([a-zA-Z\\s]+?)(?:\\s+|$)"
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()

        return None

    def get_sentiment(self, text: str) -> float:
        """Basic sentiment analysis (-1 to 1)"""
        positive_words = [
            "good",
            "great",
            "awesome",
            "excellent",
            "happy",
            "love",
            "wonderful",
        ]
        negative_words = ["bad", "terrible", "awful", "horrible", "sad", "hate", "poor"]

        text = text.lower()
        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)

        total = positive_count + negative_count
        if total == 0:
            return 0

        return (positive_count - negative_count) / total

    def extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords from text"""
        # Remove common stop words
        stop_words = {
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "is",
            "are",
        }
        words = text.lower().split()
        keywords = [word for word in words if word not in stop_words]
        return keywords
