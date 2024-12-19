import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path
import logging


class CalendarManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.data_dir = Path("data/calendar")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.events_file = self.data_dir / "events.json"
        self.events: Dict[str, dict] = {}
        self.load_events()

    def load_events(self):
        """Load events from file"""
        try:
            if self.events_file.exists():
                with open(self.events_file, "r") as f:
                    events_data = json.load(f)
                    # Convert string dates back to datetime
                    self.events = {
                        k: {**v, "datetime": datetime.fromisoformat(v["datetime"])}
                        for k, v in events_data.items()
                    }
        except Exception as e:
            self.logger.error(f"Error loading events: {e}")

    def save_events(self):
        """Save events to file"""
        try:
            events_data = {
                k: {**v, "datetime": v["datetime"].isoformat()}
                for k, v in self.events.items()
            }
            with open(self.events_file, "w") as f:
                json.dump(events_data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving events: {e}")

    def add_event(
        self,
        title: str,
        date_time: datetime,
        description: str = "",
        duration: int = 60,
        reminder: bool = True,
    ) -> str:
        """Add a new event"""
        try:
            event_id = f"event_{len(self.events) + 1}"
            self.events[event_id] = {
                "title": title,
                "datetime": date_time,
                "description": description,
                "duration": duration,  # in minutes
                "reminder": reminder,
            }
            self.save_events()
            return (
                f"Event '{title}' added for {date_time.strftime('%B %d at %I:%M %p')}"
            )
        except Exception as e:
            self.logger.error(f"Error adding event: {e}")
            return "Failed to add event"

    def get_events(
        self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None
    ) -> List[dict]:
        """Get events within date range"""
        try:
            if not start_date:
                start_date = datetime.now()
            if not end_date:
                end_date = start_date + timedelta(days=7)

            filtered_events = []
            for event_id, event in self.events.items():
                event_date = event["datetime"]
                if start_date <= event_date <= end_date:
                    filtered_events.append({"id": event_id, **event})

            return sorted(filtered_events, key=lambda x: x["datetime"])
        except Exception as e:
            self.logger.error(f"Error getting events: {e}")
            return []

    def get_upcoming_events(self, days: int = 7) -> List[dict]:
        """Get upcoming events for the next N days"""
        start_date = datetime.now()
        end_date = start_date + timedelta(days=days)
        return self.get_events(start_date, end_date)

    def delete_event(self, event_id: str) -> str:
        """Delete an event by ID"""
        try:
            if event_id in self.events:
                event = self.events.pop(event_id)
                self.save_events()
                return f"Event '{event['title']}' deleted"
            return "Event not found"
        except Exception as e:
            self.logger.error(f"Error deleting event: {e}")
            return "Failed to delete event"

    def update_event(self, event_id: str, **updates) -> str:
        """Update an existing event"""
        try:
            if event_id in self.events:
                event = self.events[event_id]
                event.update(updates)
                self.save_events()
                return f"Event '{event['title']}' updated"
            return "Event not found"
        except Exception as e:
            self.logger.error(f"Error updating event: {e}")
            return "Failed to update event"

    def get_today_events(self) -> List[dict]:
        """Get events for today"""
        today = datetime.now()
        tomorrow = today + timedelta(days=1)
        today = today.replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow = tomorrow.replace(hour=0, minute=0, second=0, microsecond=0)
        return self.get_events(today, tomorrow)

    def format_events_response(self, events: List[dict]) -> str:
        """Format events list into readable response"""
        if not events:
            return "No events found."

        response = []
        for event in events:
            time_str = event["datetime"].strftime("%I:%M %p")
            response.append(f"- {event['title']} at {time_str}")
            if event["description"]:
                response.append(f"  Description: {event['description']}")

        return "\n".join(response)
