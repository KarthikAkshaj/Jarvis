import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List
import json
import os


class ReminderSystem:
    def __init__(self):
        self.reminders: Dict[str, datetime] = {}
        self.timers: Dict[str, datetime] = {}
        self.reminder_file = "data/reminders.json"
        self.load_reminders()

        # Start the checking thread
        self.running = True
        self.check_thread = threading.Thread(target=self._check_reminders_and_timers)
        self.check_thread.daemon = True
        self.check_thread.start()

    def load_reminders(self):
        """Load saved reminders from file"""
        try:
            os.makedirs("data", exist_ok=True)
            if os.path.exists(self.reminder_file):
                with open(self.reminder_file, "r") as f:
                    data = json.load(f)
                    self.reminders = {
                        k: datetime.fromisoformat(v) for k, v in data.items()
                    }
        except Exception as e:
            print(f"Error loading reminders: {e}")

    def save_reminders(self):
        """Save reminders to file"""
        try:
            with open(self.reminder_file, "w") as f:
                data = {k: v.isoformat() for k, v in self.reminders.items()}
                json.dump(data, f)
        except Exception as e:
            print(f"Error saving reminders: {e}")

    def _parse_time(self, time_str: str) -> datetime:
        """Parse time string into datetime"""
        try:
            # Try parsing various time formats
            time_formats = [
                "%I:%M %p",  # 3:30 PM
                "%H:%M",  # 15:30
                "%I %p",  # 3 PM
                "%H",  # 15
            ]

            for fmt in time_formats:
                try:
                    parsed_time = datetime.strptime(time_str, fmt).time()
                    return datetime.combine(datetime.today(), parsed_time)
                except ValueError:
                    continue

            # If not a specific time, try for relative time
            if "minutes" in time_str or "mins" in time_str:
                mins = int("".join(filter(str.isdigit, time_str)))
                return datetime.now() + timedelta(minutes=mins)
            elif "hours" in time_str or "hrs" in time_str:
                hrs = int("".join(filter(str.isdigit, time_str)))
                return datetime.now() + timedelta(hours=hrs)

            raise ValueError(f"Couldn't parse time: {time_str}")

        except Exception as e:
            raise ValueError(f"Error parsing time: {e}")

    def add_reminder(self, reminder_text: str, time_str: str) -> str:
        """Add a new reminder"""
        try:
            reminder_time = self._parse_time(time_str)
            if reminder_time < datetime.now():
                reminder_time += timedelta(days=1)

            self.reminders[reminder_text] = reminder_time
            self.save_reminders()

            return (
                f"Reminder set for {reminder_time.strftime('%I:%M %p')}: "
                f"{reminder_text}"
            )
        except Exception as e:
            return f"Sorry, I couldn't set that reminder: {e}"

    def set_timer(self, duration_str: str, label: str = "") -> str:
        """Set a timer"""
        try:
            # Parse duration (e.g., "5 minutes", "1 hour")
            if "minute" in duration_str or "min" in duration_str:
                mins = int("".join(filter(str.isdigit, duration_str)))
                end_time = datetime.now() + timedelta(minutes=mins)
            elif "hour" in duration_str or "hr" in duration_str:
                hrs = int("".join(filter(str.isdigit, duration_str)))
                end_time = datetime.now() + timedelta(hours=hrs)
            else:
                return "Please specify the duration in minutes or hours."

            self.timers[label or f"Timer {len(self.timers) + 1}"] = end_time
            return f"Timer set for {duration_str}"

        except Exception as e:
            return f"Sorry, I couldn't set that timer: {e}"

    def _check_reminders_and_timers(self):
        """Background thread to check reminders and timers"""
        while self.running:
            now = datetime.now()

            # Check reminders
            completed_reminders = []
            for text, time in self.reminders.items():
                if time <= now:
                    print(f"REMINDER: {text}")  # Replace with TTS
                    completed_reminders.append(text)

            # Remove completed reminders
            for reminder in completed_reminders:
                del self.reminders[reminder]
            if completed_reminders:
                self.save_reminders()

            # Check timers
            completed_timers = []
            for label, end_time in self.timers.items():
                if end_time <= now:
                    print(f"TIMER FINISHED: {label}")  # Replace with TTS
                    completed_timers.append(label)

            # Remove completed timers
            for timer in completed_timers:
                del self.timers[timer]

            time.sleep(1)  # Check every second

    def list_reminders(self) -> str:
        """List all active reminders"""
        if not self.reminders:
            return "No active reminders."

        response = "Active reminders:\n"
        for text, time in sorted(self.reminders.items(), key=lambda x: x[1]):
            response += f"- {text}: {time.strftime('%I:%M %p')}\n"
        return response

    def list_timers(self) -> str:
        """List all active timers"""
        if not self.timers:
            return "No active timers."

        response = "Active timers:\n"
        now = datetime.now()
        for label, end_time in self.timers.items():
            remaining = end_time - now
            minutes = remaining.total_seconds() // 60
            response += f"- {label}: {int(minutes)} minutes remaining\n"
        return response

    def cleanup(self):
        """Cleanup resources"""
        self.running = False
        if hasattr(self, "check_thread"):
            self.check_thread.join()
        self.save_reminders()
