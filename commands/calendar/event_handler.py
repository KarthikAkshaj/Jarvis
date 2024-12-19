from datetime import datetime, timedelta
import re
from typing import Optional, Tuple
from .calendar_manager import CalendarManager


class EventHandler:
    def __init__(self):
        self.calendar = CalendarManager()

    def _parse_date_time(self, date_str: str) -> Optional[datetime]:
        """Parse various date and time formats"""
        try:
            # Try common formats
            formats = [
                "%Y-%m-%d %H:%M",
                "%d/%m/%Y %H:%M",
                "%B %d at %I:%M %p",
                "%B %d %I:%M %p",
                "%d %B at %I:%M %p",
                "%d %B %I:%M %p",
            ]

            for fmt in formats:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue

            # Handle relative dates
            today = datetime.now()
            tomorrow = today + timedelta(days=1)

            if "today" in date_str.lower():
                time_str = re.search(
                    r"at\s+(\d{1,2}(?::\d{2})?(?:\s*[ap]m)?)", date_str.lower()
                )
                if time_str:
                    try:
                        time = datetime.strptime(time_str.group(1), "%I:%M %p").time()
                        return datetime.combine(today.date(), time)
                    except ValueError:
                        pass

            elif "tomorrow" in date_str.lower():
                time_str = re.search(
                    r"at\s+(\d{1,2}(?::\d{2})?(?:\s*[ap]m)?)", date_str.lower()
                )
                if time_str:
                    try:
                        time = datetime.strptime(time_str.group(1), "%I:%M %p").time()
                        return datetime.combine(tomorrow.date(), time)
                    except ValueError:
                        pass

            return None

        except Exception as e:
            print(f"Error parsing date time: {e}")
            return None

    def process_event_command(self, command: str) -> str:
        """Process calendar-related commands"""
        command = command.lower()

        try:
            # Add event
            if "add event" in command or "schedule" in command:
                # Extract event details
                title_match = re.search(
                    r"(?:called|titled|named)\s+['\"](.*?)['\"]", command
                )
                if not title_match:
                    return "Please specify an event title (in quotes)"

                title = title_match.group(1)

                # Extract date/time
                date_str = (
                    command.split(" at ", 1)[1].strip() if " at " in command else ""
                )
                if not date_str:
                    return "Please specify when the event should occur"

                date_time = self._parse_date_time(date_str)
                if not date_time:
                    return "I couldn't understand the date and time format"

                # Extract description if provided
                desc_match = re.search(r"description\s+['\"](.*?)['\"]", command)
                description = desc_match.group(1) if desc_match else ""

                return self.calendar.add_event(title, date_time, description)

            # List events
            elif (
                "list events" in command
                or "show events" in command
                or "what events" in command
            ):
                if "today" in command:
                    events = self.calendar.get_today_events()
                else:
                    events = self.calendar.get_upcoming_events()
                return self.calendar.format_events_response(events)

            # Delete event
            elif "delete event" in command or "remove event" in command:
                title_match = re.search(
                    r"(?:called|titled|named)\s+['\"](.*?)['\"]", command
                )
                if not title_match:
                    return "Please specify which event to delete (in quotes)"

                title = title_match.group(1)
                # Find event by title
                for event_id, event in self.calendar.events.items():
                    if event["title"].lower() == title.lower():
                        return self.calendar.delete_event(event_id)

                return "Event not found"

            else:
                return "I'm not sure what you want to do with the calendar. Try adding or listing events."

        except Exception as e:
            print(f"Error processing event command: {e}")
            return "Sorry, I couldn't process that calendar command"
