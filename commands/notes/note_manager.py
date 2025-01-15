import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import logging


class NoteManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.data_dir = Path("data/notes")
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Files for storage
        self.notes_file = self.data_dir / "notes.json"
        self.notes: Dict[str, dict] = {}
        self.load_notes()

    def load_notes(self):
        """Load notes from file"""
        try:
            if self.notes_file.exists():
                with open(self.notes_file, "r") as f:
                    notes_data = json.load(f)
                    self.notes = {
                        k: {**v, "created_at": datetime.fromisoformat(v["created_at"])}
                        for k, v in notes_data.items()
                    }
        except Exception as e:
            self.logger.error(f"Error loading notes: {e}")

    def save_notes(self):
        """Save notes to file"""
        try:
            notes_data = {
                k: {**v, "created_at": v["created_at"].isoformat()}
                for k, v in self.notes.items()
            }
            with open(self.notes_file, "w") as f:
                json.dump(notes_data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving notes: {e}")

    def add_note(
        self, content: str, title: Optional[str] = None, tags: List[str] = None
    ) -> str:
        """Add a new note"""
        try:
            # Generate title from content if not provided
            if not title:
                title = f"Note_{len(self.notes) + 1}"

            note_id = f"note_{len(self.notes) + 1}"
            self.notes[note_id] = {
                "title": title,
                "content": content,
                "tags": tags or [],
                "created_at": datetime.now(),
                "is_voice_memo": False,
            }
            self.save_notes()
            return f"Note '{title}' saved successfully"
        except Exception as e:
            self.logger.error(f"Error adding note: {e}")
            return "Failed to save note"

    def get_notes(self, tag: Optional[str] = None) -> List[dict]:
        """Get all notes, optionally filtered by tag"""
        try:
            filtered_notes = []
            for note_id, note in self.notes.items():
                if not tag or tag in note["tags"]:
                    filtered_notes.append({"id": note_id, **note})
            return sorted(filtered_notes, key=lambda x: x["created_at"], reverse=True)
        except Exception as e:
            self.logger.error(f"Error getting notes: {e}")
            return []

    def delete_note(self, note_id: str) -> str:
        """Delete a note by ID"""
        try:
            if note_id in self.notes:
                note = self.notes.pop(note_id)
                self.save_notes()
                return f"Note '{note['title']}' deleted"
            return "Note not found"
        except Exception as e:
            self.logger.error(f"Error deleting note: {e}")
            return "Failed to delete note"

    def search_notes(self, query: str) -> List[dict]:
        """Search notes by content"""
        try:
            query = query.lower()
            results = []
            for note_id, note in self.notes.items():
                if (
                    query in note["content"].lower()
                    or query in note["title"].lower()
                    or any(query in tag.lower() for tag in note["tags"])
                ):
                    results.append({"id": note_id, **note})
            return sorted(results, key=lambda x: x["created_at"], reverse=True)
        except Exception as e:
            self.logger.error(f"Error searching notes: {e}")
            return []

    def format_notes_response(self, notes: List[dict]) -> str:
        """Format notes list into readable response"""
        if not notes:
            return "No notes found."

        response = []
        for note in notes:
            date_str = note["created_at"].strftime("%B %d, %Y")
            response.append(f"- {note['title']} (Created: {date_str})")
            if len(note["content"]) > 100:
                response.append(f"  {note['content'][:100]}...")
            else:
                response.append(f"  {note['content']}")
            if note["tags"]:
                response.append(f"  Tags: {', '.join(note['tags'])}")
            response.append("")

        return "\n".join(response)

    def export_notes(self, format: str = "txt") -> str:
        """Export all notes to a file"""
        try:
            export_file = (
                self.data_dir
                / f"notes_export_{datetime.now().strftime('%Y%m%d')}.{format}"
            )

            if format == "txt":
                with open(export_file, "w") as f:
                    for note in self.get_notes():
                        f.write(f"Title: {note['title']}\n")
                        f.write(f"Date: {note['created_at'].strftime('%B %d, %Y')}\n")
                        f.write(f"Tags: {', '.join(note['tags'])}\n\n")
                        f.write(f"{note['content']}\n")
                        f.write("\n" + "=" * 50 + "\n\n")

            elif format == "json":
                notes_data = {
                    k: {**v, "created_at": v["created_at"].isoformat()}
                    for k, v in self.notes.items()
                }
                with open(export_file, "w") as f:
                    json.dump(notes_data, f, indent=2)

            return f"Notes exported to {export_file}"
        except Exception as e:
            self.logger.error(f"Error exporting notes: {e}")
            return "Failed to export notes"
